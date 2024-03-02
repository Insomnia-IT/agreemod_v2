# import sys
# sys.path.insert(1, 'C:/Users/ilyam/Documents/Insomnia_integrations/agreemod_v2/agreemod_v2/')

from pydantic import BaseModel, Field
from app.dictionaries.badge_diet_type import DietType
from app.dictionaries.badge_feed_type import FeedType


class Badge(BaseModel):

    name: str
    last_name: str | None = None # nullable поля в таблице должны иметь дефолтные значения
    first_name: str | None = None
    nickname: str | None = None
    gender: str | None = None
    phone: str | None = None
    infant: bool
    diet: DietType = Field(default_factory=DietType.default)
    feed: FeedType | None = None
    number: str
    batch: int
    role: str
    position: str | None = None
    photo: str | None = None
    person: str | None = None
    direction: str | None = None
    comment: str | None = None
    notion_id: str