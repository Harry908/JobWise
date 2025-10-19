"""Job description service for business logic operations."""

from typing import List, Optional
from uuid import UUID

from ...domain.entities.job_description import JobDescription, JobDescriptionMetadata, JobDescriptionStatus, JobDescriptionSource
from ...infrastructure.repositories.job_description_repository import JobDescriptionRepository


class JobDescriptionService:
    """Service for job description business logic operations."""

    def __init__(self, job_description_repository: JobDescriptionRepository):
        self.repository = job_description_repository

    async def create_job_description(
        self,
        user_id: UUID,
        title: str,
        company: str,
        description: str,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        source: JobDescriptionSource = JobDescriptionSource.MANUAL,
        metadata: Optional[JobDescriptionMetadata] = None,
        created_from_url: Optional[str] = None,
    ) -> JobDescription:
        """Create a new job description for a user."""
        # Validate input
        if not title or not title.strip():
            raise ValueError("Job title is required")
        if not company or not company.strip():
            raise ValueError("Company name is required")
        if not description or not description.strip():
            raise ValueError("Job description is required")

        # Create metadata if not provided
        if metadata is None:
            metadata = JobDescriptionMetadata.create_empty()

        # Create job description
        job_description = JobDescription.create(
            user_id=user_id,
            title=title.strip(),
            company=company.strip(),
            description=description.strip(),
            requirements=requirements or [],
            benefits=benefits or [],
            source=source,
            metadata=metadata,
            created_from_url=created_from_url,
        )

        # Extract keywords and update metadata
        await self._extract_and_update_keywords(job_description)

        # Save to repository
        return await self.repository.create(job_description)

    async def get_job_description(self, job_description_id: UUID) -> Optional[JobDescription]:
        """Get job description by ID."""
        return await self.repository.get_by_id(job_description_id)

    async def get_user_job_descriptions(
        self,
        user_id: UUID,
        include_archived: bool = False
    ) -> List[JobDescription]:
        """Get all job descriptions for a user."""
        if include_archived:
            return await self.repository.get_by_user_id(user_id)
        else:
            return await self.repository.get_active_by_user_id(user_id)

    async def update_job_description(
        self,
        job_description_id: UUID,
        title: Optional[str] = None,
        company: Optional[str] = None,
        description: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        metadata: Optional[JobDescriptionMetadata] = None,
    ) -> JobDescription:
        """Update an existing job description."""
        # Get existing job description
        job_description = await self.repository.get_by_id(job_description_id)
        if not job_description:
            raise ValueError("Job description not found")

        # Update content
        job_description.update_content(
            title=title,
            company=company,
            description=description,
            requirements=requirements,
            benefits=benefits,
        )

        # Update metadata if provided
        if metadata is not None:
            job_description.update_metadata(metadata)

        # Re-extract keywords if content changed
        if title or company or description or requirements:
            await self._extract_and_update_keywords(job_description)

        # Save updated job description
        return await self.repository.update(job_description)

    async def delete_job_description(self, job_description_id: UUID) -> bool:
        """Delete a job description."""
        # Check if job description exists
        job_description = await self.repository.get_by_id(job_description_id)
        if not job_description:
            raise ValueError("Job description not found")

        # Delete job description
        return await self.repository.delete(job_description_id)

    async def activate_job_description(self, job_description_id: UUID) -> JobDescription:
        """Activate a job description."""
        job_description = await self.repository.get_by_id(job_description_id)
        if not job_description:
            raise ValueError("Job description not found")

        job_description.activate()
        return await self.repository.update(job_description)

    async def archive_job_description(self, job_description_id: UUID) -> JobDescription:
        """Archive a job description."""
        job_description = await self.repository.get_by_id(job_description_id)
        if not job_description:
            raise ValueError("Job description not found")

        job_description.archive()
        return await self.repository.update(job_description)

    async def parse_job_description(self, job_description_id: UUID) -> JobDescription:
        """Parse job description to extract keywords and update metadata."""
        job_description = await self.repository.get_by_id(job_description_id)
        if not job_description:
            raise ValueError("Job description not found")

        # Extract and update keywords
        await self._extract_and_update_keywords(job_description)

        return await self.repository.update(job_description)

    async def search_job_descriptions(
        self,
        user_id: UUID,
        query: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDescription]:
        """Search job descriptions for a user with filters."""
        return await self.repository.search_by_user_id(
            user_id=user_id,
            query=query,
            status=status,
            limit=limit,
            offset=offset
        )

    async def get_job_description_count(self, user_id: UUID) -> int:
        """Get count of job descriptions for a user."""
        return await self.repository.count_by_user_id(user_id)

    async def _extract_and_update_keywords(self, job_description: JobDescription) -> None:
        """Extract keywords from job description and update metadata."""
        # Extract keywords from content
        keywords = job_description.extract_keywords()

        # Extract technical and soft skills
        technical_skills = job_description.get_technical_requirements()
        soft_skills = job_description.get_soft_skills_requirements()

        # Update metadata
        job_description.metadata.keywords = keywords
        job_description.metadata.technical_skills = technical_skills
        job_description.metadata.soft_skills = soft_skills

        # Try to extract experience level from content
        experience_indicators = {
            "senior": ["senior", "lead", "principal", "staff", "architect"],
            "mid": ["mid", "intermediate", "experienced"],
            "entry": ["entry", "junior", "graduate", "new grad"]
        }

        content_lower = f"{job_description.title} {job_description.description} {' '.join(job_description.requirements)}".lower()

        for level, indicators in experience_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                job_description.metadata.experience_level = level
                break