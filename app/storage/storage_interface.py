from abc import ABC, abstractmethod
from typing import List


class AbstractStorage(ABC):
    @abstractmethod
    def list_objects(self) -> List[str]:
        pass

    @abstractmethod
    def get_random_object(self) -> str:
        pass
