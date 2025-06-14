import random

from pathlib import Path

from pydantic import AnyUrl, BaseModel, computed_field
from app.schemas.notion.primitives.base import BaseNotionModel, ExternalFile, File


class FilesBody(BaseModel):
    name: str
    type: str
    file: File | None = None


class Files(BaseNotionModel):
    files: list[FilesBody]

    @classmethod
    def create_model(cls, value: str):
        return cls.model_validate(
            {
                "files": [
                    {
                        "name": value,
                        "type": "file",
                        "file": {
                            "url": value
                        }
                    }
                ]
            }
        )


class UrlFiles(Files):
    pass