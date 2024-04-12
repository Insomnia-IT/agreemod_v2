from pydantic import BaseModel, computed_field
from updater.src.notion.models.primitives.base import BaseNotionModel


class MultiselectBody(BaseModel):
    id: str
    name: str
    color: str


class Multiselect(BaseNotionModel):
    multi_select: list[MultiselectBody]

    @computed_field
    @property
    def value(self) -> list[str]:
        return [str(r.name) for r in self.multi_select]

    @computed_field
    @property
    def title(self) -> str:
        return ", ".join(r.name for r in self.multi_select if r)
