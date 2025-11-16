#!/usr/bin/env python3
"""Test script to check browse jobs functionality."""

import asyncio
import sys
import traceback
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from app.application.services.job_service import JobService
    from app.infrastructure.repositories.job_repository import JobRepository
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)


async def test_browse_jobs():
    """Test the browse jobs functionality."""
    try:
        # Create repository and service
        repo = JobRepository(None)  # No database session needed for browse
        service = JobService(repo)
        
        print("📁 Loading mock jobs...")
        
        # Test count
        count = await service.count_browse_jobs()
        print(f"📊 Total mock jobs available: {count}")
        
        # Test browse
        jobs = await service.browse_jobs(limit=3)
        print(f"🔍 Loaded {len(jobs)} jobs")
        
        if jobs:
            print(f"📋 First job: '{jobs[0].title}' at '{jobs[0].company}'")
            print(f"📋 Second job: '{jobs[1].title}' at '{jobs[1].company}'" if len(jobs) > 1 else "No second job")
            print(f"📋 Third job: '{jobs[2].title}' at '{jobs[2].company}'" if len(jobs) > 2 else "No third job")
        else:
            print("❌ No jobs loaded!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Testing JobWise browse jobs functionality...")
    asyncio.run(test_browse_jobs())
    print("✅ Test completed!")