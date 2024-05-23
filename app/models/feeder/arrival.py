from uuid import UUID

from pydantic import BaseModel
from datetime import datetime


class Arrival(BaseModel):
    id: str
    deleted: bool
    badge: str
    status: str
    arrival_date: str
    arrival_transport: str
    departure_date: str
    departure_transport: str


class ArrivalWithMetadata(BaseModel):
    actor_badge: UUID
    date: datetime
    data: Arrival
