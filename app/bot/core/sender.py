from io import BytesIO
from typing import Callable

import telebot
from loguru import logger
from telebot.types import Message

from app.bot.schema.response_types import SendFailure, SendStatus, SendSuccess
from app.database.models import Item, ItemType
from app.utils.logger_setup import setup_logger

setup_logger("telegram_bot")


class Sender:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.send_methods: dict[ItemType, Callable] = {
            "image": self.bot.send_photo,
            "video": self.bot.send_video,
        }

    def send(self, message: Message, item: Item, file: BytesIO, handler_name: str) -> SendFailure | SendSuccess:
        chat_id = message.chat.id
        user_id = message.from_user.id

        send_method = self.send_methods.get(item.type)
        if send_method is None:
            logger.error(f"Invalid item type '{item.type}' for item: {item}")
            return SendFailure(status=SendStatus.INVALID_TYPE, reason="Invalid type")

        try:
            send_method(chat_id, file)
            logger.info(f"Sent {item.type} to {user_id}, item: {item}, handler: {handler_name}")
            return SendSuccess(status=SendStatus.SUCCESS, item=item, file=file)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Telegram error for {item.s3_name} to {user_id}: {e}")
            return SendFailure(status=SendStatus.TELEGRAM_ERROR, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected Telegram error for {item.s3_name} to {user_id}: {e}")
            return SendFailure(status=SendStatus.UNKNOWN_ERROR, reason=str(e))
