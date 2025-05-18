import asyncio
import logging

from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from database.config import config
from database.create_db import create_database_if_not_exists

logger = logging.getLogger(__name__)

PG_URL = (
    f"postgresql+asyncpg://{config.postgres.user}:{config.postgres.password}"
    #TODO: Check what's going on here
    f"@{config.postgres.host}:{config.postgres.port}/{config.postgres.name}"
    #f"@localhost:5432/{config.postgres.name}"
)
PG_URL_MIGRATIONS = PG_URL.replace("asyncpg", "psycopg2")

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)
# asyncio.run(create_database_if_not_exists())

# FIXME: patch it in conftest instead
if config.TESTING:
    engine_params = dict(poolclass=NullPool)
else:
    engine_params = dict(
        pool_size=config.postgres.MIN_POOL_SIZE,
        max_overflow=config.postgres.MIN_POOL_SIZE + config.postgres.MAX_POOL_SIZE,
    )

engine = create_async_engine(
    PG_URL,
    connect_args={"server_settings": {"jit": "off"}},
    **engine_params,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
