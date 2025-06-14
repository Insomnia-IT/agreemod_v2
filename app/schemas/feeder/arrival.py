from datetime import date, datetime
from enum import StrEnum
from uuid import UUID

from dictionaries import TransportType
from dictionaries.dictionaries import ParticipationStatus
from pydantic import BaseModel, Field, field_serializer, field_validator


class Arrival(BaseModel):
    id: UUID
    deleted: bool | None = None
    badge_id: UUID | None = Field(None, validation_alias="badge")
    status: ParticipationStatus | None = None
    arrival_date: date | None = None
    arrival_transport: TransportType | None = None
    departure_date: date | None = None
    departure_transport: TransportType | None = None

    @field_validator("status", mode="before")
    @classmethod
    def convert_status(cls, value: str):
        try:
            return ParticipationStatus[value].value
        except KeyError:
            return value

    @field_validator("arrival_transport", "departure_transport", mode="before")
    @classmethod
    def convert_transport(cls, value: str):
        try:
            return TransportType[value].value
        except KeyError:
            return value


class ArrivalWithMetadata(BaseModel):
    actor_badge: UUID | None = None
    date: datetime | None = None
    data: Arrival | None = None


class ArrivalResponse(BaseModel):
    id: UUID
    deleted: bool = False
    badge: UUID | None = None
    status: ParticipationStatus
    arrival_date: date | None = None
    arrival_transport: TransportType | None = None
    departure_date: date | None = None
    departure_transport: TransportType | None = None

    @field_serializer("status", "arrival_transport", "departure_transport")
    def serialize_enums(self, strenum: StrEnum, _info):
        return strenum.name

    @staticmethod
    def get_strenum_name(strenum: type[StrEnum], value: str):
        return strenum(value).name
