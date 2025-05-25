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
        selected_db_item_id = self.service.get_db_item_id(user_id=user_id)

        s3_object = self.service.get_next_unseen_object(selected_db_item_id)

        if not s3_object:
            self.bot.reply_to(message, "No prophecies found.")
            return

        # TODO handle both video/img
        self.bot.send_photo(message.chat.id, s3_object)

        # TODO: update Ineractions table in DB

    def _register_handlers(self):
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handle_random)

    def run(self):
        self.bot.infinity_polling()
