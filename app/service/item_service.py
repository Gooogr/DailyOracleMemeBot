from app.database.factory_interface import AbstractItemRepositoryFactory
from app.database.models import Item
from app.database.provider_interface import AbstractDatabaseProvider


class ItemService:

    def __init__(self, provider: AbstractDatabaseProvider, item_repo_factory: AbstractItemRepositoryFactory):
        self.provider = provider
        self.item_repo_factory = item_repo_factory

    def get_top_k_unseen_items(self, user_id: int, limit: int = 10) -> list[Item]:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.list_least_viewed_unseen(user_id, limit)

    def get_random_item(self) -> Item:
        session = self.provider.get_session()
        item_repo = self.item_repo_factory.create(session)
        return item_repo.random_item()
