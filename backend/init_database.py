"""Initialize database and create tables."""

import asyncio
from app.infrastructure.database.connection import create_engine
from app.infrastructure.database.models import Base


async def init_database():
    """Initialize database and create all tables."""
    engine = create_engine()

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()
    print("Database initialized successfully")


if __name__ == "__main__":
    asyncio.run(init_database())