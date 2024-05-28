from enum import StrEnum

from dictionaries.badge_color import BadgeColor


class ParticipationType(StrEnum):
    ORGANIZER = "организатор"
    CAMP_LEAD = "лидер нефедеральной локации"
    VICE_HEAD = "зам руководителя"
    TEAM_LEAD = "бригадир"
    VOLUNTEER = "волонтёр"
    CAMP_GUY = "волонтёр нефедеральной локации"
    PARTICIPANT = "участник"
    FELLOW = "свои"
    CONTRACTOR = "подрядчик"

    @property
    def badge_color(self):
        match self:
            case ParticipationType.ORGANIZER:
                return BadgeColor.RED

            case (
                ParticipationType.VOLUNTEER
                | ParticipationType.VICE_HEAD
                | ParticipationType.TEAM_LEAD
            ):
                return BadgeColor.GREEN

            # case ParticipationType.MEDICIAN:
            #     return BadgeColor.PURPLE

            case ParticipationType.CAMP_LEAD | ParticipationType.CAMP_GUY:
                return BadgeColor.BLUE

            case ParticipationType.FELLOW:
                return BadgeColor.YELLOW

            case ParticipationType.CONTRACTOR:
                return BadgeColor.GRAY

            case _:
                return BadgeColor.ORANGE
