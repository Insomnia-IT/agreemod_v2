from pydantic import BaseModel, computed_field
from updater.src.notion.models.primitives.base import (
    Annotations,
    BaseNotionModel,
    MentionPage,
    MentionUser,
    Text,
)


class RichTextBody(BaseModel):
    type: str
    text: Text | None
    annotations: Annotations
    plain_text: str
    href: str | None


class RichMentionBody(BaseModel):
    type: str
    mention: MentionPage | MentionUser
    annotations: Annotations
    plain_text: str
    href: str | None


class RichText(BaseNotionModel):
    rich_text: list[RichTextBody | RichMentionBody]

    @computed_field
    @property
    def value(self) -> str:
        return "".join(
            rt.plain_text for rt in self.rich_text if isinstance(rt, RichTextBody)
        ).strip()
