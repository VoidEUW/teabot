from __future__ import annotations

from teabot.core.exceptions.base import TeaBotError


class ConfigurationError(TeaBotError):
    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message, code="CONFIGURATION_ERROR")
