import json

from typing import Type

from pydantic import BaseModel

from updater.notion.models.base import BaseNotionResponseItem


_DATABASE_REGISTRY: dict[str, Type["NotionDatabase"]] = {}


def get_database(name: str) -> "NotionDatabase":
    return _DATABASE_REGISTRY[name]()


with open("updater/notion_dbs_info.json", "r") as f:
    dbs = json.load(f)


class NotionDatabase(BaseModel):
    data: list[BaseNotionResponseItem]

    def __init_subclass__(cls, **kwargs):
        _DATABASE_REGISTRY[cls.__name__] = cls

    @property
    def id(self):
        return dbs[self.name]["id"]


class People(NotionDatabase):
    name: str = "get_people"


class Locations(NotionDatabase):
    name: str = "get_locations"


class Directions(NotionDatabase):
    name: str = "get_directions"


class Participants(NotionDatabase):
    name: str = "get_participants"


class UnnamedBadges(NotionDatabase):
    name: str = "unnamed_badges"


class LocationSchedules(NotionDatabase):
    name: str = "location_schedules"
