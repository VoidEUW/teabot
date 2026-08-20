from __future__ import annotations

from teabot.core.registry import ModuleInfo
from teabot.modules.health.router import router as router

MODULE = ModuleInfo(
    name="health",
    icon="heart-pulse",
    prefix="/health",
)
