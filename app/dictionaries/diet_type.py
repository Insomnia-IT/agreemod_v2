from enum import StrEnum


class DietType(StrEnum):
    STANDARD = "с мясом"
    VEGAN = "без мяса"

    @classmethod
    def default(cls):
        return cls.STANDARD
