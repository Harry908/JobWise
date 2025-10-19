# Job service - Multi-provider job discovery

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ...application.dtos.job_dtos import (
    JobDTO,
    JobSummaryDTO,
    JobSearchRequestDTO,
    JobSearchResponseDTO,
    JobFiltersDTO,
    SalaryRangeDTO
)


class JobService:
    """Service for job discovery and management using static data"""

    def __init__(self, data_file_path: Optional[str] = None):
        """
        Initialize job service with static data

        Args:
            data_file_path: Path to the static jobs JSON file
        """
        if data_file_path is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent
            backend_dir = current_dir.parent.parent.parent
            data_file_path = str(backend_dir / "data" / "static_jobs.json")

        self.data_file_path = Path(data_file_path)
        self._jobs_cache: Optional[List[Dict[str, Any]]] = None
        self._last_load_time: Optional[datetime] = None

    def _load_jobs_data(self) -> List[Dict[str, Any]]:
        """
        Load jobs data from JSON file with caching

        Returns:
            List of job dictionaries
        """
        # Simple caching - reload if file modified or never loaded
        if self._jobs_cache is None or self._should_reload_data():
            try:
                with open(self.data_file_path, 'r', encoding='utf-8') as f:
                    self._jobs_cache = json.load(f)
                    self._last_load_time = datetime.now()
            except FileNotFoundError:
                # Return empty list if file doesn't exist
                self._jobs_cache = []
                self._last_load_time = datetime.now()
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in jobs data file: {e}")

        return self._jobs_cache or []

    def _should_reload_data(self) -> bool:
        """Check if data should be reloaded (file modified)"""
        if self._last_load_time is None:
            return True

        try:
            file_mtime = datetime.fromtimestamp(self.data_file_path.stat().st_mtime)
            return file_mtime > self._last_load_time
        except (OSError, FileNotFoundError):
            return True

    def search_jobs(self, search_request: JobSearchRequestDTO) -> JobSearchResponseDTO:
        """
        Search jobs based on criteria

        Args:
            search_request: Search criteria

        Returns:
            Job search response with results and pagination
        """
        all_jobs = self._load_jobs_data()

        # Apply filters
        filtered_jobs = self._apply_filters(all_jobs, search_request)

        # Sort by posted date (newest first)
        filtered_jobs.sort(key=lambda x: x.get('posted_date', ''), reverse=True)

        # Apply pagination
        total_count = len(filtered_jobs)
        start_idx = search_request.offset
        end_idx = start_idx + search_request.limit
        paginated_jobs = filtered_jobs[start_idx:end_idx]

        # Convert to DTOs
        job_summaries = [
            self._job_dict_to_summary_dto(job_dict)
            for job_dict in paginated_jobs
        ]

        return JobSearchResponseDTO(
            jobs=job_summaries,
            total_count=total_count,
            limit=search_request.limit,
            offset=search_request.offset,
            has_more=(end_idx < total_count)
        )

    def get_job_by_id(self, job_id: str) -> Optional[JobDTO]:
        """
        Get detailed job information by ID

        Args:
            job_id: Job identifier

        Returns:
            Job details or None if not found
        """
        all_jobs = self._load_jobs_data()

        for job_dict in all_jobs:
            if job_dict.get('id') == job_id:
                return self._job_dict_to_dto(job_dict)

        return None

    def get_job_filters(self) -> JobFiltersDTO:
        """
        Get available filter options from current job data

        Returns:
            Available filter options
        """
        all_jobs = self._load_jobs_data()

        # Extract unique values for each filter
        job_types = sorted(set(job.get('job_type', '') for job in all_jobs if job.get('job_type')))
        experience_levels = sorted(set(job.get('experience_level', '') for job in all_jobs if job.get('experience_level')))
        remote_work_policies = sorted(set(job.get('remote_work_policy', '') for job in all_jobs if job.get('remote_work_policy')))
        industries = sorted(set(job.get('industry', '') for job in all_jobs if job.get('industry')))
        company_sizes = sorted(set(job.get('company_size', '') for job in all_jobs if job.get('company_size')))
        locations = sorted(set(job.get('location', '') for job in all_jobs if job.get('location')))

        # Extract all tags
        all_tags = set()
        for job in all_jobs:
            all_tags.update(job.get('tags', []))
        tags = sorted(list(all_tags))

        # Calculate salary statistics
        salaries = []
        for job in all_jobs:
            salary_range = job.get('salary_range')
            if salary_range and isinstance(salary_range, dict):
                salaries.extend([salary_range.get('min', 0), salary_range.get('max', 0)])

        salary_stats = {}
        if salaries:
            salary_stats = {
                'min': min(salaries),
                'max': max(salaries),
                'average': sum(salaries) // len(salaries)
            }

        return JobFiltersDTO(
            job_types=job_types,
            experience_levels=experience_levels,
            remote_work_policies=remote_work_policies,
            industries=industries,
            company_sizes=company_sizes,
            locations=locations,
            tags=tags,
            salary_ranges=salary_stats
        )

    def _apply_filters(self, jobs: List[Dict[str, Any]], search_request: JobSearchRequestDTO) -> List[Dict[str, Any]]:
        """
        Apply search filters to job list

        Args:
            jobs: List of job dictionaries
            search_request: Search criteria

        Returns:
            Filtered list of jobs
        """
        filtered_jobs = jobs.copy()

        # Text search in title, company, description, and tags
        if search_request.query:
            query_lower = search_request.query.lower()
            filtered_jobs = [
                job for job in filtered_jobs
                if (
                    query_lower in job.get('title', '').lower() or
                    query_lower in job.get('company', '').lower() or
                    query_lower in job.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in job.get('tags', []))
                )
            ]

        # Location filter
        if search_request.location:
            location_lower = search_request.location.lower()
            filtered_jobs = [
                job for job in filtered_jobs
                if location_lower in job.get('location', '').lower()
            ]

        # Job type filter
        if search_request.job_type:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('job_type') == search_request.job_type
            ]

        # Experience level filter
        if search_request.experience_level:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('experience_level') == search_request.experience_level
            ]

        # Remote work policy filter
        if search_request.remote_work_policy:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('remote_work_policy') == search_request.remote_work_policy
            ]

        # Industry filter
        if search_request.industry:
            industry_lower = search_request.industry.lower()
            filtered_jobs = [
                job for job in filtered_jobs
                if industry_lower in job.get('industry', '').lower()
            ]

        # Company size filter
        if search_request.company_size:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('company_size') == search_request.company_size
            ]

        # Tags filter
        if search_request.tags:
            filtered_jobs = [
                job for job in filtered_jobs
                if any(tag in job.get('tags', []) for tag in search_request.tags)
            ]

        # Salary range filters
        if search_request.min_salary or search_request.max_salary:
            filtered_jobs = [
                job for job in filtered_jobs
                if self._matches_salary_range(job, search_request.min_salary, search_request.max_salary)
            ]

        return filtered_jobs

    def _matches_salary_range(self, job: Dict[str, Any], min_salary: Optional[int], max_salary: Optional[int]) -> bool:
        """
        Check if job matches salary range criteria

        Args:
            job: Job dictionary
            min_salary: Minimum salary filter
            max_salary: Maximum salary filter

        Returns:
            True if job matches salary criteria
        """
        salary_range = job.get('salary_range')
        if not salary_range or not isinstance(salary_range, dict):
            return True  # No salary info, include in results

        job_min = salary_range.get('min', 0)
        job_max = salary_range.get('max', float('inf'))

        # Check minimum salary requirement
        if min_salary is not None:
            if job_max < min_salary:
                return False

        # Check maximum salary requirement
        if max_salary is not None:
            if job_min > max_salary:
                return False

        return True

    def _job_dict_to_summary_dto(self, job_dict: Dict[str, Any]) -> JobSummaryDTO:
        """
        Convert job dictionary to JobSummaryDTO

        Args:
            job_dict: Job dictionary from JSON

        Returns:
            JobSummaryDTO instance
        """
        salary_range = None
        if job_dict.get('salary_range'):
            salary_range = SalaryRangeDTO(**job_dict['salary_range'])

        return JobSummaryDTO(
            id=job_dict['id'],
            title=job_dict['title'],
            company=job_dict['company'],
            location=job_dict['location'],
            job_type=job_dict['job_type'],
            experience_level=job_dict['experience_level'],
            salary_range=salary_range,
            posted_date=datetime.fromisoformat(job_dict['posted_date'].replace('Z', '+00:00')),
            remote_work_policy=job_dict['remote_work_policy'],
            tags=job_dict.get('tags', [])
        )

    def _job_dict_to_dto(self, job_dict: Dict[str, Any]) -> JobDTO:
        """
        Convert job dictionary to JobDTO

        Args:
            job_dict: Job dictionary from JSON

        Returns:
            JobDTO instance
        """
        salary_range = None
        if job_dict.get('salary_range'):
            salary_range = SalaryRangeDTO(**job_dict['salary_range'])

        application_deadline = None
        if job_dict.get('application_deadline'):
            application_deadline = datetime.fromisoformat(job_dict['application_deadline'].replace('Z', '+00:00'))

        return JobDTO(
            id=job_dict['id'],
            title=job_dict['title'],
            company=job_dict['company'],
            location=job_dict['location'],
            job_type=job_dict['job_type'],
            experience_level=job_dict['experience_level'],
            salary_range=salary_range,
            description=job_dict['description'],
            requirements=job_dict.get('requirements', []),
            benefits=job_dict.get('benefits', []),
            posted_date=datetime.fromisoformat(job_dict['posted_date'].replace('Z', '+00:00')),
            application_deadline=application_deadline,
            company_size=job_dict['company_size'],
            industry=job_dict['industry'],
            remote_work_policy=job_dict['remote_work_policy'],
            tags=job_dict.get('tags', [])
        )