import uuid
from sqlalchemy import UUID, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import Mapped

from database.meta import Base


class ParticipationRoleORM(Base):
    __tablename__ = "participation_role"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    is_lead: Mapped[bool] = Column(Boolean, nullable=True)
    is_team: Mapped[bool] = Column(Boolean, nullable=True)
    is_free_feed: Mapped[bool] = Column(Boolean)
    color: Mapped[str] = Column(String, ForeignKey("badge_color.code"), nullable=True)
    notion_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), nullable=True)
    comment: Mapped[str] = Column(String)
