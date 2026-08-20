from __future__ import annotations

from teabot.core.exceptions.base import TeaBotError


class NotFoundError(TeaBotError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="NOT_FOUND")


class ConflictError(TeaBotError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, code="CONFLICT")


class ValidationFailedError(TeaBotError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="VALIDATION_FAILED")
