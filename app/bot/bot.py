import telebot


class MemeOracleBot:
    def __init__(self, meme_service, token):
        self.bot = telebot.TeleBot(token)
        self.service = meme_service
        self._register_handlers()

    def handle_ask_oracle(self, message):
        user_id = message.from_user.id
        selected_db_item_id = self.service.get_db_item_id(user_id=user_id)

        # TODO: switch to service.get_object(selected_db_item_id)
        s3_object = self.service.get_random_object()

        if not s3_object:
            self.bot.reply_to(message, "No prophecies found.")
            return
        # TODO handle both video/img
        self.bot.send_photo(message.chat.id, s3_object)
        # TODO: update Ineractions table in DB

    def _register_handlers(self):
        self.bot.message_handler(commands=["ask_oracle"])(self.handle_ask_oracle)

    def run(self):
        self.bot.infinity_polling()
