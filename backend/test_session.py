import pytest
from app.infrastructure.database.connection import initialize_database, get_database_session

@pytest.fixture(scope="function")
async def db_session():
    """Provide a database session for tests."""
    initialize_database()

    async with get_database_session() as session:
        yield session