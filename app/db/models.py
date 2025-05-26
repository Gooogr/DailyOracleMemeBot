from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[str] = mapped_column(String(), primary_key=True)
    s3_name: Mapped[str] = mapped_column(String())
    type: Mapped[str] = mapped_column(String(10))
    upload_dt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Item(id={self.id!r}, s3_name={self.s3_name!r}, type={self.type!r}, upload_dt={self.upload_dt!r})"


class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer())
    item_id: Mapped[str] = mapped_column(ForeignKey("items.id"))
    interaction_dt: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"Interaction(id={self.id!r}, user_id={self.user_id!r}, item_id={self.item_id!r}, interaction_dt={self.interaction_dt!r})"
