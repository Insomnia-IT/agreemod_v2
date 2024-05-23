from __future__ import annotations

from typing import List

from pydantic import BaseModel

from app.models.feeder import Direction
from app.models.feeder.arrival import Arrival, ArrivalWithMetadata
from app.models.feeder.badge import Badge, BadgeWithMetadata
from app.models.feeder.engagement import Engagement
from app.models.feeder.person import Person


class ResponseModelGET(BaseModel):
    badges: List[Badge]
    arrivals: List[Arrival]
    engagements: List[Engagement]
    persons: List[Person]
    directions: List[Direction]


class RequestModelPOST(BaseModel):
    badges: List[BadgeWithMetadata]
    arrivals: List[ArrivalWithMetadata]