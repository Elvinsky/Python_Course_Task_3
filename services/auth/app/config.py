"""Settings read from environment variables (Twelve-Factor: config lives in the environment)."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://auth:auth@localhost:5433/auth"
    redis_url: str = "redis://localhost:6379/0"
    # Required, no default: set JWT_SECRET in the environment (see .env.example).
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 900
    otp_ttl_seconds: int = 300
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    # jwt_secret has no default on purpose: it must come from the environment (mypy cannot see that).
    return Settings()  # type: ignore[call-arg]
