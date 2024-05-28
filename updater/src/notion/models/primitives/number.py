from pydantic import computed_field
from updater.src.notion.models.primitives.base import BaseNotionModel


class Number(BaseNotionModel):
    number: int | None

    @computed_field
    @property
    def value(self) -> int | None:
        return self.number
