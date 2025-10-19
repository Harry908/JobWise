"""Job description API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos.job_description_dtos import (
    CreateJobDescriptionDTO,
    UpdateJobDescriptionDTO,
    JobDescriptionDTO,
    JobDescriptionSummaryDTO,
    JobDescriptionListDTO,
    JobDescriptionSearchDTO,
    JobDescriptionAnalyticsDTO,
    ParseJobDescriptionDTO,
    ActivateJobDescriptionDTO,
    ArchiveJobDescriptionDTO,
)
from ...application.services.job_description_service import JobDescriptionService
from ...core.dependencies import get_db_session, get_current_user
from ...domain.entities.user import User
from ...infrastructure.repositories.job_description_repository import JobDescriptionRepository

from ...domain.entities.job_description import JobDescriptionSource

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


# Dependency to get job description service
async def get_job_description_service(session: AsyncSession = Depends(get_db_session)) -> JobDescriptionService:
    """Get job description service instance."""
    repository = JobDescriptionRepository(session)
    return JobDescriptionService(repository)


@router.post("", response_model=JobDescriptionDTO, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    job_description_data: CreateJobDescriptionDTO,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Create a new custom job description.

    - **title**: Job title (required)
    - **company**: Company name (required)
    - **description**: Job description text (required)
    - **requirements**: List of job requirements (optional)
    - **benefits**: List of job benefits (optional)
    - **source**: Source of the job description (manual, scraped, uploaded)
    - **metadata**: Additional metadata (optional)
    - **created_from_url**: URL where job was found (optional)
    """
    try:
        # Convert source string to enum
        source_enum = JobDescriptionSource(job_description_data.source)

        job_description = await service.create_job_description(
            user_id=current_user.id,
            title=job_description_data.title,
            company=job_description_data.company,
            description=job_description_data.description,
            requirements=job_description_data.requirements,
            benefits=job_description_data.benefits,
            source=source_enum,
            metadata=job_description_data.metadata,
            created_from_url=str(job_description_data.created_from_url) if job_description_data.created_from_url else None,
        )

        return JobDescriptionDTO(**job_description.to_dict())

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("", response_model=JobDescriptionListDTO)
async def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
    query: Optional[str] = Query(None, description="Search query"),
    status_filter: Optional[str] = Query(None, description="Filter by status (draft, active, archived)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    include_archived: bool = Query(False, description="Include archived job descriptions"),
) -> JobDescriptionListDTO:
    """
    List user's job descriptions with optional filtering and pagination.

    - **query**: Search in title, company, and description
    - **status_filter**: Filter by status
    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip
    - **include_archived**: Include archived job descriptions
    """
    try:
        # Get job descriptions
        if query or status_filter:
            job_descriptions = await service.search_job_descriptions(
                user_id=current_user.id,
                query=query,
                status=status_filter,
                limit=limit,
                offset=offset
            )
        else:
            job_descriptions = await service.get_user_job_descriptions(
                user_id=current_user.id,
                include_archived=include_archived
            )

        # Apply pagination if not already done by search
        if not (query or status_filter):
            job_descriptions = job_descriptions[offset:offset + limit]

        # Convert to summary DTOs
        items = []
        for jd in job_descriptions:
            items.append(JobDescriptionSummaryDTO(
                id=jd.id,
                user_id=jd.user_id,
                title=jd.title,
                company=jd.company,
                status=jd.status.value,
                version=jd.version,
                created_at=jd.created_at.isoformat(),
                updated_at=jd.updated_at.isoformat(),
                keywords_count=len(jd.metadata.keywords),
                technical_skills_count=len(jd.metadata.technical_skills),
                requirements_count=len(jd.requirements)
            ))

        # Get total count
        total = await service.get_job_description_count(current_user.id)
        if not include_archived:
            # Count only active ones
            total = len([jd for jd in await service.get_user_job_descriptions(current_user.id, include_archived=False)])

        return JobDescriptionListDTO(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{job_description_id}", response_model=JobDescriptionDTO)
async def get_job_description(
    job_description_id: UUID,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Get a specific job description by ID.

    - **job_description_id**: UUID of the job description
    """
    try:
        job_description = await service.get_job_description(job_description_id)
        if not job_description:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")

        # Check ownership
        if job_description.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        return JobDescriptionDTO(**job_description.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/{job_description_id}", response_model=JobDescriptionDTO)
async def update_job_description(
    job_description_id: UUID,
    job_description_data: UpdateJobDescriptionDTO,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Update an existing job description.

    - **job_description_id**: UUID of the job description to update
    - **title**: New job title (optional)
    - **company**: New company name (optional)
    - **description**: New job description (optional)
    - **requirements**: New requirements list (optional)
    - **benefits**: New benefits list (optional)
    - **metadata**: New metadata (optional)
    """
    try:
        # Check if job description exists and user owns it
        existing = await service.get_job_description(job_description_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        if existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        job_description = await service.update_job_description(
            job_description_id=job_description_id,
            title=job_description_data.title,
            company=job_description_data.company,
            description=job_description_data.description,
            requirements=job_description_data.requirements,
            benefits=job_description_data.benefits,
            metadata=job_description_data.metadata,
        )

        return JobDescriptionDTO(**job_description.to_dict())

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{job_description_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(
    job_description_id: UUID,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
):
    """
    Delete a job description.

    - **job_description_id**: UUID of the job description to delete
    """
    try:
        # Check if job description exists and user owns it
        existing = await service.get_job_description(job_description_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        if existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        await service.delete_job_description(job_description_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{job_description_id}/parse", response_model=JobDescriptionDTO)
async def parse_job_description(
    job_description_id: UUID,
    parse_data: ParseJobDescriptionDTO,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Parse job description to extract keywords and update metadata.

    - **job_description_id**: UUID of the job description to parse
    """
    try:
        # Check if job description exists and user owns it
        existing = await service.get_job_description(job_description_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        if existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        job_description = await service.parse_job_description(job_description_id)

        return JobDescriptionDTO(**job_description.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{job_description_id}/activate", response_model=JobDescriptionDTO)
async def activate_job_description(
    job_description_id: UUID,
    activate_data: ActivateJobDescriptionDTO,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Activate a job description.

    - **job_description_id**: UUID of the job description to activate
    """
    try:
        # Check if job description exists and user owns it
        existing = await service.get_job_description(job_description_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        if existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        job_description = await service.activate_job_description(job_description_id)

        return JobDescriptionDTO(**job_description.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{job_description_id}/archive", response_model=JobDescriptionDTO)
async def archive_job_description(
    job_description_id: UUID,
    archive_data: ArchiveJobDescriptionDTO,
    current_user: User = Depends(get_current_user),
    service: JobDescriptionService = Depends(get_job_description_service),
) -> JobDescriptionDTO:
    """
    Archive a job description.

    - **job_description_id**: UUID of the job description to archive
    """
    try:
        # Check if job description exists and user owns it
        existing = await service.get_job_description(job_description_id)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        if existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        job_description = await service.archive_job_description(job_description_id)

        return JobDescriptionDTO(**job_description.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")