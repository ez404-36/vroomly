import asyncio
import logging
import os
import sys
from logging.config import fileConfig

from alembic import context
from alembic.operations.ops import CreateTableOp
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from common.models import render_item
from core.db import DATABASE_URL
from core.models import AutoSchemaBase
from core.models.loader import load_all_models

# Добавляем корень проекта в sys.path для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

base = AutoSchemaBase

# Загружаем .env
load_dotenv()

logger = logging.getLogger(__name__)


def sort_columns_create_table(op: CreateTableOp):
    """
    Переносит колонку 'id' в начало при создании таблицы
    """
    id_column = None
    other_columns = []

    for col in op.columns:
        if col.name == "id":
            id_column = col
        else:
            other_columns.append(col)

    if id_column is not None:
        op.columns = [id_column] + other_columns


def process_revision_directives(_, _revision, directives):
    for directive in directives:
        if hasattr(directive, "upgrade_ops"):
            for op in directive.upgrade_ops.ops:
                if isinstance(op, CreateTableOp):
                    sort_columns_create_table(op)


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

load_all_models()
target_metadata = base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item,
        include_schemas=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
