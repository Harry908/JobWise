"""Test configuration and fixtures for authentication API tests."""

import os
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings
from app.infrastructure.database.connection import get_database_url
from app.infrastructure.database.models import Base
from app.main import app


@pytest.fixture(autouse=True)
def setup_database(request):
    """Setup database before each test."""
    import asyncio
    import os
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.core.config import get_settings
    from app.infrastructure.database.connection import get_database_url
    from app.infrastructure.database.models import Base

    # Skip database setup for live tests that connect to external server
    if "live" in request.node.name or "Live" in str(request.cls):
        return

    db_path = "test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Recreate database and tables
    settings = get_settings()
    database_url = get_database_url()

    async def create_tables():
        engine = create_async_engine(database_url, echo=False, future=True)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(create_tables())


@pytest.fixture
def client():
    """Create test HTTP client."""
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.fixture
def test_user_data():
    """Test user data for registration."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user_data_2():
    """Second test user data."""
    return {
        "email": "test2@example.com",
        "password": "SecurePass456!",
        "full_name": "Test User 2"
    }


@pytest.fixture
def weak_password_data():
    """Test data with weak password."""
    return {
        "email": "weak@example.com",
        "password": "123",
        "full_name": "Weak User"
    }


@pytest.fixture
def invalid_email_data():
    """Test data with invalid email."""
    return {
        "email": "invalid-email",
        "password": "SecurePass123!",
        "full_name": "Invalid Email User"
    }