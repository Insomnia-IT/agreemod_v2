import logging
import os
import zipfile

import httpx
import pandas as pd

from dictionaries.badge_color import BadgeColor
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.db.repos.badge import BadgeRepo
from app.models.badge import Badge
from app.schemas.badge import BadgeFilterDTO


logger = logging.getLogger(__name__)


class BadgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.badges = BadgeRepo(session)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_photo(self, link: str, filename: str, color: BadgeColor, client: httpx.AsyncClient) -> str:
        if link.split("/")[-1] == f"{color.value}.png":
            return f"{color.value}.png"
        file_exists = os.path.isfile(path=f"{color.name}/{filename}.jpg")
        if file_exists:
            return f"{filename}.jpg"
        image_file = await client.get(link)
        try:
            filetype = image_file.headers["content-type"].split("/")[-1]
            with open(f"{color.name}/{filename}.{filetype}", "wb") as f:
                f.write(image_file.content)
        except KeyError:
            logger.warning(f"image for notion_id={filename} is unavailable")
            return f"{color.value}.png"
        return f"{filename}.{filetype}"

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
            for badge in raw_badges:
                photo = await self.get_photo(badge["photo"], badge["notion_id"], color, client)
                badge["photo"] = photo

        for rb in raw_badges:
            rb["directions"] = ", ".join([x["name"] for x in rb["directions"]])
        df = pd.DataFrame(raw_badges)
        df.to_excel(
            f"{color}.xlsx",
            header=("name", "badge_number", "photo", "position", "qr", "directions"),
            index=False,
        )

    async def prepare_to_print(self, batch_num: int):
        filters = BadgeFilterDTO(
            batch=batch_num,
        )
        batch = await self.badges.retrieve_many(
            filters=filters,
            include_directions=True,
            include_infant=True,
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
