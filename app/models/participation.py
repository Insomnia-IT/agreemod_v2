from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus
from dictionaries.participation_type import ParticipationType

from uuid import UUID
from pydantic import BaseModel

from app.models.direction import Direction
from app.models.person import Person


class Participation(BaseModel):
    year: int
    person: Person
    direction: Direction
    role: ParticipationRole
    position: ParticipationType | None = None
    status: ParticipationStatus
    notion_id: UUID | None = None
