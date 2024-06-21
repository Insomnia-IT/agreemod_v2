from datetime import time
import uuid

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class BadgeORM(Base, BaseORM):
    """
    infant: признак, что это ребенок
    diet: особенности питания, строка на основе справочника app.dictionaries.diet_type
    feed: платное / бесплатное питание, строка на основе справочника app.dictionaries.feed_type
    role: ForeignKey, строка на основе справочника app.dictionaries.participation_role
    person: ForeignKey, строка на основе таблицы app.models.person
    direction ForeignKey, строка на основе таблицы app.models.direction
    """

    __tablename__ = "badge"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String)
    first_name: Mapped[str] = Column(String)
    nickname: Mapped[str] = Column(String)
    gender: Mapped[str] = Column(String)
    phone: Mapped[str] = Column(String)
    infant_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("badge.notion_id", ondelete="CASCADE"),
        nullable=True,
    )
    diet: Mapped[str] = Column(String)
    feed: Mapped[str] = Column(String)
    number: Mapped[str] = Column(String)
    batch: Mapped[int] = Column(Integer)
    occupation: Mapped[str] = Column(String)
    role_code: Mapped[str] = Column(String, ForeignKey("participation_role.code"))
    photo: Mapped[str] = Column(String)
    person_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("person.notion_id"),
    )
    comment: Mapped[str] = Column(String)
    notion_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True))
    last_updated: Mapped[time] = Column(TIMESTAMP)

    _unique_constraint_number = UniqueConstraint(number)
    _unique_constraint_notion = UniqueConstraint(notion_id)


class AnonsORM(Base, BaseORM):
    __tablename__ = "anonymous_badges"
    notion_id: Mapped[int] = Column(UUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = Column(String)
    subtitle: Mapped[str] = Column(String)
    batch: Mapped[str] = Column(String)
    color: Mapped[str] = Column(String, ForeignKey("badge_color.code"))
    quantity: Mapped[int] = Column(Integer)
    to_print: Mapped[bool] = Column(Boolean)
    last_updated: Mapped[time] = Column(TIMESTAMP)
