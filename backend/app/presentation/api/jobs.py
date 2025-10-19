# Job API endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pathlib import Path

from app.application.dtos.job_dtos import (
    JobDTO,
    JobSummaryDTO,
    JobSearchRequestDTO,
    JobSearchResponseDTO,
    JobFiltersDTO
)
from app.application.services.job_service import JobService

router = APIRouter(tags=["jobs"])

# Dependency injection for job service
def get_job_service() -> JobService:
    """Get job service instance with static data"""
    return JobService()


@router.get("/", response_model=JobSearchResponseDTO)
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query for jobs"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type (full-time, part-time, contract, internship)"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level (entry, mid, senior, lead)"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    remote_work: Optional[bool] = Query(None, description="Filter by remote work availability"),
    min_salary: Optional[int] = Query(None, description="Minimum salary filter"),
    max_salary: Optional[int] = Query(None, description="Maximum salary filter"),
    company_size: Optional[str] = Query(None, description="Filter by company size"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: JobService = Depends(get_job_service)
) -> JobSearchResponseDTO:
    """
    Search and filter jobs with pagination.

    Supports text search across job titles, descriptions, companies, and requirements.
    Multiple filters can be combined for precise job matching.
    """
    try:
        # Build search request
        request = JobSearchRequestDTO(
            query=q or "",
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            industry=industry,
            remote_work=remote_work,
            min_salary=min_salary,
            max_salary=max_salary,
            company_size=company_size,
            limit=limit,
            offset=offset
        )

        return service.search_jobs(request)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.get("/{job_id}", response_model=JobDTO)
async def get_job_details(
    job_id: str,
    service: JobService = Depends(get_job_service)
) -> JobDTO:
    """
    Get detailed information for a specific job.

    Returns comprehensive job details including requirements, benefits,
    and application information.
    """
    try:
        job = service.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")

        return job

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job details: {str(e)}")


@router.get("/filters/options", response_model=JobFiltersDTO)
async def get_job_filters(
    service: JobService = Depends(get_job_service)
) -> JobFiltersDTO:
    """
    Get available filter options for job search.

    Returns all possible values for location, job type, experience level,
    industry, and other filterable fields based on current job data.
    """
    try:
        return service.get_job_filters()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter options: {str(e)}")


@router.get("/stats/summary")
async def get_job_stats(
    service: JobService = Depends(get_job_service)
):
    """
    Get job statistics summary.

    Returns counts and statistics about available jobs.
    """
    try:
        # Get all jobs for statistics
        all_jobs = service._load_jobs_data()

        # Calculate statistics
        total_jobs = len(all_jobs)
        remote_jobs = len([job for job in all_jobs if job.get('remote_work_policy') == 'remote'])
        job_types = {}
        experience_levels = {}
        industries = {}

        for job in all_jobs:
            job_type = job.get('job_type', 'unknown')
            exp_level = job.get('experience_level', 'unknown')
            industry = job.get('industry', '')

            job_types[job_type] = job_types.get(job_type, 0) + 1
            experience_levels[exp_level] = experience_levels.get(exp_level, 0) + 1
            if industry:
                industries[industry] = industries.get(industry, 0) + 1

        return {
            "total_jobs": total_jobs,
            "remote_jobs": remote_jobs,
            "remote_percentage": round((remote_jobs / total_jobs * 100), 1) if total_jobs > 0 else 0,
            "job_types": job_types,
            "experience_levels": experience_levels,
            "industries": industries,
            "last_updated": "2024-01-15T10:00:00Z"  # Static for now
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve job statistics: {str(e)}")