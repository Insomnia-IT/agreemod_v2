from datetime import date, datetime, time
from enum import StrEnum
from uuid import UUID

from dictionaries.dictionaries import ParticipationStatus
from dictionaries.transport_type import TransportType
from pydantic import BaseModel, Field, field_serializer, field_validator


class CodaArrival(BaseModel):
    coda_index: str = Field(..., alias="id")
    badge_id: UUID = Field(..., alias="badge_id")
    arrival_date: date = Field(..., alias="Дата заезда")
    arrival_transport: TransportType = Field(
        default=TransportType.UNDEFINED, alias="Способ заезда"
    )
    arrival_registered: str | None = None
    departure_date: date = Field(..., alias="Дата отъезда")
    departure_transport: TransportType = Field(
        default=TransportType.UNDEFINED, alias="Способ выезда"
    )
    departure_registered: str | None = None
    status: ParticipationStatus = Field(..., alias="Статус")
    extra_data: dict = Field(default_factory=dict)
    comment: str = Field(..., alias="Комментарии")
    last_updated: datetime = Field(default_factory=datetime.now)

    @field_validator("arrival_date", "departure_date", mode="before")
    @classmethod
    def format_date(cls, value: str) -> date | None:
        if not value:
            return None
        date_dt = date.fromisoformat(value.split("T")[0])
        assert date_dt.year == datetime.now().year
        return date_dt

    @field_validator("status", mode="before")
    @classmethod
    def format_status(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("arrival_transport", "departure_transport", mode="before")
    @classmethod
    def default_transport(cls, transport: str, _info):
        if not transport:
            return TransportType.UNDEFINED.value
        return transport

    @field_validator("arrival_registered", "departure_registered", mode="before")
    @classmethod
    def format_time(cls, value: str) -> time | None:
        if not value:
            return None
        return time.fromisoformat(value.split("T")[1].split("+")[0])

    @field_serializer("arrival_transport", "departure_transport", "status")
    def serialize_transport(self, strenum: StrEnum, _info):
        return strenum.name
