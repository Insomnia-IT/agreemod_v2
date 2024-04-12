import logging

from aiogram import Router, types
from aiogram.filters import Command

from bot.src.config import publisher
from bot.src.utils.decorators import check_access_decorator

logging.basicConfig(level=logging.INFO)

router_person = Router()


@router_person.message(Command("update_persons"))
@check_access_decorator
async def update_persons(message: types.Message):
    cmd = {
        "channel": "telegram",
        "message": "update",
        "table": "persons",
        "user_id": message.from_user.id,
    }

    await publisher.publish_message(cmd)
    await message.answer("Запрос на обновление Человеков отправлен")
