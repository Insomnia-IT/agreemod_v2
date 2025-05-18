from pydantic import BaseModel, computed_field
from app.schemas.notion.primitives.base import Annotations, BaseNotionModel, MentionPage, MentionUser, Text


class RichTextBody(BaseModel):
    type: str
    text: Text | None = None
    plain_text: str | int | float
    href: str | None = None


class RichMentionBody(BaseModel):
    type: str
    mention: MentionPage | MentionUser
    annotations: Annotations
    plain_text: str
    href: str | None


class RichText(BaseNotionModel):
    rich_text: list[RichTextBody]

    @classmethod
    def create_model(
        cls,
        values: list[str | dict],
    ):
        result = []
        for value in values:
            if isinstance(value, (str, int, float, type(None))):
                result.append(
                    {
                        "type": "text",
                        "text": {"content": value if value is not None else ''},
                        "plain_text": value if value is not None else '',
                    }
                )
            elif isinstance(value, dict):
                result.append(value)
            else:
                raise ValueError(f"{type(value)=}, {value=} is a wrong type")
        return cls.model_validate(dict(rich_text=[RichTextBody.model_validate(x) for x in result]))
