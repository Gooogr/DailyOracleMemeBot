from datetime import datetime
from typing import cast

from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql.expression import func

from app.database.exceptions import (
    DatabaseError,
    ItemAlreadyExistsError,
    ItemNotFoundError,
)
from app.database.models import Interaction, Item
from app.database.repository_interface import (
    AbstractInteractionRepository,
    AbstractItemRepository,
)


class PostgresItemRepository(AbstractItemRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, item_id: str, s3_name: str, item_type: str, upload_datetime: datetime) -> None:
        item = Item(id=item_id, s3_name=s3_name, type=item_type, upload_dt=upload_datetime)
        self.session.add(item)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ItemAlreadyExistsError(item_id) from e

    def read(self, item_id: str) -> Item:
        try:
            item = self.session.query(Item).filter(Item.id == item_id).one_or_none()
            if not item:
                raise ItemNotFoundError(item_id)
            return cast(Item, item)  # cast() to supress typehint warning
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to read item '{item_id}'") from e

    def delete(self, item_id: str) -> None:
        try:
            item = self.session.query(Item).filter(Item.id == item_id).one_or_none()  # verify item existence in session
            if not item:
                raise ItemNotFoundError(item_id)
            self.session.delete(item)  # could be already unsafe, so keep it under 'try'
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to delete item '{item_id}'") from e

    def list_least_viewed_unseen(self, user_id: int, k: int = 10) -> list[Item]:
        """
        SQL analog
        SELECT items.*
        FROM items
        LEFT JOIN interactions i ON items.id = i.item_id /*interactions of all users*/
        LEFT JOIN interactions ui ON items.id = ui.item_id AND ui.user_id = :user_id /*interactions of :user_id*/
        WHERE ui.item_id IS NULL
        GROUP BY items.id
        ORDER BY COUNT(i.id) ASC, items.upload_dt DESC
        LIMIT :k;
        """
        try:
            InteractionsAll = aliased(Interaction)
            InteractionsUser = aliased(Interaction)

            query = (
                self.session.query(Item)
                .outerjoin(InteractionsAll, Item.id == InteractionsAll.item_id)  # 'outerjoin' == 'LEFT JOIN' in SQL
                .outerjoin(
                    InteractionsUser,
                    and_(
                        Item.id == InteractionsUser.item_id,
                        InteractionsUser.user_id == user_id,
                    ),
                )
                .filter(InteractionsUser.item_id.is_(None))  # unseen by user
                .group_by(Item.id)
                .order_by(
                    func.count(InteractionsAll.id).asc(),  # least seen by all users
                    Item.upload_dt.desc(),  # but the most fresh
                )
                .limit(k)
            )
            return query.all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to list unseen items for user {user_id}") from e

    def random_item(self) -> Item:
        try:
            item = self.session.query(Item).order_by(func.random()).limit(1).first()
            if not item:
                raise ItemNotFoundError("<random item>")
            return cast(Item, item)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError("Failed to read <random item>") from e


class PostgresInteractionRepository(AbstractInteractionRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, item_id: str, interaction_datetime: datetime) -> None:
        interaction = Interaction(user_id=user_id, item_id=item_id, interaction_dt=interaction_datetime)
        self.session.add(interaction)
        try:
            self.session.commit()
        except IntegrityError as e:
            self.session.rollback()
            raise ItemAlreadyExistsError(item_id) from e

    def list_user_interactions_desc(self, user_id: int) -> list[Interaction]:
        try:
            query = (
                self.session.query(Interaction)
                .filter(Interaction.user_id == user_id)
                .distinct()  # just in case, be design should be unique
                .order_by(Interaction.interaction_dt.desc())
            )
            return query.all()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Failed to list desc user interactions for user {user_id}") from e
