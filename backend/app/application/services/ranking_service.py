"""Ranking service for content ranking."""

from uuid import UUID, uuid4
from typing import Optional

from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.ranking_repository import RankingRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.domain.entities.job_content_ranking import JobContentRanking
from app.domain.enums.generation_status import GenerationStatus


class RankingService:
    """Service for creating and managing content rankings."""
    
    def __init__(
        self,
        llm_adapter: GroqAdapter,
        ranking_repo: RankingRepository,
        profile_repo: ProfileRepository,
        job_repo: JobRepository
    ):
        self.llm = llm_adapter
        self.ranking_repo = ranking_repo
        self.profile_repo = profile_repo
        self.job_repo = job_repo
    
    async def create_ranking(
        self,
        user_id: int,
        job_id: UUID,
        custom_prompt: Optional[str] = None
    ) -> JobContentRanking:
        """Create content ranking for a job."""
        # Check if ranking already exists (cached)
        existing = await self.ranking_repo.get_by_job(user_id, job_id)
        if existing:
            return existing
        
        # Get job
        job = await self.job_repo.get_by_id(str(job_id))
        if not job or job.user_id != user_id:
            raise ValueError("Job not found")
        
        # Get profile
        profile = await self.profile_repo.get_active_by_user_id(user_id)
        if not profile:
            raise ValueError("No profile found")
        
        # Get experiences and projects
        experiences = await self.profile_repo.get_experiences_by_profile_id(profile.id)
        
        # Debug: Check what we got
        if not experiences:
            experiences = []
        
        # Format for LLM
        exp_list = [
            {
                "id": str(exp.id) if hasattr(exp, 'id') else str(exp),
                "title": exp.title if hasattr(exp, 'title') else "",
                "company": exp.company if hasattr(exp, 'company') else "",
                "description": exp.description if hasattr(exp, 'description') else ""
            }
            for exp in experiences
        ]
        
        # Get projects from profile
        projects = profile.projects if hasattr(profile, 'projects') else []
        if not projects:
            projects = []
            
        proj_list = [
            {
                "id": str(proj.id) if hasattr(proj, 'id') else str(proj),
                "name": proj.name if hasattr(proj, 'name') else "",
                "description": proj.description if hasattr(proj, 'description') else "",
                "technologies": proj.technologies if hasattr(proj, 'technologies') else []
            }
            for proj in projects
        ]
        
        # Rank using LLM
        job_description = job.description or f"{job.title} at {job.company}"
        result = await self.llm.rank_content(job_description, exp_list, proj_list)
        
        # Create ranking entity
        ranking = JobContentRanking(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            profile_id=UUID(profile.id),  # profile.id is UUID string from DB
            ranked_experience_ids=result["ranked_experience_ids"],
            ranked_project_ids=result["ranked_project_ids"],
            ranking_rationale=result.get("ranking_rationale"),
            keyword_matches=result.get("keyword_matches"),
            relevance_scores=None,  # Could add later
            llm_metadata=str(result.get("llm_metadata")),
            status=GenerationStatus.COMPLETED
        )
        
        # Save ranking
        await self.ranking_repo.create(ranking)
        
        return ranking
    
    async def get_ranking_for_job(
        self,
        user_id: int,
        job_id: UUID
    ) -> Optional[JobContentRanking]:
        """Get ranking for a specific job."""
        return await self.ranking_repo.get_by_job(user_id, job_id)
