import os

from dotenv import load_dotenv

from bot import MemeOracleBot
from service import MemeOracleService
from storage import MinioStorage

load_dotenv()

BUCKET_NAME = "test"

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in environment variables.")


def main():
    storage = MinioStorage(
        endpoint="minio:9000",
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        bucket_name=os.getenv("MINIO_BUCKET_NAME"),
    )
    service = MemeOracleService(storage)
    bot = MemeOracleBot(BOT_TOKEN, service)
    bot.run()


if __name__ == "__main__":
    main()
