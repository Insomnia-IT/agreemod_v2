from pydantic import BaseModel, computed_field

from updater.src.notion.models.primitives.base import BaseNotionModel


class SelectBody(BaseModel):
    id: str | None = None
    name: str
    color: str | None = None


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
    
    @classmethod
    def create_model(cls, value: str | dict):
        return cls.model_validate(
            dict(select=SelectBody.model_validate(
                {'name': value} if isinstance(value, str) else value
            ))
        )



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
