import logging
import random
import re
import aiohttp
import asyncio
from googleapiclient.discovery import build
from app.config import config


logger = logging.getLogger(__name__)

class GoogleRateLimitError(Exception):
    pass


class PhotoSyncService:
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

    async def sync(self, record_id: int):
        await self.init()
        try:
            return await self.sync_folder(record_id)
        finally:
            await self.close()

    async def sync_all(self):
        await self.init()

        try:
            records = await self.get_import_series_records()
            result = {"processed": 0, "success": 0, "failed": 0}
            for record in records:
                try:
                    await self.sync_folder(record["id"])
                    result["success"] += 1

                except GoogleRateLimitError:
                    logger.error("Google rate limit hit - stopping batch sync")
                    result["stopped_reason"] = "google_rate_limit"
                    break

                except Exception:
                    logger.exception("Sync failed for record_id=%s", record["id"])
                    result["failed"] += 1

                result["processed"] += 1

            return result

        finally:
            await self.close()

    async def sync_folder(self, record_id: int):
        logger.info("Starting photo sync for record_id=%s", record_id)

        record = await self.get_record(record_id)
        folder_url = record.get("photo_folder")
        if not folder_url:
            raise ValueError("photo_folder is empty")

        folder_id = self.extract_google_drive_folder_id(folder_url)
        logger.info("Resolved Google Drive folder for record_id=%s", record_id)

        files = await self.get_drive_files(folder_id)
        rows = await self.get_import_purgatory_rows(record_id)

        logger.info("Found %s image files in folder", len(files))

        for row in rows:
            try:
                filename = row.get("filename")
                if not filename:
                    continue
                matched_file = next(
                    (f for f in files if f["name"].lower().startswith(filename.lower())),
                    None,
                )
                if not matched_file:
                    logger.warning("No match filename=%s row_id=%s", filename, row["id"])
                    await self.update_comment(row["id"], "Фото не найдено в папке Google Drive")
                    continue
                await self.upload_photo_to_grist(
                    row_id=row["id"],
                    file_id=matched_file["id"],
                    file_name=matched_file["name"],
                )
                await self.update_comment(row["id"], None)
                await asyncio.sleep(random.uniform(0.2, 0.7))
            except GoogleRateLimitError:
                logger.error("Google Drive rate limit exceeded")
                raise

            except Exception as e:
                await self.update_comment(row["id"], "Ошибка загрузки фото")
                logger.exception("Row processing failed row_id=%s err=%s", row.get("id"), e)
                continue
                

        logger.info("Photo sync finished for record_id=%s (files=%s rows=%s)", record_id, len(files), len(rows))

        await self.remove_unused_attachments()
        
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

    async def get_record(self, record_id: int):
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

    def extract_google_drive_folder_id(self, folder_url: str):
        match = re.search(r"(?:https://drive\.google\.com/drive/folders/)([a-zA-Z0-9_-]+)", folder_url)
        if not match:
            raise ValueError(f"Invalid Google Drive folder link: {folder_url}")
        return match.group(1)

    async def get_drive_files(self, folder_id: str):
        query = f"'{folder_id}' in parents and trashed=false"

        results = await asyncio.to_thread(
            lambda: self.google_drive.files().list(
                q=query,
                fields="files(id,name,mimeType)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
        )

        files = [
            f for f in results.get("files", [])
            if f["mimeType"].startswith("image/")
        ]

        return files

    async def get_import_purgatory_rows(self, import_series_id: int):
        url = f"{self.server}/api/docs/{self.doc_id}/sql"
        payload = {"sql": f"SELECT * FROM import_purgatory WHERE batch = {import_series_id}"}

        async with self.session.post(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            data = await resp.json()

        return [r["fields"] for r in data.get("records", [])]

    async def upload_photo_to_grist(self, row_id: int, file_id: str, file_name: str):
        file_bytes = await self.download_drive_file(file_id)
        attachment_id = await self.upload_attachment(file_bytes, file_name)

        url = f"{self.server}/api/docs/{self.doc_id}/tables/Import_purgatory/records"
        payload = {"records": [{"id": row_id, "fields": {"photo_upload": ["L", attachment_id]}}]}

        async with self.session.patch(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

        logger.info("Uploaded %s -> row %s", file_name, row_id)

    async def download_drive_file(self, file_id: str):
        url = f"https://docs.google.com/uc?export=download&id={file_id}"
        browser_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive"
        }

        async with self.session.get(url, headers=browser_headers) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if resp.status == 200 and "text/html" not in content_type:
                return await resp.read()

            text = await resp.text()

            if resp.status in (403, 429) or "automated queries" in text.lower():
                raise GoogleRateLimitError()

            raise Exception(text)

    async def upload_attachment(self, file_bytes: bytes, file_name: str):
        url = f"{self.server}/api/docs/{self.doc_id}/attachments"

        form = aiohttp.FormData()
        form.add_field("upload", file_bytes, filename=file_name, content_type="image/jpeg")

        async with self.session.post(url, headers=self.headers, data=form) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())
            result = await resp.json()

        attachment_id = result[0]
        logger.info("Attachment created: %s for %s", attachment_id, file_name)
        return attachment_id

    async def remove_unused_attachments(self):
        url = f"{self.server}/api/docs/{self.doc_id}/attachments/removeUnused"

        async with self.session.post(url, headers=self.headers) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

        logger.info("Unused attachments removed")

    async def update_comment(self, row_id: int, comment: str | None):
        url = f"{self.server}/api/docs/{self.doc_id}/tables/Import_purgatory/records"
        payload = {"records": [{"id": row_id, "fields": {"comment": comment}}]}

        async with self.session.patch(url, headers=self.headers, json=payload) as resp:
            if resp.status != 200:
                raise Exception(await resp.text())

