import os
import random
from io import BytesIO

import telebot
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

BUCKET_NAME = "test"

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=False,
)


def get_random_image():
    objects = list(minio_client.list_objects(BUCKET_NAME, recursive=True))
    if not objects:
        return None

    obj = random.choice(objects)
    response = minio_client.get_object(BUCKET_NAME, obj.object_name)

    image_data = BytesIO(response.read())
    image_data.name = obj.object_name  # Telegram API uses this as filename
    return image_data


@bot.message_handler(
    commands=["echo"],
    content_types=["text"],
)
def echo_message(message):
    bot.reply_to(message, message.text)


@bot.message_handler(
    commands=["ask_oracle"],
)
def get_meme_from_minio(message):
    image = get_random_image()
    if image:
        bot.send_photo(message.chat.id, photo=image)
    else:
        bot.reply_to(message, "can't show image")


if __name__ == "__main__":
    bot.infinity_polling()
