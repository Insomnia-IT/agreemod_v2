from typing import Self
from datetime import date, time

from sqlalchemy import Column, ForeignKey, Integer, String, Date, TIMESTAMP
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.dialects.postgresql import JSONB

# import sys
# sys.path.insert(1, 'C:/Users/ilyam/Documents/Insomnia_integrations/agreemod_v2/agreemod_v2/')
from app.db.meta import Base
from app.db.orm.dictionaries.transport_type import TransportTypeORM
from app.models.arrival import Arrival

class ArrivalORM(Base):
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
    id: Mapped[int] = Column(Integer, primary_key=True)
    badge: Mapped[str] = Column(String, ForeignKey("badge.number"), nullable=False)
    arrival_date: Mapped[date] = Column(Date, nullable=False)
    arrival_transport: Mapped[str] = Column(String, ForeignKey("transport_type.code"))
    arrival_registered: Mapped[time] = Column(TIMESTAMP)
    departure_date: Mapped[date] = Column(Date, nullable=False)
    departure_transport: Mapped[str] = Column(String, ForeignKey("transport_type.code"))
    departure_registered: Mapped[time] = Column(TIMESTAMP)
    extra_data: Mapped[dict|list] = Column(JSONB)
    comment: Mapped[str] = Column(String)

    transport_type: Mapped[TransportTypeORM] = relationship("TransportTypeORM")


    def __repr__(self):
        return (
            f"badge='{self.badge.number}', "
            f"arrival_date='{self.arrival_date}', "
            f"arrival_transport='{self.transport_type.code}', "
            f"arrival_registered='{self.arrival_registered}', "
            f"departure_date='{self.departure_date}', "
            f"departure_transport='{self.transport_type.code}', "
            f"departure_registered='{self.departure_registered}', "
            f"extra_data='{self.extra_data}', "
            f"comment='{self.comment}', "
        )

    @classmethod
    def to_orm(cls, model: Arrival) -> Self:
        return cls(
            badge=model.badge.number,
            arrival_date=model.arrival_date,
            arrival_transport=model.transport_type.name,
            arrival_registered=model.arrival_registered,
            departure_date=model.departure_date,
            departure_transport=model.transport_type.name,
            departure_registered=model.departure_registered,
            extra_data=model.extra_data,
            comment=model.comment,
        )

    def to_model(self) -> Arrival:
        return Arrival(
            badge=self.badge.number,
            arrival_date=self.arrival_date,
            arrival_transport=self.transport_type.name,
            arrival_registered=self.arrival_registered,
            departure_date=self.departure_date,
            departure_transport=self.transport_type.name,
            departure_registered=self.departure_registered,
            extra_data=self.extra_data,
            comment=self.comment,
        )
