

from pydantic import BaseModel


class PersonFiltersDTO(BaseModel):
    telegram: str
    phone_number: str
    email: str

class PersonResponseSchema(BaseModel):
    ...