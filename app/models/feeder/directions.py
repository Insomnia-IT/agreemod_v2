from pydantic import BaseModel


class Direction(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    name: str | None = None
    first_year: int | None = None
    last_year: int | None = None
    type: str | None = None
    notion_id: str | None = None
