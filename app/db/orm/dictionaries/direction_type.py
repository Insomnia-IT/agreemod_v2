from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped

from app.db.meta import Base
from app.dictionaries.direction_type import DirectionType


class DirectionTypeORM(Base):
    __tablename__ = "direction_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    is_federal: Mapped[int] = Column(Boolean, nullable=False)
    comment: Mapped[str] = Column(String)

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                is_federal=x.is_federal,
            )
            for x in DirectionType
        ]
