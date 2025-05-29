from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Optional

from app.db.factory_interface import (
    AbstractInteractionRepositoryFactory,
    AbstractItemRepositoryFactory,
)
from app.db.models import Interaction, Item
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

    def can_user_receive_new_object(self, user_id: int) -> bool:
        interaction = self.get_last_time_user_interaction(user_id)
        if not interaction:
            return True
        return interaction.interaction_dt <= datetime.now(timezone.utc) - timedelta(days=1)

    def get_next_eligible_item(self, user_id: int) -> Optional[Item]:
        if not self.can_user_receive_new_object(user_id):
            return None
        unseen_items = self.get_unseen_items(user_id)
        return unseen_items[0] if unseen_items else None

    def get_unseen_items(self, user_id: int) -> Optional[list[Item]]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.list_unseen(user_id)

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

    def get_last_time_user_interaction(self, user_id: int) -> Optional[Interaction]:
        session = self.provider.get_session()
        interaction_repo = self.interaction_repo_factory.create(session)
        user_events = interaction_repo.read(user_id)
        return user_events[0] if user_events else None
