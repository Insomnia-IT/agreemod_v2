from typing import Self

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from db.meta import Base
from db.orm.dictionaries.participation_role import ParticipationRoleORM
from db.orm.dictionaries.participation_type import ParticipationTypeORM
from db.orm.direction import DirectionORM
from db.orm.person import PersonORM
from app.models.badge import Badge


class BadgeORM(Base):
    """
    infant: признак, что это ребенок
    diet: особенности питания, строка на основе справочника app.dictionaries.diet_type
    feed: платное / бесплатное питание, строка на основе справочника app.dictionaries.feed_type
    role: ForeignKey, строка на основе справочника app.dictionaries.participation_role
    person: ForeignKey, строка на основе таблицы app.models.person
    direction ForeignKey, строка на основе таблицы app.models.direction
    """

    __tablename__ = "badge"

    name: Mapped[str] = Column(String, nullable=False)
    last_name: Mapped[str] = Column(String)
    first_name: Mapped[str] = Column(String)
    nickname: Mapped[str] = Column(String)
    gender: Mapped[str] = Column(String)
    phone: Mapped[str] = Column(String)
    infant: Mapped[bool] = Column(Boolean)
    diet: Mapped[str] = Column(String)
    feed: Mapped[str] = Column(String)
    number: Mapped[str] = Column(String, nullable=False)
    batch: Mapped[int] = Column(Integer, nullable=False)
    participation_code: Mapped[str] = Column(String, ForeignKey("participation_type.code"), nullable=False)
    role_code: Mapped[str] = Column(String, ForeignKey("participation_role.code"))
    photo: Mapped[str] = Column(String)
    person_id: Mapped[str] = Column(String, ForeignKey("person.notion_id"))
    direction_id: Mapped[str] = Column(String, ForeignKey("direction.notion_id"))
    comment: Mapped[str] = Column(String)
    notion_id: Mapped[str] = Column(String, nullable=False, primary_key=True)

    _unique_constraint = UniqueConstraint(number)

    participation: Mapped[ParticipationTypeORM] = relationship("ParticipationTypeORM")
    role: Mapped[ParticipationRoleORM] = relationship("ParticipationRoleORM")
    person: Mapped[PersonORM] = relationship("PersonORM")
    direction: Mapped[DirectionORM] = relationship("DirectionORM")

    @classmethod
    def to_orm(cls, model: Badge) -> Self:
        return cls(
            name=model.name,
            last_name=model.last_name,
            first_name=model.first_name,
            nickname=model.nickname,
            gender=model.gender,
            phone=model.phone,
            infant=model.infant,
            diet=model.diet,
            feed=model.feed,
            number=model.number,
            batch=model.batch,
            participation=model.participation.name,
            role=model.role.name if model.role else None,
            photo=model.photo,
            person_id=model.person.notion_id.hex if model.person else None,
            direction_id=model.direction.notion_id.hex if model.direction else None,
            comment=model.comment,
            notion_id=model.notion_id.hex,
        )

    def to_model(self) -> Badge:
        return Badge(
            name=self.name,
            last_name=self.last_name,
            first_name=self.first_name,
            nickname=self.nickname,
            gender=self.gender,
            phone=self.phone,
            infant=self.infant,
            diet=self.diet,
            feed=self.feed,
            number=self.number,
            batch=self.batch,
            participation=self.participation.name,
            role=self.role.name,
            photo=self.photo,
            person=self.person.to_model(),
            direction=self.direction.to_model(),
            comment=self.comment,
            notion_id=self.notion_id,
        )

    def __repr__(self):
        return (
            f"Badge(name='{self.name}', "
            f"last_name='{self.last_name}', "
            f"first_name='{self.first_name}', "
            f"nickname='{self.nickname}', "
            f"gender='{self.gender}', "
            f"phone='{self.phone}', "
            f"infant='{self.infant}', "
            f"diet='{self.diet}', "
            f"feed='{self.feed}', "
            f"number='{self.number}', "
            f"batch='{self.batch}', "
            f"participation='{self.participation.name}', "
            f"role='{self.role.name}', "
            f"photo='{self.photo}', "
            f"person='{self.person.name}', "
            f"direction='{self.direction.name}', "
            f"comment='{self.comment}', "
            f"notion_id='{self.notion_id}')"
        )
