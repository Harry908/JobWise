import asyncio
from uuid import uuid4
from datetime import datetime

import pytest

from app.infrastructure.database.connection import (
    initialize_database,
    create_database_tables,
    get_database_session,
)
from app.infrastructure.repositories.job_description_repository import JobDescriptionRepository
from app.domain.entities.job_description import JobDescription, JobDescriptionMetadata, JobDescriptionSource


@pytest.mark.asyncio
async def test_job_description_repository_crud(tmp_path):
    # initialize database and create tables
    initialize_database()
    await create_database_tables()

    # open a session
    async with get_database_session() as session:
        repo = JobDescriptionRepository(session)

        user_id = uuid4()

        # Create
        jd = JobDescription.create(
            user_id=user_id,
            title="Test Job",
            company="TestCorp",
            description="A test job description",
            requirements=["python", "pytest"],
            benefits=["health"],
            source=JobDescriptionSource.MANUAL,
            metadata=JobDescriptionMetadata.create_empty(),
        )

        created = await repo.create(jd)
        assert created.id == jd.id
        assert created.created_at is not None

        # Get by id
        fetched = await repo.get_by_id(jd.id)
        assert fetched is not None
        assert fetched.title == "Test Job"

        # Count by user
        count = await repo.count_by_user_id(user_id)
        assert count == 1

        # Search
        results = await repo.search_by_user_id(user_id, query="Test")
        assert any(r.id == jd.id for r in results)

        # Update
        jd.title = "Updated Test Job"
        updated = await repo.update(jd)
        assert updated.title == "Updated Test Job"

        # Delete
        ok = await repo.delete(jd.id)
        assert ok is True

        # Ensure gone
        none = await repo.get_by_id(jd.id)
        assert none is None
