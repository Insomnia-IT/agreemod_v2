from datetime import datetime
from uuid import UUID

from dictionaries.dictionaries import EngagementRole, EngagementStatus
from pydantic import ConfigDict

from app.dto.direction import DirectionDTO
from app.models.base import DomainModel
from app.models.person import Person


class Engagement(DomainModel):
    year: int
    person: Person | int | UUID
    direction: DirectionDTO | int | UUID
    role: EngagementRole
    status: EngagementStatus | None
    nocode_int_id: int | None = None
    last_updated: datetime = None
    deleted: bool | None = False

    model_config = ConfigDict(
        json_encoders={EngagementRole: lambda t: t.name, EngagementStatus: lambda p: p.name}, use_enum_values=True
    )
