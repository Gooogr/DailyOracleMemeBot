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
        if message.from_user.id not in self.get_authorized_testers():
            self.bot.reply_to(message, "Unknown command.")
            return
        s3_object = self.service.get_random_object()
        if not s3_object:
            self.bot.reply_to(message, "No prophecies found.")
            return
        # TODO: add video support as well
        self.bot.send_photo(message.chat.id, s3_object)

    def handle_ask_oracle(self, message):
        user_id = message.from_user.id
        item = self.service.get_next_unseen_item(user_id)
        logger.info(item)

        if not item:
            self.bot.reply_to(message, "No prophecies found.")
            return

        s3_object = self.service.get_object(item.s3_name)  # raise error in storage level

        try:
            if item.type == "image":
                self.bot.send_photo(message.chat.id, s3_object)
                self.service.log_interaction(user_id, item.id)
                logger.info(f"Send image to {user_id}, item {item}")
            elif item.type == "video":
                self.bot.send_video(message.chat.id, s3_object)
                self.service.log_interaction(user_id, item.id)
                logger.info(f"Send video to {user_id}, item {item}")
            else:
                logger.error(f"Got undefined item type {item.type}. Should be `image` or `video`")
        # TODO: log log_intercation Excelption as well. How to make it independent from provider?
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f"Can't send {s3_object.name} with error {e}")
            return

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
