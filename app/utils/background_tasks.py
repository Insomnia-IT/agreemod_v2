import os

from pathlib import Path


class BackgroungInterlock:
    def __init__(self, task_name: str) -> None:
        self.task_name = task_name

    async def __aenter__(self):
        Path(f"__tasks__/{self.task_name}").touch()

    async def __aexit__(self, exc_type, exc, tb):
        os.remove(f"__tasks__/{self.task_name}")
