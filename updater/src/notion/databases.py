import json

from typing import Type

from pydantic import BaseModel

from database.orm.participation import ParticipationORM
from updater.src.notion.models.direction import Direction
from updater.src.notion.models.participation import Participation
from updater.src.notion.models.person import Person

from database.orm.direction import DirectionORM
from database.orm.person import PersonORM

DATABASE_REGISTRY: dict[str, Type["NotionDatabase"]] = {}

# TODO: replace updater/notion_dbs_info.json with notion_dbs_info.ini
with open("updater/notion_dbs_info.json", "r") as f:
    dbs = json.load(f)


class NotionDatabase(BaseModel):
    def __init_subclass__(cls, **kwargs):
        DATABASE_REGISTRY[cls.__name__] = cls

    @property
    def id(self):
        return dbs[self.name]["id"]


class Directions(NotionDatabase):
    name: str = "get_directions"
    model: type = Direction
    orm: type = DirectionORM


class Persons(NotionDatabase):
    name: str = "get_people"
    model: type = Person
    orm: type = PersonORM


class Participations(NotionDatabase):
    name: str = "get_participation"
    model: type = Participation
    orm: type = ParticipationORM
