from enum import StrEnum


class DirectionType(StrEnum):
    """
    сделан для поля type таблицы Direction api/db/models/directions.py
    """

    CITY_SERVICE = "Городская служба"
    FIELD_SERVICE = "Полевая служба"
    UNIVERSAL_SERVICE = "Универсальная служба"
    FEDERAL_LOCATION = "Федеральная локация"
    GRANT_LOCATION = "Грантовая локация"
    COMMERCIAL_LOCATION = "Коммерческая локация"
    LATERAL_LOCATION = "Сторонняя локация"
    RESPONSIBILITY_AREA = "Зона ответственности"

    @property
    def is_federal(self) -> bool:
        if self.name in ["GRANT_LOCATION", "COMMERCIAL_LOCATION"]:
            return False
        return True

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                name=x.value,
                is_federal=x.is_federal,
            )
            for x in DirectionType
        ]
