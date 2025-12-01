"""Core configuration settings."""

from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./jobwise.db",
        alias="DATABASE_URL",
        description="SQLAlchemy connection string"
    )

    # JWT Configuration  
    secret_key: str = Field(
        ...,
        alias="SECRET_KEY",
        description="JWT signing secret loaded from environment variables"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # CORS Configuration
    allowed_origins: List[str] = Field(default=["*"], alias="ALLOWED_ORIGINS")
    
    # Application Configuration
    app_name: str = Field(default="JobWise Backend API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        case_sensitive=False,
        populate_by_name=True,
        # Remove env_nested_delimiter since we're using flat environment variables
        extra="ignore"  # Ignore unknown environment variables
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get (and cache) application settings."""
    return Settings()  # type: ignore[call-arg]