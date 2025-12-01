"""Core configuration settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./jobwise.db"

    # JWT Configuration  
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # CORS Configuration
    allowed_origins: List[str] = ["*"]
    
    # Application Configuration
    app_name: str = "JobWise Backend API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=False,
        # Remove env_nested_delimiter since we're using flat environment variables
        extra="ignore"  # Ignore unknown environment variables
    )


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings