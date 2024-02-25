from pydantic import BaseModel
from typing import Optional, Union


class Direction(BaseModel):
    name: str | None = None
    type: Optional[Union[str, None]] = None
    first_year: Optional[Union[int, None]] = None
    last_year: Optional[Union[int, None]] = None
    notion_id: str

    class Config:
        orm_mode = True

    @classmethod
    def from_notion_data(cls, data_raw, notion_id):
        name = data_raw.get("Name", {}).get("title", [{}])[0].get("text", {}).get("content")
        type_ = data_raw.get("Тип", {}).get("select", {}).get("name")
        first_year = data_raw.get("Год появления", {}).get("number") if data_raw.get("Год появления") else None
        last_year = data_raw.get("Последний год", {}).get("number") if data_raw.get("Последний год") else None

        return cls(
            name=name,
            type=type_,
            first_year=first_year,
            last_year=last_year,
            notion_id=notion_id
        )
