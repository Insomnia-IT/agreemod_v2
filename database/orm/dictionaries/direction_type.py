from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped

from database.meta import Base


class DirectionTypeORM(Base):
    __tablename__ = "direction_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False, unique=True)
    is_federal: Mapped[int] = Column(Boolean, nullable=False)
    comment: Mapped[str] = Column(String)
