from datetime import time
import uuid

from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, UniqueConstraint
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
    noiton_id          Идентификатор   Notion        Строка UUID  Opt
    """

    __tablename__ = "participation"

    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    year: Mapped[int] = Column(Integer, nullable=False)  # req
    person_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("person.id"), nullable=False
    )  # req fk
    direction_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("direction.id"), nullable=False
    )  # req fk
    role_code: Mapped[str] = Column(
        String, ForeignKey("participation_role.code")
    )  # req fk
    participation_code: Mapped[str] = Column(
        String, ForeignKey("participation_type.code"), nullable=False
    )  # opt
    status_code: Mapped[str] = Column(
        String, ForeignKey("participation_status.code"), nullable=False
    )  # req fk
    notion_id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True))  # opt
    last_updated: Mapped[time] = Column(TIMESTAMP)


    _unique_constraint_notion = UniqueConstraint(notion_id)

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
