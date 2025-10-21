"""Job Description Repository - CRUD operations for job descriptions"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos.job_description_dtos import (
    CreateJobDescriptionRequest,
    UpdateJobDescriptionRequest,
    JobDescriptionResponse
)
from ...application.services.job_description_parser import JobDescriptionParser
from ...infrastructure.database.models import JobDescriptionModel


class JobDescriptionRepository:
    """Repository for job description CRUD operations"""

    def __init__(self, session: AsyncSession, parser: JobDescriptionParser):
        self.session = session
        self.parser = parser

    async def create(
        self,
        user_id: str,
        data: CreateJobDescriptionRequest
    ) -> JobDescriptionResponse:
        """
        Create job description from raw text or structured data.

        If raw_text is provided, parse it first and merge with structured data.
        """

        # Parse raw text if provided
        if data.raw_text:
            parsed = self.parser.parse(data.raw_text)

            # Merge parsed data with provided structured data (structured data wins)
            job_data = {
                **parsed,  # Parsed from text
                **data.model_dump(exclude={"raw_text"}, exclude_none=True),  # Override
            }
            job_data["raw_text"] = data.raw_text
        else:
            # Use structured data directly
            job_data = data.model_dump(exclude_none=True)

        # Validate required fields after parsing
        if not job_data.get("title"):
            raise ValueError("Could not extract title from text")
        if not job_data.get("company"):
            raise ValueError("Could not extract company from text")
        if not job_data.get("description"):
            raise ValueError("Could not extract description from text")

        # Create database model
        job_desc = JobDescriptionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            **job_data
        )

        self.session.add(job_desc)
        await self.session.commit()
        await self.session.refresh(job_desc)

        return JobDescriptionResponse.model_validate(job_desc)

    async def get_by_id(self, job_id: str) -> Optional[JobDescriptionResponse]:
        """Get job description by ID"""
        result = await self.session.execute(
            select(JobDescriptionModel).where(JobDescriptionModel.id == job_id)
        )
        job_desc = result.scalar_one_or_none()

        if job_desc:
            return JobDescriptionResponse.model_validate(job_desc)
        return None

    async def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[JobDescriptionResponse]:
        """List user's job descriptions with filters"""
        query = select(JobDescriptionModel).where(
            JobDescriptionModel.user_id == user_id
        )

        # Filter by status (exclude deleted by default)
        if status:
            query = query.where(JobDescriptionModel.status == status)
        else:
            query = query.where(JobDescriptionModel.status != "deleted")

        # Filter by source
        if source:
            query = query.where(JobDescriptionModel.source == source)

        query = query.order_by(JobDescriptionModel.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        jobs = result.scalars().all()

        return [JobDescriptionResponse.model_validate(j) for j in jobs]

    async def count_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        """Count user's job descriptions"""
        query = select(func.count(JobDescriptionModel.id)).where(
            JobDescriptionModel.user_id == user_id
        )

        # Filter by status (exclude deleted by default)
        if status:
            query = query.where(JobDescriptionModel.status == status)
        else:
            query = query.where(JobDescriptionModel.status != "deleted")

        # Filter by source
        if source:
            query = query.where(JobDescriptionModel.source == source)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def update(
        self,
        job_id: str,
        data: UpdateJobDescriptionRequest
    ) -> JobDescriptionResponse:
        """Update job description"""
        job_desc = await self.session.get(JobDescriptionModel, job_id)

        if not job_desc:
            raise ValueError("Job description not found")

        # Update fields
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(job_desc, field, value)

        job_desc.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(job_desc)

        return JobDescriptionResponse.model_validate(job_desc)

    async def delete(self, job_id: str) -> bool:
        """Soft delete job description (set status to deleted)"""
        job_desc = await self.session.get(JobDescriptionModel, job_id)

        if not job_desc:
            return False

        job_desc.status = "deleted"
        job_desc.updated_at = datetime.utcnow()

        await self.session.commit()
        return True

    async def verify_ownership(self, job_id: str, user_id: str) -> bool:
        """Verify that the job belongs to the user"""
        result = await self.session.execute(
            select(JobDescriptionModel).where(
                JobDescriptionModel.id == job_id,
                JobDescriptionModel.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None
