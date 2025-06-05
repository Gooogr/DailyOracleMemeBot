import telebot

from app.bot.core.access import AccessControl
from app.bot.core.handler import CommandHandler
from app.bot.core.interactor import Interactor
from app.bot.core.sender import Sender
from app.service.facade import MemeOracleService


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, token: str) -> None:
        bot = telebot.TeleBot(token)
        sender = Sender(bot)
        interactor = Interactor(service)
        access_controller = AccessControl()
        handler = CommandHandler(bot, access_controller, interactor, sender)

        self.bot = bot
        self.handler = handler
        self._register_handlers()

    def _register_handlers(self) -> None:
        self.bot.message_handler(commands=["ask_oracle"])(self.handler.ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handler.random)
        self.bot.message_handler(commands=["help"])(self.handler.help)

    def run(self) -> None:
        self.bot.infinity_polling()
