import asyncio
import json
import logging
import random
import aiohttp
from googleapiclient.discovery import build

from app.config import config

from .attachments import upload_attachment
from .drive import download_drive_file, extract_drive_folder_id, find_drive_file, get_drive_files


logger = logging.getLogger(__name__)


class BadgePhotoService:
    def __init__(self):
        self.server = config.grist.server
        self.doc_id = config.grist.doc_id
        self.api_key = config.grist.api_key
        self.headers = {"Authorization": f"Bearer " + self.api_key}
        self.google_drive = build("drive", "v3", developerKey=config.google.api_key)
        self.session: aiohttp.ClientSession | None = None

    async def init(self):
        if not self.session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            self.session = aiohttp.ClientSession(headers=headers)

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def import_badge_photos(self):
        await self.init()

        try:
            badge_records = await self.get_badges_for_drive()
            result = {"processed": 0, "success": 0, "failed": 0}

            for badge_record in badge_records:
                try:
                    import_series = await self.get_import_series(badge_record["import_batch"])
                    folder_id = extract_drive_folder_id(import_series["photo_folder"])

                    files = await get_drive_files(self.google_drive, folder_id)
                    file = find_drive_file(files, badge_record["filename"])

                    if not file:
                        raise ValueError(f"File not found: {badge_record['filename']}")

                    file_bytes = await download_drive_file(self.session, file["id"])

                    attachment_id = await upload_attachment(
                        session=self.session,
                        server=self.server,
                        doc_id=self.doc_id,
                        headers=self.headers,
                        file_bytes=file_bytes,
                        file_name=file["name"],
                    )

                    photo_id = await self.create_photo(badge_record["person"], attachment_id)
                    await self.update_badge_photo(badge_record["id"], photo_id)

                    result["success"] += 1
                    await asyncio.sleep(random.uniform(0.2, 0.7))

                except Exception:
                    logger.exception("Drive photo creation failed badge=%s", badge_record["id"])
                    result["failed"] += 1

                finally:
                    result["processed"] += 1

            return result

        finally:
            await self.close()

    async def attach_badge_photos(self):
        await self.init()

        try:
            badge_records = await self.get_badges_with_upload()
            existing_photos = await self.get_existing_photos()
            result = {"processed": 0, "success": 0, "failed": 0, "skipped": 0}

            for badge_record in badge_records:
                try:
                    person = badge_record["person"]
                    attachment = json.loads(badge_record["photo_upload"])[0]

                    if attachment in existing_photos.get(person, set()):
                        logger.info("Photo already exists for badge=%s", badge_record["id"])
                        result["skipped"] += 1
                        continue

                    await self.create_photo(person, attachment)
                    existing_photos.setdefault(person, set()).add(attachment)

                    result["success"] += 1

                except Exception:
                    logger.exception("Photo creation failed for badge_id=%s", badge_record["id"])
                    result["failed"] += 1

                finally:
                    result["processed"] += 1

            return result

        finally:
            await self.close()

    async def get_badges_for_drive(self):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {
            "sql": """
                SELECT id, person, filename, import_batch
                FROM Badges_2026
                WHERE person != 0
                AND filename != ''
                AND import_batch != 0
                AND photo = 0
            """
        }

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

            data = await resp.json()

        return [record["fields"] for record in data.get("records", [])]

    async def get_badges_with_upload(self):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {
            "sql": """
                SELECT id, person, photo_upload
                FROM Badges_2026
                WHERE person != 0
                AND photo_upload IS NOT NULL
            """
        }

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

            data = await resp.json()

        return [record["fields"] for record in data.get("records", [])]

    async def get_existing_photos(self):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {
            "sql": """
                SELECT person, photo
                FROM Photo
                WHERE person != 0
                AND photo IS NOT NULL
            """
        }

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

            data = await resp.json()

        photos = {}

        for record in data.get("records", []):
            person = record["fields"]["person"]
            attachment = json.loads(record["fields"]["photo"])[0]

            photos.setdefault(person, set()).add(attachment)

        return photos

    async def get_import_series(self, record_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {"sql": f"SELECT photo_folder FROM Import_series WHERE id = {record_id}"}

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

            data = await resp.json()

        return data["records"][0]["fields"]

    async def create_photo(self, person: int, attachment_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/tables/Photo/records"
        payload = {
            "records": [{
                "fields": {
                    "person": person,
                    "photo": ["L", attachment_id],
                    "isForBage": True,
                }
            }]
        }

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

            data = await resp.json()

        photo_id = data["records"][0]["id"]
        logger.info("Created photo=%s for person=%s", photo_id, person)

        return photo_id

    async def update_badge_photo(self, badge_id: int, photo_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/tables/Badges_2026/records"
        payload = {
            "records": [{
                "id": badge_id,
                "fields": {
                    "photo": photo_id,
                }
            }]
        }

        async with self.session.patch(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
