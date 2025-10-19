# Job repository
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
import json
from datetime import datetime

from app.application.dtos.job_dtos import JobDTO, JobFiltersDTO


class JobRepositoryInterface(ABC):
    """Abstract interface for job data access"""

    @abstractmethod
    async def get_all_jobs(self) -> List[JobDTO]:
        """Get all jobs"""
        pass

    @abstractmethod
    async def get_job_by_id(self, job_id: str) -> Optional[JobDTO]:
        """Get a specific job by ID"""
        pass

    @abstractmethod
    async def search_jobs(
        self,
        query: str = "",
        filters: Optional[JobFiltersDTO] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDTO]:
        """Search jobs with filters and pagination"""
        pass

    @abstractmethod
    async def get_job_filters(self) -> JobFiltersDTO:
        """Get available filter options"""
        pass

    @abstractmethod
    async def get_filter_options(self) -> dict:
        """Get filter options as dictionary"""
        pass

    @abstractmethod
    async def get_statistics(self) -> dict:
        """Get job statistics"""
        pass

    @abstractmethod
    async def get_total_count(self) -> int:
        """Get total number of jobs"""
        pass


class StaticJobRepository(JobRepositoryInterface):
    """Static JSON-based job repository for development/testing"""

    def __init__(self, data_file: Path):
        self.data_file = data_file
        self._jobs_cache: Optional[List[JobDTO]] = None
        self._filters_cache: Optional[JobFiltersDTO] = None

    async def _load_jobs(self) -> List[JobDTO]:
        """Load jobs from JSON file with caching"""
        if self._jobs_cache is not None:
            return self._jobs_cache

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            jobs = []
            # Handle both formats: direct list or object with 'jobs' key
            job_list = data if isinstance(data, list) else data.get('jobs', [])
            
            for job_data in job_list:
                # Parse posted_date string to datetime
                posted_date = None
                if job_data.get('posted_date'):
                    try:
                        posted_date = datetime.fromisoformat(job_data['posted_date'])
                    except (ValueError, TypeError):
                        # If parsing fails, use current date
                        posted_date = datetime.now()

                job = JobDTO(
                    id=job_data['id'],
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    salary_range=job_data.get('salary_range'),
                    description=job_data['description'],
                    requirements=job_data.get('requirements', []),
                    benefits=job_data.get('benefits', []),
                    job_type=job_data.get('job_type', 'full-time'),
                    experience_level=job_data.get('experience_level', 'entry'),
                    industry=job_data.get('industry', ''),
                    posted_date=posted_date,
                    application_deadline=job_data.get('application_deadline'),
                    remote_work_policy=job_data.get('remote_work_policy', 'onsite'),
                    company_size=job_data.get('company_size'),
                    tags=job_data.get('tags', [])
                )
                jobs.append(job)

            self._jobs_cache = jobs
            return jobs

        except FileNotFoundError:
            raise ValueError(f"Job data file not found: {self.data_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in job data file: {e}")

    async def get_all_jobs(self) -> List[JobDTO]:
        """Get all jobs from static data"""
        return await self._load_jobs()

    async def get_job_by_id(self, job_id: str) -> Optional[JobDTO]:
        """Get a specific job by ID"""
        jobs = await self._load_jobs()
        return next((job for job in jobs if job.id == job_id), None)

    async def search_jobs(
        self,
        query: str = "",
        filters: Optional[JobFiltersDTO] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDTO]:
        """Search jobs with filters and pagination"""
        jobs = await self._load_jobs()

        # Apply text search
        if query:
            query_lower = query.lower()
            jobs = [
                job for job in jobs
                if (query_lower in job.title.lower() or
                    query_lower in job.description.lower() or
                    query_lower in job.company.lower() or
                    any(query_lower in req.lower() for req in job.requirements))
            ]

        # Apply filters
        if filters:
            jobs = await self._apply_filters(jobs, filters)

        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        return jobs[start_idx:end_idx]

    async def _apply_filters(self, jobs: List[JobDTO], filters: JobFiltersDTO) -> List[JobDTO]:
        """Apply filter criteria to job list"""
        filtered_jobs = jobs

        if filters.location:
            location_lower = filters.location.lower()
            filtered_jobs = [
                job for job in filtered_jobs
                if location_lower in job.location.lower()
            ]

        if filters.job_type:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.job_type == filters.job_type
            ]

        if filters.experience_level:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.experience_level == filters.experience_level
            ]

        if filters.industry:
            industry_lower = filters.industry.lower()
            filtered_jobs = [
                job for job in filtered_jobs
                if industry_lower in job.industry.lower()
            ]

        if filters.remote_work is not None:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.remote_work == filters.remote_work
            ]

        if filters.min_salary:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.salary_range and
                self._parse_salary_range(job.salary_range)[0] >= filters.min_salary
            ]

        if filters.max_salary:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.salary_range and
                self._parse_salary_range(job.salary_range)[1] <= filters.max_salary
            ]

        if filters.company_size:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.company_size == filters.company_size
            ]

        return filtered_jobs

    def _parse_salary_range(self, salary_range: str) -> tuple[int, int]:
        """Parse salary range string like '$50,000 - $70,000'"""
        try:
            # Remove $ and commas, split by dash
            parts = salary_range.replace('$', '').replace(',', '').split('-')
            if len(parts) == 2:
                min_salary = int(parts[0].strip())
                max_salary = int(parts[1].strip())
                return min_salary, max_salary
            else:
                # If single value, assume it's the minimum
                salary = int(parts[0].strip())
                return salary, salary
        except (ValueError, IndexError):
            return 0, 0

    async def get_job_filters(self) -> JobFiltersDTO:
        """Get available filter options from job data"""
        if self._filters_cache is not None:
            return self._filters_cache

        jobs = await self._load_jobs()

        # Extract unique values for filters
        locations = list(set(job.location for job in jobs))
        job_types = list(set(job.job_type for job in jobs))
        experience_levels = list(set(job.experience_level for job in jobs))
        remote_work_policies = list(set(job.remote_work_policy for job in jobs if job.remote_work_policy))
        industries = list(set(job.industry for job in jobs if job.industry))
        company_sizes = list(set(job.company_size for job in jobs if job.company_size))

        # Extract all tags
        all_tags = set()
        for job in jobs:
            all_tags.update(job.tags)
        tags = list(all_tags)

        # Calculate salary statistics
        salaries = []
        for job in jobs:
            if job.salary_range:
                if isinstance(job.salary_range, dict):
                    # Handle dict format from JSON
                    min_sal = job.salary_range.get('min', 0)
                    max_sal = job.salary_range.get('max', 0)
                elif hasattr(job.salary_range, 'min') and hasattr(job.salary_range, 'max'):
                    # Handle SalaryRangeDTO object
                    min_sal = job.salary_range.min
                    max_sal = job.salary_range.max
                else:
                    # Handle string format
                    min_sal, max_sal = self._parse_salary_range(str(job.salary_range))
                
                if min_sal > 0:
                    salaries.extend([min_sal, max_sal])

        salary_stats = {}
        if salaries:
            salary_stats = {
                'min': min(salaries),
                'max': max(salaries),
                'average': sum(salaries) // len(salaries)
            }

        self._filters_cache = JobFiltersDTO(
            locations=sorted(locations),
            job_types=sorted(job_types),
            experience_levels=sorted(experience_levels),
            remote_work_policies=sorted(remote_work_policies),
            industries=sorted(industries),
            company_sizes=sorted(company_sizes) if company_sizes else None,
            tags=sorted(tags),
            salary_ranges=salary_stats
        )

        return self._filters_cache

    async def get_filter_options(self) -> dict:
        """Get available filter options (alias for get_job_filters)"""
        filters_dto = await self.get_job_filters()
        return {
            "locations": filters_dto.locations,
            "job_types": filters_dto.job_types,
            "experience_levels": filters_dto.experience_levels,
            "companies": [],  # Not implemented in DTO
            "salary_ranges": []  # Not implemented in DTO
        }

    async def get_statistics(self) -> dict:
        """Get job statistics"""
        jobs = await self._load_jobs()

        total_jobs = len(jobs)
        active_jobs = total_jobs  # All jobs are considered active

        # Calculate jobs posted today/this week (simplified)
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        today = now.date()
        week_ago = now - timedelta(days=7)

        jobs_posted_today = sum(1 for job in jobs if job.posted_date and job.posted_date.date() == today)
        jobs_posted_this_week = sum(1 for job in jobs if job.posted_date and job.posted_date >= week_ago)

        # Calculate average salary
        salaries = []
        for job in jobs:
            if job.salary_range:
                if isinstance(job.salary_range, dict):
                    # Handle dict format from JSON
                    min_sal = job.salary_range.get('min', 0)
                    max_sal = job.salary_range.get('max', 0)
                elif hasattr(job.salary_range, 'min') and hasattr(job.salary_range, 'max'):
                    # Handle SalaryRangeDTO object
                    min_sal = job.salary_range.min
                    max_sal = job.salary_range.max
                else:
                    # Handle string format
                    min_sal, max_sal = self._parse_salary_range(str(job.salary_range))
                
                if min_sal > 0 and max_sal > 0:
                    salaries.append((min_sal + max_sal) / 2)

        average_salary = sum(salaries) / len(salaries) if salaries else 0

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "jobs_posted_today": jobs_posted_today,
            "jobs_posted_this_week": jobs_posted_this_week,
            "average_salary": int(average_salary)
        }

    async def get_total_count(self) -> int:
        """Get total number of jobs"""
        jobs = await self._load_jobs()
        return len(jobs)