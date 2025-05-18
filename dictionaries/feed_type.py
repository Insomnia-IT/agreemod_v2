from enum import StrEnum


class FeedType(StrEnum):
    """
    сделан для поля feed таблицы badge app/models/badge.py
    """

    FREE = "Бесплатно"
    PAID = "Платно"
    NO = "Без питания"
    

    @property
    def is_free(self) -> bool:
        if self.name == "FREE":
            return True
        return False
