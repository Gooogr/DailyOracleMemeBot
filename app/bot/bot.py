from telebot import TeleBot

from app.bot.core.authorizer import Authorizer
from app.bot.core.getter import Getter
from app.bot.core.handler import CommandHandler
from app.bot.core.sender import Sender
from app.bot.core.writer import Writer
from app.service.facade import MemeOracleService


class MemeOracleBot:
    def __init__(self, service: MemeOracleService, bot: TeleBot) -> None:
        sender = Sender(bot)
        getter = Getter(service)
        writer = Writer(service)
        authorizer = Authorizer()
        handler = CommandHandler(bot, authorizer, getter, sender, writer)

        self.bot = bot
        self.handler = handler

    def _register_handlers(self) -> None:
        self.bot.message_handler(commands=["ask_oracle"])(self.handler.ask_oracle)
        self.bot.message_handler(commands=["random"])(self.handler.random)
        self.bot.message_handler(commands=["help"])(self.handler.help)

    def run(self) -> None:
        self._register_handlers()
        self.bot.infinity_polling()
