from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Life Assistant Orchestrator"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    openai_api_key: str | None = None
    default_model: str = "gpt-4.1-mini"
    data_dir: Path = Path("./data")
    assistant_email_enabled: bool = False
    assistant_email_provider: str = "gmail_smtp"
    assistant_email_from: str | None = None
    assistant_email_app_password: str | None = None
    assistant_email_smtp_host: str = "smtp.gmail.com"
    assistant_email_smtp_port: int = 587
    assistant_email_use_starttls: bool = True
    github_token: str | None = None
    github_models_enabled: bool = False
    github_models_model: str = "gpt-4o-mini"
    github_models_timeout: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
