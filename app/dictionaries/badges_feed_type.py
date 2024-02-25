from enum import StrEnum


class BadgesFeedType(StrEnum):
    """
    сделан для поля feed таблицы Badges app/models/badges.py
    """

    FREE = "Бесплатно"
    PAYMENT = "Платно"
    UNAVAILABLE = "Без питания"

    @property
    def is_free(self) -> bool:
        if self.name == "FREE":
            return True
        return False