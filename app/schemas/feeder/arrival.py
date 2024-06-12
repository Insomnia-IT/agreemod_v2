from datetime import datetime
from enum import StrEnum
from uuid import UUID

from dictionaries import TransportType
from dictionaries.dictionaries import ParticipationStatus
from pydantic import BaseModel, field_serializer


class Arrival(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    badge: UUID | None = None
    status: ParticipationStatus | None = None
    arrival_date: datetime | None = None
    arrival_transport: TransportType | None = None
    departure_date: datetime | None = None
    departure_transport: str | None = None


class ArrivalWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Arrival | None = None


class ArrivalResponse(BaseModel):
    id: UUID
    deleted: bool = False
    badge: UUID | None = None
    status: ParticipationStatus
    arrival_date: datetime | None = None
    arrival_transport: TransportType | None = None
    departure_date: datetime | None = None
    departure_transport: TransportType | None = None

    @field_serializer("status", "arrival_transport", "departure_transport")
    def serialize_enums(self, strenum: StrEnum, _info):
        return strenum.name

    @staticmethod
    def get_strenum_name(strenum: type[StrEnum], value: str):
        return strenum(value).name
