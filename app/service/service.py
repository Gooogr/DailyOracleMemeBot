from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

from app.db.factory_interface import (
    AbstractInteractionRepositoryFactory,
    AbstractItemRepositoryFactory,
)
from app.db.models import Item
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

    def get_unseen_items(self, user_id: int) -> Optional[list[Item]]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)

        unseen_items = item_repo.list_unseen(user_id)
        if not unseen_items:
            return None
        return unseen_items

    def log_interaction(self, user_id: int, item_id: str) -> None:
        session = self.provider.get_session()
        interaction_repo = self.interaction_repo_factory.create(session)
        interaction_repo.create(
            user_id=user_id,
            item_id=item_id,
            interaction_datetime=datetime.now(timezone.utc),
        )

    def get_object(self, object_name: str) -> BytesIO:
        return self.storage.get_object(object_name=object_name)

    def get_random_item(self) -> Optional[Item]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.random_item()
