from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from db.meta import Base
from db.orm.dictionaries.participation_status import ParticipationStatusORM
from db.orm.dictionaries.participation_role import ParticipationRoleORM
from db.orm.dictionaries.participation_type import ParticipationTypeORM
from db.orm.direction import DirectionORM
from db.orm.person import PersonORM

from app.models.participation import Participation

class ParticipationORM(Base):
    """
Атрибут            Содержимое      Тип данных    Cardinality
year               Год             Число         Req
person             Человек         Человеки      Req FK
direction          Служба/локация  Службы        Req FK
role               Роль            Справочник    Req FK
position           Должность       Срока         Opt
status             Статус          Справочник    Req FK
noiton_id          Идентификатор   Notion        Строка UUID  Opt
    """

    __tablename__ = "participation"

    id: Mapped[int] = Column(Integer, primary_key=True)
    year: Mapped[int] = Column(Integer, nullable=False) #req
    person_id: Mapped[str] = Column(String, ForeignKey("person.notion_id"), nullable=False) #req fk
    direction_id: Mapped[str] = Column(String, ForeignKey("direction.notion_id"), nullable=False) #req fk
    role_code: Mapped[str] = Column(String, ForeignKey("participation_role.code")) #req fk
    participation_code: Mapped[str] = Column(String, ForeignKey("participation_type.code"), nullable=False) #opt
    status_code: Mapped[str] = Column(String, ForeignKey("participation_status.code"), nullable=False) #req fk
    notion_id: Mapped[str] = Column(String, nullable=False, primary_key=True) #opt

    person: Mapped[PersonORM] = relationship("PersonORM")
    direction: Mapped[DirectionORM] = relationship("DirectionORM")
    role: Mapped[ParticipationRoleORM] = relationship("ParticipationRoleORM")
    status: Mapped[ParticipationStatusORM] = relationship("ParticipationStatusORM")
    participation: Mapped[ParticipationTypeORM] = relationship("ParticipationTypeORM")


    def __repr__(self):
        return (
            f"year='{self.year}',"
            f"person='{self.person_id}',"
            f"direction='{self.direction_id}',"
            f"role='{self.role_code}',"
            f"participation='{self.participation_code}',"
            f"status='{self.status_code}',"
            f"notion_id='{self.notion_id}',"
        )

    @classmethod
    def to_orm(cls, model: Participation):
        return cls(
            year=model.year,
            person_id=model.person.notion_id,
            direction_id=model.direction.notion_id,
            role=model.role_code,
            participation=model.participation.name,
            status=model.status.name,
            notion_id=model.notion_id,
        )

    def to_model(self) -> Participation:
        return Participation(
            year=self.name,
            person=self.person.to_model(),
            direction=self.direction.to_model(),
            role=self.role.value,
            participation=self.participation.value,
            status=self.status.value,
            notion_id=self.notion_id,
        )
