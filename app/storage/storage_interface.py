from abc import ABC, abstractmethod
from io import BytesIO


class AbstractStorage(ABC):
    @abstractmethod
    def get_object(self, object_name: str) -> BytesIO:
        pass
