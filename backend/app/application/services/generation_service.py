"""Generation service for orchestrating AI document generation with preference-based approach."""

import asyncio
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generation import (
    Generation,
    GenerationOptions,
    GenerationResult
)
from app.domain.entities.preferences.user_generation_profile import UserGenerationProfile
from app.domain.entities.preferences.consistency_score import ConsistencyScore
from app.domain.prompts.job_analysis_prompts import JobAnalysisPrompts
from app.domain.prompts.generation_prompts import GenerationPrompts
from app.domain.prompts.validation_prompts import ValidationPrompts
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.user_generation_profile_repository import UserGenerationProfileRepository
from app.infrastructure.adapters.groq_adapter import GroqAdapter
from app.core.exceptions import NotFoundError, ForbiddenException, ValidationException, PreferenceExtractionException

logger = logging.getLogger(__name__)


# Stage information (exact strings from specification - 2-stage pipeline)
STAGE_INFO = {
    0: (None, "Queued for processing"),
    1: ("Analysis & Matching", "Analyzing job and matching with your profile content"),
    2: ("Generation & Validation", "Generating tailored resume and validating quality")
}

# Stage weights for progress calculation (2-stage pipeline)
STAGE_WEIGHTS = [40, 60]


class GenerationService:
    """Service for generation operations with preference-based approach."""

    def __init__(self, db: AsyncSession, groq_adapter: Optional[GroqAdapter] = None):
        self.db = db
        self.repository = GenerationRepository(db)
        self.profile_repository = UserGenerationProfileRepository(db)
        self.groq = groq_adapter
        
        # Initialize prompts
        self.job_analysis_prompts = JobAnalysisPrompts()
        self.generation_prompts = GenerationPrompts()
        self.validation_prompts = ValidationPrompts()

    async def start_resume_generation(
        self,
        user_id: int,
        profile_id: str,
        job_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Generation:
        """Start preference-based resume generation."""
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
        """Start preference-based cover letter generation."""
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
        """Create and start a preference-based generation."""
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

        # Get user's generation profile for preferences
        user_profile = await self.profile_repository.get_by_user_id(user_id)
        if not user_profile or not user_profile.is_ready_for_generation():
            raise PreferenceExtractionException(
                "User generation profile not complete. Please upload sample documents first."
            )

        # Create generation entity
        generation = Generation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            profile_id=profile_id,
            job_id=job_id,
            document_type=document_type,  # type: ignore
            status="pending",
            current_stage=0,
            total_stages=5,
            stage_name=STAGE_INFO[0][0],
            stage_description=STAGE_INFO[0][1],
            options=options or GenerationOptions(custom_instructions=""),
            tokens_used=0,
            generation_time=None
        )

        # Save to database
        created_generation = await self.repository.create(generation)

        # Run preference-based pipeline asynchronously
        asyncio.create_task(self._run_preference_based_pipeline(
            generation_id=created_generation.id,
            user_profile=user_profile
        ))

        return created_generation

    async def _run_preference_based_pipeline(
        self,
        generation_id: str,
        user_profile: UserGenerationProfile
    ):
        """Run the 5-stage preference-based generation pipeline."""
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Starting preference-based generation for {generation_id}")

            # Stage 1: Analysis & Matching (40%, 3s, 2500 tokens)
            await self._update_stage(generation_id, 1)
            job_analysis_result = await self._stage1_enhanced_job_analysis(generation_id, user_profile)
            await asyncio.sleep(0.6)  # Simulate 3s processing (scaled down for testing)
            tokens_stage_1 = 2500

            # Stage 2: Generation & Validation (100%, 5s, 2500 tokens)
            await self._update_stage(generation_id, 2)
            final_result = await self._stage2_generation_validation(
                generation_id, user_profile, job_analysis_result
            )
            await asyncio.sleep(1.0)  # Simulate 5s processing (scaled down for testing)
            tokens_stage_2 = 2500

            # Calculate total time and tokens
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            total_tokens = tokens_stage_1 + tokens_stage_2

            # Mark as completed
            await self.repository.set_completed(
                generation_id=generation_id,
                result=final_result,
                tokens_used=total_tokens,
                generation_time=generation_time
            )
            
            # Update user profile with generation feedback
            user_profile.record_generation_feedback(
                satisfaction_score=4.5,  # Mock satisfaction score
                generation_successful=True
            )
            await self.profile_repository.update(user_profile)

            logger.info(f"Completed preference-based generation for {generation_id} in {generation_time:.2f}s")

        except Exception as e:
            logger.error(f"Preference-based generation failed for {generation_id}: {e}")
            # Mark as failed
            await self.repository.set_failed(
                generation_id=generation_id,
                error_message=str(e)
            )

    async def _stage1_enhanced_job_analysis(
        self,
        generation_id: str,
        user_profile: UserGenerationProfile
    ) -> Dict[str, Any]:
        """Stage 1: Enhanced job analysis with user preferences."""
        try:
            logger.debug(f"Stage 1: Enhanced job analysis for {generation_id}")
            
            # Mock job analysis result - in real implementation, this would:
            # 1. Fetch job description from job_id
            # 2. Use JobAnalysisPrompts to analyze requirements
            # 3. Apply user's industry focus and preferences
            # 4. Return structured analysis
            
            return {
                "job_requirements": ["Python", "FastAPI", "SQL", "AWS"],
                "experience_level": "senior",
                "industry_keywords": ["backend", "API", "microservices"],
                "soft_skills": ["leadership", "communication"],
                "preference_alignment_score": 0.85,
                "recommended_focus_areas": ["technical_skills", "leadership_experience"]
            }
            
        except Exception as e:
            logger.error(f"Stage 1 failed: {e}")
            raise

    async def _stage2_generation_validation(
        self,
        generation_id: str,
        user_profile: UserGenerationProfile,
        job_analysis: Dict[str, Any]
    ) -> GenerationResult:
        """Stage 2: Combined generation and validation (per spec)."""
        try:
            logger.debug(f"Stage 2: Generation & Validation for {generation_id}")
            
            # Mock combined generation+validation result - in real implementation, this would:
            # 1. Generate content following user preferences and job analysis
            # 2. Validate quality and ATS compatibility
            # 3. Return final document with metrics
            
            return GenerationResult(
                document_id=str(uuid.uuid4()),
                ats_score=0.87,
                match_percentage=int(0.88 * 100),
                keyword_coverage=0.91,
                keywords_matched=15,
                keywords_total=18,
                pdf_url=f"/api/v1/documents/{str(uuid.uuid4())}/download",
                recommendations=[
                    "Increase quantified achievements by 10%",
                    "Add 2 more industry keywords",
                    "Enhance action verb diversity"
                ],
                content={
                    "text": "John Doe\nSenior Backend Engineer\n\nPROFESSIONAL SUMMARY\nExperienced backend engineer...",
                    "html": "<html><body><h1>John Doe</h1>...</body></html>",
                    "markdown": "# John Doe\n## Senior Backend Engineer\n\n### Professional Summary\n..."
                }
            )
            
        except Exception as e:
            logger.error(f"Stage 2 failed: {e}")
            raise

    async def _run_pipeline(self, generation_id: str):
        """Run the 5-stage generation pipeline."""
        try:
            start_time = datetime.utcnow()

            # Stage 1: Job Analysis (20%, 1s, 1500 tokens)
            await self._update_stage(generation_id, 1)
            await asyncio.sleep(0.2)  # Simulate processing
            tokens_stage_1 = 1500

            # Stage 2: Profile Compilation (40%, 1s, 2000 tokens)
            await self._update_stage(generation_id, 2)
            await asyncio.sleep(0.2)
            tokens_stage_2 = 2000

            # Stage 3: Content Generation (80%, 2s, 3000 tokens)
            await self._update_stage(generation_id, 3)
            await asyncio.sleep(0.4)
            tokens_stage_3 = 3000

            # Stage 4: Quality Validation (95%, 1s, 1500 tokens)
            await self._update_stage(generation_id, 4)
            await asyncio.sleep(0.2)
            tokens_stage_4 = 1500

            # Stage 5: Export Preparation (100%, 0.5s, 0 tokens)
            await self._update_stage(generation_id, 5)
            await asyncio.sleep(0.1)
            tokens_stage_5 = 0

            # Calculate total time and tokens
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            total_tokens = tokens_stage_1 + tokens_stage_2 + tokens_stage_3 + tokens_stage_4 + tokens_stage_5

            # Create mock result
            result = GenerationResult(
                document_id=str(uuid.uuid4()),
                ats_score=0.87,
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
                    "text": "John Doe\nSoftware Engineer\n\nPROFESSIONAL SUMMARY\n...",
                    "html": "<html><body>...</body></html>",
                    "markdown": "# John Doe\n## Software Engineer\n..."
                }
            )

            # Mark as completed
            await self.repository.set_completed(
                generation_id=generation_id,
                result=result,
                tokens_used=total_tokens,
                generation_time=generation_time
            )

        except Exception as e:
            # Mark as failed
            await self.repository.set_failed(
                generation_id=generation_id,
                error_message=str(e)
            )

    async def _update_stage(self, generation_id: str, stage: int):
        """Update generation to a specific stage."""
        stage_name, stage_description = STAGE_INFO[stage]
        await self.repository.update_stage(
            generation_id=generation_id,
            current_stage=stage,
            stage_name=stage_name,
            stage_description=stage_description
        )

    async def get_generation_status(self, generation_id: str, user_id: int) -> Generation:
        """Get generation status."""
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
        """Get available templates (static for Sprint 4)."""
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
