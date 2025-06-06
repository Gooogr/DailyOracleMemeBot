import telebot
from io import BytesIO
from typing import Optional

from app.bot.core.access import AccessControl
from app.database.models import Item
from app.service.facade import MemeOracleService


class MemeOracleBot:
    def __init__(
        self,
        service: MemeOracleService,
        token: Optional[str] = None,
        bot: Optional[telebot.TeleBot] = None,
        access: Optional[AccessControl] = None,
    ) -> None:
        self.service = service
        self.bot = bot or telebot.TeleBot(token)
        self.access = access or AccessControl()
        self.send_methods = {
            "image": self.bot.send_photo,
            "video": self.bot.send_video,
        }

    def register_handlers(self) -> None:
        self.bot.message_handler(commands=["ask_oracle"])(self.ask_oracle)
        self.bot.message_handler(commands=["random"])(self.random)
        self.bot.message_handler(commands=["help"])(self.help)

    def _reply(self, message, text: str) -> None:
        self.bot.reply_to(message, text)

    def _send_item(self, message, item: Item) -> bool:
        send_method = self.send_methods.get(item.type)
        if send_method is None:
            return False
        file: BytesIO = self.service.get_object(item.s3_name)
        send_method(message.chat.id, file)
        return True

    def help(self, message) -> None:
        self._reply(message, "Ask the Oracle by using `/ask_oracle`.")

    def random(self, message) -> None:
        if not self.access.is_tester(message.from_user.id):
            self._reply(message, "Unknown command.")
            return
        try:
            item = self.service.get_random_item()
            self._send_item(message, item)
        except Exception:  # pylint: disable=W0718
            self._reply(message, "Something went wrong.")

    def ask_oracle(self, message) -> None:
        user_id = message.from_user.id
        items = self.service.get_candidate_items(user_id)
        if items is None:
            self._reply(message, "Oracle is tired, come back tomorrow.")
            return
        if not items:
            self._reply(message, "No prophecies found.")
            return
        for item in items:
            try:
                if self._send_item(message, item):
                    self.service.log_interaction(user_id, item.id)
                    return
            except Exception:  # pylint: disable=W0718
                continue
        self._reply(message, "Oracle is confused, try again.")

    def run(self) -> None:
        self.register_handlers()
        self.bot.infinity_polling()
