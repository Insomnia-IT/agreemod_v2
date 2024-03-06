from pydantic import BaseModel, computed_field

from updater.notion.models.primitives.base import Annotations, BaseNotionModel, Text


class RichTextBody(BaseModel):
    type: str
    text: Text | None
    annotations: Annotations
    plain_text: str
    href: str | None


class RichText(BaseNotionModel):
    rich_text: list[RichTextBody]

    @computed_field
    @property
    def value(self) -> str:
        return "".join(rt.plain_text for rt in self.rich_text).strip()
