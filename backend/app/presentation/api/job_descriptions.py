"""Job Description API - Simplified CRUD endpoints"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos.job_description_dtos import (
    CreateJobDescriptionRequest,
    UpdateJobDescriptionRequest,
    JobDescriptionResponse,
    JobDescriptionListResponse
)
from ...application.services.job_description_parser import JobDescriptionParser
from ...core.dependencies import get_db_session, get_current_user
from ...domain.entities.user import User
from ...infrastructure.repositories.job_description_repository import JobDescriptionRepository

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])


# Dependency to get repository with parser
async def get_job_description_repository(
    session: AsyncSession = Depends(get_db_session)
) -> JobDescriptionRepository:
    """Get job description repository instance with parser"""
    parser = JobDescriptionParser()
    return JobDescriptionRepository(session, parser)


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    request: CreateJobDescriptionRequest,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_job_description_repository)
):
    """
    Create job description from raw text or structured data.

    Accepts:
    1. raw_text: Plain text job posting (will be auto-parsed)
    2. Structured fields: Pre-parsed job details

    **Use case 1 - User copy-paste:**
    ```json
    {
      "raw_text": "Senior Engineer\\nTechCorp\\nSan Francisco...",
      "source": "user_created"
    }
    ```

    **Use case 2 - External API save:**
    ```json
    {
      "title": "Senior Engineer",
      "company": "TechCorp",
      "description": "...",
      "source": "saved_external",
      "external_id": "indeed_12345"
    }
    ```
    """
    try:
        job_desc = await repo.create(user_id=str(current_user.id), data=request)
        return job_desc
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job description: {str(e)}"
        )


@router.get("/", response_model=JobDescriptionListResponse)
async def list_job_descriptions(
    status_filter: Optional[str] = Query(None, pattern="^(active|archived)$", description="Filter by status"),
    source: Optional[str] = Query(None, pattern="^(user_created|saved_external)$", description="Filter by source"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_job_description_repository)
):
    """
    List user's job descriptions with optional filters.

    Query parameters:
    - **status**: Filter by status (active, archived)
    - **source**: Filter by source (user_created, saved_external)
    - **limit**: Items per page (1-100, default: 20)
    - **offset**: Pagination offset (default: 0)
    """
    try:
        jobs = await repo.list_by_user(
            user_id=str(current_user.id),
            status=status_filter,
            source=source,
            limit=limit,
            offset=offset
        )
        total = await repo.count_by_user(str(current_user.id), status_filter, source)

        return JobDescriptionListResponse(
            jobs=jobs,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit < total)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list job descriptions: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_job_description_repository)
):
    """
    Get job description details by ID.

    Returns 404 if job not found.
    Returns 403 if job doesn't belong to current user.
    """
    try:
        job = await repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        if job.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job description: {str(e)}"
        )


@router.put("/{job_id}", response_model=JobDescriptionResponse)
async def update_job_description(
    job_id: str,
    request: UpdateJobDescriptionRequest,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_job_description_repository)
):
    """
    Update job description.

    All fields are optional. Only provided fields will be updated.

    Returns 404 if job not found.
    Returns 403 if job doesn't belong to current user.
    """
    try:
        # Verify ownership
        job = await repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        if job.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Update job
        updated = await repo.update(job_id, request)
        return updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job description: {str(e)}"
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_description(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: JobDescriptionRepository = Depends(get_job_description_repository)
):
    """
    Delete job description (soft delete - sets status to 'deleted').

    Returns 404 if job not found.
    Returns 403 if job doesn't belong to current user.
    """
    try:
        # Verify ownership
        job = await repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found"
            )

        if job.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Delete job
        await repo.delete(job_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job description: {str(e)}"
        )
