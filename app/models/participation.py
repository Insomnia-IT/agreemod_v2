from uuid import UUID

from app.dto.direction import DirectionDTO
from app.models.base import DomainModel
from app.models.person import Person
from dictionaries import (
    ParticipationRole,
    ParticipationStatus,
    ParticipationType,
)


class Participation(DomainModel):
    year: int
    person: Person | UUID
    direction: DirectionDTO | UUID
    role: ParticipationRole
    participation_type: ParticipationType
    status: ParticipationStatus
    notion_id: UUID | None = None
