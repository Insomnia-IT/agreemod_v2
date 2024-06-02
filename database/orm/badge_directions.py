import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base


class BadgeDirectionsORM(Base):
    """
    badge_id:
    direction_id:
    """

    __tablename__ = "badge_directions"
    badge_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("badge.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    direction_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("direction.notion_id", onupdate="CASCADE"),
        primary_key=True,
    )
