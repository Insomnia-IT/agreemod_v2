from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CodaArrival(BaseModel):
    coda_index: int = Field(..., alias="id")
    badge_id: UUID = Field(..., alias="badge_id")
    arrival_date: date = Field(..., alias="Дата заезда")
    arrival_transport: str = Field(..., alias="Способ заезда")
    arrival_registered: time | None = Field(..., alias="Отметка о заезде")
    departure_date: date = Field(..., alias="Дата отъезда")
    departure_transport: str = Field(..., alias="Способ выезда")
    departure_registered: time | None = Field(..., alias="Отметка об отъезде")
    extra_data: dict = Field(default_factory=dict)
    comment: str = Field(..., alias="Комментарии")
    last_updated: datetime = Field(default_factory=datetime.now)

    @field_validator("arrival_date", "departure_date", mode="before")
    @classmethod
    def format_date(cls, value: str) -> date | None:
        if not value:
            return None
        date_dt = date.fromisoformat(value.split("T")[0])
        assert date_dt.year == datetime.now().year
        return date_dt

    @field_validator("arrival_registered", "departure_registered", mode="before")
    @classmethod
    def format_time(cls, value: str) -> time | None:
        if not value:
            return None
        return time.fromisoformat(value.split("T")[1].split("+")[0])
