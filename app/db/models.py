from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[str] = mapped_column(String(), primary_key=True)
    type: Mapped[str] = mapped_column(String(10))
    upload_dt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, type={self.type!r}, upload_dt={self.upload_dt!r})"


class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String())
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id"))
    interaction_dt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Interaction(user_id={self.user_id!r}, item_id={self.item_id!r}, interaction_dt={self.interaction_dt!r})"
