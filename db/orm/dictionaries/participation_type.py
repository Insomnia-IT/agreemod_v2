from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped

from db.meta import Base
from app.dictionaries.participation_type import ParticipationType


class ParticipationTypeORM(Base):
    __tablename__ = "participation_type"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    comment: Mapped[str] = Column(String)