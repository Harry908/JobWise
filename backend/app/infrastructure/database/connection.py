"""Database connection and utilities."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.config import get_settings


def get_database_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    return settings.database_url


def create_engine():
    """Create database engine."""
    database_url = get_database_url()
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
    )


def create_session_factory(engine):
    """Create session factory."""
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_db_session():
    """Dependency to get database session."""
    engine = create_engine()
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        try:
            yield session
        finally:
            pass  # Session automatically closed by async context manager
    
    await engine.dispose()


# Alias for compatibility
get_session = get_db_session


async def check_database_health() -> bool:
    """Check database connectivity."""
    try:
        engine = create_engine()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return True
    except Exception:
        return False


async def get_database_info() -> dict:
    """Get database information."""
    return {"status": "connected", "type": "sqlite"}