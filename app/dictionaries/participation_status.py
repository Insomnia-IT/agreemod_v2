from enum import StrEnum


class ParticipationStatus(StrEnum):
    PLANNED = "Планируется"
    CANCELED = "Отменилось"
    PENDING = "Ждём ответа"
    CONFIRMED = "Подтверждено накануне"
    SKIPPED = "Не доехал"
    ARRIVED = "Заехал на поле"
    STARTED = "Приступил"
    LEFT = "Ушел"
    COMPLETE = "Состоялось"
    JOINED = "Прибился"

    @property
    def to_list(self) -> bool:
        if self.name in  ["PLANNED", "PENDING", "CONFIRMED", "ARRIVED", "STARTED", "COMPLETE", "JOINED"]:
            return True
        return False
