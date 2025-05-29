from abc import ABC, abstractmethod
from datetime import datetime

from app.db.models import Interaction, Item


class AbstractItemRepository(ABC):
    @abstractmethod
    def create(self, item_id: str, s3_name: str, item_type: str, upload_datetime: datetime) -> None:
        pass

    @abstractmethod
    def read(self, item_id: str) -> Item:
        pass

    @abstractmethod
    def delete(self, item_id: str) -> None:
        pass

    @abstractmethod
    def list_unseen(self, user_id: int) -> list[Item]:
        pass


class AbstractInteractionRepository(ABC):
    @abstractmethod
    def create(self, user_id: int, item_id: str, interaction_datetime: datetime) -> None:
        pass

    @abstractmethod
    def read(self, user_id: int) -> Interaction:
        pass
