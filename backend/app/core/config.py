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
    
    # Groq LLM Configuration
    groq_api_key: str = ""
    groq_timeout: int = 30
    groq_max_retries: int = 3
    
    # LLM Model Configuration
    llm_stage1_model: str = "llama-3.1-8b-instant"
    llm_stage2_model: str = "llama-3.3-70b-versatile"
    
    # LLM Generation Parameters
    llm_temperature_analysis: float = 0.2  # Low temperature for analysis tasks
    llm_temperature_generation: float = 0.4  # Higher temperature for content generation
    llm_temperature_preference: float = 0.1  # Very low for preference extraction
    llm_max_tokens_analysis: int = 2000
    llm_max_tokens_generation: int = 3000
    llm_max_tokens_preference: int = 1000
    llm_max_tokens_matching: int = 2500
    llm_max_tokens_validation: int = 1500
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = 30
    rate_limit_retry_delay: int = 1
    rate_limit_max_retries: int = 3
    rate_limit_retry_after: int = 3600  # 1 hour in seconds
    
    # Generation Service Configuration
    generation_pipeline_stage1_weight: int = 40  # Analysis & Matching stage weight
    generation_pipeline_stage2_weight: int = 60  # Generation & Validation stage weight
    generation_max_concurrent_jobs: int = 5
    generation_cleanup_interval: int = 300  # 5 minutes in seconds
    
    # File Upload Configuration  
    upload_max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_allowed_extensions: List[str] = [".pdf", ".doc", ".docx", ".txt"]
    upload_storage_path: str = "./uploads"
    
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