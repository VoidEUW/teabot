from __future__ import annotations

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("DISCORD_CLIENT_ID", "test-id")
os.environ.setdefault("DISCORD_CLIENT_SECRET", "test-secret")
os.environ.setdefault("SESSION_SECRET", "test-session")

from teabot.app import create_app
from teabot.db.base import Base

_test_engine: AsyncEngine | None = None


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(_test_engine.sync_engine, "connect")
        def _set_pragmas(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()

    return _test_engine


@pytest_asyncio.fixture(autouse=True)
async def setup_tables(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
