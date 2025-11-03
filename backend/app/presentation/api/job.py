"""Job API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
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
    requirements: Optional[List[str]] = Field(default_factory=list, description="Job requirements")
    benefits: Optional[List[str]] = Field(default_factory=list, description="Job benefits")
    salary_range: Optional[str] = Field(None, max_length=100, description="Salary range")
    remote: Optional[bool] = Field(default=False, description="Remote work option")
    status: Optional[str] = Field(default="active", pattern="^(active|archived|draft)$")


class JobUpdateRequest(BaseModel):
    """Request model for updating job."""
    title: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=10000)
    status: Optional[str] = Field(None, pattern="^(active|archived|draft)$")


class JobDeleteResponse(BaseModel):
    """Response model for job deletion."""
    message: str


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
    request: JobCreateFromText | JobCreateFromURL | JobCreateStructured,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Create a new job posting.
    
    - **Supports three input methods:**
      - `raw_text`: Paste job description text for parsing
      - `url`: Provide URL to fetch job details
      - Structured: Provide all fields directly
    
    - **Returns:** Created job with parsed details
    - **Authentication:** Required
    """
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


@router.get("", response_model=JobListResponse)
async def get_user_jobs(
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(active|archived|draft)$"),
    source: Optional[str] = Query(None, max_length=50),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> JobListResponse:
    """
    Get list of user's saved jobs.
    
    - **Query parameters:**
      - `status`: Filter by status (active, archived, draft)
      - `source`: Filter by source (user_created, url_import, etc.)
      - `limit`: Max results (1-100, default 20)
      - `offset`: Pagination offset (default 0)
    
    - **Returns:** List of user's jobs with pagination
    - **Authentication:** Required
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
    job_id: str,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Get specific job by ID.
    
    - **Parameters:**
      - `job_id`: Job identifier
    
    - **Returns:** Job details
    - **Authentication:** Required
    - **Errors:** 404 if job not found
    """
    job = await service.get_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found"
        )
    
    return job


@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: str,
    request: JobUpdateRequest,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Update job details.
    
    - **Parameters:**
      - `job_id`: Job identifier
    
    - **Request body:** Fields to update (all optional)
    - **Returns:** Updated job
    - **Authentication:** Required
    - **Errors:** 404 if job not found
    """
    # Filter out None values
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
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


@router.delete("/{job_id}", response_model=JobDeleteResponse)
async def delete_job(
    job_id: str,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> JobDeleteResponse:
    """
    Delete a job.
    
    - **Parameters:**
      - `job_id`: Job identifier
    
    - **Returns:** Success message
    - **Authentication:** Required
    - **Errors:** 404 if job not found
    """
    deleted = await service.delete_job(job_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found"
        )
    
    return JobDeleteResponse(message="Job deleted successfully")
