import asyncio
from httpx import AsyncClient
from app.main import app
from app.presentation.api.jobs import get_job_repository as dep_get_job_repo
from app.core.dependencies import get_current_user as dep_get_current_user
from app.application.dtos.job_dtos import CreateJobDTO, UpdateJobDTO, ConvertTextRequestDTO

# Fake repo and dummy user copied from test
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

async def fake_create_user_job(user_id, payload):
    return {
        "id": created_job["id"],
        "title": payload.title if hasattr(payload, "title") else created_job["title"],
        "company": payload.company if hasattr(payload, "company") else created_job["company"],
        "location": payload.location if hasattr(payload, "location") and payload.location is not None else created_job["location"],
        "job_type": payload.job_type if hasattr(payload, "job_type") and payload.job_type is not None else created_job["job_type"],
        "experience_level": payload.experience_level if hasattr(payload, "experience_level") and payload.experience_level is not None else created_job["experience_level"],
        "salary_range": created_job.get("salary_range"),
        "description": payload.description if hasattr(payload, "description") else created_job.get("description", ""),
        "requirements": payload.requirements if hasattr(payload, "requirements") and payload.requirements is not None else created_job.get("requirements", []),
        "benefits": payload.benefits if hasattr(payload, "benefits") and payload.benefits is not None else created_job.get("benefits", []),
        "posted_date": created_job.get("posted_date"),
        "application_deadline": created_job.get("application_deadline"),
        "company_size": payload.company_size if hasattr(payload, "company_size") and payload.company_size is not None else created_job.get("company_size", "50-200"),
        "industry": payload.industry if hasattr(payload, "industry") and payload.industry is not None else created_job.get("industry", "Technology"),
        "remote_work_policy": created_job.get("remote_work_policy", "remote"),
        "tags": created_job.get("tags", []),
    }

async def fake_update_user_job(user_id, job_id, payload):
    updated = {
        "id": job_id,
        "title": payload.title if hasattr(payload, "title") and payload.title is not None else created_job["title"],
        "company": payload.company if hasattr(payload, "company") and payload.company is not None else created_job["company"],
        "location": payload.location if hasattr(payload, "location") and payload.location is not None else created_job["location"],
        "job_type": payload.job_type if hasattr(payload, "job_type") and payload.job_type is not None else created_job["job_type"],
        "experience_level": payload.experience_level if hasattr(payload, "experience_level") and payload.experience_level is not None else created_job["experience_level"],
        "salary_range": created_job.get("salary_range"),
        "description": payload.description if hasattr(payload, "description") and payload.description is not None else created_job.get("description", ""),
        "requirements": payload.requirements if hasattr(payload, "requirements") and payload.requirements is not None else created_job.get("requirements", []),
        "benefits": payload.benefits if hasattr(payload, "benefits") and payload.benefits is not None else created_job.get("benefits", []),
        "posted_date": created_job.get("posted_date"),
        "application_deadline": created_job.get("application_deadline"),
        "company_size": payload.company_size if hasattr(payload, "company_size") and payload.company_size is not None else created_job.get("company_size", "50-200"),
        "industry": payload.industry if hasattr(payload, "industry") and payload.industry is not None else created_job.get("industry", "Technology"),
        "remote_work_policy": created_job.get("remote_work_policy", "remote"),
        "tags": created_job.get("tags", []),
    }
    created_job.update(updated)
    return updated

async def fake_delete_user_job(user_id, job_id):
    return True

async def fake_get_user_jobs(user_id, limit, offset):
    return {"items": [created_job], "total": 1, "limit": limit, "offset": offset}

async def fake_analyze_job(job_id):
    return {
        "keywords": ["python", "testing"],
        "technical_skills": ["python", "pytest"],
        "soft_skills": ["communication"],
        "experience_level": "mid",
        "match_difficulty": 0.2,
    }

async def fake_convert_text_to_job(raw_text):
    return {"template": {"title": "Converted", "company": "ConvertedCo", "description": raw_text}}

class FakeRepo:
    async def create_user_job(self, user_id, payload):
        return await fake_create_user_job(user_id, payload)
    async def update_user_job(self, user_id, job_id, payload):
        return await fake_update_user_job(user_id, job_id, payload)
    async def delete_user_job(self, user_id, job_id):
        return await fake_delete_user_job(user_id, job_id)
    async def get_user_jobs(self, user_id, limit, offset):
        return await fake_get_user_jobs(user_id, limit, offset)
    async def analyze_job(self, job_id):
        return await fake_analyze_job(job_id)
    async def convert_text_to_job(self, raw_text):
        return await fake_convert_text_to_job(raw_text)

class DummyUser:
    def __init__(self):
        self.id = "user-1"

app.dependency_overrides[dep_get_job_repo] = lambda: FakeRepo()
app.dependency_overrides[dep_get_current_user] = lambda: DummyUser()

async def run():
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = CreateJobDTO(
            title="Test Engineer",
            company="Acme",
            description="Work on tests",
            location="Remote",
            job_type="full-time",
            experience_level="mid",
        )
        r = await client.post("/api/v1/jobs/user", json=payload.model_dump())
        print('CREATE', r.status_code, r.text)

        update_payload = UpdateJobDTO(title="Senior Test Engineer", company="Acme", description="Senior role")
        r = await client.put(f"/api/v1/jobs/user/job-1", json=update_payload.model_dump(exclude_none=True))
        print('UPDATE', r.status_code, r.text)

        r = await client.get("/api/v1/jobs/my-jobs")
        print('MYJOBS', r.status_code, r.text)

if __name__ == '__main__':
    asyncio.run(run())
