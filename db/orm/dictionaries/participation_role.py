from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped

from db.meta import Base


class ParticipationRoleORM(Base):
    __tablename__ = "participation_role"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    is_lead: Mapped[bool] = Column(Boolean, nullable=False)
    is_team: Mapped[bool] = Column(Boolean, nullable=False)
    is_free_feed: Mapped[bool] = Column(Boolean)
    comment: Mapped[str] = Column(String)
