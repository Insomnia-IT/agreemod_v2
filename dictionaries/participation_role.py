from enum import StrEnum


class ParticipationRole(StrEnum):
    ORGANIZER = "организатор"  # красный

    VICE = "зам руководителя"  # зелёный
    TEAM_LEAD = "бригадир"
    VOLUNTEER = "волонтёр"

    MEDIC = "медик"  # фиолетовый

    CAMP_LEAD = "лидер нефедеральной локации"  # Синий
    CAMP_GUY = "волонтёр нефедеральной локации"

    ANIMATOR = "аниматор"  # Оранжевый
    LECTOR = "лектор"
    MASTER = "мастер"
    ARTIST = "артист"
    ART_FELLOW = "сопровождающий артиста"

    FELLOW = "свои"  # Желтый
    VIP = "VIP"
    PRESS = "пресса"
    OTHER = "другие"

    CONTRACTOR = "подрядчик"  # Серый

    @property
    def is_team(self):
        if self in [
            ParticipationRole.ORGANIZER,
            ParticipationRole.CAMP_LEAD,
            ParticipationRole.VICE,
            ParticipationRole.TEAM_LEAD,
            ParticipationRole.VOLUNTEER,
            ParticipationRole.MEDIC,
        ]:
            return True
        return False

    @property
    def is_lead(self):
        if self in [
            ParticipationRole.ORGANIZER,
            ParticipationRole.CAMP_LEAD,
        ]:
            return True
        return False

    @property
    def free_feed(self):
        if self in [
            ParticipationRole.ORGANIZER,
            ParticipationRole.CAMP_LEAD,
            ParticipationRole.VICE,
            ParticipationRole.TEAM_LEAD,
            ParticipationRole.VOLUNTEER,
            ParticipationRole.MEDIC,
            ParticipationRole.LECTOR,
            ParticipationRole.MASTER,
            ParticipationRole.ARTIST,
        ]:
            return True
