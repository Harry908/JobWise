#!/usr/bin/env python3
"""Database initialization script using the complete schema."""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Add the alembic directory to the Python path for schema import
alembic_dir = backend_dir / "alembic"
sys.path.insert(0, str(alembic_dir))

from sqlalchemy.ext.asyncio import create_async_engine
from schema import metadata, create_performance_indexes


async def init_database():
    """Initialize the database with the complete schema."""
    # Database URL from alembic.ini
    database_url = "sqlite+aiosqlite:///./jobwise.db"

    print("Creating database engine...")
    engine = create_async_engine(database_url, echo=True)

    try:
        print("Creating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        print("Creating performance indexes...")
        # Create a sync engine for the performance indexes function
        from sqlalchemy import create_engine
        sync_engine = create_engine("sqlite:///./jobwise.db")
        create_performance_indexes(sync_engine)
        sync_engine.dispose()

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("Initializing JobWise database with complete schema...")
    asyncio.run(init_database())