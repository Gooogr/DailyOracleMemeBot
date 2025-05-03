from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

class AbstractDatabaseProvider(ABC):
    @abstractmethod
    def get_session(self) -> Session:
        pass
