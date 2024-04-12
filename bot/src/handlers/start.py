from aiogram import types
from aiogram.dispatcher.router import Router
from aiogram.filters import Command

from src.utils.decorators import check_access_decorator

router_start = Router()


@router_start.message(Command("start"))
@check_access_decorator
async def start(message: types.Message):
    commands = """
Доступные команды:\n
/update_directions - Обновление Служб и Локаций\n
/update_persons - Обновление Человеков
"""
    await message.answer(f"Привет, {message.from_user.full_name}!" + "\n" + commands)
