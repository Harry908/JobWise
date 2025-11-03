"""Integration test to verify Job API uses mock_jobs.json correctly."""

import json
import asyncio
from pathlib import Path
from app.application.services.job_service import JobService
from app.infrastructure.repositories.job_repository import JobRepository
from unittest.mock import AsyncMock


async def test_integration():
    """Test that job service loads all 20 jobs from JSON."""
    
    # Create service with mock repository
    mock_repo = AsyncMock(spec=JobRepository)
    service = JobService(mock_repo)
    
    # Load jobs from service
    jobs = await service.browse_jobs(limit=100, offset=0)
    
    # Load expected data from JSON
    json_file = Path("data/mock_jobs.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    expected_jobs = data["tech_jobs"]
    
    print(f"\n✓ Jobs loaded from service: {len(jobs)}")
    print(f"✓ Jobs in JSON file: {len(expected_jobs)}")
    assert len(jobs) == len(expected_jobs), f"Expected {len(expected_jobs)} jobs, got {len(jobs)}"
    
    # Verify first job
    first_job = jobs[0]
    first_expected = expected_jobs[0]
    
    print(f"\n✓ First job title: {first_job.title}")
    assert first_job.title == first_expected["title"]
    assert first_job.company == first_expected["company"]
    assert first_job.location == first_expected["location"]
    assert first_job.source == first_expected["source"]
    assert first_job.remote == first_expected["remote"]
    assert first_job.salary_range == first_expected["salary_range"]
    
    # Verify all jobs have required fields
    for i, job in enumerate(jobs):
        assert job.id is not None, f"Job {i} missing id"
        assert job.title is not None, f"Job {i} missing title"
        assert job.company is not None, f"Job {i} missing company"
        assert job.source == "mock", f"Job {i} has wrong source: {job.source}"
        assert job.status == "active", f"Job {i} has wrong status: {job.status}"
        assert job.user_id is None, f"Job {i} should have null user_id for mock jobs"
        assert len(job.parsed_keywords) > 0, f"Job {i} missing parsed_keywords"
        assert len(job.requirements) > 0, f"Job {i} missing requirements"
        assert len(job.benefits) > 0, f"Job {i} missing benefits"
    
    print(f"\n✅ All {len(jobs)} jobs validated successfully!")
    print("✅ Job API correctly uses data from mock_jobs.json")
    
    # Test pagination
    page1 = await service.browse_jobs(limit=10, offset=0)
    page2 = await service.browse_jobs(limit=10, offset=10)
    
    assert len(page1) == 10, "First page should have 10 jobs"
    assert len(page2) == 10, "Second page should have 10 jobs"
    
    # Ensure different pages
    page1_ids = {job.id for job in page1}
    page2_ids = {job.id for job in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0, "Pages should not overlap"
    
    print("✅ Pagination working correctly")
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_integration())
    if result:
        print("\n" + "="*60)
        print("SUCCESS: Job API is correctly using mock_jobs.json")
        print("="*60)
