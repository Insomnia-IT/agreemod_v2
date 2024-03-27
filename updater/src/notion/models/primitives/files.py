import random

from pathlib import Path

from pydantic import AnyUrl, BaseModel, computed_field
from updater.src.notion.models.primitives.base import (
    BaseNotionModel,
    ExternalFile,
    File,
)


class FilesBody(BaseModel):
    name: str
    type: str
    file: File | None = None
    external: ExternalFile | None = None


class Files(BaseNotionModel):
    files: list[FilesBody]

    # internal field which shoud be defined by chosing from self.files
    photo_: FilesBody | None = None
    path_: Path | None = None
    default: bool = False

    def choose_photo(self):
        if not self.photo_ and self.files:
            self.photo_ = random.choice(self.files)

    def set_photo(self, file_path: Path, default: bool = False):
        self.photo_ = FilesBody(name=file_path.name, type="internal", file=None)
        self.path_ = file_path
        self.default = default

    @computed_field
    @property
    def value(self) -> str | None:
        if not self.photo_:
            self.choose_photo()

        if self.photo_:
            # todo: parse file name from url
            return self.photo_.name
        return None

    @computed_field
    @property
    def url(self) -> AnyUrl | Path | None:
        if not self.photo_:
            self.choose_photo()

        if self.photo_:
            if self.photo_.type == "file":
                return self.photo_.file.url
            elif self.photo_.type == "external":
                return self.photo_.external.url
            elif self.photo_.type == "internal":
                return self.path_
            else:
                return None
        return None


class UrlFiles(Files):
    @computed_field
    @property
    def value(self) -> str | None:
        value = super().url
        if value:
            return str(value)
        return None
