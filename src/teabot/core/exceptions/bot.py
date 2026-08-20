from __future__ import annotations

from teabot.core.exceptions.base import TeaBotError


class BotUnavailableError(TeaBotError):
    def __init__(self, message: str = "Bot is not available") -> None:
        super().__init__(message, code="BOT_UNAVAILABLE")


class ClientNotReadyError(TeaBotError):
    def __init__(self, message: str = "Client is not ready") -> None:
        super().__init__(message, code="CLIENT_NOT_READY")
