from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from teabot.app import create_app


class TestExceptionHandlers:
    @pytest.mark.router
    async def test_not_found_returns_json(self) -> None:
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/nonexistent")
            assert response.status_code == 404
            assert response.headers["content-type"] == "application/json"

    @pytest.mark.router
    async def test_wrong_method_returns_405(self) -> None:
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/health")
            assert response.status_code == 405
