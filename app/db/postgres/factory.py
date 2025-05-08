from sqlalchemy.orm import Session

from app.db.factory_interface import (
    AbstractInteractionRepositoryFactory,
    AbstractItemRepositoryFactory,
)
from app.db.postgres.repository import (
    PostgresInteractionRepository,
    PostgresItemRepository,
)
from app.db.repository_interface import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class PostgresItemRepositoryFactory(AbstractItemRepositoryFactory):
    def create(self, session: Session) -> AbstractItemRepository:
        return PostgresItemRepository(session=session)


class PostgresInteractionRepositoryFactory(AbstractInteractionRepositoryFactory):
    def create(self, session: Session) -> AbstractInteractionRepository:
        return PostgresInteractionRepository(session=session)
