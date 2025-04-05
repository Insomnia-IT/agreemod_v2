import uuid

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base


class BadgeDirectionsORM(Base):
    """
    badge_id:
    direction_id:
    """

    __tablename__ = "badge_directions"
    badge_id: Mapped[int] = Column(
        Integer,
        ForeignKey("badge.nocode_int_id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    direction_id: Mapped[int] = Column(
        Integer,
        ForeignKey("direction.nocode_int_id", onupdate="CASCADE"),
        primary_key=True,
    )
