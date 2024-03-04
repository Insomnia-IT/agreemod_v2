from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AnyUrl, BaseModel
from pydantic_settings import SettingsConfigDict


class NotionModel(BaseModel):
    notion_id: UUID


class ObjectItem(BaseModel):
    id: UUID
    object: str


class BaseNotionResponseItem(BaseModel):
    id: UUID
    object: str
    created_time: datetime
    last_edited_time: datetime
    created_by: ObjectItem
    last_edited_by: ObjectItem
    cover: Any
    icon: Any
    parent: Any
    archived: bool
    properties: dict
    url: AnyUrl

    @property
    def title(self) -> str:
        for v in self.properties.values():
            if v["type"] == "title":
                return v["title"][0]["plain_text"]
        return ""

    model_config = SettingsConfigDict(extra="allow")


# Данная модель просто демонстрирует структуру, которая будет храниться в редисе
# Поля создаются динамически в родительской модели
# class DirectionLocation(BaseNotionResponseItem):
#     serial_number: int = Field(description='Порядковый номер локации или направления в общем списке из них')
#     involved: list[UUID]


# Данная модель просто демонстрирует структуру, которая будет храниться в редисе
# Поля создаются динамически в родительской модели
# class PeopleParticipant(BaseNotionResponseItem):
#     serial_number: int = Field(
#       description='Порядковый номер участника в списке из участников локации или направления'
#     )
#     loc_dir_serial_number: int = Field(description='Порядковый номер локации или направления в общем списке из них')


class BaseNotionResponse(BaseModel):
    object: str
    results: list[BaseNotionResponseItem]
    next_cursor: Any
    has_more: bool
    type: str
    page: dict | None = None
