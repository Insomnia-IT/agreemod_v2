from pydantic import BaseModel as BaseModel
from pydantic import computed_field
from app.schemas.notion.primitives.base import Annotations, BaseNotionModel, Text


class TitleBody(BaseModel):
    type: str | None = "text"
    text: Text
    href: str | None = None


class Title(BaseNotionModel):
    title: list[TitleBody]

    def __str__(self):
        return self.value.replace(",", "")

    def __bool__(self):
        return bool(self.value)

    @classmethod
    def create_model(cls, values: list[str | dict]):
        result = []
        for value in values:
            if isinstance(value, str):
                result.append({"text": {"content": value}})
            elif isinstance(value, dict):
                result.append(value)
            else:
                raise ValueError(f"{type(value)=}, {value=} is a wrong type")
        return cls.model_validate({"title": result})
