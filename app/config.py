"""Application configuration.

Loaded from environment variables (with optional `.env` file in development).
Nested sub-settings use the `__` delimiter, e.g. `TELEGRAM__BOT_TOKEN`.
"""
from __future__ import annotations

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    production = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    openai = "openai"
    google = "google"


class TelegramConfig(BaseModel):
    bot_token: SecretStr
    admin_chat_id: SecretStr
    group_id: SecretStr
    webhook_secret: SecretStr


class RedisConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 6379
    database: int = 0
    password: SecretStr | None = None

    def url(self) -> str:
        auth = f":{self.password.get_secret_value()}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"


class DatabaseConfig(BaseModel):
    uri: SecretStr
    name: str = "verificationSystem"
    checkpoint_name: str = "verificationSystemStates"


class ModelConfig(BaseModel):
    provider: LLMProvider = LLMProvider.google
    model_name: str = "gemini-2.5-flash"
    api_key: SecretStr
    temperature: float = 0.7


class ExchangeCredentials(BaseModel):
    api_key: SecretStr
    secret_key: SecretStr


class Settings(BaseSettings):
    """Top-level application settings."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "jontraderlar"
    app_version: str = "2.0.0"
    environment: Environment = Environment.production
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8080
    public_url: str = ""

    log_level: LogLevel = LogLevel.INFO
    log_json: bool = True

    telegram: TelegramConfig
    redis: RedisConfig = RedisConfig()
    database: DatabaseConfig
    model: ModelConfig
    bingx: ExchangeCredentials
    bybit: ExchangeCredentials

    # NoDecode: skip pydantic-settings' JSON parsing — the validator below
    # handles the comma-separated env format instead.
    blocked_uids: Annotated[list[int], NoDecode, Field(default_factory=list)]

    @field_validator("blocked_uids", mode="before")
    @classmethod
    def _split_blocked_uids(cls, v: object) -> list[int]:
        if v is None or v == "":
            return []
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [int(x) for x in v]
        raise ValueError(f"BLOCKED_UIDS must be str or list, got {type(v)!r}")

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.production

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.development


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings instance."""
    return Settings()  # type: ignore[call-arg]


# Convenient module-level alias.
settings = get_settings()
