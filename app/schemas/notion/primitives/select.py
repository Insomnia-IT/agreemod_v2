from pydantic import BaseModel, computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class SelectBody(BaseModel):
    name: str

    @computed_field
    @property
    def color(self) -> str:
        return (
            "red" if self.name == 'Ж'
            else "blue" if self.name == 'М'
            else "gray"
        )

class Select(BaseNotionModel):
    select: SelectBody | None

    @classmethod
    def create_model(cls, value: str | dict):
        return cls.model_validate(
            dict(select=SelectBody.model_validate({"name": value} if isinstance(value, str) else value))
        )


class SelectNone(Select):
    pass

class SelectColor(Select):
    pass