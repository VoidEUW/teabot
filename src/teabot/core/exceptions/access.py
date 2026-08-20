from __future__ import annotations

from teabot.core.exceptions.base import TeaBotError


class PermissionDeniedError(TeaBotError):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message, code="PERMISSION_DENIED")


class NotAuthenticatedError(TeaBotError):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(message, code="NOT_AUTHENTICATED")
