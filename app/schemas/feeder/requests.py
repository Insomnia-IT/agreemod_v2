from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.schemas.feeder.arrival import Arrival, ArrivalWithMetadata
from app.schemas.feeder.badge import Badge, BadgeWithMetadata
from app.schemas.feeder.directions import Direction
from app.schemas.feeder.engagement import Engagement
from app.schemas.feeder.person import Person


class SyncResponseSchema(BaseModel):
    badges: List[Badge] | None = None
    arrivals: List[Arrival] | None = None
    engagements: List[Engagement] | None = None
    persons: List[Person] | None = None
    directions: List[Direction] | None = None


class BackSyncIntakeSchema(BaseModel):
    badges: List[BadgeWithMetadata] | None = None
    arrivals: List[ArrivalWithMetadata] | None = None
