from pydantic import BaseModel as BaseModel
from pydantic import computed_field
from updater.src.notion.models.primitives.base import Annotations, BaseNotionModel, Text


class TitleBody(BaseModel):
    annotations: Annotations | None = None
    type: str | None = None
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

    @classmethod
    def create_model(cls, values: list[str | dict]):
        result = []
        for value in values:
            if isinstance(value, str):
                result.append({"text": {"content": value}, "plain_text": value})
            elif isinstance(value, dict):
                result.append(value)
            else:
                raise ValueError(f"{type(value)=}, {value=} is a wrong type")
        return cls.model_validate(
            title=[TitleBody.model_validate(x) for x in result], from_attributes=True
        )
