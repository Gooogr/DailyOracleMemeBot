from pathlib import Path

import telebot
import yaml
from loguru import logger

from app.service.service import MemeOracleService

PATH_TO_TESTRES_ID_LIST = "../../authorized-testers.yaml"


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
        self.bot.send_photo(message.chat.id, s3_object)

    def handle_ask_oracle(self, message):
        user_id = message.from_user.id
        s3_object = self.service.fetch_and_log_next_object(user_id)
        if not s3_object:
            self.bot.reply_to(message, "No prophecies found.")
            return
        try:
            self.bot.send_photo(message.chat.id, s3_object)
        except telebot.apihelper.ApiTelegramException as e:
            logger.warning(f"Can't send {s3_object.name} with error {e}")

    def _register_handlers(self):
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handle_random)
        self.bot.message_handler(commands=["help"])(self.handle_help)

    def run(self):
        self.bot.infinity_polling()

    @staticmethod
    def get_authorized_testers():
        config_path = Path(PATH_TO_TESTRES_ID_LIST)
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
        return set(data.get("testers", []))
