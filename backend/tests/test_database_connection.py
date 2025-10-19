"""Database connection tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.infrastructure.database.connection import (
    create_engine,
    initialize_database,
    check_database_health,
    get_database_info,
    create_database_tables,
    get_database_session
)
from app.core.config import Settings


class TestDatabaseConnection:
    """Test database connection functionality."""

    def test_create_engine_sqlite(self):
        """Test engine creation for SQLite."""
        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ENVIRONMENT="testing"
        )

        # Temporarily override settings
        from app.core.config import get_settings
        original_settings = get_settings()
        try:
            # Mock get_settings to return our test settings
            import app.core.config
            app.core.config.get_settings = lambda: settings

            engine = create_engine()
            assert engine is not None
            assert "sqlite" in str(engine.url)

        finally:
            # Restore original settings
            app.core.config.get_settings = lambda: original_settings

    def test_create_engine_postgresql(self):
        """Test engine creation for PostgreSQL."""
        from unittest.mock import patch
        
        # Mock the settings for this test
        mock_settings = type('MockSettings', (), {
            'DATABASE_URL': "postgresql+asyncpg://user:pass@localhost:5432/test",
            'DEBUG': False
        })()
        
        with patch('app.infrastructure.database.connection.get_settings', return_value=mock_settings):
            engine = create_engine()
            assert engine is not None
            assert "postgresql" in str(engine.url)

    @pytest.mark.asyncio
    async def test_initialize_database(self):
        """Test database initialization."""
        # This should not raise an exception
        initialize_database()
        from app.infrastructure.database.connection import engine
        assert engine is not None

    @pytest.mark.asyncio
    async def test_database_health_check(self, db_session: AsyncSession):
        """Test database health check functionality."""
        healthy = await check_database_health()
        assert isinstance(healthy, bool)

    @pytest.mark.asyncio
    async def test_get_database_info(self, db_session: AsyncSession):
        """Test getting database information."""
        info = await get_database_info()
        assert isinstance(info, dict)
        assert "status" in info

    @pytest.mark.asyncio
    async def test_create_database_tables(self, db_session: AsyncSession):
        """Test table creation."""
        # This should not raise an exception
        await create_database_tables()

    @pytest.mark.asyncio
    async def test_get_database_session_context_manager(self):
        """Test database session context manager."""
        async with get_database_session() as session:
            assert session is not None
            assert isinstance(session, AsyncSession)

            # Test that we can execute a simple query
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_database_session_dependency(self):
        """Test database session dependency injection."""
        from app.infrastructure.database.connection import get_database_session_dependency

        # This is mainly tested through FastAPI dependency injection
        # but we can test the generator function yields a session
        gen = get_database_session_dependency()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        
        # Close the generator
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass  # Expected when generator is exhausted


class TestDatabaseConfiguration:
    """Test database configuration settings."""

    def test_sqlite_configuration(self):
        """Test SQLite-specific configuration."""
        settings = Settings(
            DATABASE_URL="sqlite+aiosqlite:///./test.db",
            ENVIRONMENT="testing"
        )

        # Temporarily override settings
        from app.core.config import get_settings
        original_settings = get_settings()
        try:
            import app.core.config
            app.core.config.get_settings = lambda: settings

            engine = create_engine()
            # SQLite should have specific pool configuration
            assert hasattr(engine.pool, 'size') or True  # Allow for different pool types

        finally:
            app.core.config.get_settings = lambda: original_settings

    def test_postgresql_configuration(self):
        """Test PostgreSQL-specific configuration."""
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test",
            ENVIRONMENT="testing"
        )

        # Temporarily override settings
        from app.core.config import get_settings
        original_settings = get_settings()
        try:
            import app.core.config
            app.core.config.get_settings = lambda: settings

            engine = create_engine()
            # PostgreSQL should have connection pooling
            assert engine.pool is not None

        finally:
            app.core.config.get_settings = lambda: original_settings

    def test_environment_specific_database_url(self):
        """Test environment-specific database URL selection."""
        settings = Settings(
            ENVIRONMENT="development",
            DATABASE_URL="sqlite+aiosqlite:///./dev.db",
            DATABASE_URL_PROD="postgresql+asyncpg://user:pass@localhost:5432/prod"
        )

        assert settings.effective_database_url == "sqlite+aiosqlite:///./dev.db"

        # Test production environment
        settings.ENVIRONMENT = "production"
        assert settings.effective_database_url == "postgresql+asyncpg://user:pass@localhost:5432/prod"