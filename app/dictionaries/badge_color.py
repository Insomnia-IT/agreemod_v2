from enum import StrEnum
from pathlib import Path

from app.dictionaries.participation_role import ParticipationRole


class BadgeColor(StrEnum):
    RED = "red"  # Красный. Цвет бейджа организаторов.
    GREEN = "green"  # Зелёный. Цвет бейджа волонтёра, который не принадлежит медпункту.
    PURPLE = "purple"  # Фиолетовый. Цвет бейджа волонтёра, который принадлежит медпункту.
    YELLOW = "yellow"  # Желтый. Цвет бейджа для обычных участников.
    ORANGE = "orange"  # Оранжевый. Цвет бейджа для участника который: аниматор, мастера, лектор или музыкант.
    BLUE = "blue"  # Синий. Цвет бейджа участника, который из одной из служб "Ветви дерева".
    GRAY = "gray"  # Серый, подрядчик
    DEFAULT = "white"

    @classmethod
    def define(cls, role: ParticipationRole):
        match role:
            case ParticipationRole.ORGANIZER:
                return cls.RED

            case ParticipationRole.VOLUNTEER | ParticipationRole.VICE_HEAD | ParticipationRole.BRIGADIER:
                return cls.GREEN

            case ParticipationRole.MEDICIAN:
                return cls.PURPLE

            case ParticipationRole.GRANT_LEADER | ParticipationRole.GRANT:
                return cls.BLUE

            case ParticipationRole.BUDDY | ParticipationRole.VIP | ParticipationRole.PRESS:
                return cls.YELLOW

            case ParticipationRole.CONTRACTOR:
                return cls.GRAY

            case _:
                return cls.ORANGE

    def get_default_file(self):
        path_to_files = Path.cwd() / Path("media/image/faces_no_photo")
        return path_to_files / Path(f"{self.value}.png")
