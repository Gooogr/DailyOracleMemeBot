from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Interaction, Item
from app.db.repository_interface import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class PostgresItemRepository(AbstractItemRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, item_id: str, item_type: str, upload_datetime: datetime):
        item = Item(id=item_id, type=item_type, upload_dt=upload_datetime)
        self.session.add(item)
        self.session.commit()
        return item  # TODO: remove return???

    def read(self, item_id: str):
        return self.session.query(Item).filter(Item.id == item_id).first()

    def delete(self, item_id: str):
        item = Item(id=item_id)
        self.session.delete(item)
        self.session.commit()
        return


class PostgresInteractionRepository(AbstractInteractionRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(
        self, user_id: str, item_id: str, interaction_datetime: datetime
    ):
        interaction = Interaction(
            user_id=user_id, item_id=item_id, interaction_dt=interaction_datetime
        )
        self.session.add(interaction)
        self.session.commit()
        return interaction
