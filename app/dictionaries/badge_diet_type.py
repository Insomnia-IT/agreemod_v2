from enum import StrEnum


class DietType(StrEnum):
    """
    сделан для поля diet таблицы badge app/models/badge.py
    """

    USUAL = "Без особенностей"
    VEGAN = "Веган"

    @property
    def is_vegan(self) -> bool:
        if self.name == "VEGAN":
            return True
        return False
    
    @classmethod
    def default(cls):
        return cls.USUAL