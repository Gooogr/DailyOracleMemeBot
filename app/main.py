import os

from dotenv import load_dotenv
from minio import Minio
import telebot

from app.bot.bot import MemeOracleBot
from app.database.postgres.factory import (
    PostgresInteractionRepositoryFactory,
    PostgresItemRepositoryFactory,
)
from app.database.postgres.provider import PostgresProvider
from app.service.facade import MemeOracleService
from app.service.interaction_service import InteractionService
from app.service.item_service import ItemService
from app.storage.minio_storage import MinIOStorage

load_dotenv(dotenv_path="../.env")


def main():
    # Set up storage layer
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
    # Set up database layer
    provider = PostgresProvider(
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        db=os.getenv("POSTGRES_DB"),
    )
    item_repo_factory = PostgresItemRepositoryFactory()
    interaction_repo_factory = PostgresInteractionRepositoryFactory()

    # Set up service layer
    item_service = ItemService(provider, item_repo_factory)
    interaction_service = InteractionService(provider, interaction_repo_factory)
    service = MemeOracleService(item_service, interaction_service, storage)

    # Set up bot
    bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
    oracle = MemeOracleBot(service, bot)

    oracle.run()


if __name__ == "__main__":
    main()
