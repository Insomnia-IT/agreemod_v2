import asyncio
import logging
from functools import wraps

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from app.config import Config
from db.meta import async_session
from app.db.repos.person import PersonRepo
from bot.updater_states import UpdaterStates
from updater.main import Updater
from updater.notion.client import NotionClient

logging.basicConfig(level=logging.INFO)

config = Config()
bot = Bot(token=config.TELEBOT_TOKEN)
dp = Dispatcher()

notion = NotionClient(token=config.notion.token)
updater = Updater(notion=notion)

updater_states = UpdaterStates()


def check_access_decorator(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        if not await check_access(message.from_user.username):
            msg = (
                "Отказано в доступе: края Вселенной. "
                "Вступите в ряды организаторов, "
                "обновите свой космический корабль до последней версии и попытайтесь снова. "
                "Благодарим вас за понимание и просим извинения за любые неудобства, "
                "вызванные путешествием сквозь пространство-время!"
            )
            await message.answer(msg)
            return  # If access is denied, we return and don't execute the command.
        return await func(message, *args, **kwargs)

    return wrapper


async def check_access(user_id: str) -> bool:
    async with async_session() as session:
        repo = PersonRepo(session)
        user = await repo.retrieve_by_telegram(user_id)
        return user is not None


@dp.message(Command("start"))
@check_access_decorator
async def start(message: types.Message):
    commands = """
Доступные команды:\n
/update_directions - Обновление Служб и Локаций\n
/update_persons - Обновление Человеков
"""
    await message.answer(f"Привет, {message.from_user.full_name}!" + "\n" + commands)


@dp.message(Command("update_directions"))
@check_access_decorator
async def update_directions(message: types.Message):
    if not updater_states.is_location_updater_running():
        await message.answer("Запуск синхронизации Служб и Локаций")
        updater_states.start_location_updater()
        await updater.poll_directions()
        updater_states.stop_location_updater()
        await message.answer("Процесс синхронизации Служб и Локаций успешно завершён.")
    else:
        await message.answer("Updater таблицы Служб и Локаций уже запущен")


@dp.message(Command("update_persons"))
@check_access_decorator
async def update_persons(message: types.Message):
    if updater_states.is_people_updater_running():
        await message.answer("Запуск синхронизации Человеков.")
        updater_states.start_people_updater()
        await updater.poll_persons()
        updater_states.stop_people_updater()
        await message.answer("Процесс синхронизации Человеков успешно завершён.")
    else:
        await message.answer("Updater таблицы Человеков уже запущен")


async def main():
    await dp.start_polling(bot)


def run_bot_async():
    asyncio.run(main())


if __name__ == "__main__":
    run_bot_async()
