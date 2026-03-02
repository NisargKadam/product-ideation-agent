# src/config.py
"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Application Settings
    app_name: str = "Product Ideation Agent"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Railway assigns PORT env var
    port: int | None = None

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/agent.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()