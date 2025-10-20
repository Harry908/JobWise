import asyncio
from httpx import AsyncClient
from app.main import app

# Recreate the same fake repo and dependency overrides as the test
created_job = {
    "id": "job-1",
    "title": "Test Engineer",
    "company": "Acme",
    "location": "Remote",
    "job_type": "full-time",
    "experience_level": "mid",
    "salary_range": {"min": 50000, "max": 80000},
    "posted_date": "2024-01-01T00:00:00Z",
    "remote_work_policy": "remote",
    "tags": ["python", "fastapi"],
    "description": "Work on tests",
    "company_size": "50-200",
    "industry": "Technology",
}

async def fake_get_user_jobs(user_id, limit, offset):
    return {"items": [created_job], "total": 1, "limit": limit, "offset": offset}

class FakeRepo:
    async def get_user_jobs(self, user_id, limit, offset):
        return await fake_get_user_jobs(user_id, limit, offset)
    async def get_job_by_id(self, job_id):
        if job_id == created_job["id"] or job_id == "my-jobs":
            return created_job
        return None

from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
from app.core.dependencies import get_current_user as dep_get_current_user

class DummyUser:
    def __init__(self):
        self.id = "user-1"

app.dependency_overrides[dep_get_job_repo] = lambda: FakeRepo()
app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

async def main():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.get("/api/v1/jobs/my-jobs")
        print('status_code=', r.status_code)
        try:
            print('json=', r.json())
        except Exception as e:
            print('text=', r.text)

if __name__ == '__main__':
    asyncio.run(main())
