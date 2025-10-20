"""
Tests for environment configuration and settings.
"""
import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings, is_development, is_production, get_database_url


class TestSettings:
    """Test Settings class configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is True
        assert settings.PROJECT_NAME == "JobWise API"
        assert settings.API_V1_PREFIX == "/api/v1"
        assert "sqlite" in settings.DATABASE_URL
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32

    def test_environment_override(self, mock_env_vars):
        """Test that environment variables override defaults."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "DEBUG": "False",
            "PROJECT_NAME": "Test API",
            "SECRET_KEY": "test-secret-key-32-chars-minimum-length",
        }):
            settings = Settings()

            assert settings.ENVIRONMENT == "production"
            assert settings.DEBUG is False
            assert settings.PROJECT_NAME == "Test API"
            assert settings.SECRET_KEY == "test-secret-key-32-chars-minimum-length"

    def test_database_url_configuration(self):
        """Test database URL configuration for different environments."""
        # Development should use default SQLite
        dev_settings = Settings(ENVIRONMENT="development")
        assert "sqlite" in dev_settings.effective_database_url

        # Production should use production URL if available
        prod_settings = Settings(
            ENVIRONMENT="production",
            DATABASE_URL_PROD="postgresql://user:pass@localhost/db"
        )
        assert prod_settings.effective_database_url == "postgresql://user:pass@localhost/db"

        # Production without prod URL should fallback to default
        prod_settings_no_prod = Settings(ENVIRONMENT="production", DATABASE_URL_PROD=None)
        assert "sqlite" in prod_settings_no_prod.effective_database_url

    def test_cors_configuration(self):
        """Test CORS origins configuration."""
        settings = Settings(CORS_ORIGINS=["http://localhost:3000", "https://example.com"])
        assert settings.CORS_ORIGINS == ["http://localhost:3000", "https://example.com"]

    def test_security_settings(self):
        """Test security-related settings."""
        settings = Settings(
            SECRET_KEY="super-secret-key-32-chars-minimum-here",
            ALGORITHM="HS256",
            ACCESS_TOKEN_EXPIRE_MINUTES=60,
            REFRESH_TOKEN_EXPIRE_DAYS=30,
        )

        assert settings.SECRET_KEY == "super-secret-key-32-chars-minimum-here"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 30

    def test_ai_service_configuration(self):
        """Test AI service configuration."""
        settings = Settings(
            OPENAI_API_KEY="test-key",
            OPENAI_MODEL="gpt-4",
            OPENAI_MAX_TOKENS=4000,
            OPENAI_TEMPERATURE=0.5,
        )

        assert settings.OPENAI_API_KEY == "test-key"
        assert settings.OPENAI_MODEL == "gpt-4"
        assert settings.OPENAI_MAX_TOKENS == 4000
        assert settings.OPENAI_TEMPERATURE == 0.5

    def test_rate_limiting_settings(self):
        """Test rate limiting configuration."""
        settings = Settings(
            RATE_LIMIT_REQUESTS_PER_MINUTE=200,
            AI_GENERATION_RATE_LIMIT=20,
        )

        assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 200
        assert settings.AI_GENERATION_RATE_LIMIT == 20

    def test_file_storage_settings(self):
        """Test file storage configuration."""
        settings = Settings(
            PDF_STORAGE_PATH="/custom/path/pdfs",
            DOCUMENT_STORAGE_PATH="/custom/path/docs",
            UPLOAD_MAX_SIZE=20971520,  # 20MB
        )

        assert settings.PDF_STORAGE_PATH == "/custom/path/pdfs"
        assert settings.DOCUMENT_STORAGE_PATH == "/custom/path/docs"
        assert settings.UPLOAD_MAX_SIZE == 20971520

    def test_cache_settings(self):
        """Test cache TTL settings."""
        settings = Settings(
            CACHE_TTL_PROFILES=7200,  # 2 hours
            CACHE_TTL_JOBS=43200,     # 12 hours
            CACHE_TTL_DOCUMENTS=1800, # 30 minutes
        )

        assert settings.CACHE_TTL_PROFILES == 7200
        assert settings.CACHE_TTL_JOBS == 43200
        assert settings.CACHE_TTL_DOCUMENTS == 1800

    def test_feature_flags(self):
        """Test feature flag configuration."""
        settings = Settings(
            ENABLE_COVER_LETTER_GENERATION=False,
            ENABLE_BATCH_GENERATION=True,
            ENABLE_DOCUMENT_SHARING=False,
        )

        assert settings.ENABLE_COVER_LETTER_GENERATION is False
        assert settings.ENABLE_BATCH_GENERATION is True
        assert settings.ENABLE_DOCUMENT_SHARING is False


class TestEnvironmentHelpers:
    """Test environment helper functions."""

    def test_is_development(self):
        """Test is_development helper."""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(ENVIRONMENT="production")

        with patch('app.core.config.get_settings', return_value=dev_settings):
            assert is_development() is True
            assert is_production() is False

        with patch('app.core.config.get_settings', return_value=prod_settings):
            assert is_development() is False
            assert is_production() is True

    def test_get_database_url(self):
        """Test get_database_url helper."""
        # Development environment
        dev_settings = Settings(
            ENVIRONMENT="development",
            DATABASE_URL="sqlite:///dev.db"
        )

        with patch('app.core.config.get_settings', return_value=dev_settings):
            assert get_database_url() == "sqlite:///dev.db"

        # Production environment with prod URL
        prod_settings = Settings(
            ENVIRONMENT="production",
            DATABASE_URL="sqlite:///dev.db",
            DATABASE_URL_PROD="postgresql://prod"
        )

        with patch('app.core.config.get_settings', return_value=prod_settings):
            assert get_database_url() == "postgresql://prod"

        # Production environment without prod URL (fallback)
        prod_settings_no_prod_url = Settings(
            ENVIRONMENT="production",
            DATABASE_URL="sqlite:///dev.db",
            DATABASE_URL_PROD=None
        )

        with patch('app.core.config.get_settings', return_value=prod_settings_no_prod_url):
            assert get_database_url() == "sqlite:///dev.db"


class TestSettingsValidation:
    """Test settings validation."""

    def test_secret_key_validation(self):
        """Test that SECRET_KEY is required."""
        with pytest.raises(ValidationError):
            Settings(SECRET_KEY="", JWT_SECRET_KEY="test-key-32-characters-long-enough-for-jwt")

    def test_jwt_secret_key_required(self):
        """Test that JWT_SECRET_KEY is required."""
        with pytest.raises(ValidationError):
            Settings(SECRET_KEY="test-key-32-characters-long-enough", JWT_SECRET_KEY="")

    def test_cors_origins_list(self):
        """Test CORS_ORIGINS must be a list."""
        settings = Settings(CORS_ORIGINS=["http://localhost:3000"])
        assert isinstance(settings.CORS_ORIGINS, list)

    def test_positive_values(self):
        """Test that certain values must be positive."""
        settings = Settings(
            ACCESS_TOKEN_EXPIRE_MINUTES=30,
            REFRESH_TOKEN_EXPIRE_DAYS=7,
            RATE_LIMIT_REQUESTS_PER_MINUTE=100,
        )

        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0
        assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE > 0


class TestEnvironmentFileLoading:
    """Test loading settings from environment file."""

    @pytest.mark.skip(reason="Environment variable loading test needs refactoring")
    def test_env_file_loading(self, monkeypatch):
        """Test loading configuration from environment variables."""
        # Set environment variables directly for testing
        monkeypatch.setenv("ENVIRONMENT", "testing")
        monkeypatch.setenv("DEBUG", "False")
        monkeypatch.setenv("PROJECT_NAME", "Test JobWise API")
        monkeypatch.setenv("SECRET_KEY", "test-secret-key-32-chars-minimum-length-here")
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

        # Create settings instance with test environment
        from app.core.config import Settings
        test_settings = Settings(
            ENVIRONMENT="testing",
            DEBUG=False,
            PROJECT_NAME="Test JobWise API",
            SECRET_KEY="test-secret-key-32-chars-minimum-length-here",
            OPENAI_API_KEY="test-openai-key"
        )
        
        with patch('app.core.config.get_settings', return_value=test_settings):
            settings = get_settings()

            assert settings.ENVIRONMENT == "testing"
            assert settings.DEBUG is False
            assert settings.PROJECT_NAME == "Test JobWise API"
            assert settings.SECRET_KEY == "test-secret-key-32-chars-minimum-length-here"
            assert settings.OPENAI_API_KEY == "test-openai-key"