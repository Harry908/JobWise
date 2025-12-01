"""Live tests for Job API with real server."""

import pytest
from httpx import AsyncClient
import asyncio


BASE_URL = "http://localhost:8000"


class TestJobAPILive:
    """Live tests for Job API endpoints."""
    
    async def get_auth_headers(self):
        """Create a test user and get auth token."""
        timestamp = asyncio.get_event_loop().time()
        async with AsyncClient(base_url=BASE_URL) as client:
            # Register a new user
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"test_{timestamp}@example.com",
                    "password": "TestPassword123!",
                    "full_name": f"Test User {timestamp}"
                }
            )
            assert register_response.status_code == 201
            data = register_response.json()
            token = data["access_token"]
            
            return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.asyncio
    async def test_create_job_from_text_auto_id(self):
        """Test creating job from text with automatic ID generation."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "raw_text": """Senior Python Developer - TechCorp Inc.

Location: Seattle, WA (Remote Available)

We are seeking an experienced Senior Python Developer to join our team.

Requirements:
- 5+ years Python experience
- FastAPI and Django expertise
- AWS cloud experience

Benefits:
- Competitive salary $120k-$150k
- Health insurance
- 401k matching"""
                }
            )
            
            assert response.status_code == 201
            job = response.json()
            
            # Verify ID was auto-generated as UUID
            assert "id" in job
            assert job["id"] is not None
            assert len(job["id"]) > 0
            assert "-" in job["id"]  # UUIDs contain hyphens
            
            # Verify parsed content
            assert job["title"] == "Senior Python Developer - TechCorp Inc."
            assert job["company"] == "Location: Seattle, WA (Remote Available)"
            assert job["source"] == "user_created"
            assert "python" in job["parsed_keywords"]  # Keywords are lowercase
            assert "fastapi" in job["parsed_keywords"]
            
            print(f"✅ Created job with auto-generated ID: {job['id']}")
            return job["id"]
    
    @pytest.mark.asyncio
    async def test_create_job_structured_auto_id(self):
        """Test creating job with structured data - ID should be auto-generated."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "source": "user_created",
                    "title": "Backend Developer",
                    "company": "Startup Inc",
                    "location": "San Francisco, CA",
                    "description": "Join our fast-growing startup",
                    "requirements": ["3+ years experience", "Node.js expertise"],
                    "benefits": ["Stock options", "Remote work"],
                    "salary_range": "$100k-$140k",
                    "remote": True,
                    "employment_type": "full_time"
                }
            )
            
            assert response.status_code == 201
            job = response.json()
            
            # Verify ID was auto-generated
            assert "id" in job
            assert job["id"] is not None
            assert len(job["id"]) > 0
            assert "-" in job["id"]  # UUIDs contain hyphens
            
            # Verify data
            assert job["title"] == "Backend Developer"
            assert job["company"] == "Startup Inc"
            assert job["remote"] is True
            
            print(f"✅ Created structured job with auto-generated ID: {job['id']}")
            return job["id"]
    
    @pytest.mark.asyncio
    async def test_get_user_jobs(self):
        """Test retrieving user's jobs."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create a job first
            create_response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "source": "user_created",
                    "title": "Frontend Developer",
                    "company": "WebCorp",
                    "location": "Remote"
                }
            )
            assert create_response.status_code == 201
            created_job = create_response.json()
            
            # Get user's jobs
            list_response = await client.get(
                "/api/v1/jobs",
                headers=auth_headers
            )
            
            assert list_response.status_code == 200
            data = list_response.json()
            
            assert "jobs" in data
            assert "total" in data
            assert "pagination" in data
            assert len(data["jobs"]) > 0
            
            # Verify our created job is in the list
            job_ids = [j["id"] for j in data["jobs"]]
            assert created_job["id"] in job_ids
            
            print(f"✅ Retrieved {len(data['jobs'])} jobs for user")
    
    @pytest.mark.asyncio
    async def test_get_job_by_id(self):
        """Test retrieving specific job by ID."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create a job
            create_response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "source": "user_created",
                    "title": "DevOps Engineer",
                    "company": "CloudTech",
                    "location": "New York, NY"
                }
            )
            assert create_response.status_code == 201
            job_id = create_response.json()["id"]
            
            # Get job by ID
            get_response = await client.get(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers
            )
            
            assert get_response.status_code == 200
            job = get_response.json()
            
            assert job["id"] == job_id
            assert job["title"] == "DevOps Engineer"
            assert job["company"] == "CloudTech"
            
            print(f"✅ Retrieved job by ID: {job_id}")
    
    @pytest.mark.asyncio
    async def test_update_job(self):
        """Test updating job details."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create a job
            create_response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "source": "user_created",
                    "title": "Data Scientist",
                    "company": "DataCorp",
                    "location": "Boston, MA"
                }
            )
            assert create_response.status_code == 201
            job_id = create_response.json()["id"]
            
            # Update job
            update_response = await client.put(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers,
                json={
                    "title": "Senior Data Scientist",
                    "application_status": "applied"
                }
            )
            
            assert update_response.status_code == 200
            updated_job = update_response.json()
            
            assert updated_job["id"] == job_id  # ID should remain the same
            assert updated_job["title"] == "Senior Data Scientist"
            assert updated_job["application_status"] == "applied"
            
            print(f"✅ Updated job {job_id}")
    
    @pytest.mark.asyncio
    async def test_delete_job(self):
        """Test deleting a job."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            # Create a job
            create_response = await client.post(
                "/api/v1/jobs",
                headers=auth_headers,
                json={
                    "source": "user_created",
                    "title": "QA Engineer",
                    "company": "TestCorp",
                    "location": "Austin, TX"
                }
            )
            assert create_response.status_code == 201
            job_id = create_response.json()["id"]
            
            # Delete job
            delete_response = await client.delete(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers
            )
            
            assert delete_response.status_code == 204
            
            # Verify job is deleted
            get_response = await client.get(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers
            )
            assert get_response.status_code == 404
            
            print(f"✅ Deleted job {job_id}")
    
    @pytest.mark.asyncio
    async def test_browse_jobs_no_auth(self):
        """Test browsing mock jobs without authentication."""
        async with AsyncClient(base_url=BASE_URL) as client:
            response = await client.get("/api/v1/jobs/browse")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "jobs" in data
            assert "total" in data
            assert "pagination" in data
            
            # Mock jobs should have UUIDs
            if len(data["jobs"]) > 0:
                job = data["jobs"][0]
                assert "id" in job
                assert job["id"] is not None
            
            print(f"✅ Browse jobs returned {len(data['jobs'])} mock jobs")
    
    @pytest.mark.asyncio
    async def test_multiple_jobs_unique_ids(self):
        """Test that multiple jobs get unique auto-generated IDs."""
        auth_headers = await self.get_auth_headers()
        async with AsyncClient(base_url=BASE_URL) as client:
            job_ids = []
            
            # Create 5 jobs
            for i in range(5):
                response = await client.post(
                    "/api/v1/jobs",
                    headers=auth_headers,
                    json={
                        "source": "user_created",
                        "title": f"Job {i}",
                        "company": f"Company {i}",
                        "location": "Remote"
                    }
                )
                assert response.status_code == 201
                job = response.json()
                job_ids.append(job["id"])
            
            # Verify all IDs are unique
            assert len(job_ids) == len(set(job_ids))
            
            # Verify all IDs look like UUIDs (contain hyphens, right length)
            for job_id in job_ids:
                assert "-" in job_id
                assert len(job_id) == 36  # Standard UUID length
            
            print(f"✅ Created 5 jobs with unique UUIDs: {job_ids}")
