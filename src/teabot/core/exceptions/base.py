from __future__ import annotations


class TeaBotError(Exception):
    """Base for all application-level errors."""

    def __init__(self, message: str, code: str = "") -> None:
        self.code = code
        super().__init__(message)
