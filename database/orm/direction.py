from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class DirectionORM(Base, BaseORM):
    """
    name:
    type: строка на основе справочника api.enums.services.Service
    first_year:
    last_year:
    notion_id:
    """

    __tablename__ = "direction"

    name: Mapped[str] = Column(String, nullable=False)
    type: Mapped[str] = Column(
        String, ForeignKey("direction_type.code"), nullable=False
    )
    first_year: Mapped[int] = Column(Integer)
    last_year: Mapped[int] = Column(Integer)
    notion_id: Mapped[str] = Column(String, nullable=False, primary_key=True)

    def __repr__(self):
        return (
            f"Direction(name='{self.name}', "
            f"type='{self.type}', "
            f"first_year={self.first_year}, "
            f"last_year={self.last_year}, "
            f"notion_id='{self.notion_id}')"
        )
