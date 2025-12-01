"""Job repository for database operations."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import JobModel
from app.domain.entities.job import Job


class JobRepository:
    """Repository for job database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize job repository.
        
        Args:
            db: Async database session
        """
        self.db = db

    async def create(self, job_data: dict) -> Job:
        """Create a new job.
        
        Args:
            job_data: Job data dictionary
            
        Returns:
            Created Job entity
        """
        # Create domain entity first (this triggers UUID generation if id not provided)
        job_entity = Job(**job_data)
        
        # Create database model from entity
        job_model = JobModel(
            id=job_entity.id,
            user_id=job_entity.user_id,
            source=job_entity.source,
            title=job_entity.title,
            company=job_entity.company,
            location=job_entity.location,
            description=job_entity.description,
            raw_text=job_entity.raw_text,
            parsed_keywords=job_entity.parsed_keywords,
            requirements=job_entity.requirements,
            benefits=job_entity.benefits,
            salary_range=job_entity.salary_range,
            remote=job_entity.remote,
            employment_type=job_entity.employment_type,
            status=job_entity.status,
            application_status=job_entity.application_status,
            created_at=job_entity.created_at,
            updated_at=job_entity.updated_at
        )
        
        self.db.add(job_model)
        await self.db.commit()
        await self.db.refresh(job_model)
        
        return self._model_to_entity(job_model)

    async def get_by_id(self, job_id: str) -> Optional[Job]:
        """Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job entity or None if not found
        """
        stmt = select(JobModel).where(JobModel.id == job_id)
        result = await self.db.execute(stmt)
        job_model = result.scalar_one_or_none()
        
        if not job_model:
            return None
        
        return self._model_to_entity(job_model)

    async def get_user_jobs(
        self,
        user_id: int,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Job]:
        """Get jobs for a specific user with optional filters.
        
        Args:
            user_id: User ID
            status: Optional status filter (active, archived, draft)
            source: Optional source filter (user_created, mock, etc.)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of Job entities
        """
        stmt = select(JobModel).where(JobModel.user_id == user_id)
        
        # Apply filters
        if status:
            stmt = stmt.where(JobModel.status == status)
        if source:
            stmt = stmt.where(JobModel.source == source)
        
        # Order and paginate
        stmt = stmt.order_by(JobModel.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        job_models = result.scalars().all()
        
        return [self._model_to_entity(job_model) for job_model in job_models]

    async def update(self, job_id: str, **kwargs) -> Optional[Job]:
        """Update a job.
        
        Args:
            job_id: Job ID
            **kwargs: Fields to update
            
        Returns:
            Updated Job entity or None if not found
        """
        # Add updated_at timestamp
        kwargs["updated_at"] = datetime.utcnow()
        
        stmt = (
            update(JobModel)
            .where(JobModel.id == job_id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        
        result = await self.db.execute(stmt)
        
        if result.rowcount == 0:
            return None
        
        await self.db.commit()
        
        # Fetch and return updated job
        return await self.get_by_id(job_id)

    async def delete(self, job_id: str) -> bool:
        """Delete a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if deleted, False if not found
        """
        stmt = delete(JobModel).where(JobModel.id == job_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0

    def _model_to_entity(self, model: JobModel) -> Job:
        """Convert database model to domain entity.
        
        Args:
            model: Job database model
            
        Returns:
            Job domain entity
        """
        return Job(
            id=model.id,
            user_id=model.user_id,
            source=model.source,
            title=model.title,
            company=model.company,
            location=model.location,
            description=model.description,
            raw_text=model.raw_text,
            parsed_keywords=model.parsed_keywords or [],
            requirements=model.requirements or [],
            benefits=model.benefits or [],
            salary_range=model.salary_range,
            remote=model.remote,
            employment_type=model.employment_type or "full_time",
            status=model.status,
            application_status=model.application_status or "not_applied",
            created_at=model.created_at,
            updated_at=model.updated_at
        )
