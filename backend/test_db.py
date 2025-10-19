import asyncio
from app.infrastructure.database.connection import get_database_session, create_database_tables

async def test_db():
    try:
        await create_database_tables()
        async with get_database_session() as session:
            result = await session.execute('SELECT 1')
            print('Database works:', result.scalar())
    except Exception as e:
        print('Database error:', e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())