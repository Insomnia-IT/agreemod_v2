from pydantic import computed_field
from updater.src.notion.models.primitives.base import BaseNotionModel


class Checkbox(BaseNotionModel):
    checkbox: bool

    @computed_field
    @property
    def value(self) -> bool:
        return self.checkbox

    def __bool__(self):
        return self.value
