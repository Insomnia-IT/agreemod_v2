import uuid

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Logs(BaseModel):
    author: str
    table_name: str
    row_id: uuid.UUID | None
    operation: Literal["MERGE", "INSERT", "DELETE"]
    timestamp: datetime
    new_data: dict
