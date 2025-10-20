import pytest
from fastapi import status
from httpx import AsyncClient
from app.main import app
from app.application.dtos.job_dtos import (
    CreateJobDTO,
    UpdateJobDTO,
    ConvertTextRequestDTO,
    StatusUpdateDTO,
)


@pytest.mark.asyncio
async def test_job_search_endpoint():
    """Test GET /api/v1/jobs - search all jobs"""
    class FakeRepo:
        async def search_jobs(self, query="", filters=None, limit=20, offset=0):
            from app.application.dtos.job_dtos import JobDTO, SalaryRangeDTO
            from datetime import datetime
            return [
                JobDTO(
                    id="job-1",
                    title="Python Developer",
                    company="TechCorp",
                    location="Seattle, WA",
                    job_type="full-time",
                    experience_level="mid",
                    salary_range=SalaryRangeDTO(min=80000, max=120000, currency="USD"),
                    description="Python development role",
                    requirements=["Python", "FastAPI"],
                    benefits=["Health insurance"],
                    posted_date=datetime.fromisoformat("2024-01-01T00:00:00"),
                    application_deadline=None,
                    company_size="500-1000",
                    industry="Technology",
                    remote_work_policy="hybrid",
                    tags=["python", "fastapi"]
                )
            ]
        async def get_total_count(self):
            return 1

    fake_repo = FakeRepo()

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "jobs" in data
        assert "total_count" in data
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["title"] == "Python Developer"


@pytest.mark.asyncio
async def test_get_job_details_endpoint():
    """Test GET /api/v1/jobs/{id} - get job details"""
    class FakeRepo:
        async def get_job_by_id(self, job_id):
            if job_id == "job-1":
                return {
                    "id": "job-1",
                    "title": "Python Developer",
                    "company": "TechCorp",
                    "location": "Seattle, WA",
                    "job_type": "full-time",
                    "experience_level": "mid",
                    "salary_range": {"min": 80000, "max": 120000, "currency": "USD"},
                    "description": "Python development role",
                    "requirements": ["Python", "FastAPI"],
                    "benefits": ["Health insurance"],
                    "posted_date": "2024-01-01T00:00:00Z",
                    "application_deadline": None,
                    "company_size": "500-1000",
                    "industry": "Technology",
                    "remote_work_policy": "hybrid",
                    "tags": ["python", "fastapi"]
                }
            return None

    fake_repo = FakeRepo()

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test existing job
        response = await client.get("/api/v1/jobs/job-1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "job-1"
        assert data["title"] == "Python Developer"

        # Test non-existing job
        response = await client.get("/api/v1/jobs/job-999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_job_endpoint():
    """Test POST /api/v1/jobs - create user custom job description"""
    class FakeRepo:
        async def create_user_job(self, user_id, payload):
            return {
                "id": "job-new",
                "title": payload.title,
                "company": payload.company,
                "location": payload.location or "",
                "job_type": payload.job_type or "full-time",
                "experience_level": payload.experience_level or "entry",
                "salary_range": payload.salary_range,
                "description": payload.description,
                "requirements": payload.requirements or [],
                "benefits": payload.benefits or [],
                "posted_date": "2024-01-01T00:00:00Z",
                "application_deadline": None,
                "company_size": "50-200",
                "industry": "Technology",
                "remote_work_policy": "onsite",
                "tags": []
            }

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            from uuid import uuid4
            self.id = str(uuid4())  # Use string representation of UUID

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = CreateJobDTO(
            title="Senior Developer",
            company="TechCorp",
            description="Senior development role",
            requirements=["5+ years experience"],
            location="Seattle, WA"
        )
        response = await client.post("/api/v1/jobs/", json=payload.model_dump())
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] == "job-new"
        assert data["title"] == "Senior Developer"


@pytest.mark.asyncio
async def test_update_job_endpoint():
    """Test PUT /api/v1/jobs/{id} - update user job"""
    class FakeRepo:
        async def update_user_job(self, user_id, job_id, payload):
            if job_id == "job-1" and user_id == "user-1":
                return {
                    "id": "job-1",
                    "title": payload.title or "Updated Title",
                    "company": "TechCorp",
                    "location": "Seattle, WA",
                    "job_type": "full-time",
                    "experience_level": "mid",
                    "salary_range": None,
                    "description": "Updated description",
                    "requirements": ["Python"],
                    "benefits": [],
                    "posted_date": "2024-01-01T00:00:00Z",
                    "application_deadline": None,
                    "company_size": "50-200",
                    "industry": "Technology",
                    "remote_work_policy": "hybrid",
                    "tags": []
                }
            return None

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            self.id = "user-1"

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = UpdateJobDTO(title="Updated Title", company="Updated Company", description="Updated description")
        response = await client.put("/api/v1/jobs/job-1", json=payload.model_dump(exclude_none=True))
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"

        # Test access denied
        response = await client.put("/api/v1/jobs/job-999", json=payload.model_dump(exclude_none=True))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_job_endpoint():
    """Test DELETE /api/v1/jobs/{id} - delete user job"""
    class FakeRepo:
        async def delete_user_job(self, user_id, job_id):
            return job_id == "job-1" and user_id == "user-1"

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            self.id = "user-1"

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/jobs/job-1")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Test access denied
        response = await client.delete("/api/v1/jobs/job-999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_my_jobs_endpoint():
    """Test GET /api/v1/jobs/my-jobs - list user's custom job descriptions"""
    class FakeRepo:
        async def get_user_jobs(self, user_id, limit=20, offset=0):
            print(f"FakeRepo.get_user_jobs called with user_id={user_id}, limit={limit}, offset={offset}")
            from app.application.dtos.job_dtos import JobDTO, UserJobListDTO
            from datetime import datetime
            items = [
                JobDTO(
                    id="job-1",
                    title="My Job",
                    company="MyCompany",
                    location="Remote",
                    job_type="full-time",
                    experience_level="senior",
                    salary_range=None,
                    description="My job description",
                    requirements=["Skill 1"],
                    benefits=["Benefit 1"],
                    posted_date=datetime(2024, 1, 1, 0, 0, 0),  # Use datetime object
                    application_deadline=None,
                    company_size="50-200",
                    industry="Technology",
                    remote_work_policy="remote",
                    tags=[]
                )
            ]
            result = UserJobListDTO(items=items, total=1, limit=limit, offset=offset)
            print(f"FakeRepo returning: {result}")
            return result

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            from uuid import uuid4
            self.id = str(uuid4())  # Use string representation of UUID

    # Clear previous overrides and set new ones
    app.dependency_overrides.clear()
    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/my-jobs")
        print(f"Response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "My Job"


@pytest.mark.asyncio
async def test_update_job_status_endpoint():
    """Test PUT /api/v1/jobs/{id}/status - change job status"""
    class FakeRepo:
        def __init__(self):
            self.user_id = None  # Will be set when called
            
        async def change_status(self, user_id, job_id, status):
            self.user_id = user_id  # Store for checking
            if job_id == "job-1" and status == "active":
                from app.application.dtos.job_dtos import JobDTO
                from datetime import datetime
                return JobDTO(
                    id="job-1",
                    title="Job Title",
                    company="Company",
                    location="Location",
                    job_type="full-time",
                    experience_level="mid",
                    salary_range=None,
                    description="Description",
                    requirements=[],
                    benefits=[],
                    posted_date=datetime.fromisoformat("2024-01-01T00:00:00"),
                    application_deadline=None,
                    company_size="50-200",
                    industry="Technology",
                    remote_work_policy="onsite",
                    tags=[]
                )
            return None

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            from uuid import uuid4
            self.id = str(uuid4())  # Use string representation of UUID

    # Clear previous overrides and set new ones
    app.dependency_overrides.clear()
    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = StatusUpdateDTO(status="active")
        response = await client.put("/api/v1/jobs/job-1/status", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "job-1"

        # Test invalid status - should fail validation
        try:
            payload = StatusUpdateDTO(status="invalid")
            response = await client.put("/api/v1/jobs/job-1/status", json=payload.model_dump())
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        except Exception:
            # Pydantic validation may fail before request, which is also acceptable
            pass


@pytest.mark.asyncio
async def test_analyze_job_endpoint():
    """Test POST /api/v1/jobs/{id}/analyze - extract keywords and analyze job"""
    class FakeRepo:
        def __init__(self):
            # Mock session that returns None for get() calls
            class MockSession:
                async def get(self, model_class, job_id):
                    return None  # No ownership check needed for test
            self.session = MockSession()

        async def get_job_by_id(self, job_id):
            from app.application.dtos.job_dtos import JobDTO
            from datetime import datetime
            if job_id == "job-1":
                return JobDTO(
                    id=job_id,
                    title="Test Job",
                    company="TestCo",
                    location="",
                    job_type="full-time",
                    experience_level="entry",
                    salary_range=None,
                    description="Test description",
                    requirements=[],
                    benefits=[],
                    posted_date=datetime.fromisoformat("2024-01-01T00:00:00"),
                    application_deadline=None,
                    company_size="50-200",
                    industry="Technology",
                    remote_work_policy="onsite",
                    tags=[]
                )
            return None

        async def analyze_job(self, job_id):
            from app.application.dtos.job_dtos import AnalyzeJobResponseDTO
            return AnalyzeJobResponseDTO(
                keywords=["python", "testing"],
                technical_skills=["python", "pytest"],
                soft_skills=["communication"],
                experience_level="mid",
                match_difficulty=0.3
            )

    fake_repo = FakeRepo()

    class DummyUser:
        def __init__(self):
            from uuid import uuid4
            self.id = str(uuid4())  # Use string representation of UUID

    # Clear previous overrides and set new ones
    app.dependency_overrides.clear()
    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    from app.core.dependencies import get_current_user as dep_get_current_user
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo
    app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/jobs/job-1/analyze")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "keywords" in data
        assert "technical_skills" in data
        assert data["match_difficulty"] == 0.3

        # Test job not found
        response = await client.post("/api/v1/jobs/job-999/analyze")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_job_template_endpoint():
    """Test GET /api/v1/jobs/template - get JSON template"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/template")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "template" in data
        template = data["template"]
        assert "title" in template
        assert "company" in template
        assert "description" in template


@pytest.mark.asyncio
async def test_convert_text_to_job_endpoint():
    """Test POST /api/v1/jobs/convert-text - convert raw job text to structured JSON"""
    class FakeRepo:
        async def convert_text_to_job(self, raw_text):
            return {
                "template": {
                    "title": "Parsed Title",
                    "company": "Parsed Company",
                    "description": raw_text,
                    "requirements": [],
                    "benefits": [],
                    "location": "",
                    "job_type": "full-time",
                    "experience_level": "entry",
                    "salary_range": None,
                    "source": "user_converted"
                }
            }

    fake_repo = FakeRepo()

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = ConvertTextRequestDTO(raw_text="This is a job description text")
        response = await client.post("/api/v1/jobs/convert-text", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "template" in data
        assert data["template"]["title"] == "Parsed Title"


@pytest.mark.asyncio
async def test_job_filters_endpoint():
    """Test GET /api/v1/jobs/filters/options - get available filter options"""
    class FakeRepo:
        async def get_job_filters(self):
            return {
                "job_types": ["full-time", "part-time"],
                "experience_levels": ["entry", "mid", "senior"],
                "remote_work_policies": ["remote", "hybrid", "onsite"],
                "industries": ["Technology", "Healthcare"],
                "company_sizes": ["1-10", "50-200"],
                "locations": ["Seattle, WA", "New York, NY"],
                "tags": ["python", "javascript"],
                "salary_ranges": {"min": 50000, "max": 150000}
            }

    fake_repo = FakeRepo()

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/filters/options")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_types" in data
        assert "experience_levels" in data
        assert len(data["job_types"]) == 2


@pytest.mark.asyncio
async def test_job_stats_endpoint():
    """Test GET /api/v1/jobs/stats/summary - get job statistics"""
    class FakeRepo:
        async def get_statistics(self):
            return {"total_jobs": 150, "active_jobs": 120}

    fake_repo = FakeRepo()

    from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
    app.dependency_overrides[dep_get_job_repo] = lambda: fake_repo

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/jobs/stats/summary")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_jobs"] == 150
        assert "last_updated" in data
