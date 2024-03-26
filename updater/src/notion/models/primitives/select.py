from pydantic import BaseModel, computed_field
from updater.src.notion.models.primitives.base import BaseNotionModel


class SelectBody(BaseModel):
    id: str
    name: str
    color: str


class Select(BaseNotionModel):
    select: SelectBody | None

    @computed_field
    @property
    def value(self) -> str:
        return self.select.name if self.select else None

    @computed_field
    @property
    def title(self) -> str:
        return self.select.name if self.select else ""


class SelectNone(Select):

    @computed_field
    @property
    def value(self) -> str:
        return super().value or None

    @computed_field
    @property
    def title(self) -> str:
        return self.value


class SelectColor(Select):
    @computed_field
    @property
    def value(self) -> str | None:
        return self.select.color if self.select else None
