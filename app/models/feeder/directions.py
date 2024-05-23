from __future__ import annotations
from pydantic import BaseModel


class Direction(BaseModel):
    id: str
    deleted: bool
    name: str
    first_year: int
    last_year: int
    type: str
    notion_id: str
