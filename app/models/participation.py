from pydantic import BaseModel
from datetime import datetime

from app.models.direction import Direction
from app.models.person import Person
from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_status import ParticipationStatus


class Participation(BaseModel):
    year: int
    person: Person
    direction: Direction
    role: ParticipationRole
    position: str | None = None
    status: ParticipationStatus
    last_updated: datetime = None
