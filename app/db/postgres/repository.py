from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Interaction, Item
from app.db.repository_interface import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class PostgresItemRepository(AbstractItemRepository):
    def __init__(self, db: Session):
        self.db = db

    def add_item(self, item_id: str, item_type: str, upload_datetime: datetime):
        item = Item(id=item_id, type=item_type, upload_dt=upload_datetime)
        self.db.add(item)
        self.db.commit()
        return item

    def get_item(self, item_id: str):
        return self.db.query(Item).filter(Item.id == item_id).first()


class PostgresInteractionRepository(AbstractInteractionRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_interaction(
        self, user_id: str, item_id: str, interaction_datetime: datetime
    ):
        interaction = Interaction(
            user_id=user_id, item_id=item_id, interaction_dt=interaction_datetime
        )
        self.db.add(interaction)
        self.db.commit()
        return interaction
