"""Settings read from environment variables (Twelve-Factor: config lives in the environment)."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://core:core@localhost:5432/core"
    # Required, no default: the key (or, with asymmetric keys, the PUBLIC key) used to verify tokens.
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    # jwt_secret has no default on purpose: it must come from the environment (mypy cannot see that).
    return Settings()  # type: ignore[call-arg]
