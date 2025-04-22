import random
from functools import lru_cache
from io import BytesIO
from typing import List

from app.storage.base import AbstractStorage


class MinIOStorage(AbstractStorage):
    def __init__(self, client, bucket_name):
        self.client = client
        self.bucket_name = bucket_name

    @lru_cache
    def list_objects(self) -> List[str]:
        return list(self.client.list_objects(self.bucket_name, recursive=True))

    def get_random_object(self) -> str:
        obj = random.choice(self.list_objects())
        response = self.client.get_object(self.bucket_name, obj.object_name)

        image_data = BytesIO(response.read())
        image_data.name = obj.object_name
        return image_data
