import uuid
from datetime import date, datetime

from sqlalchemy import ARRAY, TIMESTAMP, Column, Date, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class PersonORM(Base, BaseORM):
    __tablename__ = "person"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String)
    first_name: Mapped[str] = Column(String)
    nickname: Mapped[str] = Column(String)
    other_names: Mapped[list[str]] = Column(ARRAY(String))
    gender: Mapped[str] = Column(String)
    birth_date: Mapped[date] = Column(Date)
    city: Mapped[str] = Column(String)
    telegram: Mapped[str] = Column(String)
    phone: Mapped[str] = Column(String)
    email: Mapped[str] = Column(String)
    diet: Mapped[str] = Column(String)
    comment: Mapped[str] = Column(String)
    notion_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True))
    last_updated: Mapped[datetime] = Column(TIMESTAMP)

    _unique_constraint_notion = UniqueConstraint(notion_id)

    def __repr__(self):
        return (
            f"Person(name='{self.name}', "
            f"last_name='{self.last_name}', "
            f"first_name='{self.first_name}', "
            f"nickname='{self.nickname}', "
            f"other_names={self.other_names}, "
            f"gender='{self.gender}', "
            f"birth_date={self.birth_date}, "
            f"city='{self.city}', "
            f"telegram='{self.telegram}', "
            f"phone='{self.phone}', "
            f"email='{self.email}', "
            f"diet='{self.diet}', "
            f"comment='{self.comment}', "
            f"notion_id='{self.notion_id}')"
        )
