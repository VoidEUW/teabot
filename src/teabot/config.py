from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    discord_token: str = Field("", validation_alias="DISCORD_TOKEN")
    discord_client_id: str = Field("", validation_alias="DISCORD_CLIENT_ID")
    discord_client_secret: str = Field("", validation_alias="DISCORD_CLIENT_SECRET")
    session_secret: str = Field("", validation_alias="SESSION_SECRET")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/teabot.db",
        validation_alias="DATABASE_URL",
    )

    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    dev_mode: bool = Field(default=False, validation_alias="DEV_MODE")


config = Config()  # type: ignore[call-arg]


def validate_config() -> None:
    missing = []
    if not config.discord_token:
        missing.append("DISCORD_TOKEN")
    if not config.discord_client_id:
        missing.append("DISCORD_CLIENT_ID")
    if not config.discord_client_secret:
        missing.append("DISCORD_CLIENT_SECRET")
    if not config.session_secret:
        missing.append("SESSION_SECRET")
    if missing:
        msg = "Missing required configuration values: {}".format(", ".join(missing))
        raise SystemExit(msg)
