from io import BytesIO
from unittest.mock import MagicMock

import pytest
from minio.error import S3Error, MinioException

from app.storage.minio_storage import MinIOStorage
from app.storage.exceptions import (
    ObjectNotFoundError,
    ObjectListingError,
    StorageError,
    BucketNotFoundError,
)


@pytest.fixture
def mock_minio_client():
    return MagicMock()


@pytest.fixture
def storage(mock_minio_client):
    return MinIOStorage(client=mock_minio_client, bucket_name="test-bucket")


def test_get_object_success(storage, mock_minio_client):
    mock_response = MagicMock()
    mock_response.read.return_value = b"test data"
    mock_minio_client.get_object.return_value = mock_response

    result = storage.get_object("test-object")

    assert isinstance(result, BytesIO)
    assert result.read() == b"test data"
    assert result.name == "test-object"


def test_get_object_raises_object_not_found(storage, mock_minio_client):
    mock_response = MagicMock()

    error = S3Error(
        code="NoSuchKey",
        message="Object not found",
        resource="/test-bucket/test-object",
        request_id="1234",
        host_id="localhost",
        response=mock_response,
    )
    mock_minio_client.get_object.side_effect = error

    with pytest.raises(ObjectNotFoundError) as exc_info:
        storage.get_object("missing-object")
    assert "missing-object" in str(exc_info.value)


def test_get_object_raises_generic_storage_error(storage, mock_minio_client):
    mock_minio_client.get_object.side_effect = MinioException("generic failure")

    with pytest.raises(StorageError) as exc_info:
        storage.get_object("any-object")
    assert "Failed to retrieve object" in str(exc_info.value)


def test_list_objects_success(storage, mock_minio_client):
    mock_minio_client.bucket_exists.return_value = True
    mock_obj1 = MagicMock(object_name="file1.jpg")
    mock_obj2 = MagicMock(object_name="file2.jpg")
    mock_minio_client.list_objects.return_value = [mock_obj1, mock_obj2]

    result = storage.list_objects()

    assert result == ["file1.jpg", "file2.jpg"]

def test_get_random_object_success(storage, mock_minio_client):
    mock_minio_client.bucket_exists.return_value = True
    mock_obj = MagicMock(object_name="random-file.txt")
    mock_minio_client.list_objects.return_value = [mock_obj]

    mock_response = MagicMock()
    mock_response.read.return_value = b"random content"
    mock_minio_client.get_object.return_value = mock_response

    result = storage.get_random_object()

    assert isinstance(result, BytesIO)
    assert result.read() == b"random content"
    assert result.name == "random-file.txt"


def test_list_objects_bucket_missing(storage, mock_minio_client):
    mock_minio_client.bucket_exists.return_value = False

    with pytest.raises(BucketNotFoundError):
        storage.list_objects()


def test_list_objects_failure(storage, mock_minio_client):
    mock_minio_client.bucket_exists.return_value = True
    mock_minio_client.list_objects.side_effect = MinioException("oops")

    with pytest.raises(ObjectListingError):
        storage.list_objects()



def test_get_random_object_empty_bucket(storage, mock_minio_client):
    mock_minio_client.bucket_exists.return_value = True
    mock_minio_client.list_objects.return_value = []

    with pytest.raises(ObjectNotFoundError):
        storage.get_random_object()
