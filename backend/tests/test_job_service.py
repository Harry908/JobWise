"""Test suite for JobService - TDD approach."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.job_service import JobService
from app.domain.entities.job import Job
from app.infrastructure.repositories.job_repository import JobRepository


@pytest.fixture
def mock_repository():
    """Create mock job repository."""
    return AsyncMock(spec=JobRepository)


@pytest.fixture
def job_service(mock_repository):
    """Create job service with mock repository."""
    return JobService(mock_repository)


@pytest.mark.asyncio
async def test_create_job_from_text_parsing(job_service, mock_repository):
    """Test creating job by parsing raw text."""
    raw_text = """
    Senior Python Backend Developer
    TechCorp Inc.
    Seattle, WA (Remote)
    
    We are looking for a skilled Python developer with FastAPI experience.
    Requirements: 5+ years Python, AWS, Docker
    Salary: $120,000 - $180,000
    Benefits: Health insurance, 401k, Remote work
    """
    
    # Mock repository create method
    mock_repository.create.return_value = Job(
        id="job_test123",
        user_id=1,
        source="user_created",
        title="Senior Python Backend Developer",
        company="TechCorp Inc.",
        location="Seattle, WA",
        description="We are looking for a skilled Python developer with FastAPI experience.",
        raw_text=raw_text,
        parsed_keywords=["python", "fastapi", "aws", "docker"],
        requirements=["5+ years Python", "AWS", "Docker"],
        benefits=["Health insurance", "401k", "Remote work"],
        salary_range="120000-180000",
        remote=True,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Call service method
    result = await job_service.create_from_text(
        user_id=1,
        raw_text=raw_text
    )
    
    # Assertions
    assert result.title == "Senior Python Backend Developer"
    assert result.company == "TechCorp Inc."
    assert result.location == "Seattle, WA"
    assert "python" in result.parsed_keywords
    assert result.remote is True
    assert result.source == "user_created"
    
    # Verify repository was called
    mock_repository.create.assert_called_once()
    call_args = mock_repository.create.call_args[0][0]
    assert call_args["user_id"] == 1
    assert "parsed_keywords" in call_args


@pytest.mark.asyncio
async def test_create_job_from_url(job_service, mock_repository):
    """Test creating job by parsing from URL."""
    test_url = "https://example.com/job/12345"
    
    with patch("app.application.services.job_service.JobService._fetch_job_from_url") as mock_fetch:
        # Mock URL fetch
        mock_fetch.return_value = {
            "title": "Full Stack Engineer",
            "company": "StartupCo",
            "location": "San Francisco, CA",
            "description": "Build amazing products",
            "requirements": ["React", "Node.js"],
            "remote": False
        }
        
        # Mock repository create
        mock_repository.create.return_value = Job(
            id="job_url123",
            user_id=1,
            source="url_import",
            title="Full Stack Engineer",
            company="StartupCo",
            location="San Francisco, CA",
            description="Build amazing products",
            raw_text=test_url,
            parsed_keywords=["react", "node.js"],
            requirements=["React", "Node.js"],
            benefits=[],
            salary_range=None,
            remote=False,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Call service
        result = await job_service.create_from_url(
            user_id=1,
            url=test_url
        )
        
        # Assertions
        assert result.source == "url_import"
        assert result.title == "Full Stack Engineer"
        assert result.company == "StartupCo"
        mock_fetch.assert_called_once_with(test_url)


@pytest.mark.asyncio
async def test_get_user_jobs_with_filters(job_service, mock_repository):
    """Test getting user jobs with status and source filters."""
    user_id = 1
    
    # Mock repository response
    mock_repository.get_user_jobs.return_value = [
        Job(
            id="job_1",
            user_id=user_id,
            source="user_created",
            title="Job 1",
            company="Company 1",
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    # Call service
    results = await job_service.get_user_jobs(
        user_id=user_id,
        status="active",
        source="user_created"
    )
    
    # Assertions
    assert len(results) == 1
    assert results[0].status == "active"
    
    # Verify repository called with correct params
    mock_repository.get_user_jobs.assert_called_once_with(
        user_id=user_id,
        status="active",
        source="user_created",
        limit=20,
        offset=0
    )


@pytest.mark.asyncio
async def test_browse_mock_jobs(job_service):
    """Test browsing mock job listings from JSON file."""
    # Call service method
    results = await job_service.browse_jobs(
        limit=5,
        offset=0
    )
    
    # Assertions
    assert len(results) <= 5
    assert all(hasattr(job, "title") for job in results)
    assert all(hasattr(job, "company") for job in results)
    assert all(hasattr(job, "description") for job in results)


@pytest.mark.asyncio
async def test_browse_jobs_pagination(job_service):
    """Test browsing jobs with pagination."""
    # First page
    page1 = await job_service.browse_jobs(limit=10, offset=0)
    
    # Second page
    page2 = await job_service.browse_jobs(limit=10, offset=10)
    
    # Assertions
    assert len(page1) <= 10
    assert len(page2) <= 10
    
    # Ensure different results (if enough data)
    if len(page1) == 10 and len(page2) > 0:
        page1_ids = {job.id for job in page1}
        page2_ids = {job.id for job in page2}
        assert page1_ids != page2_ids


@pytest.mark.asyncio
async def test_parse_keywords_from_text(job_service):
    """Test extracting keywords from job text."""
    text = """
    Looking for Python Developer with FastAPI, AWS, Docker experience.
    Must know PostgreSQL, Redis, and CI/CD pipelines.
    """
    
    keywords = await job_service._parse_keywords(text)
    
    # Assertions
    assert isinstance(keywords, list)
    assert "python" in keywords
    assert "fastapi" in keywords
    assert "aws" in keywords
    assert "docker" in keywords
    assert "postgresql" in keywords


@pytest.mark.asyncio
async def test_extract_salary_range(job_service):
    """Test extracting salary range from text."""
    text1 = "Salary: $120,000 - $180,000"
    text2 = "Compensation: 100k-150k"
    text3 = "No salary mentioned"
    
    salary1 = await job_service._extract_salary(text1)
    salary2 = await job_service._extract_salary(text2)
    salary3 = await job_service._extract_salary(text3)
    
    # Assertions
    assert salary1 == "120000-180000"
    assert salary2 == "100000-150000"
    assert salary3 is None


@pytest.mark.asyncio
async def test_detect_remote_work(job_service):
    """Test detecting remote work option from text."""
    remote_text = "This is a remote position"
    hybrid_text = "Hybrid work available"
    onsite_text = "Must be onsite in Seattle"
    
    is_remote1 = await job_service._detect_remote(remote_text)
    is_remote2 = await job_service._detect_remote(hybrid_text)
    is_remote3 = await job_service._detect_remote(onsite_text)
    
    # Assertions
    assert is_remote1 is True
    assert is_remote2 is True
    assert is_remote3 is False


@pytest.mark.asyncio
async def test_update_job(job_service, mock_repository):
    """Test updating job details."""
    job_id = "job_123"
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    
    # Mock repository response
    mock_repository.update.return_value = Job(
        id=job_id,
        user_id=1,
        source="user_created",
        title="Updated Title",
        company="Company",
        description="Updated description",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Call service
    result = await job_service.update_job(job_id, **update_data)
    
    # Assertions
    assert result.title == "Updated Title"
    assert result.description == "Updated description"
    mock_repository.update.assert_called_once_with(job_id, **update_data)


@pytest.mark.asyncio
async def test_delete_job(job_service, mock_repository):
    """Test deleting a job."""
    job_id = "job_123"
    
    # Mock repository response
    mock_repository.delete.return_value = True
    
    # Call service
    result = await job_service.delete_job(job_id)
    
    # Assertions
    assert result is True
    mock_repository.delete.assert_called_once_with(job_id)


@pytest.mark.asyncio
async def test_get_job_by_id(job_service, mock_repository):
    """Test getting job by ID."""
    job_id = "job_123"
    
    # Mock repository response
    mock_repository.get_by_id.return_value = Job(
        id=job_id,
        user_id=1,
        source="user_created",
        title="Test Job",
        company="Test Company",
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Call service
    result = await job_service.get_by_id(job_id)
    
    # Assertions
    assert result is not None
    assert result.id == job_id
    assert result.title == "Test Job"
    mock_repository.get_by_id.assert_called_once_with(job_id)
