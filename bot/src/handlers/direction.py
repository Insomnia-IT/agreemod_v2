import logging

from aiogram import Router, types
from aiogram.filters import Command
from src.config import publisher
from src.utils.decorators import check_access_decorator

logging.basicConfig(level=logging.INFO)

router_direction = Router()


@router_direction.message(Command("update_directions"))
@check_access_decorator
async def update_directions(message: types.Message):
    cmd = {
        "channel": "telegram",
        "message": "update",
        "table": "directions",
        "user_id": message.from_user.id,
    }

    await publisher.publish_message(cmd)
    await message.answer("Запрос на обновление Направлений отправлен")
