from abc import ABC, abstractmethod
from datetime import datetime


class AbstractItemRepository(ABC):
    @abstractmethod
    def add_item(self, item_id: str, item_type: str, upload_datetime: datetime):
        pass

    @abstractmethod
    def get_item(self, item_id: str):
        pass


class AbstractInteractionRepository(ABC):
    @abstractmethod
    def save_interaction(
        self, user_id: str, item_id: str, interaction_datetime: datetime
    ):
        pass
