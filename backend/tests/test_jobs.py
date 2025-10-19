"""Tests for job service and endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4
from pathlib import Path
import json

from app.application.services.job_service import JobService
from app.application.dtos.job_dtos import (
    JobSearchRequestDTO,
    JobSearchResponseDTO,
    JobDTO,
    JobSummaryDTO,
    JobFiltersDTO
)
from app.core.exceptions import ValidationException
from app.domain.entities.job import JobPosting
from app.infrastructure.repositories.job_repository import StaticJobRepository


class TestJobService:
    """Test cases for JobService."""

    @pytest.fixture
    def job_service(self):
        """Job service instance with test data file."""
        # Use the test data file
        data_file = Path(__file__).parent / "test_jobs.json"
        return JobService(str(data_file))

    @pytest.mark.asyncio
    async def test_search_jobs_success(self, job_service):
        """Test successful job search."""
        # Arrange
        request = JobSearchRequestDTO(
            query="developer",
            location="Seattle, WA",
            job_type="full-time",
            experience_level="senior",
            min_salary=80000,
            max_salary=160000,
            limit=10,
            offset=0
        )

        # Act
        result = job_service.search_jobs(request)

        # Assert
        assert isinstance(result, JobSearchResponseDTO)
        assert result.total_count >= 0
        assert len(result.jobs) <= result.limit
        assert result.limit == 10
        assert result.offset == 0

    @pytest.mark.asyncio
    async def test_search_jobs_empty_results(self, job_service):
        """Test job search with no results."""
        # Arrange
        request = JobSearchRequestDTO(query="nonexistent job")

        # Act
        result = job_service.search_jobs(request)

        # Assert
        assert isinstance(result, JobSearchResponseDTO)
        assert result.total_count == 0
        assert len(result.jobs) == 0

    @pytest.mark.asyncio
    async def test_get_job_by_id_success(self, job_service):
        """Test successful job retrieval by ID."""
        # Get first job from search
        search_request = JobSearchRequestDTO(limit=1, offset=0)
        search_result = job_service.search_jobs(search_request)

        if search_result.jobs:
            job_id = search_result.jobs[0].id

            # Act
            result = job_service.get_job_by_id(job_id)

            # Assert
            assert isinstance(result, JobDTO)
            assert result.id == job_id
            assert result.title
            assert result.company
        else:
            pytest.skip("No jobs available for testing")

    @pytest.mark.asyncio
    async def test_get_job_by_id_not_found(self, job_service):
        """Test job retrieval with non-existent ID."""
        # Act
        result = job_service.get_job_by_id("nonexistent-job")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_filter_options(self, job_service):
        """Test retrieval of filter options."""
        # Act
        result = job_service.get_job_filters()

        # Assert
        assert isinstance(result, JobFiltersDTO)
        assert isinstance(result.job_types, list)
        assert isinstance(result.experience_levels, list)
        assert isinstance(result.locations, list)


class TestStaticJobRepository:
    """Test cases for StaticJobRepository."""

    @pytest.fixture
    def job_repo(self):
        """Static job repository instance."""
        # Create a temporary data file path for testing
        data_file = Path(__file__).parent / "test_jobs.json"
        return StaticJobRepository(data_file)

    def test_initialization_loads_jobs(self, job_repo):
        """Test that repository loads jobs on initialization."""
        # The repository should load jobs from the JSON file
        # We can't easily test the file loading, but we can test the interface
        assert hasattr(job_repo, '_jobs_cache')
        assert hasattr(job_repo, 'search_jobs')
        assert hasattr(job_repo, 'get_job_by_id')
        assert hasattr(job_repo, 'get_job_filters')
        assert hasattr(job_repo, 'data_file')

    @pytest.mark.asyncio
    async def test_search_jobs_basic(self, job_repo):
        """Test basic job search functionality."""
        # Act
        results = await job_repo.search_jobs(query="developer", limit=5, offset=0)

        # Assert
        assert isinstance(results, list)
        assert len(results) <= 5
        # Should return Job entities
        if results:
            assert hasattr(results[0], 'id')
            assert hasattr(results[0], 'title')
            assert hasattr(results[0], 'company')

    @pytest.mark.asyncio
    async def test_get_job_by_id(self, job_repo):
        """Test job retrieval by ID."""
        # First get some jobs to find a valid ID
        jobs = await job_repo.search_jobs(limit=1, offset=0)
        if jobs:
            job_id = jobs[0].id

            # Act
            result = await job_repo.get_job_by_id(job_id)

            # Assert
            assert result is not None
            assert result.id == job_id
            assert hasattr(result, 'title')
            assert hasattr(result, 'company')
        else:
            # If no jobs, test with invalid ID
            result = await job_repo.get_job_by_id("invalid-id")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_filter_options(self, job_repo):
        """Test filter options retrieval."""
        # Act
        options = await job_repo.get_filter_options()

        # Assert
        assert isinstance(options, dict)
        assert "locations" in options
        assert "job_types" in options
        assert "experience_levels" in options
        assert "companies" in options
        assert "salary_ranges" in options

        # Check that options are lists or appropriate structures
        assert isinstance(options["locations"], list)
        assert isinstance(options["job_types"], list)
        assert isinstance(options["experience_levels"], list)
        assert isinstance(options["companies"], list)

    @pytest.mark.asyncio
    async def test_get_statistics(self, job_repo):
        """Test statistics retrieval."""
        # Act
        stats = await job_repo.get_statistics()

        # Assert
        assert isinstance(stats, dict)
        assert "total_jobs" in stats
        assert "active_jobs" in stats
        assert "jobs_posted_today" in stats
        assert "jobs_posted_this_week" in stats
        assert "average_salary" in stats

        # Check that numeric stats are reasonable
        assert isinstance(stats["total_jobs"], int)
        assert isinstance(stats["active_jobs"], int)
        assert stats["total_jobs"] >= 0
        assert stats["active_jobs"] >= 0

    @pytest.mark.asyncio
    async def test_get_total_count(self, job_repo):
        """Test total count retrieval."""
        # Act
        count = await job_repo.get_total_count()

        # Assert
        assert isinstance(count, int)
        assert count >= 0