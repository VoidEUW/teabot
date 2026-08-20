from __future__ import annotations

import pytest


@pytest.mark.router
class TestHealth:
    async def test_health_returns_200(self, client) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
