from loguru import logger

from app.bot.schema.response_types import (
    FailureResult,
    InteractionResult,
    SendStatus,
    SuccessResult,
)
from app.database.exceptions import DatabaseError, ItemNotFoundError
from app.database.models import Item
from app.service.facade import MemeOracleService
from app.storage.exceptions import ObjectNotFoundError, StorageError


class Interactor:
    def __init__(self, service: MemeOracleService):
        self.service = service

    def _get_file(self, item: Item) -> InteractionResult:
        try:
            file = self.service.get_object(item.s3_name)
            return SuccessResult(status=SendStatus.SUCCESS, item=item, file=file)
        except (ObjectNotFoundError, StorageError) as e:
            logger.error(f"S3 object error for object {item.s3_name}: {e}")
            return FailureResult(status=SendStatus.S3_ERROR, reason=str(e))
        except Exception as e:
            logger.error(f"Unexpected S3 error for object {item.s3_name}: {e}")
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason=str(e))

    def get_random(self) -> InteractionResult:
        try:
            item = self.service.get_random_item()
        except (DatabaseError, ItemNotFoundError) as e:
            logger.warning(f"Get random item error: {e}")
            return FailureResult(status=SendStatus.DB_ERROR, reason="Failed to get random item.")
        except Exception as e:
            logger.exception(f"Unexpected error in get_random: {e}")
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason="Unexpected error occurred.")

        if not item:
            return FailureResult(status=SendStatus.UNKNOWN_ERROR, reason="No prophecies found.")

        file_result = self._get_file(item)
        if file_result.status != SendStatus.SUCCESS:
            return file_result

        return file_result

    def get_next_available(self, user_id: int) -> InteractionResult:
        items = self.service.get_candidate_items(user_id)

        if items is None:
            logger.info(f"User {user_id} hit daily limit")
            return FailureResult(status=SendStatus.LIMIT_REACHED)

        if not items:
            logger.warning(f"No candidates for user {user_id}")
            return FailureResult(status=SendStatus.NO_CANDIDATES)

        for item in items:
            file_result = self._get_file(item)
            if file_result.status != SendStatus.SUCCESS:
                continue

            try:
                self.service.log_interaction(user_id, item.id)
            except Exception as e:
                logger.warning(f"Interaction logging failed for user {user_id}, item {item.id}: {e}")
            file_result.status = SendStatus.SUCCESS
            return file_result

        return FailureResult(status=SendStatus.SEND_FAILED)
