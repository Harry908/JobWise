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
    StatusUpdateDTO,
    UserJobListDTO,
)
from ...core.dependencies import get_db_session, get_current_user
from ...infrastructure.repositories.job_repository import DatabaseJobRepository
from ...domain.entities.user import User

router = APIRouter(tags=["jobs"])


async def get_job_repository(session: AsyncSession = Depends(get_db_session)) -> DatabaseJobRepository:
    return DatabaseJobRepository(session)


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
    """Search all jobs (static + user-created)"""
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
            offset=offset,
        )

        jobs = await repo.search_jobs(query=request.query or "", filters=None, limit=request.limit, offset=request.offset)
        total = await repo.get_total_count()

        job_summaries: List[JobSummaryDTO] = [
            JobSummaryDTO(
                id=j.id,
                title=j.title,
                company=j.company,
                location=j.location,
                job_type=j.job_type,
                experience_level=j.experience_level,
                salary_range=j.salary_range,
                posted_date=j.posted_date,
                remote_work_policy=j.remote_work_policy,
                tags=j.tags,
            )
            for j in jobs
        ]

        return JobSearchResponseDTO(jobs=job_summaries, total_count=total, limit=limit, offset=offset, has_more=(offset + limit < total))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.get("/template", response_model=JobTemplateDTO)
async def get_job_template() -> JobTemplateDTO:
    """Get JSON template for copy-paste conversion"""
    template = {
        "title": "Job Title",
        "company": "Company Name",
        "description": "Detailed job description text...",
        "requirements": ["Requirement 1", "Requirement 2"],
        "benefits": ["Benefit 1", "Benefit 2"],
        "location": "City, State/Country",
        "remote": False,
        "job_type": "full-time",
        "experience_level": "mid",
        "industry": "Technology",
        "company_size": "50-200",
        "salary_range": {"min": 50000, "max": 80000, "currency": "USD"},
        "source": "user_created"
    }
    return JobTemplateDTO(template=template)


@router.get("/my-jobs", response_model=UserJobListDTO)
async def get_my_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> UserJobListDTO:
    """List user's custom job descriptions"""
    try:
        return await repo.get_user_jobs(str(current_user.id), limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user jobs: {str(e)}")


@router.post("/", response_model=JobDTO, status_code=status.HTTP_201_CREATED)
async def create_user_job(
    payload: CreateJobDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    """Create user custom job description"""
    try:
        created = await repo.create_user_job(str(current_user.id), payload)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create job")
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.put("/{job_id}", response_model=JobDTO)
async def update_user_job(
    job_id: str,
    payload: UpdateJobDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    """Update user job (ownership required)"""
    try:
        updated = await repo.update_user_job(str(current_user.id), job_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Job not found or access denied")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job: {str(e)}")


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
):
    """Delete user job (ownership required)"""
    try:
        ok = await repo.delete_user_job(str(current_user.id), job_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Job not found or access denied")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


@router.get("/{job_id}", response_model=JobDTO)
async def get_job_details(
    job_id: str,
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    """Get job details (any source)"""
    try:
        job = await repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job details: {str(e)}")


@router.put("/{job_id}/status", response_model=JobDTO)
async def update_job_status(
    job_id: str,
    status_update: StatusUpdateDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobDTO:
    """Change job status (draft/active/archived)"""
    try:
        updated = await repo.change_status(str(current_user.id), job_id, status_update.status)
        if not updated:
            raise HTTPException(status_code=404, detail="Job not found or access denied")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job status: {str(e)}")


@router.post("/{job_id}/analyze", response_model=AnalyzeJobResponseDTO)
async def analyze_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> AnalyzeJobResponseDTO:
    """Extract keywords and analyze job"""
    try:
        # Check if job exists and get ownership info
        job = await repo.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # For user-created jobs, check ownership
        # We need to check the database model directly for user_id
        from ...infrastructure.database.models import JobPostingModel
        model = await repo.session.get(JobPostingModel, job_id)
        if model and model.user_id and model.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return await repo.analyze_job(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job: {str(e)}")


@router.post("/convert-text", response_model=JobTemplateDTO)
async def convert_text_to_job(
    payload: ConvertTextRequestDTO,
    current_user: User = Depends(get_current_user),
    repo: DatabaseJobRepository = Depends(get_job_repository),
) -> JobTemplateDTO:
    """Convert raw job text to structured JSON"""
    try:
        return await repo.convert_text_to_job(payload.raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert text: {str(e)}")


@router.get("/filters/options", response_model=JobFiltersDTO)
async def get_job_filters(
    repo: DatabaseJobRepository = Depends(get_job_repository)
) -> JobFiltersDTO:
    """Get available filter options"""
    try:
        return await repo.get_job_filters()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter options: {str(e)}")


@router.get("/stats/summary")
async def get_job_stats(
    repo: DatabaseJobRepository = Depends(get_job_repository)
):
    """Get job statistics summary"""
    try:
        stats = await repo.get_statistics()
        return {**stats, "last_updated": "2024-01-15T10:00:00Z"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job statistics: {str(e)}")