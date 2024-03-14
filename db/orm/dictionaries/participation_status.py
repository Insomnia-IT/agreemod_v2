from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Mapped

from db.meta import Base
from app.dictionaries.participation_status import ParticipationStatus


class ParticipationStatusORM(Base):
    __tablename__ = "participation_status"

    code: Mapped[str] = Column(String, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    to_list: Mapped[int] = Column(Boolean, nullable=False)
    comment: Mapped[str] = Column(String)

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                to_list=x.to_list,
            )
            for x in ParticipationStatus
        ]
