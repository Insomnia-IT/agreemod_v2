from enum import StrEnum
from pathlib import Path


class BadgeColor(StrEnum):
    RED = "red"  # Красный. Цвет бейджа организаторов.
    GREEN = "green"  # Зелёный. Цвет бейджа волонтёра, который не принадлежит медпункту.
    PURPLE = (
        "purple"  # Фиолетовый. Цвет бейджа волонтёра, который принадлежит медпункту.
    )
    YELLOW = "yellow"  # Желтый. Цвет бейджа для обычных участников.
    ORANGE = "orange"  # Оранжевый. Цвет бейджа для участника который: аниматор, мастера, лектор или музыкант.
    BLUE = "blue"  # Синий. Цвет бейджа участника, который из одной из служб "Ветви дерева".
    GRAY = "gray"  # Серый, подрядчик
    DEFAULT = "white"

    def get_default_file(self):
        path_to_files = Path.cwd() / Path("media/image/faces_no_photo")
        return path_to_files / Path(f"{self.value}.png")

    @classmethod
    def fill_table(cls):
        return [
            cls(
                code=x.name,
                color=x.value,
            )
            for x in BadgeColor
        ]
