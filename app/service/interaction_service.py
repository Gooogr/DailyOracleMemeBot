from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database.factory_interface import AbstractInteractionRepositoryFactory
from app.database.models import Interaction
from app.database.provider_interface import AbstractDatabaseProvider


class InteractionService:
    def __init__(
        self, provider: AbstractDatabaseProvider, interaction_repo_factory: AbstractInteractionRepositoryFactory
    ):
        self.provider = provider
        self.interaction_repo_factory = interaction_repo_factory

    def log_interaction(self, user_id: int, item_id: str) -> None:
        session = self.provider.get_session()
        repo = self.interaction_repo_factory.create(session)
        repo.create(user_id, item_id, datetime.now(timezone.utc))

    def get_last_interaction(self, user_id: int) -> Optional[Interaction]:
        session = self.provider.get_session()
        repo = self.interaction_repo_factory.create(session)
        interactions = repo.list_user_interactions_desc(user_id)
        return interactions[0] if interactions else None

    def can_receive_new_object(self, user_id: int) -> bool:
        last = self.get_last_interaction(user_id)
        if not last:
            return True
        now_date = datetime.now(timezone.utc).date()
        last_date = last.interaction_dt.date()
        return now_date > last_date
