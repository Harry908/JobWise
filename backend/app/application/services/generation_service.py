# Generation Service

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.application.dtos.generation_dtos import (
    GenerationDTO,
    GenerationStatus as DTOGenerationStatus,
    GenerationProgress,
    GenerationResult,
    ResumeGenerationRequest,
    CoverLetterGenerationRequest,
    GenerationOptions,
    DocumentType as DTODocumentType,
    GenerationSummaryDTO,
    GenerationListResponse,
    GenerationResultContent
)
from app.domain.entities.generation import Generation, GenerationStatus, DocumentType, GenerationResult as DomainGenerationResult
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import DatabaseJobRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenerationService:
    """Service for managing AI-powered document generation."""

    def __init__(
        self,
        generation_repo: GenerationRepository,
        profile_repo: ProfileRepository,
        job_repo: DatabaseJobRepository
    ):
        self.generation_repo = generation_repo
        self.profile_repo = profile_repo
        self.job_repo = job_repo
        self.active_generations: Dict[str, asyncio.Task] = {}

    async def start_resume_generation(
        self,
        user_id: str,
        request: ResumeGenerationRequest
    ) -> Optional[GenerationDTO]:
        """Start resume generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(uuid.UUID(request.profile_id))
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_job_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation.create(
                id=generation_id,
                profile_id=request.profile_id,
                job_id=request.job_id
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start resume generation: {e}")
            raise

    async def start_cover_letter_generation(
        self,
        user_id: str,
        request: CoverLetterGenerationRequest
    ) -> Optional[GenerationDTO]:
        """Start cover letter generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(uuid.UUID(request.profile_id))
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_job_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation.create(
                id=generation_id,
                profile_id=request.profile_id,
                job_id=request.job_id
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start cover letter generation: {e}")
            raise

    async def get_generation(self, generation_id: str) -> Optional[GenerationDTO]:
        """Get generation by ID."""
        try:
            return await self._get_generation_dto(generation_id)
        except Exception as e:
            logger.exception(f"Failed to get generation {generation_id}: {e}")
            return None

    async def get_user_generations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> GenerationListResponse:
        """Get user's generations with pagination."""
        try:
            generations = await self.generation_repo.get_by_user_id(user_id, limit, offset)

            # Convert to summary DTOs
            summaries = []
            for gen in generations:
                job = await self.job_repo.get_job_by_id(gen.job_id)
                summary = GenerationSummaryDTO(
                    generation_id=gen.id,
                    status=self._map_status_to_dto(gen.status),
                    document_type=DTODocumentType.RESUME,  # Default for now
                    job_title=job.title if job else "Unknown Job",
                    company=job.company if job else "Unknown Company",
                    ats_score=gen.get_average_ats_score(),
                    created_at=gen.created_at,
                    completed_at=gen.completed_at
                )
                summaries.append(summary)

            # Calculate statistics
            total = await self.generation_repo.count_by_user_id(user_id)
            statistics = await self._calculate_statistics(user_id)

            pagination = {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total,
                "has_previous": offset > 0
            }

            return GenerationListResponse(
                generations=summaries,
                pagination=pagination,
                statistics=statistics
            )

        except Exception as e:
            logger.exception(f"Failed to get user generations for {user_id}: {e}")
            raise

    async def cancel_generation(self, generation_id: str, user_id: str) -> bool:
        """Cancel ongoing generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return False

            # Check if user owns this generation (through profile)
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return False

            if generation.status in [GenerationStatus.ANALYZING_JOB, GenerationStatus.COMPILING_PROFILE,
                                   GenerationStatus.GENERATING_DOCUMENTS, GenerationStatus.VALIDATING_QUALITY]:
                return False

            # Cancel background task
            if generation_id in self.active_generations:
                self.active_generations[generation_id].cancel()
                del self.active_generations[generation_id]

            # Update status
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.FAILED
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to cancel generation {generation_id}: {e}")
            return False

    async def regenerate(
        self,
        generation_id: str,
        user_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Optional[GenerationDTO]:
        """Regenerate document with updated options."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return None

            # Check ownership
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return None

            # Create new generation based on original
            new_generation_id = str(uuid.uuid4())
            new_generation = Generation.create(
                id=new_generation_id,
                profile_id=generation.profile_id,
                job_id=generation.job_id
            )

            await self.generation_repo.create(new_generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(new_generation_id)
            )
            self.active_generations[new_generation_id] = task

            await self.generation_repo.update_status(
                new_generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(new_generation_id)

        except Exception as e:
            logger.exception(f"Failed to regenerate {generation_id}: {e}")
            return None

    async def get_generation_content(
        self,
        generation_id: str,
        user_id: str
    ) -> Optional[GenerationResultContent]:
        """Get detailed content of completed generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return None

            # Check ownership
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return None

            if not generation.is_completed():
                return None

            resume_result = generation.get_resume_result()
            if not resume_result:
                return None

            return GenerationResultContent(
                generation_id=generation.id,
                document_id=generation.id,  # Use generation ID as document ID
                document_type=DTODocumentType.RESUME,
                content={
                    'text': resume_result.content,
                    'html': f'<html><body>{resume_result.content}</body></html>',
                    'markdown': f'# Generated Resume\n\n{resume_result.content}'
                },
                ats_score=resume_result.ats_score or 0.0,
                match_percentage=85,  # Mock value
                keyword_coverage=0.9,  # Mock value
                keywords_matched=15,  # Mock value
                keywords_total=18,  # Mock value
                pdf_url=f'/api/v1/documents/{generation_id}/download',
                recommendations=[],  # Mock empty list
                metadata=resume_result.metadata
            )

        except Exception as e:
            logger.exception(f"Failed to get generation content {generation_id}: {e}")
            return None

    async def _execute_generation_pipeline(self, generation_id: str) -> None:
        """Execute the 5-stage generation pipeline."""
        try:
            start_time = time.time()

            # Stage 1: Job Analysis
            await self._update_progress(generation_id, 1, "Job Analysis", "Analyzing job requirements")
            await asyncio.sleep(1)  # Simulate processing
            job_analysis = await self._stage1_analyze_job(generation_id)

            # Stage 2: Profile Compilation
            await self._update_progress(generation_id, 2, "Profile Compilation", "Scoring profile content")
            await asyncio.sleep(1.5)
            scored_profile = await self._stage2_compile_profile(generation_id, job_analysis)

            # Stage 3: Document Generation
            await self._update_progress(generation_id, 3, "Document Generation", "Creating tailored document")
            await asyncio.sleep(2)
            document_content = await self._stage3_generate_document(generation_id, scored_profile, job_analysis)

            # Stage 4: Quality Validation
            await self._update_progress(generation_id, 4, "Quality Validation", "Validating ATS compliance")
            await asyncio.sleep(1)
            validation_result = await self._stage4_validate_quality(generation_id, document_content)

            # Stage 5: PDF Export
            await self._update_progress(generation_id, 5, "PDF Export", "Generating professional PDF")
            await asyncio.sleep(1)
            pdf_result = await self._stage5_export_pdf(generation_id, document_content)

            # Complete generation
            generation_time = time.time() - start_time
            result = DomainGenerationResult(
                document_type=DocumentType.RESUME,
                content=document_content,
                ats_score=validation_result.get('ats_score', 0.85),
                word_count=len(document_content.split()),
                generated_at=datetime.utcnow(),
                metadata={
                    'generation_time': generation_time,
                    'pdf_url': pdf_result.get('pdf_url'),
                    'validation': validation_result
                }
            )

            generation = await self.generation_repo.get_by_id(generation_id)
            if generation:
                generation.add_result(result)
                generation.update_status(GenerationStatus.COMPLETED)

            await self.generation_repo.complete_generation(
                generation_id,
                {
                    'content': document_content,
                    'ats_score': validation_result.get('ats_score', 0.85),
                    'metadata': result.metadata
                },
                generation_time
            )

        except asyncio.CancelledError:
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.FAILED
            )
        except Exception as e:
            logger.exception(f"Generation pipeline failed for {generation_id}: {e}")
            await self.generation_repo.fail_generation(generation_id, str(e))
        finally:
            # Clean up active generation
            if generation_id in self.active_generations:
                del self.active_generations[generation_id]

    async def _stage1_analyze_job(self, generation_id: str) -> Dict[str, Any]:
        """Stage 1: Analyze job requirements."""
        generation = await self.generation_repo.get_by_id(generation_id)
        if not generation:
            return {}
        job = await self.job_repo.get_job_by_id(generation.job_id)

        # Mock job analysis
        return {
            'required_skills': ['python', 'fastapi', 'sqlalchemy'],
            'preferred_skills': ['docker', 'kubernetes', 'aws'],
            'experience_years': 3,
            'keywords': ['backend', 'api', 'database', 'rest'],
            'job_type': 'full-time',
            'location': job.location if job else 'remote'
        }

    async def _stage2_compile_profile(self, generation_id: str, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Compile and score profile content."""
        generation = await self.generation_repo.get_by_id(generation_id)
        if not generation:
            return {}
        profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))

        # Mock profile scoring
        return {
            'scored_experiences': [
                {'experience': 'Senior Backend Developer', 'score': 0.9, 'relevance': 0.95}
            ],
            'scored_skills': [
                {'skill': 'Python', 'score': 0.95, 'required': True},
                {'skill': 'FastAPI', 'score': 0.9, 'required': True}
            ],
            'overall_match': 0.87,
            'strengths': ['Strong backend experience', 'Relevant tech stack'],
            'gaps': ['Limited cloud experience']
        }

    async def _stage3_generate_document(self, generation_id: str, scored_profile: Dict[str, Any], job_analysis: Dict[str, Any]) -> str:
        """Stage 3: Generate tailored document."""
        # Mock document generation
        return """John Doe
Senior Python Backend Developer

Professional Summary:
Experienced backend developer with 5+ years of experience building scalable APIs and AI-powered systems.

Skills:
- Python, FastAPI, SQLAlchemy
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS, Azure

Experience:
Senior Backend Developer
TechCorp Inc, Seattle, WA
2020 - Present

- Built scalable REST APIs serving 100k+ users
- Implemented AI-powered features using OpenAI GPT
- Led team of 5 developers on microservices architecture

Education:
BS Computer Science
University of Washington, 2019"""

    async def _stage4_validate_quality(self, generation_id: str, document_content: str) -> Dict[str, Any]:
        """Stage 4: Validate quality and ATS compliance."""
        # Mock validation
        return {
            'ats_score': 0.87,
            'match_percentage': 82,
            'keyword_coverage': 0.91,
            'keywords_matched': 15,
            'keywords_total': 18,
            'recommendations': [
                'Add AWS certification to skills section',
                'Quantify team size in leadership experience'
            ]
        }

    async def _stage5_export_pdf(self, generation_id: str, document_content: str) -> Dict[str, Any]:
        """Stage 5: Export to PDF."""
        # Mock PDF generation
        return {
            'pdf_url': f'/api/v1/documents/{generation_id}/download',
            'file_size': 245760,  # bytes
            'pages': 1
        }

    async def _update_progress(
        self,
        generation_id: str,
        stage: int,
        stage_name: str,
        stage_description: str
    ) -> None:
        """Update generation progress."""
        percentage = int((stage / 5) * 100)
        progress = {
            'current_stage': stage,
            'total_stages': 5,
            'percentage': percentage,
            'stage_name': stage_name,
            'stage_description': stage_description,
            'updated_at': datetime.utcnow().isoformat()
        }
        await self.generation_repo.update_progress(generation_id, progress)

    async def _get_generation_dto(self, generation_id: str) -> Optional[GenerationDTO]:
        """Convert generation entity to DTO."""
        generation = await self.generation_repo.get_by_id(generation_id)
        if not generation:
            return None

        progress = None
        if 'current_stage' in generation.pipeline_metadata:
            progress = GenerationProgress(**generation.pipeline_metadata)

        result = None
        resume_result = generation.get_resume_result()
        if resume_result:
            result = GenerationResult(
                document_id=generation_id,
                ats_score=resume_result.ats_score or 0.0,
                match_percentage=85,  # Mock value
                keyword_coverage=0.9,  # Mock value
                pdf_url=f'/api/v1/documents/{generation_id}/download',
                recommendations=[],  # Mock empty list
            )

        return GenerationDTO(
            generation_id=generation.id,
            status=self._map_status_to_dto(generation.status),
            progress=progress,
            result=result,
            error_message=generation.error_message,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            tokens_used=7850,  # Mock value
            generation_time=generation.processing_time_seconds,
            created_at=generation.created_at,
            completed_at=generation.completed_at
        )

    def _map_status_to_dto(self, status: GenerationStatus) -> DTOGenerationStatus:
        """Map domain status to DTO status."""
        status_mapping = {
            GenerationStatus.PENDING: DTOGenerationStatus.PENDING,
            GenerationStatus.ANALYZING_JOB: DTOGenerationStatus.GENERATING,
            GenerationStatus.COMPILING_PROFILE: DTOGenerationStatus.GENERATING,
            GenerationStatus.GENERATING_DOCUMENTS: DTOGenerationStatus.GENERATING,
            GenerationStatus.VALIDATING_QUALITY: DTOGenerationStatus.GENERATING,
            GenerationStatus.EXPORTING_PDF: DTOGenerationStatus.GENERATING,
            GenerationStatus.COMPLETED: DTOGenerationStatus.COMPLETED,
            GenerationStatus.FAILED: DTOGenerationStatus.FAILED,
        }
        return status_mapping.get(status, DTOGenerationStatus.PENDING)

    async def _calculate_statistics(self, user_id: str) -> Dict[str, Any]:
        """Calculate generation statistics for user."""
        all_generations = await self.generation_repo.get_by_user_id(user_id, limit=1000)

        total = len(all_generations)
        completed = len([g for g in all_generations if g.is_completed()])
        failed = len([g for g in all_generations if g.is_failed()])
        in_progress = len([g for g in all_generations if g.status in [
            GenerationStatus.ANALYZING_JOB, GenerationStatus.COMPILING_PROFILE,
            GenerationStatus.GENERATING_DOCUMENTS, GenerationStatus.VALIDATING_QUALITY,
            GenerationStatus.EXPORTING_PDF
        ]])

        ats_scores = [
            g.get_average_ats_score() for g in all_generations
            if g.is_completed() and g.get_average_ats_score() is not None
        ]
        avg_ats_score = sum(ats_scores) / len(ats_scores) if ats_scores else 0

        return {
            'total_generations': total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'average_ats_score': round(avg_ats_score, 2)
        }

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.application.dtos.generation_dtos import (
    GenerationDTO,
    GenerationStatus as DTOGenerationStatus,
    GenerationProgress,
    GenerationResult,
    ResumeGenerationRequest,
    CoverLetterGenerationRequest,
    GenerationOptions,
    DocumentType as DTODocumentType,
    GenerationSummaryDTO,
    GenerationListResponse,
    GenerationResultContent
)
from app.domain.entities.generation import Generation, GenerationStatus, DocumentType, GenerationResult as DomainGenerationResult
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class GenerationService:
    """Service for managing AI-powered document generation."""

    def __init__(
        self,
        generation_repo: GenerationRepository,
        profile_repo: ProfileRepository,
        job_repo: JobRepository
    ):
        self.generation_repo = generation_repo
        self.profile_repo = profile_repo
        self.job_repo = job_repo
        self.active_generations: Dict[str, asyncio.Task] = {}

    async def start_resume_generation(
        self,
        user_id: str,
        request: ResumeGenerationRequest
    ) -> GenerationDTO:
        """Start resume generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(uuid.UUID(request.profile_id))
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_job_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation.create(
                id=generation_id,
                profile_id=request.profile_id,
                job_id=request.job_id
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start resume generation: {e}")
            raise

    async def start_cover_letter_generation(
        self,
        user_id: str,
        request: CoverLetterGenerationRequest
    ) -> GenerationDTO:
        """Start cover letter generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(uuid.UUID(request.profile_id))
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_job_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation.create(
                id=generation_id,
                profile_id=request.profile_id,
                job_id=request.job_id
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start cover letter generation: {e}")
            raise

    async def get_generation(self, generation_id: str) -> Optional[GenerationDTO]:
        """Get generation by ID."""
        try:
            return await self._get_generation_dto(generation_id)
        except Exception as e:
            logger.exception(f"Failed to get generation {generation_id}: {e}")
            return None

    async def get_user_generations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> GenerationListResponse:
        """Get user's generations with pagination."""
        try:
            generations = await self.generation_repo.get_by_user_id(user_id, limit, offset)

            # Convert to summary DTOs
            summaries = []
            for gen in generations:
                job = await self.job_repo.get_job_by_id(gen.job_id)
                summary = GenerationSummaryDTO(
                    generation_id=gen.id,
                    status=self._map_status_to_dto(gen.status),
                    document_type=DTODocumentType.RESUME,  # Default for now
                    job_title=job.title if job else "Unknown Job",
                    company=job.company if job else "Unknown Company",
                    ats_score=gen.get_average_ats_score(),
                    created_at=gen.created_at,
                    completed_at=gen.completed_at
                )
                summaries.append(summary)

            # Calculate statistics
            total = await self.generation_repo.count_by_user_id(user_id)
            statistics = await self._calculate_statistics(user_id)

            pagination = {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total,
                "has_previous": offset > 0
            }

            return GenerationListResponse(
                generations=summaries,
                pagination=pagination,
                statistics=statistics
            )

        except Exception as e:
            logger.exception(f"Failed to get user generations for {user_id}: {e}")
            raise

    async def cancel_generation(self, generation_id: str, user_id: str) -> bool:
        """Cancel ongoing generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return False

            # Check if user owns this generation (through profile)
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return False

            if generation.status in [GenerationStatus.ANALYZING_JOB, GenerationStatus.COMPILING_PROFILE,
                                   GenerationStatus.GENERATING_DOCUMENTS, GenerationStatus.VALIDATING_QUALITY]:
                return False

            # Cancel background task
            if generation_id in self.active_generations:
                self.active_generations[generation_id].cancel()
                del self.active_generations[generation_id]

            # Update status
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.FAILED
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to cancel generation {generation_id}: {e}")
            return False

    async def regenerate(
        self,
        generation_id: str,
        user_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Optional[GenerationDTO]:
        """Regenerate document with updated options."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return None

            # Check ownership
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return None

            # Create new generation based on original
            new_generation_id = str(uuid.uuid4())
            new_generation = Generation.create(
                id=new_generation_id,
                profile_id=generation.profile_id,
                job_id=generation.job_id
            )

            await self.generation_repo.create(new_generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(new_generation_id)
            )
            self.active_generations[new_generation_id] = task

            await self.generation_repo.update_status(
                new_generation_id,
                GenerationStatus.ANALYZING_JOB
            )

            return await self._get_generation_dto(new_generation_id)

        except Exception as e:
            logger.exception(f"Failed to regenerate {generation_id}: {e}")
            return None

    async def get_generation_content(
        self,
        generation_id: str,
        user_id: str
    ) -> Optional[GenerationResultContent]:
        """Get detailed content of completed generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation:
                return None

            # Check ownership
            profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))
            if not profile or str(profile.user_id) != user_id:
                return None

            if not generation.is_completed():
                return None

            resume_result = generation.get_resume_result()
            if not resume_result:
                return None

            return GenerationResultContent(
                generation_id=generation.id,
                document_id=generation.id,  # Use generation ID as document ID
                document_type=DTODocumentType.RESUME,
                content={
                    'text': resume_result.content,
                    'html': f'<html><body>{resume_result.content}</body></html>',
                    'markdown': f'# Generated Resume\n\n{resume_result.content}'
                },
                ats_score=resume_result.ats_score,
                match_percentage=85,  # Mock value
                keyword_coverage=0.9,  # Mock value
                keywords_matched=15,  # Mock value
                keywords_total=18,  # Mock value
                pdf_url=f'/api/v1/documents/{generation_id}/download',
                recommendations=[],  # Mock empty list
                metadata=resume_result.metadata
            )

        except Exception as e:
            logger.exception(f"Failed to get generation content {generation_id}: {e}")
            return None

    async def _execute_generation_pipeline(self, generation_id: str) -> None:
        """Execute the 5-stage generation pipeline."""
        try:
            start_time = time.time()

            # Stage 1: Job Analysis
            await self._update_progress(generation_id, 1, "Job Analysis", "Analyzing job requirements")
            await asyncio.sleep(1)  # Simulate processing
            job_analysis = await self._stage1_analyze_job(generation_id)

            # Stage 2: Profile Compilation
            await self._update_progress(generation_id, 2, "Profile Compilation", "Scoring profile content")
            await asyncio.sleep(1.5)
            scored_profile = await self._stage2_compile_profile(generation_id, job_analysis)

            # Stage 3: Document Generation
            await self._update_progress(generation_id, 3, "Document Generation", "Creating tailored document")
            await asyncio.sleep(2)
            document_content = await self._stage3_generate_document(generation_id, scored_profile, job_analysis)

            # Stage 4: Quality Validation
            await self._update_progress(generation_id, 4, "Quality Validation", "Validating ATS compliance")
            await asyncio.sleep(1)
            validation_result = await self._stage4_validate_quality(generation_id, document_content)

            # Stage 5: PDF Export
            await self._update_progress(generation_id, 5, "PDF Export", "Generating professional PDF")
            await asyncio.sleep(1)
            pdf_result = await self._stage5_export_pdf(generation_id, document_content)

            # Complete generation
            generation_time = time.time() - start_time
            result = DomainGenerationResult(
                document_type=DocumentType.RESUME,
                content=document_content,
                ats_score=validation_result.get('ats_score', 0.85),
                word_count=len(document_content.split()),
                generated_at=datetime.utcnow(),
                metadata={
                    'generation_time': generation_time,
                    'pdf_url': pdf_result.get('pdf_url'),
                    'validation': validation_result
                }
            )

            generation = await self.generation_repo.get_by_id(generation_id)
            if generation:
                generation.add_result(result)
                generation.update_status(GenerationStatus.COMPLETED)

            await self.generation_repo.complete_generation(
                generation_id,
                {
                    'content': document_content,
                    'ats_score': validation_result.get('ats_score', 0.85),
                    'metadata': result.metadata
                },
                generation_time
            )

        except asyncio.CancelledError:
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.FAILED
            )
        except Exception as e:
            logger.exception(f"Generation pipeline failed for {generation_id}: {e}")
            await self.generation_repo.fail_generation(generation_id, str(e))
        finally:
            # Clean up active generation
            if generation_id in self.active_generations:
                del self.active_generations[generation_id]

    async def _stage1_analyze_job(self, generation_id: str) -> Dict[str, Any]:
        """Stage 1: Analyze job requirements."""
        generation = await self.generation_repo.get_by_id(generation_id)
        job = await self.job_repo.get_job_by_id(generation.job_id)

        # Mock job analysis
        return {
            'required_skills': ['python', 'fastapi', 'sqlalchemy'],
            'preferred_skills': ['docker', 'kubernetes', 'aws'],
            'experience_years': 3,
            'keywords': ['backend', 'api', 'database', 'rest'],
            'job_type': 'full-time',
            'location': job.location if job else 'remote'
        }

    async def _stage2_compile_profile(self, generation_id: str, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Compile and score profile content."""
        generation = await self.generation_repo.get_by_id(generation_id)
        profile = await self.profile_repo.get_by_id(uuid.UUID(generation.profile_id))

        # Mock profile scoring
        return {
            'scored_experiences': [
                {'experience': 'Senior Backend Developer', 'score': 0.9, 'relevance': 0.95}
            ],
            'scored_skills': [
                {'skill': 'Python', 'score': 0.95, 'required': True},
                {'skill': 'FastAPI', 'score': 0.9, 'required': True}
            ],
            'overall_match': 0.87,
            'strengths': ['Strong backend experience', 'Relevant tech stack'],
            'gaps': ['Limited cloud experience']
        }

    async def _stage3_generate_document(self, generation_id: str, scored_profile: Dict[str, Any], job_analysis: Dict[str, Any]) -> str:
        """Stage 3: Generate tailored document."""
        # Mock document generation
        return """John Doe
Senior Python Backend Developer

Professional Summary:
Experienced backend developer with 5+ years of experience building scalable APIs and AI-powered systems.

Skills:
- Python, FastAPI, SQLAlchemy
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS, Azure

Experience:
Senior Backend Developer
TechCorp Inc, Seattle, WA
2020 - Present

- Built scalable REST APIs serving 100k+ users
- Implemented AI-powered features using OpenAI GPT
- Led team of 5 developers on microservices architecture

Education:
BS Computer Science
University of Washington, 2019"""

    async def _stage4_validate_quality(self, generation_id: str, document_content: str) -> Dict[str, Any]:
        """Stage 4: Validate quality and ATS compliance."""
        # Mock validation
        return {
            'ats_score': 0.87,
            'match_percentage': 82,
            'keyword_coverage': 0.91,
            'keywords_matched': 15,
            'keywords_total': 18,
            'recommendations': [
                'Add AWS certification to skills section',
                'Quantify team size in leadership experience'
            ]
        }

    async def _stage5_export_pdf(self, generation_id: str, document_content: str) -> Dict[str, Any]:
        """Stage 5: Export to PDF."""
        # Mock PDF generation
        return {
            'pdf_url': f'/api/v1/documents/{generation_id}/download',
            'file_size': 245760,  # bytes
            'pages': 1
        }

    async def _update_progress(
        self,
        generation_id: str,
        stage: int,
        stage_name: str,
        stage_description: str
    ) -> None:
        """Update generation progress."""
        percentage = int((stage / 5) * 100)
        progress = {
            'current_stage': stage,
            'total_stages': 5,
            'percentage': percentage,
            'stage_name': stage_name,
            'stage_description': stage_description,
            'updated_at': datetime.utcnow().isoformat()
        }
        await self.generation_repo.update_progress(generation_id, progress)

    async def _get_generation_dto(self, generation_id: str) -> Optional[GenerationDTO]:
        """Convert generation entity to DTO."""
        generation = await self.generation_repo.get_by_id(generation_id)
        if not generation:
            return None

        progress = None
        if 'current_stage' in generation.pipeline_metadata:
            progress = GenerationProgress(**generation.pipeline_metadata)

        result = None
        resume_result = generation.get_resume_result()
        if resume_result:
            result = GenerationResult(
                document_id=generation_id,
                ats_score=resume_result.ats_score,
                match_percentage=85,  # Mock value
                keyword_coverage=0.9,  # Mock value
                pdf_url=f'/api/v1/documents/{generation_id}/download',
                recommendations=[],  # Mock empty list
            )

        return GenerationDTO(
            generation_id=generation.id,
            status=self._map_status_to_dto(generation.status),
            progress=progress,
            result=result,
            error_message=generation.error_message,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            tokens_used=7850,  # Mock value
            generation_time=generation.processing_time_seconds,
            created_at=generation.created_at,
            completed_at=generation.completed_at
        )

    def _map_status_to_dto(self, status: GenerationStatus) -> DTOGenerationStatus:
        """Map domain status to DTO status."""
        status_mapping = {
            GenerationStatus.PENDING: DTOGenerationStatus.PENDING,
            GenerationStatus.ANALYZING_JOB: DTOGenerationStatus.GENERATING,
            GenerationStatus.COMPILING_PROFILE: DTOGenerationStatus.GENERATING,
            GenerationStatus.GENERATING_DOCUMENTS: DTOGenerationStatus.GENERATING,
            GenerationStatus.VALIDATING_QUALITY: DTOGenerationStatus.GENERATING,
            GenerationStatus.EXPORTING_PDF: DTOGenerationStatus.GENERATING,
            GenerationStatus.COMPLETED: DTOGenerationStatus.COMPLETED,
            GenerationStatus.FAILED: DTOGenerationStatus.FAILED,
        }
        return status_mapping.get(status, DTOGenerationStatus.PENDING)

    async def _calculate_statistics(self, user_id: str) -> Dict[str, Any]:
        """Calculate generation statistics for user."""
        all_generations = await self.generation_repo.get_by_user_id(user_id, limit=1000)

        total = len(all_generations)
        completed = len([g for g in all_generations if g.is_completed()])
        failed = len([g for g in all_generations if g.is_failed()])
        in_progress = len([g for g in all_generations if g.status in [
            GenerationStatus.ANALYZING_JOB, GenerationStatus.COMPILING_PROFILE,
            GenerationStatus.GENERATING_DOCUMENTS, GenerationStatus.VALIDATING_QUALITY,
            GenerationStatus.EXPORTING_PDF
        ]])

        ats_scores = [
            g.get_average_ats_score() for g in all_generations
            if g.is_completed() and g.get_average_ats_score() is not None
        ]
        avg_ats_score = sum(ats_scores) / len(ats_scores) if ats_scores else 0

        return {
            'total_generations': total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'average_ats_score': round(avg_ats_score, 2)
        }

import asyncio
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

from app.application.dtos.generation_dtos import (
    GenerationDTO,
    GenerationStatus,
    GenerationProgress,
    GenerationResult,
    ResumeGenerationRequest,
    CoverLetterGenerationRequest,
    GenerationOptions,
    DocumentType,
    GenerationSummaryDTO,
    GenerationListResponse,
    GenerationResultContent
)
from app.domain.entities.generation import Generation
from app.domain.entities.profile import Profile
from app.domain.entities.job import JobPosting
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.core.config import settings
from app.core.logging import logger


class GenerationService:
    """Service for managing AI-powered document generation."""

    def __init__(
        self,
        generation_repo: GenerationRepository,
        profile_repo: ProfileRepository,
        job_repo: JobRepository
    ):
        self.generation_repo = generation_repo
        self.profile_repo = profile_repo
        self.job_repo = job_repo
        self.active_generations: Dict[str, asyncio.Task] = {}

    async def start_resume_generation(
        self,
        user_id: str,
        request: ResumeGenerationRequest
    ) -> GenerationDTO:
        """Start resume generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(request.profile_id)
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation(
                id=generation_id,
                user_id=user_id,
                profile_id=request.profile_id,
                job_id=request.job_id,
                document_type=DocumentType.RESUME,
                status=GenerationStatus.PENDING,
                options=request.options.dict() if request.options else None,
                created_at=datetime.utcnow()
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.GENERATING
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start resume generation: {e}")
            raise

    async def start_cover_letter_generation(
        self,
        user_id: str,
        request: CoverLetterGenerationRequest
    ) -> GenerationDTO:
        """Start cover letter generation process."""
        try:
            # Validate profile and job exist
            profile = await self.profile_repo.get_by_id(request.profile_id)
            if not profile:
                raise ValueError(f"Profile {request.profile_id} not found")

            job = await self.job_repo.get_by_id(request.job_id)
            if not job:
                raise ValueError(f"Job {request.job_id} not found")

            # Create generation record
            generation_id = str(uuid.uuid4())
            generation = Generation(
                id=generation_id,
                user_id=user_id,
                profile_id=request.profile_id,
                job_id=request.job_id,
                document_type=DocumentType.COVER_LETTER,
                status=GenerationStatus.PENDING,
                options=request.options.dict() if request.options else None,
                created_at=datetime.utcnow()
            )

            await self.generation_repo.create(generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(generation_id)
            )
            self.active_generations[generation_id] = task

            # Update status to generating
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.GENERATING
            )

            return await self._get_generation_dto(generation_id)

        except Exception as e:
            logger.exception(f"Failed to start cover letter generation: {e}")
            raise

    async def get_generation(self, generation_id: str) -> Optional[GenerationDTO]:
        """Get generation by ID."""
        try:
            return await self._get_generation_dto(generation_id)
        except Exception as e:
            logger.exception(f"Failed to get generation {generation_id}: {e}")
            return None

    async def get_user_generations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> GenerationListResponse:
        """Get user's generations with pagination."""
        try:
            generations = await self.generation_repo.get_by_user_id(
                user_id, limit, offset
            )

            # Convert to summary DTOs
            summaries = []
            for gen in generations:
                job = await self.job_repo.get_by_id(gen.job_id)
                summary = GenerationSummaryDTO(
                    generation_id=gen.id,
                    status=gen.status,
                    document_type=gen.document_type,
                    job_title=job.title if job else "Unknown Job",
                    company=job.company if job else "Unknown Company",
                    ats_score=gen.result.get('ats_score') if gen.result else None,
                    created_at=gen.created_at,
                    completed_at=gen.completed_at
                )
                summaries.append(summary)

            # Calculate statistics
            total = await self.generation_repo.count_by_user_id(user_id)
            statistics = await self._calculate_statistics(user_id)

            pagination = {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_next": (offset + limit) < total,
                "has_previous": offset > 0
            }

            return GenerationListResponse(
                generations=summaries,
                pagination=pagination,
                statistics=statistics
            )

        except Exception as e:
            logger.exception(f"Failed to get user generations for {user_id}: {e}")
            raise

    async def cancel_generation(self, generation_id: str, user_id: str) -> bool:
        """Cancel ongoing generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation or generation.user_id != user_id:
                return False

            if generation.status not in [GenerationStatus.PENDING, GenerationStatus.GENERATING]:
                return False

            # Cancel background task
            if generation_id in self.active_generations:
                self.active_generations[generation_id].cancel()
                del self.active_generations[generation_id]

            # Update status
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.CANCELLED
            )

            return True

        except Exception as e:
            logger.exception(f"Failed to cancel generation {generation_id}: {e}")
            return False

    async def regenerate(
        self,
        generation_id: str,
        user_id: str,
        options: Optional[GenerationOptions] = None
    ) -> Optional[GenerationDTO]:
        """Regenerate document with updated options."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation or generation.user_id != user_id:
                return None

            # Create new generation based on original
            new_generation_id = str(uuid.uuid4())
            new_generation = Generation(
                id=new_generation_id,
                user_id=user_id,
                profile_id=generation.profile_id,
                job_id=generation.job_id,
                document_type=generation.document_type,
                status=GenerationStatus.PENDING,
                options=options.dict() if options else generation.options,
                created_at=datetime.utcnow()
            )

            await self.generation_repo.create(new_generation)

            # Start background generation
            task = asyncio.create_task(
                self._execute_generation_pipeline(new_generation_id)
            )
            self.active_generations[new_generation_id] = task

            await self.generation_repo.update_status(
                new_generation_id,
                GenerationStatus.GENERATING
            )

            return await self._get_generation_dto(new_generation_id)

        except Exception as e:
            logger.exception(f"Failed to regenerate {generation_id}: {e}")
            return None

    async def get_generation_content(
        self,
        generation_id: str,
        user_id: str
    ) -> Optional[GenerationResultContent]:
        """Get detailed content of completed generation."""
        try:
            generation = await self.generation_repo.get_by_id(generation_id)
            if not generation or generation.user_id != user_id:
                return None

            if generation.status != GenerationStatus.COMPLETED or not generation.result:
                return None

            return GenerationResultContent(
                generation_id=generation.id,
                document_id=generation.result.get('document_id', ''),
                document_type=generation.document_type,
                content=generation.result.get('content', {}),
                ats_score=generation.result.get('ats_score', 0.0),
                match_percentage=generation.result.get('match_percentage', 0),
                keyword_coverage=generation.result.get('keyword_coverage', 0.0),
                keywords_matched=generation.result.get('keywords_matched', 0),
                keywords_total=generation.result.get('keywords_total', 0),
                pdf_url=generation.result.get('pdf_url', ''),
                recommendations=generation.result.get('recommendations', []),
                metadata=generation.result.get('metadata', {})
            )

        except Exception as e:
            logger.exception(f"Failed to get generation content {generation_id}: {e}")
            return None

    async def _execute_generation_pipeline(self, generation_id: str) -> None:
        """Execute the 5-stage generation pipeline."""
        try:
            start_time = time.time()

            # Stage 1: Job Analysis
            await self._update_progress(generation_id, 1, "Job Analysis", "Analyzing job requirements")
            await asyncio.sleep(1)  # Simulate processing
            job_analysis = await self._stage1_analyze_job(generation_id)

            # Stage 2: Profile Compilation
            await self._update_progress(generation_id, 2, "Profile Compilation", "Scoring profile content")
            await asyncio.sleep(1.5)
            scored_profile = await self._stage2_compile_profile(generation_id, job_analysis)

            # Stage 3: Document Generation
            await self._update_progress(generation_id, 3, "Document Generation", "Creating tailored document")
            await asyncio.sleep(2)
            document_content = await self._stage3_generate_document(generation_id, scored_profile, job_analysis)

            # Stage 4: Quality Validation
            await self._update_progress(generation_id, 4, "Quality Validation", "Validating ATS compliance")
            await asyncio.sleep(1)
            validation_result = await self._stage4_validate_quality(generation_id, document_content)

            # Stage 5: PDF Export
            await self._update_progress(generation_id, 5, "PDF Export", "Generating professional PDF")
            await asyncio.sleep(1)
            pdf_result = await self._stage5_export_pdf(generation_id, document_content)

            # Complete generation
            generation_time = time.time() - start_time
            result = {
                'document_id': str(uuid.uuid4()),
                'ats_score': validation_result.get('ats_score', 0.85),
                'match_percentage': validation_result.get('match_percentage', 82),
                'keyword_coverage': validation_result.get('keyword_coverage', 0.91),
                'keywords_matched': validation_result.get('keywords_matched', 15),
                'keywords_total': validation_result.get('keywords_total', 18),
                'pdf_url': pdf_result.get('pdf_url', f'/api/v1/documents/{generation_id}/download'),
                'recommendations': validation_result.get('recommendations', []),
                'content': document_content,
                'metadata': {
                    'generation_time': generation_time,
                    'tokens_used': 7850,
                    'template': 'modern'
                }
            }

            await self.generation_repo.complete_generation(
                generation_id,
                result,
                generation_time
            )

        except asyncio.CancelledError:
            await self.generation_repo.update_status(
                generation_id,
                GenerationStatus.CANCELLED
            )
        except Exception as e:
            logger.exception(f"Generation pipeline failed for {generation_id}: {e}")
            await self.generation_repo.fail_generation(generation_id, str(e))
        finally:
            # Clean up active generation
            if generation_id in self.active_generations:
                del self.active_generations[generation_id]

    async def _stage1_analyze_job(self, generation_id: str) -> Dict[str, Any]:
        """Stage 1: Analyze job requirements."""
        generation = await self.generation_repo.get_by_id(generation_id)
        job = await self.job_repo.get_by_id(generation.job_id)

        # Mock job analysis
        return {
            'required_skills': ['python', 'fastapi', 'sqlalchemy'],
            'preferred_skills': ['docker', 'kubernetes', 'aws'],
            'experience_years': 3,
            'keywords': ['backend', 'api', 'database', 'rest'],
            'job_type': 'full-time',
            'location': job.location if job else 'remote'
        }

    async def _stage2_compile_profile(self, generation_id: str, job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Compile and score profile content."""
        generation = await self.generation_repo.get_by_id(generation_id)
        profile = await self.profile_repo.get_by_id(generation.profile_id)

        # Mock profile scoring
        return {
            'scored_experiences': [
                {'experience': 'Senior Backend Developer', 'score': 0.9, 'relevance': 0.95}
            ],
            'scored_skills': [
                {'skill': 'Python', 'score': 0.95, 'required': True},
                {'skill': 'FastAPI', 'score': 0.9, 'required': True}
            ],
            'overall_match': 0.87,
            'strengths': ['Strong backend experience', 'Relevant tech stack'],
            'gaps': ['Limited cloud experience']
        }

    async def _stage3_generate_document(self, generation_id: str, scored_profile: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Generate tailored document."""
        # Mock document generation
        return {
            'text': 'Generated resume content...',
            'html': '<html><body>Generated resume...</body></html>',
            'markdown': '# Generated Resume\n\nContent here...'
        }

    async def _stage4_validate_quality(self, generation_id: str, document_content: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Validate quality and ATS compliance."""
        # Mock validation
        return {
            'ats_score': 0.87,
            'match_percentage': 82,
            'keyword_coverage': 0.91,
            'keywords_matched': 15,
            'keywords_total': 18,
            'recommendations': [
                'Add AWS certification to skills section',
                'Quantify team size in leadership experience'
            ]
        }

    async def _stage5_export_pdf(self, generation_id: str, document_content: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 5: Export to PDF."""
        # Mock PDF generation
        return {
            'pdf_url': f'/api/v1/documents/{generation_id}/download',
            'file_size': 245760,  # bytes
            'pages': 1
        }

    async def _update_progress(
        self,
        generation_id: str,
        stage: int,
        stage_name: str,
        stage_description: str
    ) -> None:
        """Update generation progress."""
        percentage = int((stage / 5) * 100)
        progress = GenerationProgress(
            current_stage=stage,
            total_stages=5,
            percentage=percentage,
            stage_name=stage_name,
            stage_description=stage_description
        )
        await self.generation_repo.update_progress(generation_id, progress.dict())

    async def _get_generation_dto(self, generation_id: str) -> Optional[GenerationDTO]:
        """Convert generation entity to DTO."""
        generation = await self.generation_repo.get_by_id(generation_id)
        if not generation:
            return None

        progress = None
        if generation.progress:
            progress = GenerationProgress(**generation.progress)

        result = None
        if generation.result:
            result = GenerationResult(**generation.result)

        return GenerationDTO(
            generation_id=generation.id,
            status=generation.status,
            progress=progress,
            result=result,
            error_message=generation.error_message,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            tokens_used=generation.tokens_used,
            generation_time=generation.generation_time,
            created_at=generation.created_at,
            completed_at=generation.completed_at
        )

    async def _calculate_statistics(self, user_id: str) -> Dict[str, Any]:
        """Calculate generation statistics for user."""
        all_generations = await self.generation_repo.get_by_user_id(user_id, limit=1000)

        total = len(all_generations)
        completed = len([g for g in all_generations if g.status == GenerationStatus.COMPLETED])
        failed = len([g for g in all_generations if g.status == GenerationStatus.FAILED])
        in_progress = len([g for g in all_generations if g.status in [GenerationStatus.PENDING, GenerationStatus.GENERATING]])

        ats_scores = [
            g.result.get('ats_score', 0) for g in all_generations
            if g.status == GenerationStatus.COMPLETED and g.result
        ]
        avg_ats_score = sum(ats_scores) / len(ats_scores) if ats_scores else 0

        return {
            'total_generations': total,
            'completed': completed,
            'failed': failed,
            'in_progress': in_progress,
            'average_ats_score': round(avg_ats_score, 2)
        } - Provider-agnostic orchestration