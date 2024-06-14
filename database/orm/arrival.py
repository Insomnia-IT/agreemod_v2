import uuid
from datetime import date, time

from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped

# import sys
# sys.path.insert(1, 'C:/Users/ilyam/Documents/Insomnia_integrations/agreemod_v2/agreemod_v2/')
from database.meta import Base
from database.orm.base import BaseORM


class ArrivalORM(Base, BaseORM):
    """
    Атрибут	                Содержимое	        Тип данных	    Cardinality	    Пояснение
    badge	                Бейдж	            Бейдж	        Req
    arrival_date	        Дата заезда	        date	        Req	            Предварительно планируется
    arrival_transport	    Способ заезда	    Справочник	    Opt
    arrival_registered	    Отметка о заезде	timestamp	    Opt	            При регистрации в Бюро
    departure_date	        Дата отъезда	    date	        Req	            Предварительно планируется
    departure_transport	    Способ выезда	    Справочник	    Opt
    departure_registered	Отметка об отъезде	timestamp	    Opt	            При досрочном отъезде
    extra_data	            Для автобуса	    JSONB	        Opt	            Персональные данные для транспортной компании (желательно хранить шифровано)
    comment	                Комментарии	        Строка	        Opt
    """

    __tablename__ = "arrival"
    id: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coda_index: Mapped[int] = Column(Integer)
    badge_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("badge.notion_id"), nullable=False
    )
    arrival_date: Mapped[date] = Column(Date, nullable=False)
    arrival_transport: Mapped[str] = Column(String, ForeignKey("transport_type.code"))
    arrival_registered: Mapped[time] = Column(TIMESTAMP)
    departure_date: Mapped[date] = Column(Date, nullable=False)
    departure_transport: Mapped[str] = Column(String, ForeignKey("transport_type.code"))
    departure_registered: Mapped[time] = Column(TIMESTAMP)
    status: Mapped[str] = Column(String, ForeignKey("participation_status.code"))
    extra_data: Mapped[dict | list] = Column(JSONB)
    comment: Mapped[str] = Column(String)
    last_updated: Mapped[time] = Column(TIMESTAMP)

    _unique_constraint_coda = UniqueConstraint(coda_index)

    def __repr__(self):
        return (
            f"badge_id='{self.badge_id}', "
            f"arrival_date='{self.arrival_date}', "
            f"arrival_transport='{self.arrival_transport}', "
            f"arrival_registered='{self.arrival_registered}', "
            f"departure_date='{self.departure_date}', "
            f"departure_transport='{self.departure_transport}', "
            f"departure_registered='{self.departure_registered}', "
            f"extra_data='{self.extra_data}', "
            f"comment='{self.comment}', "
        )
