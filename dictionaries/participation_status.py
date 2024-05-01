from enum import StrEnum


class ParticipationStatus(StrEnum):
    PLANNED = "планируется"
    CANCELED = "отменилось"
    PENDING = "ждём ответа"
    CONFIRMED = "подтверждено накануне"
    SKIPPED = "не доехал"
    ARRIVED = "заехал на поле"
    STARTED = "приступил"
    LEFT = "ушел"
    COMPLETE = "состоялось"
    JOINED = "прибился"

    @property
    def to_list(self) -> bool:
        if self.name in [
            "PLANNED",
            "PENDING",
            "CONFIRMED",
            "ARRIVED",
            "STARTED",
            "COMPLETE",
            "JOINED",
        ]:
            return True
        return False
