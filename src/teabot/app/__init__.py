from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from teabot.config import config, validate_config
from teabot.core.exceptions import (
    BotUnavailableError,
    ClientNotReadyError,
    ConflictError,
    NotAuthenticatedError,
    NotFoundError,
    PermissionDeniedError,
    TeaBotError,
    ValidationFailedError,
)
from teabot.core.registry import discover_modules
from teabot.db.engine import get_engine

logger = logging.getLogger("teabot")


async def _check_alembic_head() -> None:
    try:
        from alembic.config import Config as AlembicConfig
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory

        cfg = AlembicConfig("alembic.ini")
        script = ScriptDirectory.from_config(cfg)
        head = script.get_current_head()

        engine = get_engine()
        async with engine.connect() as conn:

            def _get_revision(sync_conn: Any) -> str | None:
                ctx = MigrationContext.configure(sync_conn)
                return ctx.get_current_revision()

            current = await conn.run_sync(_get_revision)

        if current != head:
            logger.warning(
                "Database at revision %s, head is %s. Run 'alembic upgrade head' to sync.",
                current,
                head,
            )
    except Exception:
        logger.exception("Failed to check alembic head")


def create_app() -> FastAPI:
    _configure_logging()
    validate_config()

    registry = discover_modules()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
        await _check_alembic_head()
        logger.info("Database engine initialized")
        logger.info("Discovered %d modules", len(registry.modules))
        yield
        engine = get_engine()
        await engine.dispose()
        logger.info("Database engine disposed")

    app = FastAPI(lifespan=lifespan)

    for prefix, router in registry.routers:
        app.include_router(router, prefix=prefix)

    _register_exception_handlers(app)

    return app


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def _register_exception_handlers(app: FastAPI) -> None:
    status_map: dict[type[TeaBotError], int] = {
        NotFoundError: 404,
        ConflictError: 409,
        ValidationFailedError: 422,
        PermissionDeniedError: 403,
        NotAuthenticatedError: 401,
        BotUnavailableError: 503,
        ClientNotReadyError: 503,
    }

    @app.exception_handler(TeaBotError)
    async def teabot_error_handler(_request: Request, exc: TeaBotError) -> JSONResponse:
        status = 500
        for exc_type, http_status in status_map.items():
            if isinstance(exc, exc_type):
                status = http_status
                break

        return JSONResponse(
            status_code=status,
            content={"error": exc.code or "INTERNAL_ERROR", "message": str(exc)},
        )
