from datetime import date, time

from dictionaries.transport_type import TransportType
from pydantic import BaseModel

from app.models.badge import Badge
from datetime import datetime


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
    last_updated: datetime = None
