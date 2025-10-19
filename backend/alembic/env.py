"""Alembic environment configuration - DISABLED for single schema approach."""

import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# Import our models and Base
from app.infrastructure.database.models import Base

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
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode - DISABLED."""
    print("Migrations are disabled. Use init_database.py to create schema.")
    return


def do_run_migrations(connection):
    """Run migrations with a connection - DISABLED."""
    print("Migrations are disabled. Use init_database.py to create schema.")
    return


async def run_async_migrations():
    """Run migrations in async mode - DISABLED."""
    print("Migrations are disabled. Use init_database.py to create schema.")
    return


def run_migrations_online() -> None:
    """Run migrations in 'online' mode - DISABLED."""
    print("Migrations are disabled. Use init_database.py to create schema.")
    return


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()