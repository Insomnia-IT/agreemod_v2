from uuid import UUID

from pydantic import Field

from app.dto.badge import BadgeDTO
from app.models.base import DomainModel
from dictionaries import DirectionType


class Direction(DomainModel):
    name: str | None = None
    type: DirectionType | None = None
    first_year: int | None = None
    last_year: int | None = None
    notion_id: UUID

    badges: list[BadgeDTO] = Field(default_factory=list)
