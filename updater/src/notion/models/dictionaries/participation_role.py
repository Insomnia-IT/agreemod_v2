from dictionaries.badge_color import BadgeColor
from pydantic import Field, field_validator
from updater.src.notion.models.base import NotionModel
from updater.src.notion.models.primitives.checkbox import Checkbox
from updater.src.notion.models.primitives.rich_text import RichText
from updater.src.notion.models.primitives.select import Select
from updater.src.notion.models.primitives.title import Title


class ParticipationRoleNotion(NotionModel):
    code: RichText = Field(..., alias="Code")
    name: Title = Field(..., alias="Name")
    is_lead: Checkbox = Field(..., alias="Рук")
    is_team: Checkbox = Field(..., alias="Фед")
    is_free_feed: Checkbox = Field(..., alias="Питание")
    color: Select = Field(..., alias="Цвет")
    comment: str = Field(default="")

    @field_validator("color", mode="after")
    @classmethod
    def convert_color(cls, value: Select) -> str:
        return BadgeColor(value.value.lower()).name
