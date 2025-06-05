from loguru import logger

from app.bot.schema.response_types import (
    GetFailure,
    GetFailureBatch,
    GetResult,
    GetStatus,
    GetSuccess,
)
from app.database.exceptions import DatabaseError, ItemNotFoundError
from app.database.models import Item
from app.service.facade import MemeOracleService
from app.storage.exceptions import ObjectNotFoundError, StorageError
from app.utils.logger_setup import setup_logger

setup_logger("telegram_bot")


class Interactor:
    def __init__(self, service: MemeOracleService):
        self.service = service

    def _get_file(self, item: Item) -> GetFailure | GetSuccess:
        try:
            file = self.service.get_object(item.s3_name)
            return GetSuccess(status=GetStatus.SUCCESS, item=item, file=file)
        except (ObjectNotFoundError, StorageError) as e:
            logger.error(f"S3 object error for object {item.s3_name}: {e}")
            return GetFailure(status=GetStatus.S3_ERROR, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected S3 error for object {item.s3_name}: {e}")
            return GetFailure(status=GetStatus.UNKNOWN_ERROR, reason=str(e))

    def get_random(self) -> GetFailure | GetSuccess:
        try:
            item = self.service.get_random_item()
        except (DatabaseError, ItemNotFoundError) as e:
            logger.warning(f"Get random item error: {e}")
            return GetFailure(status=GetStatus.DB_ERROR, reason="Failed to get random item.")
        except Exception as e:
            logger.exception(f"Unexpected error in get_random: {e}")
            return GetFailure(status=GetStatus.UNKNOWN_ERROR, reason="Unexpected error occurred.")

        if not item:
            return GetFailure(status=GetStatus.UNKNOWN_ERROR, reason="No prophecies found.")

        return self._get_file(item)

    def get_next_available(self, user_id: int) -> GetResult:
        items = self.service.get_candidate_items(user_id)

        if items is None:
            logger.info(f"User {user_id} hit daily limit")
            return GetFailure(status=GetStatus.LIMIT_REACHED)

        if not items:
            logger.warning(f"No candidates for user {user_id}")
            return GetFailure(status=GetStatus.NO_CANDIDATES)

        failures = []
        for item in items:
            result = self._get_file(item)
            if isinstance(result, GetSuccess):
                return result
            failures.append(result)

        return GetFailureBatch(failures=failures)

    def log_intercation(self, user_id: int, item_id: str) -> None:
        try:
            self.service.log_interaction(user_id, item_id)
        except Exception as e:
            logger.error(f"Interaction logging failed for user {user_id}, item {item_id}: {e}")
