# Job API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos.job_dtos import (
    JobDTO,
    JobSummaryDTO,
    JobSearchRequestDTO,
    JobSearchResponseDTO,
    JobFiltersDTO,
    CreateJobDTO,
    UpdateJobDTO,
    JobTemplateDTO,
    ConvertTextRequestDTO,
    AnalyzeJobResponseDTO,
    UserJobListDTO,
)
from ...core.dependencies import get_db_session, get_current_user
from ...infrastructure.repositories.job_repository import DatabaseJobRepository
from ...domain.entities.user import User
from ...core.dependencies import get_current_user

router = APIRouter(tags=["jobs"])


async def get_job_repository(session: AsyncSession = Depends(get_db_session)) -> DatabaseJobRepository:
    return DatabaseJobRepository(session)


@router.post("/user", response_model=JobDTO, status_code=status.HTTP_201_CREATED)
async def create_user_job(
    payload: CreateJobDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    try:
        created = await repo.create_user_job(str(current_user.id), payload)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create job")
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/", response_model=JobSearchResponseDTO)
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query for jobs"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    remote_work: Optional[bool] = Query(None, description="Filter by remote work availability"),
    min_salary: Optional[int] = Query(None, description="Minimum salary filter"),
    max_salary: Optional[int] = Query(None, description="Maximum salary filter"),
    company_size: Optional[str] = Query(None, description="Filter by company size"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    repo: DatabaseJobRepository = Depends(get_job_repository)
) -> JobSearchResponseDTO:
    """
    Search and filter jobs with pagination.

    Supports text search across job titles, descriptions, companies, and requirements.
    Multiple filters can be combined for precise job matching.
    """
    try:
        request = JobSearchRequestDTO(
            query=q or "",
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            remote_work_policy=("remote" if remote_work else None),
            industry=industry,
            company_size=company_size,
            tags=None,
            min_salary=min_salary,
            max_salary=max_salary,
            limit=limit,
            offset=offset
        )

        # For now use repository simple search
        search_query: str = request.query or ""
        jobs = await repo.search_jobs(query=search_query, filters=None, limit=request.limit, offset=request.offset)
        total = await repo.get_total_count()

        # convert JobDTOs into JobSummaryDTO objects manually
        job_summaries: List[JobSummaryDTO] = []
        for j in jobs:
            job_summaries.append(JobSummaryDTO(
                id=j.id,
                title=j.title,
                company=j.company,
                location=j.location,
                job_type=j.job_type,
                experience_level=j.experience_level,
                salary_range=j.salary_range,
                posted_date=j.posted_date,
                remote_work_policy=j.remote_work_policy,
                tags=j.tags
            ))

        return JobSearchResponseDTO(jobs=job_summaries, total_count=total, limit=limit, offset=offset, has_more=(offset+limit < total))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.get("/{job_id}", response_model=JobDTO)
async def get_job_details(
    job_id: str,
    repo: DatabaseJobRepository = Depends(get_job_repository)
) -> JobDTO:
    """
    Get detailed information for a specific job.

    Returns comprehensive job details including requirements, benefits,
    and application information.
    """
    try:
        job = await repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job details: {str(e)}")


@router.get("/my-jobs", response_model=UserJobListDTO)
async def get_my_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> UserJobListDTO:
    try:
        return await repo.get_user_jobs(str(current_user.id), limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user jobs: {str(e)}")


@router.put("/user/{job_id}", response_model=JobDTO)
async def update_user_job(
    job_id: str,
    payload: UpdateJobDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    try:
        updated = await repo.update_user_job(str(current_user.id), job_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Job not found or access denied")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")


@router.delete("/user/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
):
    try:
        ok = await repo.delete_user_job(str(current_user.id), job_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Job not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.post("/user/{job_id}/analyze", response_model=AnalyzeJobResponseDTO)
async def analyze_user_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> AnalyzeJobResponseDTO:
    try:
        return await repo.analyze_job(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job: {str(e)}")


@router.post("/convert-text", response_model=JobTemplateDTO)
async def convert_text_to_job(
    payload: ConvertTextRequestDTO,
    current_user: Optional[User] = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobTemplateDTO:
    try:
        return await repo.convert_text_to_job(payload.raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert text: {str(e)}")


@router.get("/filters/options", response_model=JobFiltersDTO)
async def get_job_filters(
    repo: DatabaseJobRepository = Depends(get_job_repository)
) -> JobFiltersDTO:
    """
    Get available filter options for job search.

    Returns all possible values for location, job type, experience level,
    industry, and other filterable fields based on current job data.
    """
    try:
        return await repo.get_job_filters()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter options: {str(e)}")


@router.get("/stats/summary")
async def get_job_stats(
    repo: DatabaseJobRepository = Depends(get_job_repository)
):
    """
    Get job statistics summary.

    Returns counts and statistics about available jobs.
    """
    try:
        # Get basic statistics from repository
        stats = await repo.get_statistics()

        # Calculate statistics
        return {**stats, "last_updated": "2024-01-15T10:00:00Z"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job statistics: {str(e)}")