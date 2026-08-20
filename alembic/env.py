from __future__ import annotations

import asyncio
import logging
import os
import pkgutil
from contextlib import suppress
from importlib import import_module
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Alembic-Konfiguration lesen (ini)
config_ini = context.config
if config_ini.config_file_name is not None:
    fileConfig(config_ini.config_file_name)

logger = logging.getLogger("alembic.env")

# Database URL: CLI-Argument vor Umgebungsvariable vor alembic.ini
DATABASE_URL = (
    config_ini.get_main_option("sqlalchemy.url")
    if not os.environ.get("DATABASE_URL")
    else os.environ["DATABASE_URL"]
)

target_metadata: MetaData | None = None

# Batch-Options für SQLite: sqlite_autoincrement geht beim Copy-and-Move
# verloren, wenn es nicht explizit mitgegeben wird.
_BATCH_KWARGS = {
    "table_kwargs": {"sqlite_autoincrement": True},
}


def _import_all_module_metadata() -> None:
    """Import all module packages and their models so Alembic autogenerate sees them."""
    import teabot.modules

    mod_path = Path(teabot.modules.__file__).resolve().parent
    for _, modname, is_pkg in pkgutil.walk_packages(
        path=[str(mod_path)],
        prefix="teabot.modules.",
        onerror=lambda name: logger.warning("Failed to scan %s", name),
    ):
        if not is_pkg:
            continue
        try:
            import_module(modname)
        except Exception:
            logger.exception("Failed to import %s", modname)
            continue
        with suppress(ImportError):
            import_module(f"{modname}.models")


_import_all_module_metadata()

from teabot.db.base import Base  # noqa: E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        batch_op_kwargs=_BATCH_KWARGS,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        batch_op_kwargs=_BATCH_KWARGS,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
