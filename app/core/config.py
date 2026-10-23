"""Application configuration loaded from environment variables / .env."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class Settings(BaseSettings):
    """Typed settings. Add a field only when a phase actually needs it."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "HealthDay AI"
    app_version: str = "0.1.0"
    app_env: Literal["development", "testing", "staging", "production"] = "development"
    log_level: str = "INFO"

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        level = str(value).upper()
        if level not in _VALID_LOG_LEVELS:
            raise ValueError(f"log_level must be one of {sorted(_VALID_LOG_LEVELS)}")
        return level


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor, usable as a FastAPI dependency."""
    return Settings()
