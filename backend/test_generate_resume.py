"""Generate a test resume to verify structured content."""

import asyncio
from uuid import UUID
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.ranking_repository import RankingRepository
from app.infrastructure.repositories.sample_repository import SampleRepository
from app.infrastructure.repositories.writing_style_repository import WritingStyleRepository
from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.application.services.generation_service import GenerationService
from app.application.services.ranking_service import RankingService
from app.application.services.style_extraction_service import StyleExtractionService
from app.core.config import get_settings


async def generate_test_resume():
    """Generate a test resume with structured content."""
    settings = get_settings()
    engine = create_engine()
    session_factory = create_session_factory(engine)
    
    async with session_factory() as session:
        try:
            # Initialize repositories
            gen_repo = GenerationRepository(session)
            profile_repo = ProfileRepository(session)
            job_repo = JobRepository(session)
            ranking_repo = RankingRepository(session)
            sample_repo = SampleRepository(session)
            style_repo = WritingStyleRepository(session)
            
            # Initialize LLM and services
            llm = GroqAdapter(api_key=settings.groq_api_key)
            style_service = StyleExtractionService(llm, sample_repo, style_repo)
            ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
            generation_service = GenerationService(
                llm, gen_repo, profile_repo, job_repo, ranking_service, style_service
            )
            
            # Get first active profile
            profiles = await profile_repo.list_by_user_id(user_id=1)
            if not profiles:
                print("❌ No profiles found for user 1")
                await engine.dispose()
                return
            
            profile = profiles[0]
            print(f"✅ Found profile: {profile.id}")
            
            # Get first job
            jobs = await job_repo.list_by_user(user_id=1, limit=1)
            if not jobs:
                print("❌ No jobs found for user 1")
                await engine.dispose()
                return
            
            job = jobs[0]
            print(f"✅ Found job: {job.title} at {job.company}")
            
            # Generate resume
            print(f"\n🔄 Generating resume...")
            generation = await generation_service.generate_resume(
                user_id=1,
                job_id=UUID(job.id),
                max_experiences=5,
                max_projects=3,
                include_summary=True
            )
            
            print(f"\n✅ Resume generated successfully!")
            print(f"   Generation ID: {generation.id}")
            print(f"   ATS Score: {generation.ats_score}")
            print(f"   Plain Text Length: {len(generation.content_text)} chars")
            
            if generation.content_structured:
                import json
                structured = json.loads(generation.content_structured)
                print(f"   Structured JSON Keys: {list(structured.keys())}")
                print(f"\n✅ STRUCTURED CONTENT IS WORKING!")
            else:
                print(f"\n❌ WARNING: No structured content generated!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(generate_test_resume())
