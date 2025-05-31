from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Callable, Optional, Union

import telebot
from loguru import logger
from telebot.types import Message

from app.bot.access import AccessControl
from app.database.exceptions import DatabaseError, ItemNotFoundError
from app.database.models import Item, ItemType
from app.service.facade import MemeOracleService
from app.storage.exceptions import ObjectNotFoundError, StorageError


class SendStatus(Enum):
    SUCCESS = 1
    INVALID_TYPE = 2
    TELEGRAM_ERROR = 3
    S3_ERROR = 4
    DB_ERROR = 5
    UNKNOWN_ERROR = 6
    LIMIT_REACHED = 7
    NO_CANDIDATES = 8
    SEND_FAILED = 9


# @dataclass
# class InteractionResult:
#     status: SendStatus
#     item: Optional[Item] = None
#     reason: Optional[str] = None
#     file: Optional[BytesIO] = None


@dataclass
class InteractionResultBase:
    status: SendStatus


@dataclass
class SuccessResult(InteractionResultBase):
    item: Item
    file: BytesIO


@dataclass
class FailureResult(InteractionResultBase):
    reason: Optional[str] = None


InteractionResult = Union[SuccessResult, FailureResult]


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, token: str) -> None:
        self.bot = telebot.TeleBot(token)
        self.handler = CommandHandler(service, self.bot, AccessControl())
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.bot.message_handler(commands=["ask_oracle"])(self.handler.ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handler.random)
        self.bot.message_handler(commands=["help"])(self.handler.help)

    def run(self) -> None:
        self.bot.infinity_polling()


class CommandHandler:
    def __init__(self, service: MemeOracleService, bot: telebot.TeleBot, access: AccessControl):
        self.bot = bot
        self.access = access
        self.sender = TelegramSender(bot)
        self.interactor = OracleInteractor(service)

    def _reply(self, message: Message, text: str) -> None:
        self.bot.reply_to(message, text)

    def help(self, message: Message) -> None:
        self._reply(message, "Ask the Oracle by using `/ask_oracle`.")

    # only for testers and devs
    def random(self, message: Message) -> None:
        user_id = message.from_user.id

        if not self.access.is_tester(user_id):
            self._reply(message, "Unknown command.")
            return

        result = self.interactor.get_random()
        if isinstance(result, FailureResult):
            self._reply(message, result.reason or "Something went wrong.")
            return

        self.sender.send(message, result.item, result.file)

    def ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id
        result = self.interactor.get_next_available(user_id)

        if isinstance(result, SuccessResult):
            self.sender.send(message, result.item, result.file)
            return

        # Handle failure sends
        match result.status:
            case SendStatus.LIMIT_REACHED:
                self._reply(message, "Oracle is tired, come back tomorrow.")
            case SendStatus.NO_CANDIDATES:
                self._reply(message, "No prophecies found.")
            case SendStatus.SEND_FAILED:
                self._reply(message, "Failed to send prophecy.")
            case _:
                self._reply(message, "Something went wrong.")


class OracleInteractor:
    def __init__(self, service: MemeOracleService):
        self.service = service

    def _get_file(self, item: Item) -> InteractionResult:
        try:
            file = self.service.get_object(item.s3_name)
            return SuccessResult(status=SendStatus.SUCCESS, item=item, file=file)
        except (ObjectNotFoundError, StorageError) as e:
            logger.error(f"S3 object error for object {item.s3_name}: {e}")
            return FailureResult(status=SendStatus.S3_ERROR, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected S3 error for object {item.s3_name}: {e}")
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason=str(e))

    def get_random(self) -> InteractionResult:
        try:
            item = self.service.get_random_item()
        except (DatabaseError, ItemNotFoundError) as e:
            logger.warning(f"Get random item error: {e}")
            return FailureResult(status=SendStatus.DB_ERROR, reason="Failed to get random item.")
        except Exception as e:
            logger.exception(f"Unexpected error in get_random: {e}")
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason="Unexpected error occurred.")

        if not item:
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason="No prophecies found.")

        file_result = self._get_file(item)
        if file_result.status != SendStatus.SUCCESS:
            return file_result

        return file_result

    def get_next_available(self, user_id: int) -> InteractionResult:
        items = self.service.get_candidate_items(user_id)

        if items is None:
            logger.info(f"User {user_id} hit daily limit")
            return FailureResult(status=SendStatus.LIMIT_REACHED)

        if not items:
            logger.warning(f"No candidates for user {user_id}")
            return FailureResult(status=SendStatus.NO_CANDIDATES)

        for item in items:
            file_result = self._get_file(item)
            if file_result.status != SendStatus.SUCCESS:
                continue

            try:
                self.service.log_interaction(user_id, item.id)
            except Exception as e:
                logger.warning(f"Interaction logging failed for user {user_id}, item {item.id}: {e}")
            file_result.status = SendStatus.SUCCESS
            return file_result

        return FailureResult(status=SendStatus.SEND_FAILED)


class TelegramSender:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.send_methods: dict[ItemType, Callable] = {
            "image": self.bot.send_photo,
            "video": self.bot.send_video,
        }

    def send(self, message: Message, item: Item, file: BytesIO) -> InteractionResult:
        chat_id = message.chat.id
        user_id = message.from_user.id

        send_method = self.send_methods.get(item.type)
        if send_method is None:
            logger.error(f"Invalid item type '{item.type}' for item: {item}")
            return FailureResult(status=SendStatus.INVALID_TYPE, reason="Invalid type")

        try:
            send_method(chat_id, file)
            logger.info(f"Sent {item.type} to {user_id}, item: {item}")
            return SuccessResult(status=SendStatus.SUCCESS, item=item, file=file)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Telegram error for {item.s3_name} to {user_id}: {e}")
            return FailureResult(status=SendStatus.TELEGRAM_ERROR, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected Telegram error for {item.s3_name} to {user_id}: {e}")
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason=str(e))
