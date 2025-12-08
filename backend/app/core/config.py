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
    
    # LLM Configuration
    groq_api_key: str = Field(
        ...,
        alias="GROQ_API_KEY",
        description="Groq API key for LLM operations"
    )
    
    # AWS S3 Configuration for Document Exports
    aws_access_key_id: str = Field(
        ...,
        alias="AWS_ACCESS_KEY_ID",
        description="AWS access key for S3 storage"
    )
    aws_secret_access_key: str = Field(
        ...,
        alias="AWS_SECRET_ACCESS_KEY",
        description="AWS secret key for S3 storage"
    )
    s3_bucket_name: str = Field(
        ...,
        alias="S3_BUCKET_NAME",
        description="S3 bucket name for document exports"
    )
    s3_region: str = Field(
        default="us-east-1",
        alias="S3_REGION",
        description="AWS S3 region"
    )
    
    # Export Configuration
    export_max_file_size_mb: int = Field(
        default=100,
        alias="EXPORT_MAX_FILE_SIZE_MB",
        description="Maximum export file size in MB"
    )
    presigned_url_expiration_seconds: int = Field(
        default=3600,
        alias="PRESIGNED_URL_EXPIRATION_SECONDS",
        description="Presigned URL expiration time (default 1 hour)"
    )
    export_retention_days: int = Field(
        default=30,
        alias="EXPORT_RETENTION_DAYS",
        description="Days to retain exports before auto-deletion"
    )

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