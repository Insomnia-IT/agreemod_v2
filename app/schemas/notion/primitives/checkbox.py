from pydantic import computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class Checkbox(BaseNotionModel):
    checkbox: bool

    def __bool__(self):
        return self.value
    
    @classmethod
    def create_model(cls, value: bool):
        return cls.model_validate({"checkbox": value})
