from enum import StrEnum


class DietType(StrEnum):
    STANDARD = "Без особенностей"
    VEGAN = "Веган"

    @classmethod
    def default(cls):
        return cls.STANDARD
