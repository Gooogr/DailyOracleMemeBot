from abc import ABC, abstractmethod
from datetime import datetime


class AbstractItemRepository(ABC):
    @abstractmethod
    def create(
        self, item_id: str, s3_name: str, item_type: str, upload_datetime: datetime
    ):
        pass

    @abstractmethod
    def read(self, item_id: str):
        pass

    @abstractmethod
    def delete(self, item_id: str):
        pass


class AbstractInteractionRepository(ABC):
    @abstractmethod
    def create(self, user_id: str, item_id: str, interaction_datetime: datetime):
        pass

    @abstractmethod
    def read(self, user_id: str):
        pass
