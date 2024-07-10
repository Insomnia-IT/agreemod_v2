from datetime import date

from pydantic import BaseModel, computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class DateBody(BaseModel):
    start: str | None
    end: str | None
    time_zone: str | None


class Date(BaseNotionModel):
    date: DateBody | None