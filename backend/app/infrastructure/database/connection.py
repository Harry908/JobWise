"""Database connection and session management."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy import event, text
from sqlalchemy.pool import StaticPool

from ...core.config import get_settings
from ...core.logging import get_logger

logger = get_logger(__name__)

# Global engine instance
engine: AsyncEngine = None
async_session_factory: async_sessionmaker[AsyncSession] = None


def create_engine() -> AsyncEngine:
    """Create async database engine with proper configuration."""
    settings = get_settings()
    database_url = settings.DATABASE_URL
    
    # Configure engine options based on database type
    engine_kwargs = {
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
        "future": True,
        "pool_pre_ping": True,  # Validate connections before use
    }
    
    # SQLite specific configuration
    if "sqlite" in database_url:
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {
                "check_same_thread": False,
                "timeout": 20,
            }
        })
    
    # PostgreSQL specific configuration  
    elif "postgresql" in database_url:
        engine_kwargs.update({
            "pool_size": 20,
            "max_overflow": 0,
            "pool_timeout": 30,
            "pool_recycle": 3600,  # Recycle connections every hour
        })
    
    return create_async_engine(database_url, **engine_kwargs)


def initialize_database() -> None:
    """Initialize database engine and session factory."""
    global engine, async_session_factory
    
    if engine is None:
        engine = create_engine()
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )
        
        # Add connection pool logging for debugging
        @event.listens_for(engine.sync_engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            logger.info("Database connection established")
            
        @event.listens_for(engine.sync_engine, "close")  
        def receive_close(dbapi_connection, connection_record):
            logger.info("Database connection closed")


@asynccontextmanager
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_database_session() as session:
            result = await session.execute(query)
            await session.commit()
    """
    if async_session_factory is None:
        initialize_database()
        
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_database_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in FastAPI endpoints:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_database_session_dependency)):
            ...
    """
    async with get_database_session() as session:
        yield session


async def create_database_tables() -> None:
    """Create all database tables."""
    from .models import Base
    
    if engine is None:
        initialize_database()
        
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from . import models  # noqa: F401
        
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def drop_database_tables() -> None:
    """Drop all database tables (use with caution!)."""
    from .models import Base
    
    if engine is None:
        initialize_database()
        
    async with engine.begin() as conn:
        logger.warning("Dropping all database tables...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.warning("All database tables dropped")


async def close_database_connections() -> None:
    """Close all database connections."""
    global engine, async_session_factory
    
    if engine is not None:
        logger.info("Closing database connections...")
        await engine.dispose()
        engine = None
        async_session_factory = None
        logger.info("Database connections closed")


# Health check functions
async def check_database_health() -> bool:
    """Check if database is accessible and healthy."""
    try:
        async with get_database_session() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_database_info() -> dict:
    """Get database connection information."""
    if engine is None:
        return {"status": "not_initialized"}
        
    pool = engine.pool
    return {
        "status": "connected",
        "database_url": str(engine.url).split("@")[-1],  # Hide credentials
        "pool_size": getattr(pool, "size", "unknown"),
        "checked_out_connections": getattr(pool, "checkedout", "unknown"),
        "overflow": getattr(pool, "overflow", "unknown"),
    }


# Migration helper functions
async def run_migrations() -> None:
    """Run database migrations using Alembic."""
    from alembic import command
    from alembic.config import Config
    
    logger.info("Running database migrations...")
    
    # Configure Alembic
    alembic_cfg = Config("alembic.ini")
    
    # Run migrations in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: command.upgrade(alembic_cfg, "head")
    )
    
    logger.info("Database migrations completed")


# Backup functions (for SQLite)
async def backup_database(backup_path: str) -> None:
    """Create a backup of the database (SQLite only)."""
    import shutil
    from pathlib import Path
    
    settings = get_settings()
    
    if "sqlite" not in settings.DATABASE_URL:
        raise ValueError("Backup is only supported for SQLite databases")
        
    # Extract database file path from URL
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    
    if Path(db_path).exists():
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backup created at {backup_path}")
    else:
        raise FileNotFoundError(f"Database file not found: {db_path}")


# Initialize on module import
initialize_database()