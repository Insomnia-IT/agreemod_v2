from __future__ import annotations

from datetime import date, datetime, time, timezone
from uuid import UUID

from dictionaries import TransportType

from app.dto.badge import BadgeDTO
from app.models.base import DomainModel


class Arrival(DomainModel):
    badge: BadgeDTO | UUID
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    extra_data: dict | None = None
    comment: str | None = None
    last_updated: datetime | None = None

    # @staticmethod
    # def from_feeder(actor_badge: UUID, data: ArrivalAPI) -> Arrival:
    #     return Arrival(
    #         id=actor_badge,
    #         badge=data.badge,
    #         arrival_date=data.arrival_date.date(),  # TODO: уточнить можно ли так конвертить
    #         arrival_transport=TransportType(data.arrival_transport) if data.arrival_transport else None,
    #         arrival_registered=None,  # Предполагается, что данных нет # TODO: уточнить
    #         departure_date=data.departure_date.date(),  # TODO: уточнить можно ли так конвертить
    #         departure_transport=data.departure_transport if data.departure_transport else None,
    #         departure_registered=None,  # Предполагается, что данных нет # TODO: уточнить
    #         extra_data=None,  # Предполагается, что дополнительных данных нет # TODO: уточнить
    #         comment=None,  # Предполагается, что комментариев нет # TODO: уточнить
    #         last_updated=datetime.now(timezone.utc)
    #     )
