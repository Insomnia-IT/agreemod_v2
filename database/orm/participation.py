from datetime import time
import uuid

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from database.meta import Base
from database.orm.base import BaseORM


class ParticipationORM(Base, BaseORM):
    """ TODO: док стринг не в полной мере отображает действительность
    Атрибут            Содержимое      Тип данных    Cardinality
    year               Год             Число         Req
    person             Человек         Человеки      Req FK
    direction          Служба/локация  Службы        Req FK
    role               Роль            Справочник    Req FK
    position           Должность       Срока         Opt
    status             Статус          Справочник    Req FK
    nocode_int_id          Идентификатор   Notion        Строка UUID  Opt
    """

    __tablename__ = "participation"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coda_index: Mapped[str] = Column(String, nullable=True)
    year: Mapped[int] = Column(Integer, nullable=True)  # req
    person_id: Mapped[int] = Column(
        Integer, ForeignKey("person.nocode_int_id"), nullable=False
    )  # req fk
    direction_id: Mapped[int] = Column(
        Integer, ForeignKey("direction.nocode_int_id"), nullable=False
    )  # req fk
    role_code: Mapped[str] = Column(
        String, ForeignKey("participation_role.code")
    )  # req fk
    status_code: Mapped[str] = Column(
        String, ForeignKey("participation_status.code"), nullable=True
    )  # req fk
    nocode_int_id: Mapped[int] = Column(Integer)  # opt
    deleted: Mapped[bool] = Column(Boolean, nullable=True)
    last_updated: Mapped[time] = Column(TIMESTAMP)


    _unique_constraint_notion = UniqueConstraint(nocode_int_id)
    _unique_constraint_coda = UniqueConstraint(coda_index)

    def __repr__(self):
        return (
            f"year='{self.year}',"
            f"person='{self.person_id}',"
            f"direction='{self.direction_id}',"
            f"role='{self.role_code}',"
            f"status='{self.status_code}',"
            f"nocode_int_id='{self.nocode_int_id}',"
        )
