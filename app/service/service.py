from datetime import datetime, timezone

from app.db.factory_interface import (
    AbstractInteractionRepositoryFactory,
    AbstractItemRepositoryFactory,
)
from app.db.provider_interface import AbstractDatabaseProvider
from app.storage.storage_interface import AbstractStorage


class MemeOracleService:
    def __init__(
        self,
        storage: AbstractStorage,
        provider: AbstractDatabaseProvider,
        item_repo_factory: AbstractItemRepositoryFactory,
        interaction_repo_factory: AbstractInteractionRepositoryFactory,
    ):
        self.storage = storage
        self.provider = provider
        self.item_repo_factory = item_repo_factory
        self.interaction_repo_factory = interaction_repo_factory

    def fetch_and_log_next_object(self, user_id: str):
        session = self.provider.get_session()

        item_repo = self.item_repo_factory.create(session)
        interaction_repo = self.interaction_repo_factory.create(session)

        unseen_items = item_repo.list_unseen(user_id)
        if not unseen_items:
            return None

        most_fresh_item = unseen_items[0]

        # TODO: but what if bot failed to send object in a next layer? But we log there success intercation
        interaction_repo.create(
            user_id=user_id,
            item_id=most_fresh_item.id,
            interaction_datetime=datetime.now(timezone.utc),
        )

        return self.storage.get_object(object_name=most_fresh_item.s3_name)

    def get_object(self, object_name: str):
        return self.storage.get_object(object_name=object_name)

    def get_random_object(self):
        return self.storage.get_random_object()
