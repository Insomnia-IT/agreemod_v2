from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped

from db.meta import Base


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
    year: Mapped[int] = Column(Integer, nullable=False)  # req
    person_id: Mapped[str] = Column(
        String, ForeignKey("person.notion_id"), nullable=False
    )  # req fk
    direction_id: Mapped[str] = Column(
        String, ForeignKey("direction.notion_id"), nullable=False
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
    notion_id: Mapped[str] = Column(String)  # opt
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.current_timestamp())

    def __repr__(self):
        return (
            f"year='{self.year}',"
            f"person='{self.person_id}',"
            f"direction='{self.direction_id}',"
            f"role='{self.role_code}',"
            f"participation='{self.participation_code}',"
            f"status='{self.status_code}',"
            f"notion_id='{self.notion_id}',"
            f"last_updated='{self.last_updated}',"
        )
