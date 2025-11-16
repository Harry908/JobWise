"""Generation API routes."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.generation_service import GenerationService
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.application.dtos.generation import (
    GenerateResumeRequest,
    GenerateCoverLetterRequest,
    RegenerateRequest,
    GenerationResponse,
    GenerationDetailResultResponse,
    GenerationListResponse,
    GenerationListItemDTO,
    PaginationDTO,
    TemplateListResponse,
    TemplateDTO,
    GenerationProgressDTO,
    GenerationResultDTO,
    GenerationOptionsDTO
)
from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ForbiddenException, ValidationException
from app.infrastructure.database.connection import get_db_session


router = APIRouter(prefix="/api/v1/generations", tags=["Generations"])


def _generation_to_response(generation, include_job_info: bool = False) -> GenerationResponse:
    """Convert generation entity to response DTO."""
    # Calculate estimated completion time (6 seconds average)
    estimated_completion = None
    if generation.is_processing():
        estimated_delta = timedelta(seconds=6)
        estimated_completion = (generation.created_at + estimated_delta).isoformat() + "Z"

    # Convert result if present
    result_dto = None
    if generation.result:
        result_dto = GenerationResultDTO(
            document_id=generation.result.document_id,
            ats_score=generation.result.ats_score,
            match_percentage=generation.result.match_percentage,
            keyword_coverage=generation.result.keyword_coverage,
            keywords_matched=generation.result.keywords_matched,
            keywords_total=generation.result.keywords_total,
            pdf_url=generation.result.pdf_url,
            recommendations=generation.result.recommendations
        )

    return GenerationResponse(
        id=generation.id,  # CRITICAL: Use 'id' not 'generation_id'
        status=generation.status,
        progress=GenerationProgressDTO(
            current_stage=generation.current_stage,
            total_stages=generation.total_stages,
            percentage=generation.get_progress().percentage,
            stage_name=generation.stage_name,
            stage_description=generation.stage_description
        ),
        profile_id=generation.profile_id,
        job_id=generation.job_id,
        document_type=generation.document_type,
        result=result_dto,
        error_message=generation.error_message,
        tokens_used=generation.tokens_used,
        generation_time=generation.generation_time,
        estimated_completion=estimated_completion,
        created_at=generation.created_at.isoformat() + "Z",
        started_at=generation.started_at.isoformat() + "Z" if generation.started_at else None,
        completed_at=generation.completed_at.isoformat() + "Z" if generation.completed_at else None,
        updated_at=generation.updated_at.isoformat() + "Z" if generation.updated_at else None
    )


@router.post("/resume", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def start_resume_generation(
    request: GenerateResumeRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Start resume generation.

    Creates a new generation request and begins the 5-stage AI pipeline.
    The generation runs asynchronously, and clients should poll the status endpoint.

    **Rate Limit**: 10 generations per hour
    """
    try:
        service = GenerationService(db)

        # Validate profile and job ownership
        profile_repo = ProfileRepository(db)
        job_repo = JobRepository(db)
        
        # Check if profile belongs to user
        profile = await profile_repo.get_by_id(request.profile_id)
        if not profile or profile.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Profile not found or does not belong to user"
            )
        
        # Check if job exists
        job = await job_repo.get_by_id(request.job_id)
        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found"
            )

        # Convert DTO options to entity options
        options = None
        if request.options:
            from app.domain.entities.generation import GenerationOptions
            options = GenerationOptions(
                template=request.options.template,
                length=request.options.length,
                focus_areas=request.options.focus_areas,
                include_cover_letter=request.options.include_cover_letter,
                custom_instructions=request.options.custom_instructions
            )

        generation = await service.start_resume_generation(
            user_id=user_id,
            profile_id=request.profile_id,
            job_id=request.job_id,
            options=options
        )

        response = _generation_to_response(generation)

        # Add Location header
        headers = {"Location": f"/api/v1/generations/{generation.id}"}

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.model_dump(),
            headers=headers
        )

    except ValidationException as e:
        if e.error_code == "rate_limit_exceeded":
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": e.error_code,
                        "message": e.message,
                        "details": e.details
                    }
                }
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.post("/cover-letter", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def start_cover_letter_generation(
    request: GenerateCoverLetterRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Start cover letter generation.

    Creates a new cover letter generation request.
    """
    try:
        service = GenerationService(db)

        # Convert DTO options to entity options
        options = None
        if request.options:
            from app.domain.entities.generation import GenerationOptions
            options = GenerationOptions(
                template=request.options.template,
                length=request.options.length,
                focus_areas=request.options.focus_areas,
                include_cover_letter=request.options.include_cover_letter,
                custom_instructions=request.options.custom_instructions
            )

        generation = await service.start_cover_letter_generation(
            user_id=user_id,
            profile_id=request.profile_id,
            job_id=request.job_id,
            options=options
        )

        response = _generation_to_response(generation)

        headers = {"Location": f"/api/v1/generations/{generation.id}"}

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.model_dump(),
            headers=headers
        )

    except ValidationException as e:
        if e.error_code == "rate_limit_exceeded":
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": {"code": e.error_code, "message": e.message, "details": e.details}}
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List available resume templates.

    Returns template information including previews and ATS compatibility.
    """
    service = GenerationService(db)
    templates_data = service.get_templates()

    templates = [TemplateDTO(**template) for template in templates_data]

    return TemplateListResponse(templates=templates)


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation_status(
    generation_id: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get generation status and progress.

    Poll this endpoint every 2 seconds to track generation progress.
    Returns current stage, percentage complete, and estimated completion time.
    """
    try:
        service = GenerationService(db)
        generation = await service.get_generation_status(generation_id, user_id)
        return _generation_to_response(generation)

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.get("/{generation_id}/result", response_model=GenerationDetailResultResponse)
async def get_generation_result(
    generation_id: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Get final generation result with full content.

    Only available for completed generations.
    Returns document content in multiple formats (text, HTML, markdown).
    """
    try:
        service = GenerationService(db)
        generation = await service.get_generation_result(generation_id, user_id)

        if not generation.result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Generation result not available"
            )

        return GenerationDetailResultResponse(
            id=generation.id,
            document_id=generation.result.document_id,
            document_type=generation.document_type,
            content=generation.result.content or {},
            ats_score=generation.result.ats_score,
            match_percentage=generation.result.match_percentage,
            keyword_coverage=generation.result.keyword_coverage,
            keywords_matched=generation.result.keywords_matched or 0,
            keywords_total=generation.result.keywords_total or 0,
            pdf_url=generation.result.pdf_url,
            recommendations=generation.result.recommendations,
            metadata={
                "template": generation.options.template if generation.options else "modern",
                "tokens_used": generation.tokens_used,
                "generation_time": generation.generation_time
            }
        )

    except ValidationException as e:
        # Handle specific error codes with appropriate HTTP status codes
        if e.error_code == "generation_failed":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {
                        "code": e.error_code,
                        "message": e.message,
                        "details": e.details
                    }
                }
            )
        elif e.error_code == "generation_not_completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # 409 Conflict for "not ready yet"
                detail={
                    "error": {
                        "code": e.error_code,
                        "message": e.message,
                        "details": e.details
                    }
                }
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.post("/{generation_id}/regenerate", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def regenerate_with_new_options(
    generation_id: str,
    request: RegenerateRequest,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Regenerate with updated options.

    Creates a new generation based on the original, with optional updated options.
    Returns a new generation with a new ID.
    """
    try:
        service = GenerationService(db)

        # Convert DTO options to entity options
        new_options = None
        if request.options:
            from app.domain.entities.generation import GenerationOptions
            new_options = GenerationOptions(
                template=request.options.template,
                length=request.options.length,
                focus_areas=request.options.focus_areas,
                include_cover_letter=request.options.include_cover_letter,
                custom_instructions=request.options.custom_instructions
            )

        generation = await service.regenerate(generation_id, user_id, new_options)

        response = _generation_to_response(generation)

        headers = {"Location": f"/api/v1/generations/{generation.id}"}

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=response.model_dump(),
            headers=headers
        )

    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e.detail))
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.delete("/{generation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_or_delete_generation(
    generation_id: str,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Cancel ongoing generation or delete completed generation.

    If generation is in progress, it will be cancelled.
    Otherwise, the generation record will be deleted.
    """
    try:
        service = GenerationService(db)
        generation = await service.get_generation_status(generation_id, user_id)

        if generation.can_cancel():
            await service.cancel_generation(generation_id, user_id)
        else:
            await service.delete_generation(generation_id, user_id)

        return None

    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
    except ForbiddenException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e.detail))


@router.get("", response_model=GenerationListResponse)
async def list_generations(
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    List user's generations with optional filters.

    Supports filtering by job, status, and document type.
    Returns paginated results with statistics.
    """
    try:
        service = GenerationService(db)

        generations, total = await service.list_generations(
            user_id=user_id,
            job_id=job_id,
            status=status,
            document_type=document_type,
            limit=limit,
            offset=offset
        )

        # Get statistics
        statistics = await service.get_statistics(user_id)

        # Convert to DTOs
        job_repo = JobRepository(db)
        items = []
        for gen in generations:
            # Fetch job information
            job = await job_repo.get_by_id(gen.job_id) if gen.job_id else None
            job_title = job.title if job else "Unknown Job"
            company = job.company if job else "Unknown Company"
            
            items.append(GenerationListItemDTO(
                id=gen.id,
                status=gen.status,
                document_type=gen.document_type,
                job_title=job_title,
                company=company,
                ats_score=gen.result.ats_score if gen.result else None,
                created_at=gen.created_at.isoformat() + "Z",
                completed_at=gen.completed_at.isoformat() + "Z" if gen.completed_at else None
            ))

        # Create pagination metadata
        has_next = (offset + limit) < total
        has_previous = offset > 0

        pagination = PaginationDTO(
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
            has_previous=has_previous
        )

        return GenerationListResponse(
            generations=items,
            pagination=pagination,
            statistics=statistics
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
