from enum import StrEnum


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
