from pydantic import BaseModel

from app.dictionaries.participation_role import ParticipationRole
from app.dictionaries.participation_status import ParticipationStatus
from app.models.direction import Direction
from app.models.person import Person


class Participation(BaseModel):
    year: int
    person: Person
    direction: Direction
    role: ParticipationRole
    position: str | None = None
    status: ParticipationStatus
