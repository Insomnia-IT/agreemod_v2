import logging
import random
import aiohttp
import asyncio
from googleapiclient.discovery import build
from app.config import config

from .attachments import (
    AttachmentTooLargeError,
    remove_unused_attachments,
    upload_attachment,
)
from .drive import (
    GoogleRateLimitError,
    download_drive_file,
    extract_drive_folder_id,
    find_drive_file,
    get_drive_files,
)


logger = logging.getLogger(__name__)


class PhotoImportService:
    def __init__(self):
        self.server = config.grist.server
        self.doc_id = config.grist.doc_id
        self.api_key = config.grist.api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
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

    async def import_one(self, record_id: int):
        await self.init()
        try:
            return await self.import_series_photos(record_id)
        finally:
            await self.close()

    async def import_all(self):
        await self.init()

        try:
            records = await self.get_import_series_records()
            result = {"processed": 0, "success": 0, "failed": 0}
            for record in records:
                try:
                    await self.import_series_photos(record["id"])
                    result["success"] += 1

                except GoogleRateLimitError:
                    logger.error("Google rate limit hit - stopping batch import")
                    result["stopped_reason"] = "google_rate_limit"
                    break

                except Exception:
                    logger.exception("Photo import failed for record_id=%s", record["id"])
                    result["failed"] += 1

                result["processed"] += 1

            return result

        finally:
            await self.close()

    async def import_series_photos(self, record_id: int):
        logger.info("Starting photo import for record_id=%s", record_id)

        import_series_record = await self.get_import_series_record(record_id)
        folder_url = import_series_record.get("photo_folder")
        if not folder_url:
            raise ValueError("photo_folder is empty")

        folder_id = extract_drive_folder_id(folder_url)
        logger.info("Resolved Google Drive folder for record_id=%s", record_id)

        files = await get_drive_files(self.google_drive, folder_id)
        purgatory_records = await self.get_import_purgatory_records(record_id)

        logger.info("Found %s image files in folder", len(files))

        for purgatory_record in purgatory_records:
            try:
                filename = purgatory_record.get("filename")
                if not filename:
                    continue
                matched_file = find_drive_file(files, filename)
                if not matched_file:
                    logger.warning("No match filename=%s record_id=%s", filename, purgatory_record["id"])
                    await self.update_comment(purgatory_record["id"], "Фото не найдено в папке Google Drive")
                    continue
                await self.attach_photo_to_import_purgatory(
                    record_id=purgatory_record["id"],
                    file_id=matched_file["id"],
                    file_name=matched_file["name"],
                )
                await self.update_comment(purgatory_record["id"], None)
                await asyncio.sleep(random.uniform(0.2, 0.7))
            
            except GoogleRateLimitError:
                logger.error("Google Drive rate limit exceeded")
                raise

            except AttachmentTooLargeError as e:
                await self.update_comment(purgatory_record["id"], "Размер фото не должен превышать 1 МБ")
                logger.warning("Attachment too large %s record_id=%s", e, purgatory_record["id"])
                continue

            except Exception:
                await self.update_comment(purgatory_record["id"], "Ошибка загрузки фото")
                logger.exception("Record processing failed record_id=%s", purgatory_record.get("id"))
                continue
                

        logger.info("Photo import finished for record_id=%s (files=%s records=%s)", record_id, len(files), len(purgatory_records))

        await remove_unused_attachments(
            session=self.session,
            server=self.server,
            doc_id=self.doc_id,
            headers=self.headers,
        )
        
        return {
            "status": "success",
            "record_id": record_id,
        }

    async def get_import_series_records(self):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {"sql": "SELECT id FROM Import_series"}

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()

        return [r["fields"] for r in data.get("records", [])]        

    async def get_import_series_record(self, record_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {"sql": f"SELECT * FROM Import_series WHERE id = {record_id}"}

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()

        records = data.get("records", [])
        if not records:
            raise ValueError(f"Record {record_id} not found")

        return records[0]["fields"]

    async def get_import_purgatory_records(self, import_series_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {"sql": f"SELECT * FROM import_purgatory WHERE batch = {import_series_id}"}

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()

        return [r["fields"] for r in data.get("records", [])]

    async def attach_photo_to_import_purgatory(self, record_id: int, file_id: str, file_name: str):
        file_bytes = await download_drive_file(
            session=self.session,
            file_id=file_id,
        )
        attachment_id = await upload_attachment(
            session=self.session,
            server=self.server,
            doc_id=self.doc_id,
            headers=self.headers,
            file_bytes=file_bytes,
            file_name=file_name,
        )

        url = f"{self.server}/api/docs/{self.doc_id}/tables/Import_purgatory/records"
        payload = {"records": [{"id": record_id, "fields": {"photo_upload": ["L", attachment_id]}}]}

        async with self.session.patch(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

        logger.info("Uploaded %s -> record %s", file_name, record_id)

    async def update_comment(self, record_id: int, comment: str | None):
        url = f"{self.server}/api/docs/{self.doc_id}/tables/Import_purgatory/records"
        payload = {"records": [{"id": record_id, "fields": {"comment": comment}}]}

        async with self.session.patch(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
