from pydantic import BaseModel, computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class MultiselectBody(BaseModel):
    id: str
    name: str
    color: str


class Multiselect(BaseNotionModel):
    multi_select: list[MultiselectBody]