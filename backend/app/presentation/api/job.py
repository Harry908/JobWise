"""Job API endpoints."""

from typing import Annotated, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from app.application.services.job_service import JobService
from app.core.dependencies import get_current_user, get_job_service
from app.domain.entities.job import Job


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


# Request/Response models
class JobCreateFromText(BaseModel):
    """Request model for creating job from raw text."""
    raw_text: str = Field(..., min_length=10, max_length=15000, description="Raw job description text")


class JobCreateFromURL(BaseModel):
    """Request model for creating job from URL."""
    url: str = Field(..., min_length=10, max_length=500, description="Job posting URL")


class JobCreateStructured(BaseModel):
    """Request model for creating job with structured data."""
    source: str = Field(default="user_created", description="Job source")
    title: str = Field(..., min_length=1, max_length=200, description="Job title")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    description: Optional[str] = Field(None, max_length=10000, description="Job description")
    requirements: Optional[List[str]] = Field(default=None, description="Job requirements")
    benefits: Optional[List[str]] = Field(default=None, description="Job benefits")
    salary_range: Optional[str] = Field(None, max_length=100, description="Salary range")
    remote: Optional[bool] = Field(default=False, description="Remote work option")
    employment_type: Optional[str] = Field(default="full_time", pattern="^(full_time|part_time|contract|temporary|internship)$", description="Employment type")
    status: Optional[str] = Field(default="active", pattern="^(active|archived|draft)$", description="Job status")


class JobUpdateRequest(BaseModel):
    """Request model for updating job."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Job title")
    company: Optional[str] = Field(None, min_length=1, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    description: Optional[str] = Field(None, max_length=10000, description="Job description")
    status: Optional[str] = Field(None, pattern="^(active|archived|draft)$", description="Job status")
    application_status: Optional[str] = Field(None, pattern="^(not_applied|preparing|applied|interviewing|offer_received|accepted|rejected|withdrawn)$", description="Application status")
    applied_date: Optional[str] = Field(None, description="Date applied (ISO 8601 format)")
    notes: Optional[str] = Field(None, max_length=5000, description="Personal notes about the job")


class JobDeleteResponse(BaseModel):
    """Response model for job deletion."""
    message: str = Field(..., description="Success message")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    limit: int
    offset: int
    total: int
    has_more: bool = Field(alias="hasMore")
    
    class Config:
        populate_by_name = True


class JobListResponse(BaseModel):
    """Response model for job lists."""
    jobs: List[Job]
    total: int
    pagination: PaginationMeta


class BrowseJobListResponse(BaseModel):
    """Response model for browse jobs."""
    jobs: List[Job]
    total: int
    pagination: PaginationMeta


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: Union[JobCreateFromText, JobCreateFromURL, JobCreateStructured],
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Create a new job posting.
    
    Supports three input methods:
    - **raw_text**: Paste job description text for AI-powered parsing
    - **url**: Provide URL to fetch and parse job details
    - **Structured**: Provide all fields directly (no parsing needed)
    
    Returns the created job with parsed details including keywords,
    requirements, benefits, and salary information.
    
    Raises:
    - **422 Unprocessable Entity**: Invalid input format or missing required fields
    """
    try:
        # Check if request has raw_text or url
        if isinstance(request, JobCreateFromText):
            # Create from text
            return await service.create_from_text(
                user_id=user_id,
                raw_text=request.raw_text
            )
        elif isinstance(request, JobCreateFromURL):
            # Create from URL
            return await service.create_from_url(
                user_id=user_id,
                url=request.url
            )
        elif isinstance(request, JobCreateStructured):
            # Create from structured data
            return await service.create_structured(
                user_id=user_id,
                source=request.source,
                title=request.title,
                company=request.company,
                location=request.location,
                description=request.description,
                requirements=request.requirements or [],
                benefits=request.benefits or [],
                salary_range=request.salary_range,
                remote=request.remote or False,
                employment_type=request.employment_type or "full_time",
                status=request.status or "active"
            )
        else:
            # Handle either type based on fields present
            request_dict = request.model_dump()
            if "raw_text" in request_dict and request_dict["raw_text"]:
                return await service.create_from_text(
                    user_id=user_id,
                    raw_text=request_dict["raw_text"]
                )
            elif "url" in request_dict and request_dict["url"]:
                return await service.create_from_url(
                    user_id=user_id,
                    url=request_dict["url"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Either 'raw_text', 'url', or structured fields must be provided"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("", response_model=JobListResponse)
async def get_user_jobs(
    status_filter: Annotated[Optional[str], Query(alias="status", pattern="^(active|archived|draft)$", description="Filter by job status")] = None,
    source: Annotated[Optional[str], Query(pattern="^(user_created|indeed|linkedin|glassdoor|mock|imported|url_import)$", description="Filter by job source")] = None,
    employment_type: Annotated[Optional[str], Query(pattern="^(full_time|part_time|contract|temporary|internship)$", description="Filter by employment type")] = None,
    remote: Annotated[Optional[bool], Query(description="Filter remote jobs only")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum results per page")] = 20,
    offset: Annotated[int, Query(ge=0, description="Pagination offset")] = 0,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> JobListResponse:
    """
    Get list of user's saved jobs with filtering and pagination.
    
    Query parameters:
    - **status**: Filter by status (active, archived, draft)
    - **source**: Filter by source (user_created, text_parsed, url_scraped)
    - **employment_type**: Filter by type (full_time, part_time, contract, etc.)
    - **remote**: Filter remote jobs only
    - **limit**: Max results (1-100, default 20)
    - **offset**: Pagination offset (default 0)
    
    Returns paginated list of jobs with metadata.
    """
    jobs = await service.get_user_jobs(
        user_id=user_id,
        status=status_filter,
        source=source,
        limit=limit,
        offset=offset
    )
    
    # Get total count
    total = await service.count_user_jobs(user_id=user_id, status=status_filter, source=source)
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        pagination=PaginationMeta(
            limit=limit,
            offset=offset,
            total=total,
            hasMore=offset + len(jobs) < total
        )
    )


@router.get("/browse", response_model=BrowseJobListResponse)
async def browse_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: JobService = Depends(get_job_service)
) -> BrowseJobListResponse:
    """
    Browse mock job listings.
    
    - **Public endpoint** (no authentication required)
    - **Query parameters:**
      - `limit`: Max results (1-100, default 20)
      - `offset`: Pagination offset (default 0)
    
    - **Returns:** List of mock job postings with pagination
    - **Purpose:** Allows users to explore sample jobs before signing up
    """
    jobs = await service.browse_jobs(
        limit=limit,
        offset=offset
    )
    
    # Get total count from service
    total = await service.count_browse_jobs()
    
    return BrowseJobListResponse(
        jobs=jobs,
        total=total,
        pagination=PaginationMeta(
            limit=limit,
            offset=offset,
            total=total,
            hasMore=offset + len(jobs) < total
        )
    )


@router.get("/{job_id}", response_model=Job)
async def get_job(
    job_id: Annotated[str, Path(description="Job unique identifier")],
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Get specific job details by ID.
    
    Returns full job information including description, requirements,
    benefits, and application status.
    
    Raises:
    - **404 Not Found**: Job does not exist
    - **403 Forbidden**: User does not have access to this job
    """
    job = await service.get_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found"
        )
    
    # Check ownership (user's own jobs)
    if job.user_id is not None and job.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this job"
        )
    
    return job


@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: Annotated[str, Path(description="Job unique identifier")],
    request: JobUpdateRequest,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Update job details (partial updates supported).
    
    All fields are optional - only provided fields will be updated.
    Common use cases:
    - Update application status as progress is made
    - Add personal notes about the job
    - Archive old job postings
    
    Raises:
    - **404 Not Found**: Job does not exist
    - **422 Unprocessable Entity**: No fields provided or invalid values
    """
    # Filter out None values
    update_data = {k: v for k, v in request.model_dump(exclude_none=True).items()}
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for update"
        )
    
    updated_job = await service.update_job(job_id, **update_data)
    
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found"
        )
    
    return updated_job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: Annotated[str, Path(description="Job unique identifier")],
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> None:
    """
    Permanently delete a job posting.
    
    This action cannot be undone. The job and all associated data
    will be removed from the system.
    
    Raises:
    - **404 Not Found**: Job does not exist
    - **409 Conflict**: Job has associated generated documents
    """
    deleted = await service.delete_job(job_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found"
        )
