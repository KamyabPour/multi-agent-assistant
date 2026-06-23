from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Life Assistant Orchestrator"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    openai_api_key: str | None = None
    default_model: str = "gpt-4.1-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
