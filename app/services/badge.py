import asyncio
import logging
import os
import time
import uuid
import zipfile

import httpx
import pandas as pd

from dictionaries.badge_color import BadgeColor
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.db.repos.anons import AnonsRepo
from app.db.repos.badge import BadgeRepo
from app.models.badge import Badge
from app.schemas.badge import BadgeFilterDTO


logger = logging.getLogger(__name__)
REQUESTS_PER_SEC = 50


class BadgeService:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badges = BadgeRepo(session)
        self.anons = AnonsRepo(session)

    async def get_photos(self, await_badges, rps: int = REQUESTS_PER_SEC):
        max_sleep = 1 / rps
        for b in await_badges:
            start = time.perf_counter()
            yield await b
            elapsed = time.perf_counter() - start
            await asyncio.sleep(max(0.0, max_sleep - elapsed))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_photo(self, badge: dict, color: BadgeColor, client: httpx.AsyncClient) -> str:
        link = badge["photo"]
        filename = badge["notion_id"]
        if link.split("/")[-1] == f"{color.value}.png":
            badge["photo"] = f"{color.value}.png"
            return badge["photo"]
        file_exists = os.path.isfile(path=f"{color.name}/{filename}.jpg") or os.path.isfile(
            path=f"{color.name}/{filename}.jpeg"
        )
        if file_exists:
            badge["photo"] = f"{filename}.jpg"
            return badge["photo"]
        image_file = await client.get(link)
        filetype = image_file.headers["content-type"].split("/")[-1]
        if filetype not in ["jpg", "jpeg", "png", "heic"]:
            logger.warning(f"image for notion_id={filename} is unavailable")
            badge["photo"] = f"{color.value}.png"
            return badge["photo"]
        with open(f"{color.name}/{filename}.{filetype}", "wb") as f:
            f.write(image_file.content)
        badge["photo"] = f"{filename}.{filetype}"
        return badge["photo"]

    async def process_color(self, color: BadgeColor, badges: list[Badge]):
        try:
            os.mkdir(color.name)
        except FileExistsError:
            pass
        raw_badges = [
            badge.model_dump(
                include=(
                    "name",
                    "occupation",
                    "number",
                    "directions",
                    "notion_id",
                    "photo",
                )
            )
            for badge in badges
        ]
        async with httpx.AsyncClient() as client:
            await_photos = (self.get_photo(badge, color, client) for badge in raw_badges)
            async for badge in self.get_photos(await_photos):
                logging.info(f"got image {badge}")

        for rb in raw_badges:
            rb["directions"] = ", ".join([x["name"] for x in rb["directions"]])
        df = pd.DataFrame(raw_badges)
        df.to_excel(
            f"{color}.xlsx",
            header=("name", "badge_number", "photo", "position", "qr", "directions"),
            index=False,
        )

    async def prepare_to_print(self, batch_num: int):
        if os.path.isfile(f"batch_{batch_num}.zip"):
            os.remove(f"batch_{batch_num}.zip")
        filters = BadgeFilterDTO(
            batch=batch_num,
        )
        batch = await self.badges.retrieve_many(
            filters=filters,
            include_directions=True,
            include_parent=True,
            include_person=True,
        )
        await self.session.commit()
        colored = {}
        for badge in batch:
            colored.setdefault(badge.color, []).append(badge)

        for color, badges in colored.items():
            await self.process_color(color, badges)

        with zipfile.ZipFile(f"batch_{batch_num}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            for c in BadgeColor:
                if not os.path.isfile(path=f"{c.value}.xlsx"):
                    continue
                zf.write(f"{c.value}.xlsx")
                zf.write(c.name)
                for f in os.listdir(c.name):
                    zf.write(f"{c.name}/{f}")

    def generate_anon_badges(self, title, subtitle, color, quantity):
        badges = []
        for i in range(1, quantity):
            badge = {
                "name": title,
                "badge number": "",
                "photo": f"{color}.png",
                "position": subtitle,
                "qr": uuid.uuid4().hex,
            }
            badges.append(badge)
        return badges

    async def prepare_anonymous(self, batch: str):
        names = []
        anons = await self.anons.retrieve_batch(batch)
        for a in anons:
            if not a.to_print:
                continue
            badges = self.generate_anon_badges(a.title, a.subtitle, a.color, a.quantity)
            name = f"{a.title if a.title else a.subtitle}_{a.color}.xlsx"
            df = pd.DataFrame(badges)
            df.to_excel(
                name,
                header=("name", "badge_number", "photo", "position", "qr"),
                index=False,
            )
            names.append(name)
        with zipfile.ZipFile(f"batch_{batch}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            for n in names:
                if not os.path.isfile(path=n):
                    continue
                zf.write(n)
