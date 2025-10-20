"""Job description repository for data access operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.job_description import JobDescription, JobDescriptionMetadata, JobDescriptionStatus, JobDescriptionSource
from ...infrastructure.database.models import JobDescriptionModel


class JobDescriptionRepository:
    """Repository for job description data access operations using the database."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, job_description: JobDescription) -> JobDescription:
        """Persist a new JobDescription to the database and return the domain entity with IDs/timestamps."""
        model = JobDescriptionModel(
            id=str(job_description.id),
            user_id=str(job_description.user_id),
            title=job_description.title,
            company=job_description.company,
            description=job_description.description,
            requirements=job_description.requirements,
            benefits=job_description.benefits,
            status=JobDescriptionStatus.DRAFT,
            source=job_description.source if isinstance(job_description.source, JobDescriptionSource) else JobDescriptionSource.MANUAL,
            keywords=job_description.metadata.keywords if job_description.metadata else [],
            technical_skills=job_description.metadata.technical_skills if job_description.metadata else [],
            soft_skills=job_description.metadata.soft_skills if job_description.metadata else [],
            experience_level=job_description.metadata.experience_level if job_description.metadata else "",
            industry=job_description.metadata.industry if job_description.metadata else None,
            company_size=job_description.metadata.company_size if job_description.metadata else None,
            remote_policy=job_description.metadata.remote_policy if job_description.metadata else None,
            salary_range_min=job_description.metadata.salary_range_min if job_description.metadata else None,
            salary_range_max=job_description.metadata.salary_range_max if job_description.metadata else None,
            salary_currency=job_description.metadata.salary_currency if job_description.metadata else "USD",
            location=job_description.metadata.location if job_description.metadata else None,
            created_from_url=job_description.metadata.created_from_url if job_description.metadata else None,
            version=job_description.version,
        )

        self.session.add(model)
        await self.session.flush()

        # refresh model to get timestamps
        await self.session.refresh(model)

        # Map back to domain entity
        job_description.created_at = model.created_at
        job_description.updated_at = model.updated_at

        return job_description

    async def _row_to_entity(self, row: JobDescriptionModel) -> JobDescription:
        """Convert DB model row to domain JobDescription entity."""
        from ...domain.entities.job_description import JobDescription, JobDescriptionMetadata

        metadata = JobDescriptionMetadata(
            keywords=row.keywords or [],
            technical_skills=row.technical_skills or [],
            soft_skills=row.soft_skills or [],
            experience_level=row.experience_level or "",
            industry=row.industry,
            company_size=row.company_size,
            remote_policy=row.remote_policy,
            salary_range_min=row.salary_range_min,
            salary_range_max=row.salary_range_max,
            salary_currency=row.salary_currency or "USD",
            location=row.location,
            created_from_url=row.created_from_url,
        )

        return JobDescription(
            id=UUID(row.id),
            user_id=UUID(row.user_id),
            title=row.title,
            company=row.company,
            description=row.description,
            requirements=row.requirements or [],
            benefits=row.benefits or [],
            status=row.status,
            source=row.source,
            metadata=metadata,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def get_by_id(self, job_description_id: UUID) -> Optional[JobDescription]:
        query = select(JobDescriptionModel).where(JobDescriptionModel.id == str(job_description_id))
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()
        if not row:
            return None
        return await self._row_to_entity(row)

    async def get_by_user_id(self, user_id: UUID) -> List[JobDescription]:
        query = select(JobDescriptionModel).where(JobDescriptionModel.user_id == str(user_id))
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [await self._row_to_entity(r) for r in rows]

    async def get_active_by_user_id(self, user_id: UUID) -> List[JobDescription]:
        query = select(JobDescriptionModel).where(
            JobDescriptionModel.user_id == str(user_id),
            JobDescriptionModel.status == JobDescriptionStatus.ACTIVE,
        )
        result = await self.session.execute(query)
        rows = result.scalars().all()
        return [await self._row_to_entity(r) for r in rows]

    async def update(self, job_description: JobDescription) -> JobDescription:
        # Update fields
        update_values = {
            'title': job_description.title,
            'company': job_description.company,
            'description': job_description.description,
            'requirements': job_description.requirements,
            'benefits': job_description.benefits,
            'status': job_description.status,
            'source': job_description.source,
            'keywords': job_description.metadata.keywords if job_description.metadata else [],
            'technical_skills': job_description.metadata.technical_skills if job_description.metadata else [],
            'soft_skills': job_description.metadata.soft_skills if job_description.metadata else [],
            'experience_level': job_description.metadata.experience_level if job_description.metadata else "",
            'industry': job_description.metadata.industry if job_description.metadata else None,
            'company_size': job_description.metadata.company_size if job_description.metadata else None,
            'remote_policy': job_description.metadata.remote_policy if job_description.metadata else None,
            'salary_range_min': job_description.metadata.salary_range_min if job_description.metadata else None,
            'salary_range_max': job_description.metadata.salary_range_max if job_description.metadata else None,
            'salary_currency': job_description.metadata.salary_currency if job_description.metadata else "USD",
            'location': job_description.metadata.location if job_description.metadata else None,
            'created_from_url': job_description.metadata.created_from_url if job_description.metadata else None,
            'version': job_description.version,
        }

        await self.session.execute(
            update(JobDescriptionModel)
            .where(JobDescriptionModel.id == str(job_description.id))
            .values(**update_values)
        )
        await self.session.flush()

        # Reload row
        updated = await self.get_by_id(job_description.id)
        if not updated:
            raise ValueError("Failed to update job description")
        return updated

    async def delete(self, job_description_id: UUID) -> bool:
        await self.session.execute(
            delete(JobDescriptionModel).where(JobDescriptionModel.id == str(job_description_id))
        )
        await self.session.flush()
        return True

    async def exists(self, job_description_id: UUID) -> bool:
        query = select(func.count()).select_from(JobDescriptionModel).where(JobDescriptionModel.id == str(job_description_id))
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    async def count_by_user_id(self, user_id: UUID) -> int:
        query = select(func.count()).select_from(JobDescriptionModel).where(JobDescriptionModel.user_id == str(user_id))
        result = await self.session.execute(query)
        return int(result.scalar_one() or 0)

    async def search_by_user_id(
        self,
        user_id: UUID,
        query: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[JobDescription]:
        stmt = select(JobDescriptionModel).where(JobDescriptionModel.user_id == str(user_id))

        if status:
            try:
                stmt = stmt.where(JobDescriptionModel.status == JobDescriptionStatus(status))
            except Exception:
                pass

        if query:
            q = f"%{query.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(JobDescriptionModel.title).like(q),
                    func.lower(JobDescriptionModel.company).like(q),
                    func.lower(JobDescriptionModel.description).like(q),
                )
            )

        stmt = stmt.order_by(JobDescriptionModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        return [await self._row_to_entity(r) for r in rows]