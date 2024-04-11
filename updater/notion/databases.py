import json

from typing import Type

from pydantic import BaseModel
from updater.notion.models.direction import Direction
from updater.notion.models.person import Person

from db.orm.direction import DirectionORM
from db.orm.person import PersonORM


DATABASE_REGISTRY: dict[str, Type["NotionDatabase"]] = {}


def get_database(name: str) -> "NotionDatabase":
    return DATABASE_REGISTRY[name]()


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
