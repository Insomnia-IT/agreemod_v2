from dictionaries.diet_type import DietType
from dictionaries.feed_type import FeedType
from dictionaries.participation_role import ParticipationRole
from dictionaries.participation_type import ParticipationType
from pydantic import Field

from app.models.base import DomainModel
from app.models.direction import Direction
from app.models.person import Person


class Badge(DomainModel):

    name: str
    last_name: str | None = (
        None  # nullable поля в таблице должны иметь дефолтные значения
    )
    first_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    phone: str | None = None
    infant: bool
    diet: DietType = Field(default_factory=DietType.default)
    feed: FeedType | None = None
    number: str
    batch: int
    role: ParticipationRole | None
    participation: ParticipationType
    photo: str | None = None
    person: Person | None = None
    direction: Direction | None = None
    comment: str | None = None
