from functools import wraps

from aiogram import types

from app.db.repos.person import PersonRepo
from db.meta import async_session


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
