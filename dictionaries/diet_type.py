from enum import StrEnum


class DietType(StrEnum):
    STANDARD = "без особенностей"
    VEGAN = "веган"

    @classmethod
    def default(cls):
        return cls.STANDARD
