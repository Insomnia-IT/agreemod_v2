from datetime import date

from pydantic import BaseModel, computed_field
from updater.src.notion.models.primitives.base import BaseNotionModel


class DateBody(BaseModel):
    start: str | None
    end: str | None
    time_zone: str | None


class Date(BaseNotionModel):
    date: DateBody | None

    @computed_field
    @property
    def value(self) -> str | None:
        return date.fromisoformat(self.date.start) if self.date else None
