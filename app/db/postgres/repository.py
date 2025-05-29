from datetime import datetime
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import func

from app.db.models import Interaction, Item
from app.db.repository_interface import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class PostgresItemRepository(AbstractItemRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, item_id: str, s3_name: str, item_type: str, upload_datetime: datetime) -> None:
        item = Item(id=item_id, s3_name=s3_name, type=item_type, upload_dt=upload_datetime)
        self.session.add(item)
        self.session.commit()

    def read(self, item_id: str) -> Optional[Item]:
        return self.session.query(Item).filter(Item.id == item_id).first()

    def delete(self, item_id: str) -> None:
        item = Item(id=item_id)
        self.session.delete(item)
        self.session.commit()

    def list_unseen(self, user_id: int) -> Optional[list[Item]]:
        InteractionAlias = aliased(Interaction)

        query = (
            self.session.query(Item)
            .outerjoin(
                InteractionAlias,
                and_(
                    Item.id == InteractionAlias.item_id,
                    InteractionAlias.user_id == user_id,
                ),
            )
            .filter(InteractionAlias.item_id.is_(None))
            .order_by(Item.upload_dt.desc())
        )

        return query.all()

    def random_item(self) -> Optional[Item]:
        return self.session.query(Item).order_by(func.random()).limit(1).first()


class PostgresInteractionRepository(AbstractInteractionRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, item_id: str, interaction_datetime: datetime) -> None:
        interaction = Interaction(user_id=user_id, item_id=item_id, interaction_dt=interaction_datetime)
        self.session.add(interaction)
        self.session.commit()

    def read(self, user_id: int) -> Optional[list[Interaction]]:
        return self.session.query(Interaction.item_id).filter(Interaction.user_id == user_id).distinct().all()
