from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.storage.exceptions import (
    BucketNotFoundError,
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

    def get_object(self, object_name: str) -> BytesIO:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise ObjectNotFoundError(object_name, self.bucket_name) from e
            raise StorageError(f"Failed to retrieve object '{object_name}' in bucket '{self.bucket_name}'") from e
        except Exception as e:
            raise StorageError(f"Unexpected error for object '{object_name}' in bucket '{self.bucket_name}'") from e

        raw_data = response.read()
        data = BytesIO(raw_data)
        data.name = object_name

        response.close()
        response.release_conn()
        return data
