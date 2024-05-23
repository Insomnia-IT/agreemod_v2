import logging

import asyncpg

from database.config import config

logger = logging.getLogger(__name__)


async def create_database_if_not_exists():
    conn = await asyncpg.connect(
        database="postgres",
        user=config.postgres.user,
        password=config.postgres.password,
        host=config.postgres.host,
        port=config.postgres.port,
    )

    try:
        await conn.execute(f"CREATE DATABASE {config.postgres.name}")
        logger.info(f"Database {config.postgres.name} created successfully.")
    except asyncpg.DuplicateDatabaseError:
        logger.info(f"Database {config.postgres.name} already exists.")
    finally:
        await conn.close()
