from pydantic import computed_field

from updater.notion.models.primitives.base import BaseNotionModel


class PhoneNumber(BaseNotionModel):
    phone_number: str | None

    @computed_field
    @property
    def value(self):
        return self.phone_number
