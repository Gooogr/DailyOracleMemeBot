import logging
import random
from io import BytesIO
from typing import List

from minio import Minio
from minio.error import MinioException, S3Error

from app.storage.storage_interface import AbstractStorage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MinIOStorage(AbstractStorage):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def get_object(self, object_name: str) -> BytesIO:
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            try:
                data = BytesIO(response.read())
                data.name = object_name
                return data
            finally:
                response.close()
                response.release_conn()
        except (S3Error, MinioException) as e:
            logger.error(
                "Error retrieving object '%s' from bucket '%s': %s",
                object_name,
                self.bucket_name,
                e,
            )
            raise
        except Exception as e:
            logger.exception("Unexpected error retrieving object '%s': %s", object_name, e)
            raise

    def list_objects(self) -> List[str]:
        try:
            objects = [obj.object_name for obj in self.client.list_objects(self.bucket_name, recursive=True)]
            return objects
        except (S3Error, MinioException) as e:
            logger.error("Error listing objects in bucket '%s': %s", self.bucket_name, e)
            raise
        except Exception as e:
            logger.exception(
                "Unexpected error listing objects in bucket '%s': %s",
                self.bucket_name,
                e,
            )
            raise

    def get_random_object(self) -> BytesIO:
        obj_name = random.choice(self.list_objects())
        return self.get_object(obj_name)
