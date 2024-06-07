from datetime import datetime
from uuid import UUID

from dictionaries.dictionaries import ParticipationRole, ParticipationStatus

from app.dto.direction import DirectionDTO
from app.models.base import DomainModel
from app.models.person import Person


class Participation(DomainModel):
    year: int
    person: Person | UUID
    direction: DirectionDTO | UUID
    role: ParticipationRole
    status: ParticipationStatus
    notion_id: UUID | None = None
    last_updated: datetime = None
