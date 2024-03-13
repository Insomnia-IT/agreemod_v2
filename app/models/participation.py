from pydantic import BaseModel
from app.models.direction import Direction
from app.models.person import Person
from app.dictionaries.participation_status import ParticipationStatus
from app.dictionaries.participation_role import ParticipationRole

class Participation(BaseModel):
    year: int
    person: Person
    direction: Direction
    role: ParticipationRole
    position: str | None = None
    status: ParticipationStatus



