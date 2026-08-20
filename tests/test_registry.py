from __future__ import annotations

from teabot.core.registry import discover_modules


class TestRegistry:
    def test_discover_health_module(self) -> None:
        registry = discover_modules()
        assert "health" in registry.modules
        assert registry.modules["health"].name == "health"
        assert registry.modules["health"].icon == "heart-pulse"

    def test_health_router_is_discovered(self) -> None:
        registry = discover_modules()
        prefixes = [prefix for prefix, _ in registry.routers]
        assert "/health" in prefixes

    def test_no_cogs_in_bootstrap(self) -> None:
        registry = discover_modules()
        assert len(registry.cogs) == 0
