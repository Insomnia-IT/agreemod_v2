import asyncio
from app.services.badge import BadgeService
from database.meta import async_session

b = BadgeService(async_session())
asyncio.run(b.prepare_to_print(1))