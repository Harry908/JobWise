"""
Pytest configuration and fixtures for JobWise backend tests.
"""
import asyncio
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings
from app.infrastructure.database.connection import get_database_session_dependency
from app.main import app


# Test settings override
test_settings = Settings(
    ENVIRONMENT="testing",
    DATABASE_URL="sqlite+aiosqlite:///./test_jobwise.db",
    SECRET_KEY="test-secret-key-for-testing-purposes-only",
    OPENAI_API_KEY="test-openai-key",
    DEBUG=True,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI application."""
    return app


@pytest.fixture(scope="session")
def client(test_app) -> TestClient:
    """Create test client for API testing."""
    return TestClient(test_app)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    from app.infrastructure.database.models import Base
    import asyncio
    asyncio.run(create_tables(engine))

    yield engine

    # Drop all tables and dispose engine
    import asyncio
    asyncio.run(drop_tables(engine))
    asyncio.run(engine.dispose())


async def create_tables(engine):
    """Create all tables."""
    from app.infrastructure.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine):
    """Drop all tables."""
    from app.infrastructure.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def db_session(test_db_engine):
    """Create test database session."""
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    session = async_session()
    yield session
    # Note: We can't await close() in a sync fixture, but that's ok for testing


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    original_env = os.environ.copy()

    # Set test environment variables
    test_env = {
        "ENVIRONMENT": "testing",
        "DATABASE_URL": "sqlite+aiosqlite:///./test_jobwise.db",
        "SECRET_KEY": "test-secret-key-for-testing-purposes-only",
        "OPENAI_API_KEY": "test-openai-key",
        "DEBUG": "true",
        "PROJECT_NAME": "JobWise Test API",
        "API_V1_PREFIX": "/api/v1",
    }

    os.environ.update(test_env)
    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "location": "Seattle, WA",
            "linkedin_url": "https://linkedin.com/in/johndoe",
        },
        "experience": [
            {
                "company": "Tech Corp",
                "position": "Software Engineer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "description": "Developed web applications using Python and React",
                "technologies": ["Python", "FastAPI", "React", "PostgreSQL"],
            }
        ],
        "education": [
            {
                "institution": "University of Washington",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "graduation_year": 2020,
                "gpa": 3.8,
            }
        ],
        "skills": [
            {"name": "Python", "level": "Expert", "years_experience": 4},
            {"name": "FastAPI", "level": "Advanced", "years_experience": 2},
            {"name": "React", "level": "Intermediate", "years_experience": 2},
        ],
    }


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Senior Python Developer",
        "company": "Tech Startup Inc.",
        "location": "Seattle, WA",
        "description": "We are looking for a Senior Python Developer to join our team...",
        "requirements": [
            "5+ years Python experience",
            "Experience with FastAPI or Django",
            "Knowledge of PostgreSQL",
            "Experience with AWS",
        ],
        "salary_range": {
            "min": 120000,
            "max": 180000,
            "currency": "USD",
        },
        "job_type": "full-time",
        "experience_level": "senior",
        "application_url": "https://example.com/jobs/123",
        "posted_date": "2024-01-15",
    }


# Custom pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ai: mark test as requiring AI services"
    )