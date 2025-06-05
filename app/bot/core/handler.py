import telebot
from telebot.types import Message

from app.bot.core.access import AccessControl
from app.bot.core.interactor import Interactor
from app.bot.schema.response_types import FailureResult, SendStatus, SuccessResult
from app.bot.core.sender import Sender


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
        if isinstance(result, FailureResult):
            self._reply(message, result.reason or "Something went wrong.")
            return

        self.sender.send(message, result.item, result.file)

    def ask_oracle(self, message: Message) -> None:
        user_id = message.from_user.id
        result = self.interactor.get_next_available(user_id)

        if isinstance(result, SuccessResult):
            self.sender.send(message, result.item, result.file)
            return

        match result.status:
            case SendStatus.LIMIT_REACHED:
                self._reply(message, "Oracle is tired, come back tomorrow.")
            case SendStatus.NO_CANDIDATES:
                self._reply(message, "No prophecies found.")
            case SendStatus.SEND_FAILED:
                self._reply(message, "Failed to send prophecy.")
            case _:
                self._reply(message, "Something went wrong.")
