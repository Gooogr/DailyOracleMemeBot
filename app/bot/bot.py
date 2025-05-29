import os
from enum import Enum
from functools import cache

import telebot
from loguru import logger
from telebot.types import Message

from app.database.models import Item
from app.service.facade import MemeOracleService


class SendStatus(Enum):
    SUCCESS = 1
    INVALID_TYPE = 2
    TELEGRAM_ERROR = 3
    S3_ERROR = 4
    UNKNOWN_ERROR = 5


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, token: str) -> None:
        self.bot = telebot.TeleBot(token)
        self.service = service
        self._register_handlers()

    def handle_help(self, message: Message) -> None:
        self.bot.reply_to(message, "Ask the Oracle by using /ask_oracle.")

    def handle_random(self, message: Message) -> None:
        user_id = message.from_user.id
        chat_id = message.chat.id
        if user_id not in self.get_authorized_testers():
            self.bot.reply_to(message, "Unknown command.")
            return
        item = self.service.get_random_item()
        self._try_send_item(chat_id, user_id, item)

    def handle_ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id
        chat_id = message.chat.id

        item = self.service.get_next_eligible_item(user_id)
        if not item:
            self.bot.reply_to(message, "Come back tomorrow for more wisdom.")
            return

        if self._try_send_item(chat_id, user_id, item) == SendStatus.SUCCESS:
            self.service.log_interaction(user_id, item.id)
        else:
            self.bot.reply_to(message, "No prophecies found.")

    def _try_send_item(self, chat_id: int, user_id: int, item: Item) -> SendStatus:
        if not item:
            return SendStatus.UNKNOWN_ERROR

        try:
            s3_object = self.service.get_object(item.s3_name)
        except Exception as e:
            logger.warning(f"S3 error for {item.s3_name} to {user_id}: {e}")
            return SendStatus.S3_ERROR

        try:
            if item.type == "image":
                self.bot.send_photo(chat_id, s3_object)
            elif item.type == "video":
                self.bot.send_video(chat_id, s3_object)
            else:
                logger.error(f"Undefined item type: {item.type} (item: {item})")
                return SendStatus.INVALID_TYPE

            logger.info(f"Sent {item.type} to {user_id}, item: {item}")
            return SendStatus.SUCCESS

        except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"Telegram error for {item.s3_name} to {user_id}: {e}")
            return SendStatus.TELEGRAM_ERROR
        except Exception as e:
            logger.error(f"Unexpected error for {item.s3_name} to {user_id}: {e}")
            return SendStatus.UNKNOWN_ERROR

    def _register_handlers(self) -> None:
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handle_random)
        self.bot.message_handler(commands=["help"])(self.handle_help)

    def run(self) -> None:
        self.bot.infinity_polling()

    @cache
    def get_authorized_testers(self) -> set:
        testers = os.getenv("AUTHORIZED_TESTERS_TG_IDS", "")
        return set(map(int, testers.split(","))) if testers else set()
