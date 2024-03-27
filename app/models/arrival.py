from datetime import date, time

from dictionaries.transport_type import TransportType
from pydantic import BaseModel

from app.models.badge import Badge


class Arrival(BaseModel):

    badge: Badge
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    extra_data: dict | None = None
    comment: str | None = None
