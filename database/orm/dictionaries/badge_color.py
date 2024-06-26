from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from database.meta import Base


class BadgeColorORM(Base):
    __tablename__ = "badge_color"

    code: Mapped[str] = Column(String, primary_key=True)
    color: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String)
