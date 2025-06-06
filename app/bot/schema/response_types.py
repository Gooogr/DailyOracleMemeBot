from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Optional

from app.database.models import Item


class SendStatus(Enum):
    SUCCESS = 1
    INVALID_TYPE = 2
    TELEGRAM_ERROR = 3
    UNKNOWN_ERROR = 4


@dataclass
class SendResultBase:
    status: SendStatus


@dataclass
class SendSuccess(SendResultBase):
    file: BytesIO
    item: Item


@dataclass
class SendFailure(SendResultBase):
    reason: Optional[str] = None
    item: Optional[Item] = None


SendResult = SendFailure | SendSuccess


# Interactions between application and storage/database layers
class GetStatus(Enum):
    SUCCESS = 1
    S3_ERROR = 2
    DB_ERROR = 3
    LIMIT_REACHED = 4
    NO_CANDIDATES = 5
    UNKNOWN_ERROR = 6


@dataclass
class GetResultBase:
    status: GetStatus


@dataclass
class GetSuccess(GetResultBase):
    file: BytesIO
    item: Item


@dataclass
class GetFailure(GetResultBase):
    reason: Optional[str] = None
    item: Optional[Item] = None


@dataclass
class GetSuccessBatch:
    objects: list[GetSuccess]
    status: GetStatus = GetStatus.SUCCESS


GetResult = GetSuccess | GetFailure | GetSuccessBatch
