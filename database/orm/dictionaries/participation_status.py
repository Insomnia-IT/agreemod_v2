from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped

from database.meta import Base


class ParticipationStatusORM(Base):
    __tablename__ = "participation_status"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    to_list: Mapped[int] = Column(Boolean, nullable=False)
    comment: Mapped[str] = Column(String)
