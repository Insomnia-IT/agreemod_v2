from pydantic import BaseModel


class BadgeFilterDTO(BaseModel):
    batch: int | None = None
    color: str | None = None
    direction: str | None = None
    role: str | None = None
    occupation: str | None = None
    infants: str | None = None
