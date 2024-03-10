"""
Create user with all the permissions.
python -m scripts.create_user.py {username} {password}
"""
import asyncio

import venusian

from app.db.meta import engine, metadata


async def main() -> None:
    venusian.Scanner().scan(__import__('app'))
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
