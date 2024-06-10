from pydantic import BaseModel


class Engagement(BaseModel):
    id: str | None = None
    deleted: bool | None = None
    year: int | None = None
    person: str | None = None
    role: str | None = None
    position: str | None = None
    status: str | None = None
    direction: str | None = None
    notion_id: str | None = None
