import telebot
from telebot.types import Message

from app.bot.core.authorizer import Authorizer
from app.bot.core.getter import Getter
from app.bot.core.sender import Sender
from app.bot.core.writer import Writer
from app.bot.schema.response_types import (
    GetFailure,
    GetStatus,
    GetSuccessBatch,
    SendStatus,
)


class CommandHandler:
    def __init__(
        self,
        bot: telebot.TeleBot,
        authorizer: Authorizer,
        getter: Getter,
        sender: Sender,
        writer: Writer,
    ):
        self.bot = bot
        self.access = authorizer
        self.getter = getter
        self.sender = sender
        self.writer = writer

    def _reply(self, message: Message, text: str) -> None:
        self.bot.reply_to(message, text)

    def help(self, message: Message) -> None:
        self._reply(message, "Ask the Oracle by using `/ask_oracle`.")

    def random(self, message: Message) -> None:
        user_id = message.from_user.id

        if not self.access.is_tester(user_id):
            self._reply(message, "Unknown command.")
            return

        get_result = self.getter.get_random()
        if isinstance(get_result, GetFailure):
            self._reply(message, get_result.reason or "Something went wrong.")
            return

        send_result = self.sender.send(message, get_result.item, get_result.file, "random")
        if send_result.status != SendStatus.SUCCESS:
            self._reply(message, str(send_result.status))

    def ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id
        get_result = self.getter.get_candidates(user_id)

        if not isinstance(get_result, GetSuccessBatch):
            match get_result.status:
                case GetStatus.LIMIT_REACHED:
                    self._reply(message, "Oracle is tired, come back tomorrow.")
                case GetStatus.NO_CANDIDATES:
                    self._reply(message, "No prophecies found.")
                case _:
                    self._reply(message, "Something went wrong, try again later.")
            return

        for candidate in get_result.objects:
            send_result = self.sender.send(message, candidate.item, candidate.file, "ask_oracle")
            if send_result.status == SendStatus.SUCCESS:
                self.writer.interaction(user_id, candidate.item.id)
                return

        self._reply(message, "Oracle is confused, try again.")
