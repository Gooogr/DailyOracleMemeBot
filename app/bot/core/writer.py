from loguru import logger

from app.service.facade import MemeOracleService


class Writer:
    def __init__(self, service: MemeOracleService):
        self.service = service

    def interaction(self, user_id: int, item_id: str) -> None:
        try:
            self.service.log_interaction(user_id, item_id)
        except Exception as e:
            logger.error(f"Interaction logging failed for user {user_id}, item {item_id}: {e}")
