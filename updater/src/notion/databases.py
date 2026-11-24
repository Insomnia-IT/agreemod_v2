import json

from typing import Type

import yaml

from database.orm.arrival import ArrivalORM
from database.orm.badge import AnonsORM, BadgeORM
from database.orm.direction import DirectionORM
from database.orm.participation import ParticipationORM
from database.orm.person import PersonORM
from pydantic import BaseModel
from updater.src.coda.models.arrival import CodaArrival
from updater.src.coda.models.participation import CodaParticipation
from updater.src.notion.models.badge import Anons, Badge
from updater.src.notion.models.direction import Direction
from updater.src.notion.models.person import Person
from updater.src.config import config

NOTION_DB_REGISTRY: dict[str, Type["NotionDatabase"]] = {}
CODA_DB_REGISTRY: dict[str, Type["CodaDatabase"]] = {}

if config.TESTING:
    DBS_FILE = 'updater/notion_db_dev.yml'
else:
    DBS_FILE = 'updater/notion_db_prod.yml'

with open(DBS_FILE, 'r', encoding='utf-8') as file:
    dbs = yaml.safe_load(file)


class ExternalDatabase(BaseModel):
    pass


class NotionDatabase(ExternalDatabase):
    source: str = "notion"

    def __init_subclass__(cls, **kwargs):
        NOTION_DB_REGISTRY[cls.__name__] = cls

    @property
    def id(self):
        return dbs[self.name]["id"]


class CodaDatabase(ExternalDatabase):
    source: str = "coda"

    def __init_subclass__(cls, **kwargs):
        CODA_DB_REGISTRY[cls.__name__] = cls

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


class Badges(NotionDatabase):
    name: str = "get_badges"
    model: type = Badge
    orm: type = BadgeORM


class Participations(CodaDatabase):
    name: str = "get_participations"
    model: type = CodaParticipation
    orm: type = ParticipationORM


class Arrivals(CodaDatabase):
    name: str = "get_arrivals"
    model: type = CodaArrival
    orm: type = ArrivalORM


class AnonymousBadges(NotionDatabase):
    name: str = "anonymous_badges"
    model: type = Anons
    orm: type = AnonsORM
