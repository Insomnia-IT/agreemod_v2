from datetime import date, time
from app.dictionaries.transport_type import TransportType
from app.models.base import DomainModel

class Arrival(DomainModel):

    badge: str
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    extra_data: dict | None = None
    comment: str | None = None

    class Config:
        from_attributes = True