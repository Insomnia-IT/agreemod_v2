from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.models.feeder.arrival import Arrival, ArrivalWithMetadata
from app.models.feeder.badge import Badge, BadgeWithMetadata
from app.models.feeder.directions import Direction
from app.models.feeder.engagement import Engagement
from app.models.feeder.person import Person


class ResponseModelGET(BaseModel):
    badges: List[Badge] | None = None
    arrivals: List[Arrival] | None = None
    engagements: List[Engagement] | None = None
    persons: List[Person] | None = None
    directions: List[Direction] | None = None


class RequestModelPOST(BaseModel):
    badges: List[BadgeWithMetadata] | None = None
    arrivals: List[ArrivalWithMetadata] | None = None
