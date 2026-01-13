"""
Simplified agent runner to collect cover letter responses for evaluation.

This script calls the generation service API-style without creating duplicate data.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict
from uuid import uuid4

from app.core.config import get_settings
from app.infrastructure.database.connection import create_engine, create_session_factory
from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def generate_cover_letter_direct(llm: GroqAdapter, query: Dict) -> Dict:
    """
    Generate cover letter directly using LLM without database.
    
    Args:
        llm: LLM adapter
        query: Query data
        
    Returns:
        Response dictionary
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Query: {query['query_id']} - {query['job_title']} at {query['company']}")
    logger.info(f"{'='*60}")
    
    try:
        user_profile = query["user_profile"]
        
        # Prepare profile data for LLM
        experiences = []
        for exp in user_profile.get("experiences", []):
            experiences.append({
                "title": exp["title"],
                "company": exp["company"],
                "duration": exp["duration"],
                "description": exp["description"]
            })
        
        profile_data = {
            "full_name": user_profile["full_name"],
            "professional_summary": user_profile["professional_summary"],
            "technical_skills": ", ".join(user_profile["skills"]["technical"]),
            "soft_skills": ", ".join(user_profile["skills"]["soft"]),
            "experiences": experiences,
            "projects": [],
            "education": []
        }
        
        # Generate cover letter
        logger.info("Generating cover letter...")
        cover_letter = await llm.generate_cover_letter(
            job_description=query["job_description"],
            profile_data=profile_data,
            writing_style=None,
            company_name=query.get("company_name", query["company"]),
            hiring_manager=query.get("hiring_manager"),
            max_paragraphs=4
        )
        
        logger.info(f"✅ Generated ({len(cover_letter)} chars)")
        
        # Build response
        response = {
            "query_id": query["query_id"],
            "query": {
                "job_title": query["job_title"],
                "company": query["company"],
                "job_description": query["job_description"],
                "job_requirements": query.get("job_requirements", []),
                "candidate_name": user_profile["full_name"],
                "candidate_summary": user_profile["professional_summary"],
                "candidate_skills": user_profile["skills"]["technical"] + user_profile["skills"]["soft"]
            },
            "response": {
                "cover_letter": cover_letter,
                "status": "completed"
            },
            "context": {
                "user_profile": user_profile,
                "generation_params": {
                    "company_name": query.get("company_name", query["company"]),
                    "hiring_manager": query.get("hiring_manager"),
                    "max_paragraphs": 4
                }
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return {
            "query_id": query["query_id"],
            "query": query,
            "response": None,
            "error": str(e)
        }


async def collect_responses():
    """Main function to collect responses."""
    logger.info("="*60)
    logger.info("JobWise Evaluation - Cover Letter Response Collection")
    logger.info("="*60)
    
    # Load settings
    settings = get_settings()
    
    # Load queries
    queries_file = Path("data/evaluation_queries.json")
    if not queries_file.exists():
        logger.error(f"❌ Queries file not found: {queries_file}")
        return
    
    with open(queries_file) as f:
        queries = json.load(f)
    
    logger.info(f"Loaded {len(queries)} test queries\n")
    
    # Initialize LLM
    llm = GroqAdapter(api_key=settings.groq_api_key)
    
    # Collect responses
    responses = []
    successful = 0
    failed = 0
    
    for i, query in enumerate(queries, 1):
        logger.info(f"Processing {i}/{len(queries)}")
        
        response = await generate_cover_letter_direct(llm, query)
        responses.append(response)
        
        if response.get("response"):
            successful += 1
        else:
            failed += 1
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    # Save responses
    responses_file = Path("data/evaluation_responses.json")
    with open(responses_file, 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Collection Complete!")
    logger.info(f"   Total: {len(queries)}")
    logger.info(f"   Successful: {successful}")
    logger.info(f"   Failed: {failed}")
    logger.info(f"   Output: {responses_file}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(collect_responses())
