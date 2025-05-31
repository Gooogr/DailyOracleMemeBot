from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from typing import Optional, Union

from app.database.models import Item


class SendStatus(Enum):
    SUCCESS = 1
    INVALID_TYPE = 2
    TELEGRAM_ERROR = 3
    S3_ERROR = 4
    DB_ERROR = 5
    UNKNOWN_ERROR = 6
    LIMIT_REACHED = 7
    NO_CANDIDATES = 8
    SEND_FAILED = 9


@dataclass
class InteractionResultBase:
    status: SendStatus


@dataclass
class SuccessResult(InteractionResultBase):
    item: Item
    file: BytesIO


@dataclass
class FailureResult(InteractionResultBase):
    reason: Optional[str] = None


InteractionResult = Union[SuccessResult, FailureResult]
