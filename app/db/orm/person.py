from datetime import date
from typing import Self

from sqlalchemy import ARRAY, Column, Date, String
from sqlalchemy.orm import Mapped

from app.db.meta import Base
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

    @classmethod
    def to_orm(cls, person: Person) -> Self:
        return cls(
            name=person.name,
            last_name=person.last_name,
            first_name=person.first_name,
            nickname=person.nickname,
            other_names=person.other_names,
            gender=person.gender,
            birth_date=person.birth_date,
            city=person.city,
            telegram=person.telegram,
            phone=person.phone,
            email=person.email,
            diet=person.diet,
            comment=person.comment,
            notion_id=person.notion_id.hex,
        )

    def to_model(self) -> Person:
        return Person(
            name=self.name,
            last_name=self.last_name,
            first_name=self.first_name,
            nickname=self.nickname,
            other_names=self.other_names,
            gender=self.gender,
            birth_date=self.birth_date,
            city=self.city,
            telegram=self.telegram,
            phone=self.phone,
            email=self.email,
            diet=self.diet,
            comment=self.comment,
            notion_id=self.notion_id,
        )
