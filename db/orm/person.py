from datetime import date
from typing import Self

from sqlalchemy import ARRAY, Column, Date, String
from sqlalchemy.orm import Mapped

from db.meta import Base
from app.models.person import Person


class PersonORM(Base):
    __tablename__ = "person"

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
    notion_id: Mapped[str] = Column(String, nullable=False, primary_key=True)

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

