from pydantic import BaseModel as BaseModel
from pydantic import computed_field
from updater.notion.models.primitives.base import Annotations, BaseNotionModel, Text


class TitleBody(BaseModel):
    annotations: Annotations
    type: str
    text: Text
    plain_text: str
    href: str | None


class Title(BaseNotionModel):
    title: list[TitleBody]

    @computed_field
    @property
    def value(self) -> str:
        return ", ".join(title.plain_text for title in self.title)

    def __str__(self):
        return self.value.replace(",", "")

    def __bool__(self):
        return bool(self.value)
