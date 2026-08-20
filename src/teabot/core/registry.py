from __future__ import annotations

import logging
import pkgutil
from dataclasses import dataclass, field
from importlib import import_module
from pathlib import Path
from types import ModuleType
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    name: str
    icon: str = ""
    prefix: str = ""
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ModuleRegistry:
    modules: dict[str, ModuleInfo] = field(default_factory=dict)
    routers: list[tuple[str, Any]] = field(default_factory=list)
    cogs: list[type] = field(default_factory=list)
    settings_schemas: list[type] = field(default_factory=list)
    permission_actions: list[Any] = field(default_factory=list)


def discover_modules() -> ModuleRegistry:
    registry = ModuleRegistry()
    package = import_module("teabot.modules")
    package_file = package.__file__
    if not package_file:
        logger.error("Cannot locate teabot.modules package")
        return registry
    package_path = str(Path(package_file).resolve().parent)

    for _importer, modname, is_pkg in pkgutil.walk_packages(
        path=[package_path],
        prefix="teabot.modules.",
        onerror=lambda name: logger.warning("Failed to scan module %s", name),
    ):
        if not is_pkg:
            continue

        try:
            mod = import_module(modname)
        except Exception:
            logger.exception("Failed to import module %s", modname)
            continue

        _collect_module(registry, mod)

    return registry


def _collect_module(registry: ModuleRegistry, mod: ModuleType) -> None:
    module_info: ModuleInfo | None = getattr(mod, "MODULE", None)
    if module_info is None:
        return

    registry.modules[module_info.name] = module_info

    router = getattr(mod, "router", None)
    if router is not None:
        registry.routers.append((module_info.prefix or f"/{module_info.name}", router))

    cog = getattr(mod, "Cog", None)
    if cog is not None:
        registry.cogs.append(cog)

    settings = getattr(mod, "SETTINGS", None)
    if settings is not None:
        registry.settings_schemas.append(settings)

    permissions = getattr(mod, "PERMISSIONS", None)
    if permissions is not None:
        registry.permission_actions.append(permissions)
