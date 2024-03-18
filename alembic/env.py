import asyncio
from logging.config import fileConfig

import venusian
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from db.meta import PG_URL, metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = metadata
venusian.Scanner().scan(__import__("db"))


def do_run_migrations(connection):
    context.configure(
        transaction_per_migration=True,
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    async_engine = create_async_engine(PG_URL)

    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


async def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=PG_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    asyncio.run(run_migrations_offline())
else:
    asyncio.run(run_migrations_online())
