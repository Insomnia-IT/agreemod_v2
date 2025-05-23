from pydantic import computed_field

from app.schemas.notion.primitives.base import BaseNotionModel


class Email(BaseNotionModel):
    # email: EmailStr | None = None
    email: str | None = None
