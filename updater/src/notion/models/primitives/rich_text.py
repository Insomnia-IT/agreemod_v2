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
    text: Text | None = None
    annotations: Annotations | None = None
    plain_text: str
    href: str | None = None


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

    @classmethod
    def create_model(
        cls,
        values: list[str | dict],
    ):
        result = []
        for value in values:
            if isinstance(value, str):
                result.append(
                    {
                        "type": "rich_text",
                        "text": {"content": value},
                        "plain_text": value,
                    }
                )
            elif isinstance(value, dict):
                result.append(value)
            else:
                raise ValueError(f"{type(value)=}, {value=} is a wrong type")
        return cls.model_validate(
            dict(rich_text=[RichTextBody.model_validate(x) for x in result])
        )
