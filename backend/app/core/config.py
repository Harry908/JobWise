"""Core configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # API Configuration
    PROJECT_NAME: str = Field(default="JobWise API")
    API_V1_PREFIX: str = Field(default="/api/v1")
    
    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./jobwise.db")
    DATABASE_URL_PROD: Optional[str] = None
    
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL based on environment."""
        if self.ENVIRONMENT == "production" and self.DATABASE_URL_PROD:
            return self.DATABASE_URL_PROD
        return self.DATABASE_URL
    
    # Security
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # JWT Configuration
    JWT_SECRET_KEY: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = Field(default="gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = Field(default=8000)
    OPENAI_TEMPERATURE: float = Field(default=0.7)
    OPENAI_REQUEST_TIMEOUT: int = Field(default=60)
    
    # Alternative AI Models (Optional)
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = Field(default="claude-3-sonnet-20240229")
    
    # Redis Configuration
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=100)
    AI_GENERATION_RATE_LIMIT: int = Field(default=10)  # per hour per user
    
    # File Storage
    PDF_STORAGE_PATH: str = Field(default="./storage/pdfs")
    DOCUMENT_STORAGE_PATH: str = Field(default="./storage/documents")
    UPLOAD_MAX_SIZE: int = Field(default=10485760)  # 10MB
    
    # External APIs
    INDEED_PUBLISHER_ID: Optional[str] = None
    LINKEDIN_API_KEY: Optional[str] = None
    
    # Monitoring
    LOG_LEVEL: str = Field(default="INFO")
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = Field(default=True)
    
    # Cache TTL (in seconds)
    CACHE_TTL_PROFILES: int = Field(default=3600)  # 1 hour
    CACHE_TTL_JOBS: int = Field(default=86400)     # 24 hours
    CACHE_TTL_DOCUMENTS: int = Field(default=3600) # 1 hour
    
    # Performance
    PDF_GENERATION_TIMEOUT: int = Field(default=30)
    HTTP_TIMEOUT: int = Field(default=30)
    
    # Feature Flags
    ENABLE_COVER_LETTER_GENERATION: bool = Field(default=True)
    ENABLE_BATCH_GENERATION: bool = Field(default=False)
    ENABLE_DOCUMENT_SHARING: bool = Field(default=True)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()


# Environment-specific settings
def is_development() -> bool:
    """Check if running in development mode."""
    return get_settings().ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return get_settings().ENVIRONMENT == "production"


def get_database_url() -> str:
    """Get appropriate database URL for current environment."""
    settings = get_settings()
    return settings.effective_database_url