from pydantic import computed_field

from app.schemas.notion.primitives.base import BaseNotionModel



class Number(BaseNotionModel):
    number: int | None
