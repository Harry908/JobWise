"""Update database tables with sample_documents."""

import asyncio
from app.infrastructure.database.connection import create_engine
from app.infrastructure.database.models import Base


async def init_db():
    """Initialize database tables."""
    engine = create_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print('Database tables created/updated successfully')


if __name__ == "__main__":
    asyncio.run(init_db())
