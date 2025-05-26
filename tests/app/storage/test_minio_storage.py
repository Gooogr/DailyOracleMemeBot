from io import BytesIO
from unittest.mock import MagicMock

import pytest
from minio.error import MinioException, S3Error

from app.storage.minio_storage import MinIOStorage


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
    mock_response.close.assert_called_once()
    mock_response.release_conn.assert_called_once()
    mock_minio_client.get_object.assert_called_once_with("test-bucket", "test-object")


def test_get_object_s3_error(storage, mock_minio_client):
    mock_response = MagicMock()
    mock_response.read.return_value = b"error"

    error = S3Error(
        code="NoSuchKey",
        message="Object not found",
        resource="/test-bucket/test-object",
        request_id="1234",
        host_id="localhost",
        response=mock_response,
    )

    mock_minio_client.get_object.side_effect = error

    with pytest.raises(S3Error):
        storage.get_object("bad-object")


def test_get_object_minio_error(storage, mock_minio_client):
    mock_minio_client.get_object.side_effect = MinioException("MinIO failure")

    with pytest.raises(MinioException):
        storage.get_object("bad-object")


def test_list_objects_success(storage, mock_minio_client):
    mock_obj1 = MagicMock()
    mock_obj1.object_name = "file1.jpg"
    mock_obj2 = MagicMock()
    mock_obj2.object_name = "file2.jpg"

    mock_minio_client.list_objects.return_value = [mock_obj1, mock_obj2]

    result = storage.list_objects()

    assert result == ["file1.jpg", "file2.jpg"]
    mock_minio_client.list_objects.assert_called_once_with("test-bucket", recursive=True)


def test_list_objects_failure(storage, mock_minio_client):
    mock_minio_client.list_objects.side_effect = MinioException("List failure")

    with pytest.raises(MinioException):
        storage.list_objects()


def test_get_random_object_success(storage, mock_minio_client):
    mock_obj = MagicMock()
    mock_obj.object_name = "random-file.txt"
    mock_minio_client.list_objects.return_value = [mock_obj]

    mock_response = MagicMock()
    mock_response.read.return_value = b"random content"
    mock_minio_client.get_object.return_value = mock_response

    result = storage.get_random_object()

    assert isinstance(result, BytesIO)
    assert result.read() == b"random content"
    assert result.name == "random-file.txt"


def test_get_random_object_empty_bucket(storage, mock_minio_client):
    mock_minio_client.list_objects.return_value = []

    with pytest.raises(IndexError):  # random.choice([]) raises IndexError
        storage.get_random_object()
