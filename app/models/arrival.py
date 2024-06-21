from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from dictionaries import TransportType
from dictionaries.dictionaries import ParticipationStatus
from pydantic import ConfigDict

from app.dto.badge import BadgeDTO
from app.models.base import DomainModel


class Arrival(DomainModel):
    badge: BadgeDTO | UUID
    arrival_date: date
    arrival_transport: TransportType | None = None
    arrival_registered: time | None = None
    departure_date: date
    departure_transport: TransportType | None = None
    departure_registered: time | None = None
    status: ParticipationStatus
    extra_data: dict | None = None
    comment: str | None = None
    last_updated: datetime | None = None

    model_config = ConfigDict(
        json_encoders={
            TransportType: lambda t: t.name,
            ParticipationStatus: lambda s: s.name,
        },
        use_enum_values=False,
    )

    # @field_validator("status", mode="before")
    # @classmethod
    # def convert_status(cls, value: str) -> ParticipationStatus:
    #     try:
    #         return ParticipationStatus[value]
    #     except KeyError:
    #         return value

    # @field_validator("arrival_transport", "departure_transport", mode="before")
    # @classmethod
    # def convert_transport(cls, value: str) -> TransportType:
    #     try:
    #         return TransportType[value]
    #     except KeyError:
    #         return value
