from pydantic import BaseModel, Field

from app.schemas.notion.primitives.checkbox import Checkbox
from app.schemas.notion.primitives.files import Files
from app.schemas.notion.primitives.relation import Relation
from app.schemas.notion.primitives.rich_text import RichText
from app.schemas.notion.primitives.select import Select
from app.schemas.notion.primitives.title import Title


class Badge(BaseModel):
    name: Title = Field(..., alias="Надпись")
    last_name: RichText = Field(..., alias="Фамилия")
    first_name: RichText = Field(..., alias="Имя")
    gender: Select = Field(..., alias="Пол")
    phone: RichText = Field(..., alias="Телефон")
    child: Checkbox = Field(..., alias="Ребенок")
    diet: Select = Field(..., alias="Особенности питания")
    feed: Select = Field(..., alias="Тип питания")
    occupation: RichText = Field(..., alias="Должность")
    role: Relation = Field(..., alias="Роль")
    # photo: Files = Field(..., alias="Фото")
    person: Relation = Field(..., alias="Человек")
    comment: RichText = Field(..., alias="Комментарий")
    directions: Relation = Field(..., alias="Службы и локации")
    # color: Select = Field(..., alias="Цвет")

    @classmethod
    def create_model(cls, values: dict):
        model_dict = {}
        for x, y in values.items():
            print(x, y)
            if cls.model_fields.get(x):
                field = cls.model_fields[x]
                if cls.model_fields[x].annotation in [Relation, RichText, Title]:
                    model_dict[field.alias if field.alias else x] = field.annotation.create_model([y] if not isinstance(y, list) else y)
                elif field.annotation in [Select, Checkbox, Files]:
                    model_dict[field.alias if field.alias else x] = field.annotation.create_model(y)
                else:
                    model_dict[field.alias if field.alias else x] = y
        return cls.model_validate(model_dict, from_attributes=True)
