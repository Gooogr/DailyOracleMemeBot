from typing import Optional

from app.database.factory_interface import AbstractItemRepositoryFactory
from app.database.models import Item
from app.database.provider_interface import AbstractDatabaseProvider


class ItemService:

    unseen_limit = 10

    def __init__(self, provider: AbstractDatabaseProvider, item_repo_factory: AbstractItemRepositoryFactory):
        self.provider = provider
        self.item_repo_factory = item_repo_factory

    def _get_unseen_items(self, user_id: int) -> Optional[list[Item]]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.list_least_viewed_unseen(user_id, self.unseen_limit)

    def get_next_unseen_item(self, user_id: int) -> Optional[Item]:
        items = self._get_unseen_items(user_id)
        return items[0] if items else None

    def get_random_item(self) -> Optional[Item]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.random_item()
