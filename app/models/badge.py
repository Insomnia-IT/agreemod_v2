# import sys
# sys.path.insert(1, 'C:/Users/ilyam/Documents/Insomnia_integrations/agreemod_v2/agreemod_v2/')

from uuid import UUID
from pydantic import Field

from app.dictionaries.diet_type import DietType
from app.dictionaries.feed_type import FeedType
from app.dictionaries.participation_role import ParticipationRole
from app.dictionaries.participation_type import ParticipationType
from app.models.base import DomainModel


class Badge(DomainModel):

    name: str
    last_name: str | None = None  # nullable поля в таблице должны иметь дефолтные значения
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
    person: UUID | None = None
    direction: UUID | None = None
    comment: str | None = None
