from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from teabot.app import create_app
from teabot.core.registry import discover_modules


@pytest.mark.router
class TestRegistryIntegration:
    async def test_registry_mounts_health_router_via_http(self) -> None:
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200

    async def test_discovered_router_is_mounted_in_app(self) -> None:
        registry = discover_modules()
        for prefix, _ in registry.routers:
            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(prefix)
                assert response.status_code != 404, (
                    f"Router with prefix '{prefix}' is discovered but not mounted"
                )


@pytest.mark.router
class TestModuleDiscovery:
    async def test_new_module_is_discovered_and_mounted(self) -> None:
        probe_dir = Path("src/teabot/modules/probe")
        probe_dir.mkdir(exist_ok=True)
        (probe_dir / "__init__.py").write_text(
            "from teabot.core.registry import ModuleInfo\n"
            "from teabot.modules.probe.router import router\n"
            'MODULE = ModuleInfo(name="probe", prefix="/probe")\n'
        )
        (probe_dir / "router.py").write_text(
            "from fastapi import APIRouter\n"
            "router = APIRouter()\n"
            "@router.get('')\n"
            "async def probe() -> dict:\n"
            '    return {"status": "probe"}\n'
        )

        try:
            import importlib

            import teabot.modules

            importlib.reload(teabot.modules)

            registry = discover_modules()
            assert "probe" in registry.modules
            assert "/probe" in [p for p, _ in registry.routers]

            app = create_app()
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/probe")
                assert response.status_code == 200
                assert response.json() == {"status": "probe"}
        finally:
            if probe_dir.exists():
                shutil.rmtree(probe_dir)
            for cache_dir in Path("src/teabot/modules").rglob("__pycache__"):
                shutil.rmtree(cache_dir, ignore_errors=True)
