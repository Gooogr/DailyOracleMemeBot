import os

from dotenv import load_dotenv
from minio import Minio

from app.bot.bot import MemeOracleBot
from app.service.service import MemeOracleService
from app.storage.minio_storage import MinIOStorage

load_dotenv(dotenv_path="../.env")


def main():
    minio_client = Minio(
        endpoint="minio:9000",
        access_key=os.getenv("MINIO_ROOT_USER"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
        secure=False,
    )
    storage = MinIOStorage(minio_client, os.getenv("MINIO_BUCKET_NAME"))
    service = MemeOracleService(storage)
    token = os.getenv("BOT_TOKEN")
    if token is None:
        raise ValueError("empty bot token")
    bot = MemeOracleBot(service, token)
    bot.run()


if __name__ == "__main__":
    main()
