from datetime import datetime
from zoneinfo import ZoneInfo

from sync_worker.event_models import MinioWebhookPayload


def test_event_convertion():
    body = {
        "EventName": "s3:ObjectCreated:Put",
        "Key": "test/test_img.jpg",
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "minio:s3",
                "awsRegion": "",
                "eventTime": "2025-05-07T18:27:43.866Z",
                "eventName": "s3:ObjectCreated:Put",
                "userIdentity": {"principalId": "user"},
                "requestParameters": {
                    "principalId": "user",
                    "region": "",
                    "sourceIPAddress": "0.0.0.0",
                },
                "responseElements": {
                    "x-amz-id-2": "dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8",
                    "x-amz-request-id": "183D521117E888D8",
                    "x-minio-deployment-id": "8e4a0955-b0aa-444b-a62f-a74cd3d6c3a6",
                    "x-minio-origin-endpoint": "http://0.0.0.0:9000",
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "Config",
                    "bucket": {
                        "name": "test",
                        "ownerIdentity": {"principalId": "user"},
                        "arn": "arn:aws:s3:::test",
                    },
                    "object": {
                        "key": "test_img.jpg",
                        "size": 46806,
                        "eTag": "43d35848b68212475fc4dbd100b3bc6c",
                        "contentType": "image/jpeg",
                        "userMetadata": {"content-type": "image/jpeg"},
                        "sequencer": "183D5211182CED8E",
                    },
                },
                "source": {
                    "host": "0.0.0.0",
                    "port": "",
                    "userAgent": "MinIO (linux; amd64) minio-go/v7.0.89 MinIO Console/(dev)",
                },
            }
        ],
    }

    payload = MinioWebhookPayload(**body)
    assert payload.Records[0].eventName == "s3:ObjectCreated:Put"
    assert payload.Records[0].eventTime == datetime(
        2025, 5, 7, 18, 27, 43, 866000, tzinfo=ZoneInfo("UTC")
    )
    assert payload.Records[0].s3.object.key == "test_img.jpg"
    assert payload.Records[0].s3.object.contentType == "image/jpeg"
    assert payload.Records[0].s3.object.eTag == "43d35848b68212475fc4dbd100b3bc6c"
