import telebot


class MemeOracleBot:
    def __init__(self, meme_service, token):
        self.bot = telebot.TeleBot(token)
        self.service = meme_service
        self._register_handlers()

    def _register_handlers(self):
        @self.bot.message_handler(commands=["ask_oracle"])
        def handle_ask_oracle(message):
            # TODO: select object ID from DB  # should be in service layer, not in bots handler!!!
            # TODO: get object by ID
            meme = self.service.get_random_object()
            # TODO: validate object
            if not meme:
                self.bot.reply_to(message, "No prophecies found.")
                return
            # TODO: send img/video
            self.bot.send_photo(message.chat.id, meme)
            # TODO: update Ineractions table in DB

    def run(self):
        self.bot.infinity_polling()
