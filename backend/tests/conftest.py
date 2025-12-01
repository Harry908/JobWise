"""Test configuration and fixtures for authentication API tests."""

import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.infrastructure.database.connection import get_database_url, get_db_session
from app.infrastructure.database.models import Base
from app.main import app


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database(request):
    """Setup test database before each test."""
    # Skip database setup for live tests that connect to external server
    if "live" in request.node.name or "Live" in str(request.cls):
        yield
        return

    # Remove existing test database
    db_path = "test.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create fresh database and tables
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    
    yield
    
    # Cleanup after test
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except:
            pass  # Ignore cleanup errors


async def override_get_db_session():
    """Override database session to use test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with session_factory() as session:
        try:
            yield session
        finally:
            pass
    
    await engine.dispose()


@pytest_asyncio.fixture
async def client():
    """Create test HTTP client with test database."""
    # Override the database dependency
    app.dependency_overrides[get_db_session] = override_get_db_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    """Create async database session for testing."""
    from sqlalchemy.ext.asyncio import async_sessionmaker
    
    database_url = get_database_url()
    engine = create_async_engine(database_url, echo=False, future=True)
    
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_factory() as session:
        yield session
    
    await engine.dispose()


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