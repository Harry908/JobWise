"""Generation service with Context7 BackgroundTasks pattern and 2-stage LLM pipeline."""

import logging
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.entities.generation import (
    Generation,
    GenerationOptions,
    GenerationResult
)
from app.domain.ports.llm_service import ILLMService, LLMMessage
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.core.exceptions import (
    NotFoundError,
    ForbiddenException,
    ValidationException,
    LLMServiceError
)

logger = logging.getLogger(__name__)


# 2-Stage pipeline information (simplified from 5 stages)
STAGE_INFO = {
    0: (None, "Queued for processing"),
    1: ("Job Analysis", "Analyzing job requirements and extracting keywords"),
    2: ("Resume Generation", "Generating tailored resume content with LLM")
}

# Stage weights for progress: [40, 60]
STAGE_WEIGHTS = [40, 60]


class GenerationService:
    """Service for AI generation operations (Context7 patterns)."""

    def __init__(self, db: AsyncSession, llm_service: ILLMService):
        """
        Initialize generation service.
        
        Args:
            db: Database session (for endpoint request context)
            llm_service: LLM service port interface
        """
        self.db = db
        self.llm_service = llm_service
        self.repository = GenerationRepository(db)
        self.profile_repository = ProfileRepository(db)
        self.job_repository = JobRepository(db)

    async def start_resume_generation(
        self,
        user_id: int,
        profile_id: str,
        job_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Generation:
        """Start resume generation."""
        return await self._start_generation(
            user_id=user_id,
            profile_id=profile_id,
            job_id=job_id,
            document_type="resume",
            options=options
        )

    async def start_cover_letter_generation(
        self,
        user_id: int,
        profile_id: str,
        job_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Generation:
        """Start cover letter generation."""
        return await self._start_generation(
            user_id=user_id,
            profile_id=profile_id,
            job_id=job_id,
            document_type="cover_letter",
            options=options
        )

    async def _start_generation(
        self,
        user_id: int,
        profile_id: str,
        job_id: str,
        document_type: str,
        options: Optional[GenerationOptions] = None
    ) -> Generation:
        """Create and queue generation (internal method)."""
        # Validate ownership
        profile = await self.profile_repository.get_by_id(profile_id)
        if not profile or profile.user_id != user_id:
            raise ForbiddenException("Profile not found or access denied")
        
        job = await self.job_repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(detail="Job not found")
        
        # Check rate limiting
        recent_count = await self.repository.count_recent_by_user(user_id, hours=1)
        if recent_count >= 10:
            raise ValidationException(
                error_code="rate_limit_exceeded",
                message="Generation limit reached. Try again later.",
                details={
                    "current_usage": recent_count,
                    "limit": 10,
                    "retry_after": 3600
                }
            )

        # Create generation entity
        generation = Generation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            profile_id=profile_id,
            job_id=job_id,
            document_type=document_type,
            status="pending",
            current_stage=0,
            total_stages=2,  # 2-stage pipeline
            stage_name=STAGE_INFO[0][0],
            stage_description=STAGE_INFO[0][1],
            options=options or GenerationOptions(),
            tokens_used=0
        )

        # Save to database
        created_generation = await self.repository.create(generation)
        logger.info(f"Generation created: {created_generation.id}, user={user_id}")

        return created_generation

    async def run_pipeline(
        self,
        generation_id: str,
        session_factory: async_sessionmaker
    ):
        """
        Run 2-stage LLM pipeline (Context7 BackgroundTasks pattern).
        
        This method runs in background task with independent DB session.
        
        Args:
            generation_id: Generation ID to process
            session_factory: Session factory for creating new DB session
        """
        # Create independent DB session for background task (Context7 pattern)
        async with session_factory() as bg_session:
            try:
                repo = GenerationRepository(bg_session)
                profile_repo = ProfileRepository(bg_session)
                job_repo = JobRepository(bg_session)
                
                start_time = datetime.utcnow()
                logger.info(f"Pipeline started: {generation_id}")

                # Load generation with expire_on_commit=False pattern
                generation = await repo.get_by_id(generation_id)
                if not generation:
                    logger.error(f"Generation not found: {generation_id}")
                    return
                
                # Load profile and job
                profile = await profile_repo.get_by_id(generation.profile_id)
                job = await job_repo.get_by_id(generation.job_id)
                
                if not profile or not job:
                    await repo.set_failed(generation_id, "Profile or job not found")
                    return

                # Stage 1: Job Analysis (40%, fast model)
                await repo.update_stage(
                    generation_id=generation_id,
                    current_stage=1,
                    stage_name=STAGE_INFO[1][0],
                    stage_description=STAGE_INFO[1][1]
                )
                await repo.update_status(generation_id, "generating")
                
                stage1_messages = [
                    LLMMessage(
                        role="system",
                        content="You are an expert job requirements analyzer. Extract key requirements, skills, and qualifications from job descriptions."
                    ),
                    LLMMessage(
                        role="user",
                        content=f"Analyze this job posting and extract:\n1. Required technical skills\n2. Years of experience needed\n3. Key responsibilities\n4. Must-have qualifications\n\nJob Title: {job.title}\nCompany: {job.company}\nDescription:\n{job.description or job.raw_text}"
                    )
                ]
                
                stage1_response = await self.llm_service.generate(
                    messages=stage1_messages,
                    model="llama-3.1-8b-instant",  # Fast model for analysis
                    max_tokens=1500,
                    temperature=0.3
                )
                
                job_analysis = stage1_response.content
                tokens_stage_1 = stage1_response.tokens_used
                logger.info(f"Stage 1 complete: {generation_id}, tokens={tokens_stage_1}")

                # Stage 2: Resume Generation (100%, powerful model)
                await repo.update_stage(
                    generation_id=generation_id,
                    current_stage=2,
                    stage_name=STAGE_INFO[2][0],
                    stage_description=STAGE_INFO[2][1]
                )
                
                # Build profile context
                profile_context = f"""
Personal Info: {profile.personal_info.get('full_name', 'N/A')}
Email: {profile.personal_info.get('email', 'N/A')}
Phone: {profile.personal_info.get('phone', 'N/A')}
Location: {profile.personal_info.get('location', 'N/A')}

Professional Summary:
{profile.professional_summary or 'Not provided'}

Technical Skills: {', '.join(profile.skills.get('technical', []))}
Soft Skills: {', '.join(profile.skills.get('soft', []))}
Languages: {', '.join(profile.skills.get('languages', []))}
Certifications: {', '.join(profile.skills.get('certifications', []))}

Work Experience: {len(profile.experiences)} positions
"""
                
                stage2_messages = [
                    LLMMessage(
                        role="system",
                        content=f"You are an expert resume writer. Create an ATS-optimized {generation.document_type} tailored to the job requirements. Use {generation.options.template} template style and target {generation.options.length} format."
                    ),
                    LLMMessage(
                        role="user",
                        content=f"""Based on the job analysis and candidate profile below, generate a professional {generation.document_type}.

JOB ANALYSIS:
{job_analysis}

CANDIDATE PROFILE:
{profile_context}

CUSTOM INSTRUCTIONS:
{generation.options.custom_instructions or 'None'}

Generate the {generation.document_type} in Markdown format with clear sections and ATS-friendly formatting."""
                    )
                ]
                
                stage2_response = await self.llm_service.generate(
                    messages=stage2_messages,
                    model="llama-3.3-70b-versatile",  # Powerful model for content
                    max_tokens=3000,
                    temperature=0.7
                )
                
                generated_content = stage2_response.content
                tokens_stage_2 = stage2_response.tokens_used
                logger.info(f"Stage 2 complete: {generation_id}, tokens={tokens_stage_2}")

                # Calculate total metrics
                end_time = datetime.utcnow()
                generation_time = (end_time - start_time).total_seconds()
                total_tokens = tokens_stage_1 + tokens_stage_2
                
                # Create result
                result = GenerationResult(
                    document_id=str(uuid.uuid4()),
                    ats_score=0.87,  # Mock score (would be calculated in production)
                    match_percentage=82,
                    keyword_coverage=0.91,
                    keywords_matched=15,
                    keywords_total=18,
                    pdf_url=f"/api/v1/documents/{str(uuid.uuid4())}/download",
                    recommendations=[
                        "Add AWS certification to skills",
                        "Quantify team size in leadership experience",
                        "Include metrics for project impact"
                    ],
                    content={
                        "text": generated_content,
                        "markdown": generated_content,
                        "html": f"<div>{generated_content}</div>"
                    }
                )

                # Mark as completed
                await repo.set_completed(
                    generation_id=generation_id,
                    result=result,
                    tokens_used=total_tokens,
                    generation_time=generation_time
                )
                
                logger.info(
                    f"Pipeline complete: {generation_id}, "
                    f"tokens={total_tokens}, time={generation_time:.2f}s"
                )

            except LLMServiceError as e:
                logger.error(f"LLM error in pipeline {generation_id}: {e}")
                await repo.set_failed(generation_id, f"LLM error: {str(e)}")
            
            except Exception as e:
                logger.exception(f"Unexpected error in pipeline {generation_id}")
                await repo.set_failed(generation_id, f"Unexpected error: {str(e)}")

    async def get_generation_status(self, generation_id: str, user_id: int) -> Generation:
        """Get generation status with ownership check."""
        generation = await self.repository.get_by_id(generation_id)

        if not generation:
            raise NotFoundError(detail="Generation not found")

        if generation.user_id != user_id:
            raise ForbiddenException(detail="You do not have permission to access this generation")

        return generation

    async def get_generation_result(self, generation_id: str, user_id: int) -> Generation:
        """Get final generation result (must be completed)."""
        generation = await self.get_generation_status(generation_id, user_id)

        if generation.status != "completed":
            raise ValidationException(
                error_code="generation_not_completed",
                message="Generation is not yet completed",
                details={
                    "generation_id": generation_id,
                    "status": generation.status
                }
            )

        return generation

    async def list_generations(
        self,
        user_id: int,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[Generation], int]:
        """List user's generations with filters."""
        return await self.repository.get_by_user_id(
            user_id=user_id,
            job_id=job_id,
            status=status,
            document_type=document_type,
            limit=limit,
            offset=offset
        )

    async def cancel_generation(self, generation_id: str, user_id: int) -> bool:
        """Cancel an in-progress generation."""
        generation = await self.get_generation_status(generation_id, user_id)

        if not generation.can_cancel():
            raise ValidationException(
                error_code="cannot_cancel",
                message="Generation cannot be cancelled",
                details={
                    "generation_id": generation_id,
                    "status": generation.status
                }
            )

        await self.repository.update_status(generation_id, "cancelled")
        return True

    async def delete_generation(self, generation_id: str, user_id: int) -> bool:
        """Delete a generation."""
        generation = await self.get_generation_status(generation_id, user_id)
        return await self.repository.delete(generation_id)

    async def regenerate(
        self,
        original_generation_id: str,
        user_id: int,
        new_options: Optional[GenerationOptions] = None
    ) -> Generation:
        """Regenerate with updated options."""
        original = await self.get_generation_status(original_generation_id, user_id)

        # Use new options or original options
        options = new_options if new_options else original.options

        # Start new generation
        return await self._start_generation(
            user_id=user_id,
            profile_id=original.profile_id,
            job_id=original.job_id,
            document_type=original.document_type,
            options=options
        )

    async def get_statistics(self, user_id: int) -> dict:
        """Get generation statistics for user."""
        return await self.repository.get_statistics_by_user(user_id)

    def get_templates(self) -> list[dict]:
        """Get available templates (static)."""
        return [
            {
                "id": "modern",
                "name": "Modern",
                "description": "Clean, contemporary design",
                "preview_url": "/templates/modern/preview.png",
                "recommended_for": ["tech", "startup"],
                "ats_friendly": True
            },
            {
                "id": "classic",
                "name": "Classic",
                "description": "Traditional professional layout",
                "preview_url": "/templates/classic/preview.png",
                "recommended_for": ["finance", "law", "corporate"],
                "ats_friendly": True
            },
            {
                "id": "creative",
                "name": "Creative",
                "description": "Bold design for creative roles",
                "preview_url": "/templates/creative/preview.png",
                "recommended_for": ["design", "marketing"],
                "ats_friendly": False
            }
        ]
