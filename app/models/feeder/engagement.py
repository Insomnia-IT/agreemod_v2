from pydantic import BaseModel


class Engagement(BaseModel):
    id: str
    deleted: bool
    year: int
    person: str
    role: str
    position: str
    status: str
    direction: str
    notion_id: str
