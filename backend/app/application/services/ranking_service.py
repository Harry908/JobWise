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
        # Delete existing ranking for this job+profile (force regeneration with updated system)
        existing = await self.ranking_repo.get_by_job(user_id, job_id)
        if existing:
            await self.ranking_repo.delete(existing.id)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Deleted old ranking {existing.id} for job {job_id} to create fresh ranking")
        
        # Get job
        job = await self.job_repo.get_by_id(str(job_id), user_id)
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
        
        # Create integer-to-UUID mapping for experiences
        exp_id_to_int = {}
        int_to_exp_id = {}
        for idx, exp in enumerate(experiences, start=1):
            exp_uuid = str(exp.id) if hasattr(exp, 'id') else str(exp)
            exp_id_to_int[exp_uuid] = idx
            int_to_exp_id[idx] = exp_uuid
        
        # Format for LLM with simple integer IDs
        exp_list = [
            {
                "id": exp_id_to_int[str(exp.id)],  # Use simple integer instead of UUID
                "title": exp.title if hasattr(exp, 'title') else "",
                "company": exp.company if hasattr(exp, 'company') else "",
                "description": exp.description if hasattr(exp, 'description') else ""
            }
            for exp in experiences
        ]
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Sending {len(exp_list)} experiences to LLM for ranking")
        logger.info(f"Experience integer IDs being sent: {[exp['id'] for exp in exp_list]}")
        logger.info(f"Integer-to-UUID mapping: {int_to_exp_id}")
        
        # Get projects from profile
        projects = profile.projects if hasattr(profile, 'projects') else []
        if not projects:
            projects = []
        
        # Create integer-to-UUID mapping for projects
        proj_id_to_int = {}
        int_to_proj_id = {}
        for idx, proj in enumerate(projects, start=1):
            proj_uuid = str(proj.id) if hasattr(proj, 'id') else str(proj)
            proj_id_to_int[proj_uuid] = idx
            int_to_proj_id[idx] = proj_uuid
            
        # Format for LLM with simple integer IDs
        proj_list = [
            {
                "id": proj_id_to_int[str(proj.id)],  # Use simple integer instead of UUID
                "name": proj.name if hasattr(proj, 'name') else "",
                "description": proj.description if hasattr(proj, 'description') else "",
                "technologies": proj.technologies if hasattr(proj, 'technologies') else []
            }
            for proj in projects
        ]
        
        # Debug logging
        logger.info(f"Sending {len(proj_list)} projects to LLM for ranking")
        logger.info(f"Project integer IDs being sent: {[proj['id'] for proj in proj_list]}")
        logger.info(f"Integer-to-UUID mapping: {int_to_proj_id}")
        
        # Rank using LLM
        job_description = job.description or f"{job.title} at {job.company}"
        logger.info(f"Job description being sent (first 200 chars): {job_description[:200]}")
        logger.info(f"Sample experience data: {exp_list[0] if exp_list else 'No experiences'}")
        logger.info(f"Sample project data: {proj_list[0] if proj_list else 'No projects'}")
        
        result = await self.llm.rank_content(job_description, exp_list, proj_list)
        
        # Debug logging - show raw LLM response
        logger.info(f"LLM returned ranked experience integer IDs: {result.get('ranked_experience_ids', [])}")
        logger.info(f"LLM returned ranked project integer IDs: {result.get('ranked_project_ids', [])}")
        logger.info(f"LLM keyword matches: {result.get('keyword_matches', {})}")
        logger.info(f"LLM ranking rationale: {result.get('ranking_rationale', 'None')}")
        
        # Map integer IDs back to UUIDs
        ranked_exp_uuids = []
        for int_id in result.get("ranked_experience_ids", []):
            # Handle both integer and string integer IDs from LLM
            try:
                int_key = int(int_id)
                if int_key in int_to_exp_id:
                    ranked_exp_uuids.append(int_to_exp_id[int_key])
                else:
                    logger.warning(f"LLM returned invalid experience ID: {int_id}")
            except (ValueError, TypeError):
                logger.warning(f"LLM returned non-integer experience ID: {int_id}")
        
        ranked_proj_uuids = []
        for int_id in result.get("ranked_project_ids", []):
            # Handle both integer and string integer IDs from LLM
            try:
                int_key = int(int_id)
                if int_key in int_to_proj_id:
                    ranked_proj_uuids.append(int_to_proj_id[int_key])
                else:
                    logger.warning(f"LLM returned invalid project ID: {int_id}")
            except (ValueError, TypeError):
                logger.warning(f"LLM returned non-integer project ID: {int_id}")
        
        logger.info(f"Mapped back to {len(ranked_exp_uuids)} experience UUIDs: {ranked_exp_uuids}")
        logger.info(f"Mapped back to {len(ranked_proj_uuids)} project UUIDs: {ranked_proj_uuids}")
        
        # Create ranking entity
        ranking = JobContentRanking(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            profile_id=UUID(profile.id),  # profile.id is UUID string from DB
            ranked_experience_ids=ranked_exp_uuids,  # Store UUIDs in database
            ranked_project_ids=ranked_proj_uuids,    # Store UUIDs in database
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
