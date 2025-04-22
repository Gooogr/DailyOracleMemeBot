import os

from dotenv import load_dotenv

from app.bot.bot import MemeOracleBot
from app.service.service import MemeOracleService
from app.storage.minio_storage import MinIOStorage

load_dotenv(dotenv_path="../.env")


def main():
    storage = MinIOStorage()
    service = MemeOracleService(storage)
    token = os.getenv("BOT_TOKEN")
    if token is None:
        raise ValueError("empty bot token")
    bot = MemeOracleBot(service, token)
    bot.run()


if __name__ == "__main__":
    main()
