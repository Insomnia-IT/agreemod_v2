from pydantic import computed_field
from updater.notion.models.primitives.base import BaseNotionModel


class Email(BaseNotionModel):
    # email: EmailStr | None = None
    email: str | None = None

    @computed_field
    @property
    def value(self) -> str:
        return self.email
