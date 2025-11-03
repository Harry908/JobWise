"""Job API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.application.services.job_service import JobService
from app.core.dependencies import get_current_user, get_job_service
from app.domain.entities.job import Job


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


# Request/Response models
class JobCreateFromText(BaseModel):
    """Request model for creating job from raw text."""
    raw_text: str = Field(..., min_length=10, max_length=15000, description="Raw job description text")


class JobCreateFromURL(BaseModel):
    """Request model for creating job from URL."""
    url: str = Field(..., min_length=10, max_length=500, description="Job posting URL")


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


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateFromText | JobCreateFromURL,
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> Job:
    """
    Create a new job posting.
    
    - **Supports two input methods:**
      - `raw_text`: Paste job description text for parsing
      - `url`: Provide URL to fetch job details
    
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
                detail="Either 'raw_text' or 'url' must be provided"
            )


@router.get("", response_model=List[Job])
async def get_user_jobs(
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(active|archived|draft)$"),
    source: Optional[str] = Query(None, max_length=50),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: JobService = Depends(get_job_service),
    user_id: int = Depends(get_current_user)
) -> List[Job]:
    """
    Get list of user's saved jobs.
    
    - **Query parameters:**
      - `status`: Filter by status (active, archived, draft)
      - `source`: Filter by source (user_created, url_import, etc.)
      - `limit`: Max results (1-100, default 20)
      - `offset`: Pagination offset (default 0)
    
    - **Returns:** List of user's jobs
    - **Authentication:** Required
    """
    return await service.get_user_jobs(
        user_id=user_id,
        status=status_filter,
        source=source,
        limit=limit,
        offset=offset
    )


@router.get("/browse", response_model=List[Job])
async def browse_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: JobService = Depends(get_job_service)
) -> List[Job]:
    """
    Browse mock job listings.
    
    - **Public endpoint** (no authentication required)
    - **Query parameters:**
      - `limit`: Max results (1-100, default 20)
      - `offset`: Pagination offset (default 0)
    
    - **Returns:** List of mock job postings
    - **Purpose:** Allows users to explore sample jobs before signing up
    """
    return await service.browse_jobs(
        limit=limit,
        offset=offset
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
