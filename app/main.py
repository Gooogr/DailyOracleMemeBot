import os

from dotenv import load_dotenv
from minio import Minio

from app.bot.bot import MemeOracleBot
from app.db.postgres.factory import PostgresItemRepositoryFactory
from app.db.postgres.provider import PostgresProvider
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
    storage = MinIOStorage(
        minio_client,
        os.getenv("MINIO_BUCKET_NAME"),
    )
    provider = PostgresProvider(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        db=os.getenv("POSTGRES_DB"),
    )
    service = MemeOracleService(
        storage, provider, PostgresItemRepositoryFactory
    )  # TODO: looks like a refactoring place
    bot = MemeOracleBot(service, os.getenv("BOT_TOKEN"))
    bot.run()


if __name__ == "__main__":
    main()
