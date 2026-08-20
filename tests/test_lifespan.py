from __future__ import annotations

from fastapi.testclient import TestClient

from teabot.app import create_app


class TestLifespan:
    def test_app_startup_and_shutdown_logs(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
