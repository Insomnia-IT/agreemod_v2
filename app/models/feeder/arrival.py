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


class ArrivalWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Arrival | None = None
