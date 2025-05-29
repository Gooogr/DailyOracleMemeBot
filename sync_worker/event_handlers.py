import hashlib
import os
from datetime import datetime

from app.db.factory_interface import AbstractItemRepositoryFactory
from app.db.provider_interface import AbstractDatabaseProvider
from app.db.repository_interface import AbstractItemRepository
from sync_worker.event_models import MinioWebhookPayload

HASH_KEY_HALF_SIZE = 5


class MinioEventHandler:
    def __init__(
        self,
        provider: AbstractDatabaseProvider,
        item_repo_factory: AbstractItemRepositoryFactory,
    ):
        self.provider = provider
        self.item_repo_factory = item_repo_factory

    def handle_event(self, event: MinioWebhookPayload) -> None:
        session = self.provider.get_session()
        repo = self.item_repo_factory.create(session)

        for record in event.Records:
            event_type = record.eventName
            key = record.s3.object.key
            timestamp = record.eventTime

            if event_type.startswith("s3:ObjectCreated:"):
                self._handle_create(repo, key, timestamp)

            elif event_type.startswith("s3:ObjectRemoved:"):
                self._handle_delete(repo, key)

        session.close()

    def _handle_create(self, repo: AbstractItemRepository, key: str, timestamp: datetime) -> None:
        item_id = self.key_to_id(key)
        object_type = self.infer_type(key)
        object_name = os.path.basename(key)
        if not repo.read(item_id):
            repo.create(item_id, object_name, object_type, timestamp)

    def _handle_delete(self, repo: AbstractItemRepository, key: str) -> None:
        item_id = self.key_to_id(key)
        if repo.read(item_id):
            repo.delete(item_id)

    @staticmethod
    def infer_type(key: str) -> str:
        key = key.lower()
        if key.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".avif")):
            return "image"
        if key.endswith((".mp4", ".webm", ".mov", ".mkv")):
            return "video"
        return "unknown"

    @staticmethod
    def key_to_id(key: str) -> str:
        return hashlib.shake_128(key.encode()).hexdigest(HASH_KEY_HALF_SIZE)
