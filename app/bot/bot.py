import os
from functools import cache

import telebot
from loguru import logger

from app.service.service import MemeOracleService


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, token: str):
        self.bot = telebot.TeleBot(token)
        self.service = service
        self._register_handlers()

    def handle_help(self, message):
        self.bot.reply_to(message, "Ask the Oracle by using /ask_oracle.")

    # only for testers
    def handle_random(self, message):
        user_id = message.from_user.id
        if user_id not in self.get_authorized_testers():
            self.bot.reply_to(message, "Unknown command.")
            return
        item = self.service.get_random_item()
        if not item:
            self.bot.reply_to(message, "No prophecies found.")
            return
        try:
            s3_object = self.service.get_object(item.s3_name)
            if item.type == "image":
                self.bot.send_photo(message.chat.id, s3_object)
                logger.info(f"Sent image to {user_id}, item {item}")
            elif item.type == "video":
                self.bot.send_video(message.chat.id, s3_object)
                logger.info(f"Sent video to {user_id}, item {item}")
            else:
                logger.error(f"Undefined item type {item.type} for item {item}")
                self.bot.reply_to(message, "No prophecies found.")
        except telebot.apihelper.ApiTelegramException as e:
            self.bot.reply_to(message, "No prophecies found.")
            logger.warning(f"Failed to send {item.s3_name} for user {user_id}: {e}")
        except Exception as e:
            self.bot.reply_to(message, "No prophecies found.")
            logger.error(f"Unexpected error for item {item.s3_name}: {e}")

    def handle_ask_oracle(self, message):
        user_id = message.from_user.id
        unseen_items = self.service.get_unseen_items(user_id)

        if not unseen_items:
            self.bot.reply_to(message, "No prophecies found.")
            return

        for item in unseen_items:
            try:
                s3_object = self.service.get_object(item.s3_name)  # May raise if object not found

                if item.type == "image":
                    self.bot.send_photo(message.chat.id, s3_object)
                    logger.info(f"Sent image to {user_id}, item {item}")
                elif item.type == "video":
                    self.bot.send_video(message.chat.id, s3_object)
                    logger.info(f"Sent video to {user_id}, item {item}")
                else:
                    logger.error(f"Undefined item type {item.type} for item {item}")
                    continue

                self.service.log_interaction(user_id, item.id)
                break

            except telebot.apihelper.ApiTelegramException as e:
                logger.warning(f"Failed to send {item.s3_name} for user {user_id}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error for item {item.s3_name}: {e}")
        else:
            self.bot.reply_to(message, "No prophecies found.")

    def _register_handlers(self):
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handle_random)
        self.bot.message_handler(commands=["help"])(self.handle_help)

    def run(self):
        self.bot.infinity_polling()

    @cache
    def get_authorized_testers(self):
        testers = os.getenv("AUTHORIZED_TESTERS_TG_IDS", "")
        return set(map(int, testers.split(","))) if testers else set()
