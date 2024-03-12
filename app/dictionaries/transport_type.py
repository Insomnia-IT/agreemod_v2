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
    
    UNKNOWN = "Не определен"
    BY_BUS = "На автобусе"
    BY_OWN_CAR = "На своей машине"
    BY_YOUR_OWN = "Своим ходом"
    BY_FESTIVAL_TRANSFER = "Трансфер от фестиваля"

    @classmethod
    def default(cls):
        return cls.UNKNOWN