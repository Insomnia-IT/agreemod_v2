from datetime import datetime
import uuid

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class DirectionORM(Base, BaseORM):
    """
    name:
    type: строка на основе справочника api.enums.services.Service
    first_year:
    last_year:
    nocode_int_id:
    """

    __tablename__ = "direction"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    type: Mapped[str] = Column(
        String,
        ForeignKey("direction_type.name"),
        nullable=False,
    )
    first_year: Mapped[int] = Column(Integer)
    last_year: Mapped[int] = Column(Integer)
    nocode_int_id: Mapped[int] = Column(Integer)
    deleted: Mapped[bool] = Column(Boolean, nullable=True)
    last_updated: Mapped[datetime] = Column(TIMESTAMP)

    _unique_constraint = UniqueConstraint(nocode_int_id)

    def __repr__(self):
        return (
            f"Direction(name='{self.name}', "
            f"type='{self.type}', "
            f"first_year={self.first_year}, "
            f"last_year={self.last_year}, "
            f"nocode_int_id='{self.nocode_int_id}')"
        )
