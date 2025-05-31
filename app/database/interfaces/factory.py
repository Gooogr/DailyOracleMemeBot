from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.database.interfaces.repository import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class AbstractItemRepositoryFactory(ABC):
    @abstractmethod
    def create(self, session: Session) -> AbstractItemRepository:
        pass


class AbstractInteractionRepositoryFactory(ABC):
    @abstractmethod
    def create(self, session: Session) -> AbstractInteractionRepository:
        pass
