from datetime import datetime
from uuid import UUID

from dictionaries.dictionaries import DirectionType
from pydantic import ConfigDict, Field

from app.dto.badge import BadgeDTO
from app.models.base import DomainModel


class Direction(DomainModel):
    name: str | None = None
    type: DirectionType | None = None
    first_year: int | None = None
    last_year: int | None = None
    last_updated: datetime | None = None

    nocode_int_id: int

    badges: list[BadgeDTO] = Field(default_factory=list)

    model_config = ConfigDict(
        json_encoders={
            DirectionType: lambda t: t.value,
        },
        use_enum_values=True,
    )
