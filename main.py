import os

import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(
    func=lambda message: True,
    content_types=["text"],
)
def echo_message(message):
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    bot.infinity_polling()
