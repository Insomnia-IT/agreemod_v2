import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from db.meta import Base


class DirectionORM(Base):
    """
    name:
    type: строка на основе справочника api.enums.services.Service
    first_year:
    last_year:
    notion_id:
    """

    __tablename__ = "direction"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    type: Mapped[str] = Column(
        String,
        ForeignKey("direction_type.code"),
        nullable=False,
    )
    first_year: Mapped[int] = Column(Integer)
    last_year: Mapped[int] = Column(Integer)
    notion_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True))

    _unique_constraint = UniqueConstraint(notion_id)

    def __repr__(self):
        return (
            f"Direction(name='{self.name}', "
            f"type='{self.type}', "
            f"first_year={self.first_year}, "
            f"last_year={self.last_year}, "
            f"notion_id='{self.notion_id}')"
        )
