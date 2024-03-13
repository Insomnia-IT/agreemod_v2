from enum import StrEnum


class ParticipationStatus(StrEnum):
    PLANNED = "планирует приехать"
    CANCELLED = "не сможет приехать"
    CONFIRMED_RECENTLY = "подвердил накануне"
    NO_SHOW = "не доехал"
    ON_SITE = "на поле"
    SNAPPED = "соскочил"
    COMPLETED = "отработал"
    WALKED_IN = "прибился"

    @property
    def to_list(self) -> bool:
        if self.name in [
            "PLANNED",
            "CONFIRMED_RECENTLY",
            "ON_SITE",
            "COMPLETED",
            "WALKED_IN",
        ]:
            return True
        return False
