from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    @abstractmethod
    def get_object(self, object_id: str) -> str:
        pass
