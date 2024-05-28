from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import Mapped

from database.meta import Base


class ParticipationTypeORM(Base):
    __tablename__ = "participation_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    badge_color: Mapped[str] = Column(String, ForeignKey("badge_color.code"))
    comment: Mapped[str] = Column(String)
