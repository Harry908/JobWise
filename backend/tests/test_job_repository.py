"""Tests for Job repository."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.job_repository import JobRepository
from app.domain.entities.job import Job


@pytest.mark.asyncio
async def test_create_job(db_session: AsyncSession):
    """Test creating a job."""
    repo = JobRepository(db_session)
    
    job_data = {
        "user_id": 1,
        "source": "user_created",
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "Seattle, WA",
        "description": "We are looking for a skilled Python developer...",
        "raw_text": "Senior Python Developer at Tech Corp...",
        "parsed_keywords": ["python", "fastapi", "aws"],
        "requirements": ["5+ years Python", "AWS experience"],
        "benefits": ["Health insurance", "Remote work"],
        "salary_range": "120000-180000",
        "remote": True,
        "status": "active"
    }
    
    job = await repo.create(job_data)
    
    assert job.id is not None
    assert job.user_id == 1
    assert job.title == "Senior Python Developer"
    assert job.company == "Tech Corp"
    assert job.source == "user_created"
    assert job.remote is True
    assert len(job.parsed_keywords) == 3
    assert len(job.requirements) == 2


@pytest.mark.asyncio
async def test_get_job_by_id(db_session: AsyncSession):
    """Test getting a job by ID."""
    repo = JobRepository(db_session)
    
    # Create a job first
    job_data = {
        "user_id": 1,
        "source": "user_created",
        "title": "Backend Developer",
        "company": "StartupCo",
        "description": "Join our team..."
    }
    created_job = await repo.create(job_data)
    
    # Retrieve it
    fetched_job = await repo.get_by_id(created_job.id)
    
    assert fetched_job is not None
    assert fetched_job.id == created_job.id
    assert fetched_job.title == "Backend Developer"
    assert fetched_job.company == "StartupCo"


@pytest.mark.asyncio
async def test_get_job_by_id_not_found(db_session: AsyncSession):
    """Test getting a non-existent job."""
    repo = JobRepository(db_session)
    
    job = await repo.get_by_id("non_existent_id")
    
    assert job is None


@pytest.mark.asyncio
async def test_get_user_jobs(db_session: AsyncSession):
    """Test getting jobs for a specific user."""
    repo = JobRepository(db_session)
    
    # Create jobs for user 1
    await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Job 1",
        "company": "Company 1"
    })
    await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Job 2",
        "company": "Company 2"
    })
    
    # Create job for user 2
    await repo.create({
        "user_id": 2,
        "source": "user_created",
        "title": "Job 3",
        "company": "Company 3"
    })
    
    # Get jobs for user 1
    jobs = await repo.get_user_jobs(user_id=1, limit=10, offset=0)
    
    assert len(jobs) == 2
    assert all(job.user_id == 1 for job in jobs)


@pytest.mark.asyncio
async def test_get_user_jobs_with_filters(db_session: AsyncSession):
    """Test getting user jobs with status and source filters."""
    repo = JobRepository(db_session)
    
    # Create jobs with different statuses
    await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Active Job",
        "company": "Company 1",
        "status": "active"
    })
    await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Archived Job",
        "company": "Company 2",
        "status": "archived"
    })
    await repo.create({
        "user_id": 1,
        "source": "mock",
        "title": "Mock Job",
        "company": "Company 3",
        "status": "active"
    })
    
    # Filter by status
    active_jobs = await repo.get_user_jobs(user_id=1, status="active")
    assert len(active_jobs) == 2
    
    # Filter by source
    user_created_jobs = await repo.get_user_jobs(user_id=1, source="user_created")
    assert len(user_created_jobs) == 2
    
    # Filter by both
    filtered_jobs = await repo.get_user_jobs(
        user_id=1,
        status="active",
        source="user_created"
    )
    assert len(filtered_jobs) == 1
    assert filtered_jobs[0].title == "Active Job"


@pytest.mark.asyncio
async def test_update_job(db_session: AsyncSession):
    """Test updating a job."""
    repo = JobRepository(db_session)
    
    # Create a job
    job = await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Original Title",
        "company": "Original Company",
        "description": "Original description"
    })
    
    # Update it
    updated_job = await repo.update(
        job_id=job.id,
        title="Updated Title",
        description="Updated description",
        remote=True
    )
    
    assert updated_job.title == "Updated Title"
    assert updated_job.description == "Updated description"
    assert updated_job.remote is True
    assert updated_job.company == "Original Company"  # Unchanged


@pytest.mark.asyncio
async def test_delete_job(db_session: AsyncSession):
    """Test deleting a job."""
    repo = JobRepository(db_session)
    
    # Create a job
    job = await repo.create({
        "user_id": 1,
        "source": "user_created",
        "title": "Job to Delete",
        "company": "Company"
    })
    
    # Delete it
    deleted = await repo.delete(job.id)
    
    assert deleted is True
    
    # Verify it's gone
    fetched_job = await repo.get_by_id(job.id)
    assert fetched_job is None


@pytest.mark.asyncio
async def test_delete_non_existent_job(db_session: AsyncSession):
    """Test deleting a non-existent job returns False."""
    repo = JobRepository(db_session)
    
    deleted = await repo.delete("non_existent_id")
    
    assert deleted is False


@pytest.mark.asyncio
async def test_pagination(db_session: AsyncSession):
    """Test pagination of user jobs."""
    repo = JobRepository(db_session)
    
    # Create 5 jobs
    for i in range(5):
        await repo.create({
            "user_id": 1,
            "source": "user_created",
            "title": f"Job {i}",
            "company": f"Company {i}"
        })
    
    # Get first page
    page1 = await repo.get_user_jobs(user_id=1, limit=2, offset=0)
    assert len(page1) == 2
    
    # Get second page
    page2 = await repo.get_user_jobs(user_id=1, limit=2, offset=2)
    assert len(page2) == 2
    
    # Get third page
    page3 = await repo.get_user_jobs(user_id=1, limit=2, offset=4)
    assert len(page3) == 1
    
    # Ensure no duplicates
    all_ids = [job.id for job in page1 + page2 + page3]
    assert len(all_ids) == len(set(all_ids))
