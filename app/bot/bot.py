import os
from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Callable, Optional

import telebot
from loguru import logger
from telebot.types import Message

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


@dataclass
class InteractionResult:
    status: SendStatus
    item: Optional[Item] = None
    reason: Optional[str] = None
    file: Optional[BytesIO] = None


class AccessControl:

    env_key = "AUTHORIZED_TESTERS_TG_IDS"

    def __init__(self) -> None:
        self.allowed_ids = self._parse_env(self.env_key)

    @staticmethod
    def _parse_env(env_var: str) -> set:
        raw = os.getenv(env_var, "")
        return set(map(int, raw.split(","))) if raw else set()

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self.allowed_ids


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
        self.service = service
        self.bot = bot
        self.access = access
        self.sender = TelegramSender(bot, service)

    def help(self, message: Message) -> None:
        self.bot.reply_to(message, "Ask the Oracle by using /ask_oracle.")

    def random(self, message: Message) -> None:
        user_id = message.from_user.id

        if not self.access.is_authorized(user_id):
            self.bot.reply_to(message, "Unknown command.")
            return

        try:
            item = self.service.get_random_item()
        except (DatabaseError, ItemNotFoundError):
            self.bot.reply_to(message, "Failed to get random item from service layer")
            return
        except Exception:
            self.bot.reply_to(message, "Unexpected error occurred.")
            return

        if not item:
            self.bot.reply_to(message, "No prophecies found.")
            return

        result = self.sender.send_item(message, item)
        if result.status != SendStatus.SUCCESS:
            self.bot.reply_to(message, "Failed to send object")

    def ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id

        items = self.service.get_candidate_items(user_id)
        if items is None:
            self.bot.reply_to(message, "Come back tomorrow for more wisdom.")
            logger.info(f"User {user_id} got message of hitting daily limit")
            return
        if not items:
            self.bot.reply_to(message, "No prophecies found.")
            logger.warning(f"Didn't find any candidates for user {user_id}")
            return

        for item in items:
            result = self.sender.send_item(message, item)
            if result.status == SendStatus.SUCCESS:
                try:
                    self.service.log_interaction(user_id, item.id)
                except DatabaseError:
                    logger.error(f"Failed to log interaction for user {user_id} and item {item.id}")
                except Exception as e:
                    logger.error(f"Unexpected error while logging: {e}")
                return

        self.bot.reply_to(message, "No prophecies found.")


class TelegramSender:
    def __init__(self, bot: telebot.TeleBot, service: MemeOracleService):
        self.bot = bot
        self.service = service

    def send_item(self, message: Message, item: Item) -> InteractionResult:
        get_result = self._get_object(item)
        if get_result.status != SendStatus.SUCCESS:
            return get_result
        return self._send_object(message, item, get_result.file)

    def _get_object(self, item: Item) -> InteractionResult:
        try:
            s3_object = self.service.get_object(item.s3_name)
            return InteractionResult(status=SendStatus.SUCCESS, item=item, file=s3_object)
        except (ObjectNotFoundError, StorageError) as e:
            logger.error(f"S3 object error for object {item.s3_name}: {e}")
            return InteractionResult(status=SendStatus.S3_ERROR, item=item, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected S3 error for object {item.s3_name}: {e}")
            return InteractionResult(status=SendStatus.UNKNOWN_ERROR, item=item, reason=str(e))

    def _send_object(self, message: Message, item: Item, s3_object: BytesIO) -> InteractionResult:
        user_id = message.from_user.id
        chat_id = message.chat.id
        send_method = self._get_send_method(item.type)
        if send_method is None:
            logger.error(f"Invalid item type '{item.type}' for item: {item}")
            return InteractionResult(status=SendStatus.INVALID_TYPE, item=item, reason="Invalid type")

        try:
            send_method(chat_id, s3_object)
            logger.info(f"Sent {item.type} to {user_id}, item: {item}")
            return InteractionResult(status=SendStatus.SUCCESS, item=item)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Telegram error for {item.s3_name} to {user_id}: {e}")
            return InteractionResult(status=SendStatus.TELEGRAM_ERROR, item=item, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected Telegram error for {item.s3_name} to {user_id}: {e}")
            return InteractionResult(status=SendStatus.UNKNOWN_ERROR, item=item, reason=str(e))

    def _get_send_method(self, item_type: ItemType) -> Optional[Callable]:
        return {
            "image": self.bot.send_photo,
            "video": self.bot.send_video,
        }.get(item_type)
