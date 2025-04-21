import random
from io import BytesIO

from minio import Minio


class MinioStorage:
    def __init__(self, endpoint, access_key, secret_key, bucket_name):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
        )
        self.bucket_name = bucket_name

    def get_random_object(self):
        objects = list(self.client.list_objects(self.bucket_name, recursive=True))
        if not objects:
            return None
        obj = random.choice(objects)
        response = self.client.get_object(self.bucket_name, obj.object_name)

        image_data = BytesIO(response.read())
        image_data.name = obj.object_name  # Telegram API uses this as filename
        return image_data
