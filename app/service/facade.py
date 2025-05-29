from io import BytesIO
from typing import Optional

from app.db.models import Item
from app.service.interaction_service import InteractionService
from app.service.item_service import ItemService
from app.storage.storage_interface import AbstractStorage


class MemeOracleService:
    def __init__(
        self,
        item_service: ItemService,
        interaction_service: InteractionService,
        storage: AbstractStorage,
    ):
        self.item_service = item_service
        self.interaction_service = interaction_service
        self.storage = storage

    def get_next_eligible_item(self, user_id: int) -> Optional[Item]:
        if not self.interaction_service.can_receive_new_object(user_id):
            return None
        return self.item_service.get_next_unseen_item(user_id)

    def get_random_item(self) -> Optional[Item]:
        return self.item_service.get_random_item()

    def get_object(self, object_name: str) -> BytesIO:
        return self.storage.get_object(object_name)

    def log_interaction(self, user_id: int, item_id: str) -> None:
        self.interaction_service.log_interaction(user_id, item_id)
