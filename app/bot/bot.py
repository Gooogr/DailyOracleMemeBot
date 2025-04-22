import telebot


class MemeOracleBot:
    def __init__(self, meme_service, token):
        self.bot = telebot.TeleBot(token)
        self.service = meme_service
        self._register_handlers()

    def _register_handlers(self):
        @self.bot.message_handler(commands=["ask_oracle"])
        def handle_ask_oracle(message):
            meme = self.service.get_object()
            if meme:  # TODO: check that object is image
                self.bot.send_photo(message.chat.id, meme)
            else:
                self.bot.reply_to(message, "No prophecies found.")

    def run(self):
        self.bot.infinity_polling()
