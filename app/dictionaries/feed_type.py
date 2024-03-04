from enum import StrEnum


class FeedType(StrEnum):
    """
    сделан для поля feed таблицы badge app/models/badge.py
    """

    FREE = "Бесплатно"
    PAYMENT = "Платно"
    UNAVAILABLE = "Без питания"

    @property
    def is_free(self) -> bool:
        if self.name == "FREE":
            return True
        return False
