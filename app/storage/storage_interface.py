from abc import ABC, abstractmethod
from io import BytesIO
from typing import Optional


class AbstractStorage(ABC):
    @abstractmethod
    def get_object(self, object_name: str) -> Optional[BytesIO]:
        pass
