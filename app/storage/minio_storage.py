import random
from functools import lru_cache
from io import BytesIO
from typing import List

from minio import Minio

from app.storage.storage_interface import AbstractStorage


class MinIOStorage(AbstractStorage):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def get_object(self, object_name: str) -> BytesIO:
        response = self.client.get_object(self.bucket_name, object_name)
        data = BytesIO(response.read())
        data.name = object_name
        return data

    def list_objects(self) -> List[str]:
        return [obj.object_name for obj in self.client.list_objects(self.bucket_name, recursive=True)]

    def get_random_object(self) -> BytesIO:
        obj_name = random.choice(self.list_objects())
        return self.get_object(obj_name)
