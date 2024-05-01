from datetime import date, time
from uuid import uuid4

from pydantic import BaseModel, Field
from dictionaries.transport_type import TransportType

from app.models.badge import Badge


class Arrival(BaseModel):
    id: str = Field(default_factory=uuid4().hex)
    badge: Badge
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    extra_data: dict | None = None
    comment: str | None = None
