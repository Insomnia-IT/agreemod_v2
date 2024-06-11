from enum import StrEnum


class TransportType(StrEnum):
    """
    сделан для поля arrival_transport таблицы arrival app/db/orm/arrival.py

    - Не определен
    - На автобусе — нужен автобус
    - На своей машине — нужна парковка и можно привлекать к логистике
    - Своим ходом — никаких особенностей
    - Трансфер от фестиваля — нужно организовать (для особо важных персон)
    """

    UNDEFINED = "Не определен"
    SELF = "Своим ходом"
    BUS = "На автобусе"
    CAR = "На своей машине"
    TRANSFER = "Трансфер от фестиваля"
    MOVE = "Смена направления"
    
    @classmethod
    def default(cls):
        return cls.UNDEFINED
