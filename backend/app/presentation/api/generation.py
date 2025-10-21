# Generation API Router

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.generation_dtos import (
    ResumeGenerationRequest,
    CoverLetterGenerationRequest,
    GenerationDTO,
    GenerationListResponse,
    GenerationResultContent,
    RegenerateRequest,
    TemplatesResponse,
    ResumeTemplateDTO,
    GenerationStatus,
    GenerationProgress,
    GenerationResult,
    DocumentType,
    GenerationSummaryDTO
)
from app.core.dependencies import get_db_session, get_current_user
from app.domain.entities.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/generations",
    tags=["generations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/resume", response_model=GenerationDTO)
async def start_resume_generation(
    request: ResumeGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationDTO:
    """
    Start resume generation process.

    This endpoint initiates the 5-stage AI pipeline for generating a tailored resume:
    1. Job Analysis - Extract requirements from job description
    2. Profile Compilation - Score and rank profile content by relevance
    3. Document Generation - Create tailored resume content
    4. Quality Validation - Validate ATS compliance and quality
    5. PDF Export - Generate professional PDF document
    """
    try:
        # Mock implementation - in real implementation, this would use GenerationService
        from uuid import uuid4
        from datetime import datetime

        generation_id = str(uuid4())

        # Mock response
        return GenerationDTO(
            generation_id=generation_id,
            status=GenerationStatus.GENERATING,
            progress=GenerationProgress(
                current_stage=1,
                total_stages=5,
                percentage=20,
                stage_name="Job Analysis",
                stage_description="Analyzing job requirements"
            ),
            result=None,
            error_message=None,
            profile_id=request.profile_id,
            job_id=request.job_id,
            tokens_used=0,
            generation_time=None,
            created_at=datetime.utcnow(),
            completed_at=None
        )

    except Exception as e:
        logger.exception(f"Failed to start resume generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/cover-letter", response_model=GenerationDTO)
async def start_cover_letter_generation(
    request: CoverLetterGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationDTO:
    """
    Start cover letter generation process.

    This endpoint initiates the 5-stage AI pipeline for generating a tailored cover letter.
    """
    try:
        # Mock implementation
        from uuid import uuid4
        from datetime import datetime

        generation_id = str(uuid4())

        return GenerationDTO(
            generation_id=generation_id,
            status=GenerationStatus.GENERATING,
            progress=GenerationProgress(
                current_stage=1,
                total_stages=5,
                percentage=20,
                stage_name="Job Analysis",
                stage_description="Analyzing job requirements"
            ),
            result=None,
            error_message=None,
            profile_id=request.profile_id,
            job_id=request.job_id,
            tokens_used=0,
            generation_time=None,
            created_at=datetime.utcnow(),
            completed_at=None
        )

    except Exception as e:
        logger.exception(f"Failed to start cover letter generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{generation_id}", response_model=GenerationDTO)
async def get_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationDTO:
    """Get generation status and details by ID."""
    try:
        # Mock implementation - return completed generation
        from datetime import datetime

        return GenerationDTO(
            generation_id=generation_id,
            status=GenerationStatus.COMPLETED,
            progress=None,
            result=GenerationResult(
                document_id=generation_id,
                ats_score=0.87,
                match_percentage=82,
                keyword_coverage=0.91,
                pdf_url=f"/api/v1/documents/{generation_id}/download",
                recommendations=[
                    "Add AWS certification to skills",
                    "Quantify team size in leadership experience"
                ]
            ),
            error_message=None,
            profile_id="profile-uuid",
            job_id="job-uuid",
            tokens_used=7850,
            generation_time=5.2,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )

    except Exception as e:
        logger.exception(f"Failed to get generation {generation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=GenerationListResponse)
async def list_generations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationListResponse:
    """List user's generations with pagination."""
    try:
        # Mock implementation
        from datetime import datetime

        return GenerationListResponse(
            generations=[
                GenerationSummaryDTO(
                    generation_id="gen-uuid-1",
                    status=GenerationStatus.COMPLETED,
                    document_type=DocumentType.RESUME,
                    job_title="Senior Python Developer",
                    company="TechCorp",
                    ats_score=0.87,
                    created_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
            ],
            pagination={
                "total": 1,
                "limit": limit,
                "offset": offset,
                "has_next": False,
                "has_previous": False
            },
            statistics={
                "total_generations": 1,
                "completed": 1,
                "failed": 0,
                "in_progress": 0,
                "average_ats_score": 0.87
            }
        )

    except Exception as e:
        logger.exception("Failed to list generations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{generation_id}")
async def cancel_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """Cancel ongoing generation."""
    try:
        # Mock implementation
        return {"message": "Generation cancelled successfully"}

    except Exception as e:
        logger.exception(f"Failed to cancel generation {generation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{generation_id}/regenerate", response_model=GenerationDTO)
async def regenerate_document(
    generation_id: str,
    request: RegenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationDTO:
    """Regenerate document with updated options."""
    try:
        # Mock implementation
        from uuid import uuid4
        from datetime import datetime

        new_generation_id = str(uuid4())

        return GenerationDTO(
            generation_id=new_generation_id,
            status=GenerationStatus.GENERATING,
            progress=GenerationProgress(
                current_stage=1,
                total_stages=5,
                percentage=20,
                stage_name="Job Analysis",
                stage_description="Analyzing job requirements"
            ),
            result=None,
            error_message=None,
            profile_id="profile-uuid",
            job_id="job-uuid",
            tokens_used=0,
            generation_time=None,
            created_at=datetime.utcnow(),
            completed_at=None
        )

    except Exception as e:
        logger.exception(f"Failed to regenerate {generation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{generation_id}/content", response_model=GenerationResultContent)
async def get_generation_content(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> GenerationResultContent:
    """Get detailed content of completed generation."""
    try:
        # Mock implementation
        return GenerationResultContent(
            generation_id=generation_id,
            document_id=generation_id,
            document_type=DocumentType.RESUME,
            content={
                "text": "Generated resume content...",
                "html": "<html><body>Generated resume...</body></html>",
                "markdown": "# Generated Resume\n\nContent here..."
            },
            ats_score=0.87,
            match_percentage=82,
            keyword_coverage=0.91,
            keywords_matched=15,
            keywords_total=18,
            pdf_url=f"/api/v1/documents/{generation_id}/download",
            recommendations=[
                "Add AWS certification to skills section",
                "Quantify team size in leadership experience"
            ],
            metadata={
                "template": "modern",
                "tokens_used": 7850,
                "generation_time": 5.2
            }
        )

    except Exception as e:
        logger.exception(f"Failed to get generation content {generation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/templates/", response_model=TemplatesResponse)
async def get_resume_templates(
    current_user: User = Depends(get_current_user)
) -> TemplatesResponse:
    """Get available resume templates."""
    try:
        # Mock implementation
        return TemplatesResponse(
            templates=[
                ResumeTemplateDTO(
                    id="modern",
                    name="Modern",
                    description="Clean, contemporary design",
                    preview_url="/templates/modern/preview.png",
                    recommended_for=["tech", "startup"],
                    ats_friendly=True
                ),
                ResumeTemplateDTO(
                    id="professional",
                    name="Professional",
                    description="Traditional corporate style",
                    preview_url="/templates/professional/preview.png",
                    recommended_for=["finance", "consulting"],
                    ats_friendly=True
                )
            ]
        )

    except Exception as e:
        logger.exception("Failed to get resume templates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")