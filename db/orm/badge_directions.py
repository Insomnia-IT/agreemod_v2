from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped

from db.meta import Base

class BadgeDirectionsORM(Base):
    """
    badge_id:
    direction_id:
    """

    __tablename__ = "badge_directions"

    badge_id: Mapped[str] = Column(String, ForeignKey("badge.notion_id"), primary_key=True)
    direction_id: Mapped[str] = Column(String, ForeignKey("direction.notion_id"), primary_key=True)