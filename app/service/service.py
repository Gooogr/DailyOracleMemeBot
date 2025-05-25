from app.db.factory_interface import AbstractItemRepositoryFactory
from app.db.provider_interface import AbstractDatabaseProvider
from app.storage.storage_interface import AbstractStorage


class MemeOracleService:
    def __init__(
        self,
        storage: AbstractStorage,
        provider: AbstractDatabaseProvider,
        item_repo_factory: AbstractItemRepositoryFactory,
    ):
        self.storage = storage
        self.provider = provider
        self.item_repo_factory = item_repo_factory

    def get_next_unseen_object(self, user_id: str):
        session = self.provider.get_session()

        item_repo = self.item_repo_factory(session)

        unseen_items = item_repo.list_unseen(user_id)
        most_fresh_item = unseen_items[0]

        if not unseen_items:
            return None

        return self.storage.get_object(object_id=most_fresh_item.s3_name)

    def get_object(self, object_name: str):
        return self.storage.get_object(object_id=object_name)

    def get_random_object(self):
        return self.storage.get_random_object()
