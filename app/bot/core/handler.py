import telebot
from telebot.types import Message

from app.bot.core.access import AccessControl
from app.bot.core.interactor import Interactor
from app.bot.core.sender import Sender
from app.bot.schema.response_types import (
    GetStatus,
    GetSuccess,
    SendFailure,
    SendStatus,
    SendSuccess,
)


class CommandHandler:
    def __init__(
        self,
        bot: telebot.TeleBot,
        access: AccessControl,
        interactor: Interactor,
        sender: Sender,
    ):
        self.bot = bot
        self.access = access
        self.interactor = interactor
        self.sender = sender

    def _reply(self, message: Message, text: str) -> None:
        self.bot.reply_to(message, text)

    def help(self, message: Message) -> None:
        self._reply(message, "Ask the Oracle by using `/ask_oracle`.")

    def random(self, message: Message) -> None:
        user_id = message.from_user.id

        if not self.access.is_tester(user_id):
            self._reply(message, "Unknown command.")
            return

        result = self.interactor.get_random()
        if isinstance(result, SendFailure):
            self._reply(message, result.reason or "Something went wrong.")
            return

        result = self.sender.send(message, result.item, result.file, "random")
        if result.status != SendStatus.SUCCESS:
            self._reply(message, str(result.status))

    def ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id
        get_result = self.interactor.get_next_available(user_id)

        if not isinstance(get_result, GetSuccess):
            match get_result.status:
                case GetStatus.LIMIT_REACHED:
                    self._reply(message, "Oracle is tired, come back tomorrow.")
                case GetStatus.NO_CANDIDATES:
                    self._reply(message, "No prophecies found.")
                case _:
                    self._reply(message, "Something went wrong.")
            return

        send_result = self.sender.send(message, get_result.item, get_result.file, "ask_oracle")
        if send_result.status == SendStatus.SUCCESS:
            self.interactor.log_intercation(user_id, get_result.item.id)
        else:
            self._reply(message, "Oracle is confused, try again.")
