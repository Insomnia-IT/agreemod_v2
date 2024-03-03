from sqlalchemy import Column, Integer, String

from app.db.meta import Base
from app.models.direction import Direction


class DirectionORM(Base):
    """
    name:
    type: строка на основе справочника api.enums.services.Service
    first_year:
    last_year:
    notion_id:
    """

    __tablename__ = "direction"

    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    first_year = Column(Integer, nullable=True)
    last_year = Column(Integer, nullable=True)
    notion_id = Column(String, nullable=False, primary_key=True)

    def __repr__(self):
        return (
            f"Direction(name='{self.name}', "
            f"type='{self.type}', "
            f"first_year={self.first_year}, "
            f"last_year={self.last_year}, "
            f"notion_id='{self.notion_id}')"
        )

    @classmethod
    def to_orm(cls, model: Direction):
        return cls(
            name=model.name,
            type=model.type,
            first_year=model.first_year,
            last_year=model.last_year,
            notion_id=model.notion_id
        )

    def to_model(self) -> Direction:
        return Direction(
            name=self.name,
            type=self.type,
            first_year=self.first_year,
            last_year=self.last_year,
            notion_id=self.notion_id
        )