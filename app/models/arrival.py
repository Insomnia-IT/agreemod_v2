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

    model_config = ConfigDict(use_enum_values=True)
