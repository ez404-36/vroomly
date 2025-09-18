import asyncio
import logging
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from alembic.operations.ops import CreateTableOp
from common.models import render_item
from core.db import DATABASE_URL
from core.models import AutoSchemaBase
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Добавляем корень проекта в sys.path для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

base = AutoSchemaBase

# Загружаем .env
load_dotenv()

logger = logging.getLogger(__name__)


def load_all_models():
    """
    Сканирует директорию apps/ и загружает модели из всех apps/<service>/models
    """
    apps_dir = Path(__file__).parent.parent / "apps"
    if not apps_dir.exists():
        raise FileNotFoundError("Директория apps/ не найдена")

    for service_dir in apps_dir.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = service_dir.name
        root_models_dir = service_dir / "models"

        def load_models_in_module(models_dir: Path):
            if not models_dir.exists():
                return

            for model_file in models_dir.iterdir():
                if model_file.is_dir():
                    load_models_in_module(model_file)
                else:
                    file_name = model_file.stem
                    if (
                        file_name.startswith("__")
                        and file_name.endswith("__")
                        or model_file.suffix != ".py"
                    ):
                        continue
                    try:
                        models_file_module = __import__(
                            f"apps.{service_name}.models.{file_name}", fromlist=["*"]
                        )
                        # Собираем все объекты, которые могут быть моделями
                        for name in filter(
                            lambda var: var != base.__name__, dir(models_file_module)
                        ):
                            obj = getattr(models_file_module, name)
                            if (
                                isinstance(obj, type)
                                and issubclass(obj, base)
                                and obj is not base
                            ):
                                obj.metadata  # Регистрируем модель
                    except ImportError as e:
                        logger.warning(
                            f"Предупреждение: Не удалось загрузить модели для сервиса {service_name}: {e}"
                        )
                        continue

        load_models_in_module(root_models_dir)


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


def process_revision_directives(_, revision, directives):
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
