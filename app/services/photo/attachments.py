import logging

import aiohttp


logger = logging.getLogger(__name__)


class AttachmentTooLargeError(Exception):
    pass


async def upload_attachment(
    session: aiohttp.ClientSession,
    server: str,
    doc_id: str,
    headers: dict,
    file_bytes: bytes,
    file_name: str,
):
    url = f"{server}/api/docs/{doc_id}/attachments"

    form = aiohttp.FormData()
    form.add_field(
        "upload",
        file_bytes,
        filename=file_name,
        content_type="image/jpeg",
    )

    async with session.post(url, headers=headers, data=form) as resp:
        if resp.status != 200:
            if resp.status == 413:
                raise AttachmentTooLargeError(
                    f"filename={file_name} size={len(file_bytes) / 1024 / 1024:.2f} MB"
                )
            raise Exception(await resp.text())

        result = await resp.json()

    attachment_id = result[0]
    logger.info("Attachment created: %s for %s", attachment_id, file_name)
    return attachment_id


async def remove_unused_attachments(
    session: aiohttp.ClientSession,
    server: str,
    doc_id: str,
    headers: dict,
):
    url = f"{server}/api/docs/{doc_id}/attachments/removeUnused"

    async with session.post(url, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(await resp.text())

    logger.info("Unused attachments removed")
