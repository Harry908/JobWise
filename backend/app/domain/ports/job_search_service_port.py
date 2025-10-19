"""Universal job search service port - abstract interface for job providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class JobSearchRequest:
    """Request model for job search operations."""
    keywords: List[str]
    location: Optional[str] = None
    remote: Optional[bool] = None
    salary_min: Optional[int] = None
    job_type: Optional[str] = None
    limit: int = 20
    offset: int = 0


@dataclass
class JobPosting:
    """Job posting data model."""
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    posted_date: str
    job_type: str = "full_time"
    remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_url: Optional[str] = None


@dataclass
class JobSearchResponse:
    """Response model for job search operations."""
    jobs: List[JobPosting]
    total_count: int
    has_more: bool


class JobSearchServicePort(ABC):
    """Abstract interface for job search services."""

    @abstractmethod
    async def search_jobs(self, request: JobSearchRequest) -> JobSearchResponse:
        """Search for jobs based on criteria."""
        pass

    @abstractmethod
    async def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """Get detailed information for a specific job."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the job search service is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass