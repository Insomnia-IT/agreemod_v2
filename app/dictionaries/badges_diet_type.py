from enum import StrEnum


class BadgesDietType(StrEnum):
    """
    сделан для поля diet таблицы Badges app/models/badges.py
    """

    USUAL = "Без особенностей"
    VEGAN = "Веган"

    @property
    def is_vegan(self) -> bool:
        if self.name == "VEGAN":
            return True
        return False