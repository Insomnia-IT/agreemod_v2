from datetime import date, time
from app.dictionaries.transport_type import TransportType
from pydantic import BaseModel

class Arrival(BaseModel):

    badge: str
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    extra_data: dict | None = None
    comment: str | None = None