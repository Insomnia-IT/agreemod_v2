from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped

from db.meta import Base

class BadgeDirectionsORM(Base):
    """
    badge_id:
    direction_id:
    """

    __tablename__ = "badge_directions"
    __table_args__ = (
        PrimaryKeyConstraint('badge_id', 'direction_id'),
    )

    badge_id: Mapped[str] = Column(String, ForeignKey("badge.notion_id", onupdate="CASCADE", ondelete="CASCADE"))
    direction_id: Mapped[str] = Column(String, ForeignKey("direction.notion_id", onupdate="CASCADE"))