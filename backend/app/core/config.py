"""Core configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./test.db"  # Override in .env

    # JWT
    secret_key: str = "change-this-in-env-file"  # Override in .env
    algorithm: str = "HS256"  # Override in .env if needed
    access_token_expire_minutes: int = 60  # Override in .env
    refresh_token_expire_days: int = 7  # Override in .env

    # CORS
    allowed_origins: list[str] = ["*"]  # Override in .env
    
    # Groq LLM Configuration
    groq_api_key: str = ""  # Override in .env
    groq_timeout: int = 30
    groq_max_retries: int = 3
    llm_stage1_model: str = "llama-3.1-8b-instant"
    llm_stage2_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings