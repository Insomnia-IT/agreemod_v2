from pydantic import computed_field

from app.schemas.notion.primitives.base import BaseNotionModel



class Number(BaseNotionModel):
    number: int | None

    @computed_field
    @property
    def value(self) -> int | None:
        return self.number
