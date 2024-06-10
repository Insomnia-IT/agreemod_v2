from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from dictionaries import TransportType


class Arrival(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    badge: str | None = None
    status: str | None = None
    arrival_date: datetime | None = None
    arrival_transport: TransportType | None = None
    departure_date: datetime | None = None
    departure_transport: str | None = None

    @staticmethod
    def from_db(arrival: 'Arrival') -> Arrival:
        return Arrival(
            id=str(arrival.id),
            badge=str(arrival.badge),
            arrival_date=arrival.arrival_date,
            arrival_transport=arrival.arrival_transport,
            departure_date=arrival.departure_date,
            departure_transport=arrival.departure_transport,
            deleted=False,  # TODO: добавить проверку на удаление
            status=arrival.arrival_registered  # TODO: уточнить по этому параметру
        )


class ArrivalWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Arrival | None = None
