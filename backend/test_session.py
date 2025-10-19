import asyncio
from app.infrastructure.database.connection import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

async def test_fixture():
    test_settings = type('obj', (object,), {
        'DATABASE_URL': 'sqlite+aiosqlite:///./test_jobwise.db'
    })()

    engine = create_async_engine(test_settings.DATABASE_URL, echo=False, future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f'Session type: {type(session)}')
        print(f'Has add method: {hasattr(session, "add")}')

if __name__ == "__main__":
    asyncio.run(test_fixture())