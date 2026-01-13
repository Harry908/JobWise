"""
Agent runner script to collect responses for evaluation.

This script:
1. Loads test queries from evaluation_queries.json
2. Runs the JobWise cover letter generation for each query
3. Collects responses and saves them for evaluation

Usage:
    python collect_evaluation_responses.py
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict
from uuid import uuid4

from app.core.config import get_settings
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.infrastructure.repositories.ranking_repository import RankingRepository
from app.infrastructure.repositories.sample_repository import SampleRepository
from app.infrastructure.repositories.writing_style_repository import WritingStyleRepository
from app.application.services.generation_service import GenerationService
from app.application.services.ranking_service import RankingService
from app.application.services.style_extraction_service import StyleExtractionService
from app.domain.entities.job import Job
from app.domain.entities.profile import Profile, PersonalInfo, Skills, Experience

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_test_data(session, query: Dict, user_id: int = 1) -> tuple:
    """
    Setup test profile and job from query data.
    
    Args:
        session: Database session
        query: Query data containing job and profile info
        user_id: User ID to associate data with
        
    Returns:
        Tuple of (profile, job)
    """
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    
    # Create profile from query data
    user_profile = query["user_profile"]
    
    # Check if profile exists
    existing_profile = await profile_repo.get_active_by_user_id(user_id)
    if existing_profile:
        profile = existing_profile
        logger.info(f"Using existing profile for user {user_id}")
    else:
        # Create new profile
        personal_info = PersonalInfo(
            full_name=user_profile["full_name"],
            email=f"test{user_id}@example.com",
            phone="555-0100",
            location="Remote"
        )
        
        skills = Skills(
            technical=user_profile["skills"]["technical"],
            soft=user_profile["skills"]["soft"]
        )
        
        profile = Profile(
            user_id=user_id,
            personal_info=personal_info,
            professional_summary=user_profile["professional_summary"],
            skills=skills,
            is_active=True
        )
        
        await profile_repo.create(profile)
        logger.info(f"Created new profile for user {user_id}")
        
        # Add experiences
        for i, exp_data in enumerate(user_profile.get("experiences", [])):
            experience = Experience(
                profile_id=profile.id,
                title=exp_data["title"],
                company=exp_data["company"],
                location="Remote",
                start_date=exp_data["duration"].split("-")[0].strip(),
                end_date=exp_data["duration"].split("-")[1].strip() if "-" in exp_data["duration"] else "Present",
                description=exp_data["description"],
                is_current=exp_data["duration"].endswith("Present")
            )
            await profile_repo.add_experience(experience)
        
        logger.info(f"Added {len(user_profile.get('experiences', []))} experiences")
    
    # Create job from query data
    job = Job(
        id=str(uuid4()),
        user_id=user_id,
        title=query["job_title"],
        company=query["company"],
        description=query["job_description"],
        requirements=query.get("job_requirements", []),
        location="Remote",
        source="evaluation_test"
    )
    
    await job_repo.create(job)
    logger.info(f"Created job: {job.title} at {job.company}")
    
    return profile, job


async def generate_cover_letter_for_query(
    session,
    query: Dict,
    llm: GroqAdapter,
    user_id: int = 1
) -> Dict:
    """
    Generate cover letter for a single query.
    
    Args:
        session: Database session
        query: Query data
        llm: LLM adapter
        user_id: User ID
        
    Returns:
        Response dictionary with query, generated content, and metadata
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing Query: {query['query_id']}")
    logger.info(f"Job: {query['job_title']} at {query['company']}")
    logger.info(f"{'='*60}")
    
    # Setup repositories
    generation_repo = GenerationRepository(session)
    profile_repo = ProfileRepository(session)
    job_repo = JobRepository(session)
    ranking_repo = RankingRepository(session)
    sample_repo = SampleRepository(session)
    style_repo = WritingStyleRepository(session)
    
    # Setup services
    ranking_service = RankingService(llm, ranking_repo, profile_repo, job_repo)
    style_service = StyleExtractionService(llm, sample_repo, style_repo)
    generation_service = GenerationService(
        llm, generation_repo, profile_repo, job_repo, ranking_service, style_service
    )
    
    try:
        # Setup test data
        profile, job = await setup_test_data(session, query, user_id)
        
        # Generate cover letter
        logger.info("Generating cover letter...")
        generation = await generation_service.generate_cover_letter(
            user_id=user_id,
            job_id=job.id,
            company_name=query.get("company_name"),
            hiring_manager_name=query.get("hiring_manager"),
            max_paragraphs=4
        )
        
        logger.info(f"✅ Cover letter generated successfully")
        logger.info(f"   Generation ID: {generation.id}")
        logger.info(f"   ATS Score: {generation.ats_score}")
        logger.info(f"   Status: {generation.status}")
        
        # Build response
        response = {
            "query_id": query["query_id"],
            "query": {
                "job_title": query["job_title"],
                "company": query["company"],
                "job_description": query["job_description"],
                "job_requirements": query.get("job_requirements", []),
                "candidate_name": query["user_profile"]["full_name"],
                "candidate_summary": query["user_profile"]["professional_summary"]
            },
            "response": {
                "cover_letter": generation.content_text,
                "generation_id": str(generation.id),
                "ats_score": generation.ats_score,
                "ats_feedback": generation.ats_feedback,
                "status": generation.status.value,
                "created_at": generation.created_at.isoformat()
            },
            "context": {
                "job_id": str(job.id),
                "profile_id": profile.id,
                "user_profile": query["user_profile"]
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating cover letter: {e}", exc_info=True)
        return {
            "query_id": query["query_id"],
            "query": query,
            "response": None,
            "error": str(e)
        }


async def collect_responses():
    """Main function to collect responses for all queries."""
    logger.info("="*60)
    logger.info("JobWise Evaluation Response Collection")
    logger.info("="*60)
    
    # Load configuration
    settings = get_settings()
    
    # Setup database
    engine = create_engine()
    session_factory = create_session_factory(engine)
    
    # Load queries
    queries_file = Path("data/evaluation_queries.json")
    if not queries_file.exists():
        logger.error(f"❌ Queries file not found: {queries_file}")
        return
    
    with open(queries_file) as f:
        queries = json.load(f)
    
    logger.info(f"Loaded {len(queries)} test queries")
    
    # Initialize LLM
    llm = GroqAdapter(api_key=settings.groq_api_key)
    logger.info("Initialized Groq LLM adapter")
    
    # Collect responses
    responses = []
    
    async with session_factory() as session:
        for i, query in enumerate(queries, 1):
            logger.info(f"\nProcessing query {i}/{len(queries)}")
            
            response = await generate_cover_letter_for_query(
                session,
                query,
                llm,
                user_id=1
            )
            
            responses.append(response)
            
            # Commit after each query
            await session.commit()
    
    # Save responses
    responses_file = Path("data/evaluation_responses.json")
    with open(responses_file, 'w') as f:
        json.dump(responses, f, indent=2)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Response collection complete!")
    logger.info(f"   Total queries: {len(queries)}")
    logger.info(f"   Successful: {sum(1 for r in responses if r.get('response'))}")
    logger.info(f"   Failed: {sum(1 for r in responses if r.get('error'))}")
    logger.info(f"   Output file: {responses_file}")
    logger.info(f"{'='*60}")
    
    # Dispose engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(collect_responses())
