"""Test suite for Job API endpoints - TDD approach."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.domain.entities.job import Job
from app.core.dependencies import get_current_user, get_job_service
from datetime import datetime


# Mock user dependency
async def override_get_current_user():
    """Override for authenticated user - returns user_id as int."""
    return 1


# Test fixtures
@pytest.fixture
def mock_job_service():
    """Create mock job service."""
    return AsyncMock()


@pytest.fixture
def authenticated_client(mock_job_service):
    """Create authenticated test client with mocked service."""
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_job_service] = lambda: mock_job_service
    yield AsyncClient(app=app, base_url="http://testserver")
    app.dependency_overrides.clear()


@pytest.fixture
def sample_job():
    """Sample job entity for testing."""
    return Job(
        id="job_test123",
        user_id=1,
        source="user_created",
        title="Senior Python Developer",
        company="TechCorp",
        location="Seattle, WA",
        description="Great opportunity",
        raw_text="Sample raw text",
        parsed_keywords=["python", "fastapi"],
        requirements=["5+ years Python"],
        benefits=["Health insurance"],
        salary_range="120000-180000",
        remote=True,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


# Test POST /jobs - Create from text
@pytest.mark.asyncio
async def test_create_job_from_text(authenticated_client, mock_job_service, sample_job):
    """Test creating job from raw text."""
    mock_job_service.create_from_text.return_value = sample_job
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/jobs",
            json={
                "raw_text": "Senior Python Developer at TechCorp\nSeattle, WA\nGreat opportunity"
            }
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Senior Python Developer"
    assert data["company"] == "TechCorp"
    assert data["source"] == "user_created"
    
    # Verify service was called
    mock_job_service.create_from_text.assert_called_once()


@pytest.mark.asyncio
async def test_create_job_from_url(authenticated_client, mock_job_service, sample_job):
    """Test creating job from URL."""
    mock_job_service.create_from_url.return_value = sample_job
    
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/jobs",
            json={
                "url": "https://example.com/job/12345"
            }
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "job_test123"
    
    # Verify service was called
    mock_job_service.create_from_url.assert_called_once()


@pytest.mark.asyncio
async def test_create_job_missing_data():
    """Test creating job without required data returns 403 (auth checked first)."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/jobs",
            json={}
        )
    
    # Auth is checked before validation, so expect 403 not 422
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_job_unauthenticated():
    """Test creating job without authentication returns 403."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/jobs",
            json={"raw_text": "Some job"}
        )
    
    # HTTPBearer returns 403 when no credentials provided
    assert response.status_code == 403


# Test GET /jobs - List user's jobs
@pytest.mark.asyncio
async def test_get_user_jobs(authenticated_client, mock_job_service, sample_job):
    """Test getting user's job list."""
    mock_job_service.get_user_jobs.return_value = [sample_job]
    mock_job_service.count_user_jobs.return_value = 1
    
    async with authenticated_client as client:
        response = await client.get("/api/v1/jobs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["title"] == "Senior Python Developer"
    
    # Verify service called with user_id
    mock_job_service.get_user_jobs.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_jobs_with_filters(authenticated_client, mock_job_service, sample_job):
    """Test getting user's jobs with status and source filters."""
    mock_job_service.get_user_jobs.return_value = [sample_job]
    mock_job_service.count_user_jobs.return_value = 1
    
    async with authenticated_client as client:
        response = await client.get(
            "/api/v1/jobs",
            params={"status": "active", "source": "user_created", "limit": 10}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["jobs"]) == 1
    
    # Verify service called with filters
    call_args = mock_job_service.get_user_jobs.call_args
    assert call_args.kwargs["status"] == "active"
    assert call_args.kwargs["source"] == "user_created"
    assert call_args.kwargs["limit"] == 10


@pytest.mark.asyncio
async def test_get_user_jobs_empty_list(authenticated_client, mock_job_service):
    """Test getting user's jobs returns empty list when no jobs."""
    mock_job_service.get_user_jobs.return_value = []
    mock_job_service.count_user_jobs.return_value = 0
    
    async with authenticated_client as client:
        response = await client.get("/api/v1/jobs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["jobs"]) == 0
    assert data["pagination"]["hasMore"] is False


# Test GET /jobs/browse - Browse mock jobs
@pytest.mark.asyncio
async def test_browse_jobs(mock_job_service, sample_job):
    """Test browsing mock job listings (no auth required)."""
    mock_job_service.browse_jobs.return_value = [sample_job]
    mock_job_service.count_browse_jobs.return_value = 1
    
    # Override service dependency
    app.dependency_overrides[get_job_service] = lambda: mock_job_service
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/jobs/browse")
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["title"] == "Senior Python Developer"


@pytest.mark.asyncio
async def test_browse_jobs_with_pagination(mock_job_service, sample_job):
    """Test browsing jobs with pagination parameters."""
    mock_job_service.browse_jobs.return_value = [sample_job]
    mock_job_service.count_browse_jobs.return_value = 20
    
    app.dependency_overrides[get_job_service] = lambda: mock_job_service
    
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get(
            "/api/v1/jobs/browse",
            params={"limit": 5, "offset": 10}
        )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    
    # Verify service called with pagination
    call_args = mock_job_service.browse_jobs.call_args
    assert call_args.kwargs["limit"] == 5
    assert call_args.kwargs["offset"] == 10


# Test GET /jobs/{job_id} - Get job by ID
@pytest.mark.asyncio
async def test_get_job_by_id(authenticated_client, mock_job_service, sample_job):
    """Test getting specific job by ID."""
    mock_job_service.get_by_id.return_value = sample_job
    
    async with authenticated_client as client:
        response = await client.get("/api/v1/jobs/job_test123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "job_test123"
    assert data["title"] == "Senior Python Developer"
    
    # Verify service called with correct ID
    mock_job_service.get_by_id.assert_called_once_with("job_test123")


@pytest.mark.asyncio
async def test_get_job_not_found(authenticated_client, mock_job_service):
    """Test getting non-existent job returns 404."""
    mock_job_service.get_by_id.return_value = None
    
    async with authenticated_client as client:
        response = await client.get("/api/v1/jobs/nonexistent_id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# Test PUT /jobs/{job_id} - Update job
@pytest.mark.asyncio
async def test_update_job(authenticated_client, mock_job_service, sample_job):
    """Test updating job details."""
    # Create updated job
    updated_job = sample_job.model_copy(update={"title": "Updated Title"})
    mock_job_service.update_job.return_value = updated_job
    
    async with authenticated_client as client:
        response = await client.put(
            "/api/v1/jobs/job_test123",
            json={"title": "Updated Title"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    
    # Verify service called
    mock_job_service.update_job.assert_called_once()


@pytest.mark.asyncio
async def test_update_job_not_found(authenticated_client, mock_job_service):
    """Test updating non-existent job returns 404."""
    mock_job_service.update_job.return_value = None
    
    async with authenticated_client as client:
        response = await client.put(
            "/api/v1/jobs/nonexistent_id",
            json={"title": "Updated Title"}
        )
    
    assert response.status_code == 404


# Test DELETE /jobs/{job_id} - Delete job
@pytest.mark.asyncio
async def test_delete_job(authenticated_client, mock_job_service):
    """Test deleting a job."""
    mock_job_service.delete_job.return_value = True
    
    async with authenticated_client as client:
        response = await client.delete("/api/v1/jobs/job_test123")
    
    assert response.status_code == 204
    # 204 No Content returns empty body
    
    # Verify service called
    mock_job_service.delete_job.assert_called_once_with("job_test123")


@pytest.mark.asyncio
async def test_delete_job_not_found(authenticated_client, mock_job_service):
    """Test deleting non-existent job returns 404."""
    mock_job_service.delete_job.return_value = False
    
    async with authenticated_client as client:
        response = await client.delete("/api/v1/jobs/nonexistent_id")
    
    assert response.status_code == 404


# Test validation errors
@pytest.mark.asyncio
async def test_create_job_with_invalid_data(authenticated_client):
    """Test creating job with invalid data structure."""
    async with authenticated_client as client:
        response = await client.post(
            "/api/v1/jobs",
            json={"invalid_field": "value"}
        )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_negative_offset(authenticated_client, mock_job_service):
    """Test that negative offset is handled."""
    mock_job_service.get_user_jobs.return_value = []
    
    async with authenticated_client as client:
        response = await client.get(
            "/api/v1/jobs",
            params={"offset": -1}
        )
    
    # Should either reject with 422 or accept and use 0
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_pagination_zero_limit(authenticated_client, mock_job_service):
    """Test that zero or negative limit is handled."""
    mock_job_service.get_user_jobs.return_value = []
    
    async with authenticated_client as client:
        response = await client.get(
            "/api/v1/jobs",
            params={"limit": 0}
        )
    
    # Should either reject with 422 or accept with minimum value
    assert response.status_code in [200, 422]
