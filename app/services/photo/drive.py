import asyncio
import re


class GoogleRateLimitError(Exception):
    pass


def extract_drive_folder_id(folder_url: str) -> str:
    match = re.search(
        r"(?:https://drive\.google\.com/drive/folders/)([a-zA-Z0-9_-]+)",
        folder_url,
    )
    if not match:
        raise ValueError(f"Invalid Google Drive folder link: {folder_url}")

    return match.group(1)


async def get_drive_files(google_drive, folder_id: str):
    query = f"'{folder_id}' in parents and trashed=false"

    results = await asyncio.to_thread(
        lambda: google_drive.files().list(
            q=query,
            fields="files(id,name,mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
    )

    return [
        f
        for f in results.get("files", [])
        if f["mimeType"].startswith("image/")
    ]


def find_drive_file(files: list[dict], filename: str) -> dict | None:
    filename = filename.lower()

    for file in files:
        if file["name"].lower().startswith(filename):
            return file

    return None


async def download_drive_file(session, file_id: str):
    
    url = f"https://docs.google.com/uc?export=download&id={file_id}"
    browser_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }

    async with session.get(url, headers=browser_headers) as resp:
        content_type = resp.headers.get("Content-Type", "")
        if resp.status == 200 and "text/html" not in content_type:
            return await resp.read()

        text = await resp.text()

        if resp.status in (403, 429) or "automated queries" in text.lower():
            raise GoogleRateLimitError()

        raise Exception(text)
