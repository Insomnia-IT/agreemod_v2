from pydantic import computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class PhoneNumber(BaseNotionModel):
    phone_number: str | None
