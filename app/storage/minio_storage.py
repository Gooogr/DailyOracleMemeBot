import os
import random
from functools import lru_cache
from io import BytesIO
from typing import List

from minio import Minio

from app.storage.base import AbstractStorage


# TODO: separate client and make it testable
class MinIOStorage(AbstractStorage):
    def __init__(self):
        self.client = Minio(
            endpoint="minio:9000",
            access_key=os.getenv("MINIO_ROOT_USER"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
            secure=False,
        )
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME")

    @lru_cache
    def list_objects(self) -> List[str]:
        return list(self.client.list_objects(self.bucket_name, recursive=True))

    def get_random_object(self) -> str:
        obj = random.choice(self.list_objects())
        response = self.client.get_object(self.bucket_name, obj.object_name)

        image_data = BytesIO(response.read())
        image_data.name = obj.object_name
        return image_data
