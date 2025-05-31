from sqlalchemy.orm import Session

from app.database.interfaces.factory import (
    AbstractInteractionRepositoryFactory,
    AbstractItemRepositoryFactory,
)
from app.database.interfaces.repository import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)
from app.database.postgres.repository import (
    PostgresInteractionRepository,
    PostgresItemRepository,
)


class PostgresItemRepositoryFactory(AbstractItemRepositoryFactory):
    def create(self, session: Session) -> AbstractItemRepository:
        return PostgresItemRepository(session=session)


class PostgresInteractionRepositoryFactory(AbstractInteractionRepositoryFactory):
    def create(self, session: Session) -> AbstractInteractionRepository:
        return PostgresInteractionRepository(session=session)
