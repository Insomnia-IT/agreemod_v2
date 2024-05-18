from typing import ForwardRef
from uuid import UUID

from app.dto.badge import BadgeDTO
from dictionaries import DirectionType
from pydantic import Field

from app.models.base import DomainModel

class Direction(DomainModel):
    name: str | None = None
    type: DirectionType | None = None
    first_year: int | None = None
    last_year: int | None = None
    notion_id: UUID

    badges: list[BadgeDTO] = Field(default_factory=list)