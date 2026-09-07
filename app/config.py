from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "YouTube Content Engine"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    postgres_url: str = (
        "postgresql+psycopg://youtube_engine:"
        "youtube_engine_dev@localhost:5432/youtube_engine"
    )

    redis_url: str = "redis://localhost:6379/0"
    quota_default_limit: int = 10_000
    quota_default_window_seconds: int = 86_400
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()