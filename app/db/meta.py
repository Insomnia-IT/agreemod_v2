from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import config


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

# FIXME: patch it in conftest instead
if config.TESTING:
    engine_params = dict(poolclass=NullPool)
else:
    engine_params = dict(
        pool_size=config.POSTGRES_MIN_POOL_SIZE,
        max_overflow=config.POSTGRES_MIN_POOL_SIZE + config.POSTGRES_MAX_POOL_SIZE,
    )

engine = create_async_engine(
    config.DB_URL,
    connect_args={"server_settings": {"jit": "off"}},
    **engine_params,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
