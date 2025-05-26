import telebot

from app.service.service import MemeOracleService


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, token: str):
        self.bot = telebot.TeleBot(token)
        self.service = service
        self._register_handlers()

    # only for tests
    def handle_random(self, message):
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
        # TODO: handle and log here telebot.apihelper.ApiTelegramException: A request to the Telegram API was unsuccessful.
        # Error code: 400. Description: Bad Request: IMAGE_PROCESS_FAILED
        self.bot.send_photo(message.chat.id, s3_object)

    def _register_handlers(self):
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handle_random)

    def run(self):
        self.bot.infinity_polling()
