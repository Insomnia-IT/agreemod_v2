from typing import List

from pydantic import BaseModel

from app.schemas.feeder.arrival import ArrivalResponse, ArrivalWithMetadata
from app.schemas.feeder.badge import BadgeResponse, BadgeWithMetadata
from app.schemas.feeder.directions import DirectionResponse
from app.schemas.feeder.engagement import EngagementResponse
from app.schemas.feeder.person import PersonResponse


class SyncResponseSchema(BaseModel):
    badges: List[BadgeResponse] | None = None
    arrivals: List[ArrivalResponse] | None = None
    engagements: List[EngagementResponse] | None = None
    persons: List[PersonResponse] | None = None
    directions: List[DirectionResponse] | None = None


class BackSyncIntakeSchema(BaseModel):
    badges: List[BadgeWithMetadata] | None = None
    arrivals: List[ArrivalWithMetadata] | None = None
