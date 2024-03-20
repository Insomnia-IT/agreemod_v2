from enum import StrEnum

from dictionaries.badge_color import BadgeColor


class ParticipationRole(StrEnum):
    ORGANIZER = "организатор"  # красный

    VICE_HEAD = "зам руководителя"  # зелёный
    TEAM_LEAD = "бригадир"
    VOLUNTEER = "волонтёр"

    MEDICIAN = "медик"  # фиолетовый

    CAMP_LEAD = "лидер нефедеральной локации"  # Синий
    CAMP_GUY = "волонтёр нефедеральной локации"

    ANIMATOR = "аниматор"  # Оранжевый
    LECTOR = "лектор"
    MASTER = "мастер"
    ARTIST = "артист"

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
            ParticipationRole.VICE_HEAD,
            ParticipationRole.TEAM_LEAD,
            ParticipationRole.VOLUNTEER,
            ParticipationRole.MEDICIAN,
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
    def badge_color(self):
        match self:
            case ParticipationRole.ORGANIZER:
                return BadgeColor.RED

            case (
                ParticipationRole.VOLUNTEER
                | ParticipationRole.VICE_HEAD
                | ParticipationRole.TEAM_LEAD
            ):
                return BadgeColor.GREEN

            case ParticipationRole.MEDICIAN:
                return BadgeColor.PURPLE

            case ParticipationRole.CAMP_LEAD | ParticipationRole.CAMP_GUY:
                return BadgeColor.BLUE

            case (
                ParticipationRole.FELLOW
                | ParticipationRole.VIP
                | ParticipationRole.PRESS
                | ParticipationRole.OTHER
            ):
                return BadgeColor.YELLOW

            case ParticipationRole.CONTRACTOR:
                return BadgeColor.GRAY

            case _:
                return BadgeColor.ORANGE

    @property
    def free_feed(self):
        if self in [
            ParticipationRole.ORGANIZER,
            ParticipationRole.CAMP_LEAD,
            ParticipationRole.VICE_HEAD,
            ParticipationRole.TEAM_LEAD,
            ParticipationRole.VOLUNTEER,
            ParticipationRole.MEDICIAN,
            ParticipationRole.LECTOR,
            ParticipationRole.MASTER,
            ParticipationRole.ARTIST,
        ]:
            return True
