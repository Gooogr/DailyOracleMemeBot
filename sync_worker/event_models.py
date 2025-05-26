from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class S3Object(BaseModel):
    key: str
    size: Optional[int] = None
    eTag: Optional[str] = None
    contentType: Optional[str] = None
    userMetadata: Optional[dict] = None
    sequencer: Optional[str] = None


class S3Bucket(BaseModel):
    name: str


class S3Info(BaseModel):
    bucket: S3Bucket
    object: S3Object


class Record(BaseModel):
    eventTime: datetime
    eventName: str
    s3: S3Info


class MinioWebhookPayload(BaseModel):
    EventName: Optional[str]
    Key: Optional[str]
    Records: List[Record]
