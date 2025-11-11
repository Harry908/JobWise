"""Repository for example resume operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models import ExampleResumeModel


class ExampleResumeRepository:
    """Repository for example resume operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, example_resume: ExampleResumeModel) -> ExampleResumeModel:
        """Create a new example resume record."""
        self.db.add(example_resume)
        await self.db.commit()
        await self.db.refresh(example_resume)
        return example_resume
    
    async def get_by_id(self, example_id: str) -> Optional[ExampleResumeModel]:
        """Get example resume by ID."""
        result = await self.db.execute(
            select(ExampleResumeModel).where(ExampleResumeModel.id == example_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: str) -> List[ExampleResumeModel]:
        """Get all example resumes for a user."""
        result = await self.db.execute(
            select(ExampleResumeModel)
            .where(ExampleResumeModel.user_id == user_id)
            .order_by(desc(ExampleResumeModel.created_at))
        )
        return list(result.scalars().all())
    
    async def update(self, example_resume: ExampleResumeModel) -> ExampleResumeModel:
        """Update an example resume record."""
        await self.db.merge(example_resume)
        await self.db.commit()
        await self.db.refresh(example_resume)
        return example_resume
    
    async def delete_by_id(self, example_id: str, user_id: str) -> bool:
        """Delete an example resume by ID for a specific user."""
        result = await self.db.execute(
            delete(ExampleResumeModel)
            .where(
                ExampleResumeModel.id == example_id,
                ExampleResumeModel.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_latest_by_user(self, user_id: str) -> Optional[ExampleResumeModel]:
        """Get the latest example resume for a user."""
        result = await self.db.execute(
            select(ExampleResumeModel)
            .where(ExampleResumeModel.user_id == user_id)
            .order_by(desc(ExampleResumeModel.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def count_by_user(self, user_id: str) -> int:
        """Count example resumes for a user."""
        result = await self.db.execute(
            select(ExampleResumeModel)
            .where(ExampleResumeModel.user_id == user_id)
        )
        return len(list(result.scalars().all()))