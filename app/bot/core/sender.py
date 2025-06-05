from io import BytesIO
from typing import Callable

import telebot
from loguru import logger
from telebot.types import Message

from app.bot.schema.response_types import (
    FailureResult,
    InteractionResult,
    SendStatus,
    SuccessResult,
)
from app.database.models import Item, ItemType


class Sender:
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
