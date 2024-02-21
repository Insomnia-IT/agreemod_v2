from enum import StrEnum


class ParticipationRole(StrEnum):
    ORGANIZER = "организатор"
    GRANT_LEADER = "лидер нефедеральной локации"
    VICE_HEAD = "зам руководителя"
    BRIGADIER = "бригадир"
    VOLUNTEER = "волонтёр"
    MEDICIAN = "медик"
    GRANT = "грант"  # Синий

    BUDDY = "свои"  # Желтый
    VIP = "VIP"
    PRESS = "пресса"

    CONTRACTOR = "подрядчик"  # Серый

    ANIMATOR = "аниматор"  # Оранжевый
    LECTOR = "лектор"
    MASTER = "мастер"
    ARTIST = "артист"
    OTHER = "другие"

    @property
    def is_team(self):
        if self.name in [
            "ORGANIZER",
            "NON_FED_LEADER",
            "VICE_HEAD",
            "BRIGADIER",
            "VOLUNTEER",
            "MEDICIAN",
        ]:
            return True
        return False
