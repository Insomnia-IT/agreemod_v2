from pydantic import BaseModel


class NotionDataBase(BaseModel):
    id: str
    name: str
