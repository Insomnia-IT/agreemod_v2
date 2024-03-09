import asyncio
import logging
from functools import wraps

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from app.config import Config
from app.db.meta import async_session
from app.db.repos.person import PersonRepo
from updater.main import Updater
from updater.notion.client import NotionClient

logging.basicConfig(level=logging.INFO)

config = Config()
bot = Bot(token=config.TELEBOT_TOKEN)
dp = Dispatcher()

notion = NotionClient(token=config.notion.token)
updater = Updater(notion=notion)


def check_access_decorator(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        if not await check_access(message.from_user.username):
            msg = ("Отказано в доступе: края Вселенной. "
                   "Вступите в ряды организаторов, "
                   "обновите свой космический корабль до последней версии и попытайтесь снова. "
                   "Благодарим вас за понимание и просим извинения за любые неудобства, "
                   "вызванные путешествием сквозь пространство-время!")
            await message.answer(msg)
            return  # If access is denied, we return and don't execute the command.
        return await func(message, *args, **kwargs)

    return wrapper


async def check_access(user_id: str) -> bool:
    async with async_session() as session:
        repo = PersonRepo(session)
        user = await repo.retrieve_by_telegram(user_id)
        return user is not None


@dp.message(Command('start'))
@check_access_decorator
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")


@dp.message(Command('update_directions'))
@check_access_decorator
async def update_directions(message: types.Message):
    await message.answer("Запуск синхронизации Служб и Локаций")
    await updater.poll_directions()
    await message.answer("Процесс синхронизации успешно завершён.")


@dp.message(Command('update_persons'))
@check_access_decorator
async def update_persons(message: types.Message):
    await message.answer("Запуск синхронизации Человеков.")
    await updater.poll_directions()
    await message.answer("Процесс синхронизации успешно завершён.")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
