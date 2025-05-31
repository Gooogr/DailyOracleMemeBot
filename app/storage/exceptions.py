class StorageError(Exception):
    """Generic storage layer error."""


class BucketNotFoundError(StorageError):
    def __init__(self, bucket_name: str):
        super().__init__(f"Bucket '{bucket_name} not found")
        self.bucket_name = bucket_name


class ObjectNotFoundError(StorageError):
    def __init__(self, object_name: str, bucket_name: str):
        super().__init__(f"Object '{object_name}' not found in  bucket '{bucket_name}'.")
        self.object_name = object_name
        self.bucket_name = bucket_name
