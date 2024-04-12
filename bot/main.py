import asyncio
import logging

from aiogram import Dispatcher

from src.config import bot
from src.handlers.direction import router_direction
from src.handlers.person import router_person
from src.handlers.start import router_start

logging.basicConfig(level=logging.INFO)


def include_routers(dp: Dispatcher):
    dp.include_router(router_start)
    dp.include_router(router_person)
    dp.include_router(router_direction)


async def main(dp: Dispatcher):
    await dp.start_polling(bot)


if __name__ == "__main__":
    disp = Dispatcher()
    include_routers(disp)
    asyncio.run(main(disp))
