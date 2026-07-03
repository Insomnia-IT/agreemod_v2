import logging
from io import BytesIO

import aiohttp
from PIL import Image


logger = logging.getLogger(__name__)

MAX_ATTACHMENT_SIZE = 1024 * 1024  # 1 MB
MIN_SIDE_SIZE = 500


def resize_image(file_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(file_bytes))

    if image.mode != "RGB":
        image = image.convert("RGB")

    width, height = image.size
    min_side = min(width, height)

    if min_side > MIN_SIDE_SIZE:
        scale = MIN_SIDE_SIZE / min_side
        image = image.resize(
            (
                int(width * scale),
                int(height * scale),
            ),
            Image.Resampling.LANCZOS,
        )

    output = BytesIO()
    image.save(output, format="JPEG", optimize=True)

    return output.getvalue()


async def upload_attachment(
    session: aiohttp.ClientSession,
    server: str,
    doc_id: str,
    headers: dict,
    file_bytes: bytes,
    file_name: str,
):
    if len(file_bytes) > MAX_ATTACHMENT_SIZE:
        logger.info(
            "Image %s is larger than 1 MB (%.2f MB), resizing",
            file_name,
            len(file_bytes) / 1024 / 1024,
        )
        file_bytes = resize_image(file_bytes)

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
