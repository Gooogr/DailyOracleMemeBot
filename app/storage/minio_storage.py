import random
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import MinioException, S3Error

from app.storage.exceptions import (
    BucketNotFoundError,
    ObjectListingError,
    ObjectNotFoundError,
    StorageError,
)
from app.storage.storage_interface import AbstractStorage


class MinIOStorage(AbstractStorage):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

        if not self.client.bucket_exists(self.bucket_name):
            raise BucketNotFoundError(self.bucket_name)

    def get_object(self, object_name: str) -> Optional[BytesIO]:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            try:
                data = BytesIO(response.read())
                data.name = object_name
                return data
            finally:
                response.close()
                response.release_conn()
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise ObjectNotFoundError(object_name, self.bucket_name) from e
            raise StorageError(f"Failed to retrieve object '{object_name}' in  bucket '{self.bucket_name}'") from e
        except Exception as e:
            raise StorageError(f"Unexpected error for object '{object_name}' in bucket '{self.bucket_name}'") from e

    def list_objects(self) -> list[str]:
        try:
            objects = [obj.object_name for obj in self.client.list_objects(self.bucket_name, recursive=True)]
            return objects
        except (S3Error, MinioException) as e:
            raise ObjectListingError(self.bucket_name) from e
        except Exception as e:
            raise StorageError(f"Unexpected error for bucket '{self.bucket_name}'") from e

    def get_random_object(self) -> Optional[BytesIO]:
        objects = self.list_objects()
        if not objects:
            raise ObjectNotFoundError("<random>", self.bucket_name)
        obj_name = random.choice(objects)
        return self.get_object(obj_name)
