from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from db.meta import Base
from app.dictionaries.badge_color import BadgeColor


class BadgeColorORM(Base):
    __tablename__ = "badge_color"

    code: Mapped[str] = Column(String, primary_key=True)
    color: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String)

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                color=x.value,
            )
            for x in BadgeColor
        ]
