"""Sample document repository for database operations."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.domain.entities.sample import Sample
from app.infrastructure.database.models import SampleDocumentModel


class SampleRepository:
    """Repository for sample document database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, sample: Sample) -> Sample:
        """
        Create a new sample document.
        Automatically deactivates previous samples of the same type.
        """
        # Deactivate previous samples of the same type
        await self.db.execute(
            update(SampleDocumentModel)
            .where(
                SampleDocumentModel.user_id == sample.user_id,
                SampleDocumentModel.document_type == sample.document_type,
                SampleDocumentModel.is_active == True
            )
            .values(is_active=False)
        )

        # Create new sample
        db_sample = SampleDocumentModel(
            id=sample.id,
            user_id=sample.user_id,
            document_type=sample.document_type,
            original_filename=sample.original_filename,
            full_text=sample.full_text,
            writing_style=sample.writing_style,
            word_count=sample.word_count,
            character_count=sample.character_count,
            is_active=sample.is_active,
            created_at=sample.created_at,
            updated_at=sample.updated_at
        )
        self.db.add(db_sample)
        await self.db.commit()
        await self.db.refresh(db_sample)

        return self._to_entity(db_sample)

    async def get_by_id(self, sample_id: str, user_id: int) -> Optional[Sample]:
        """Get sample by ID (scoped to user)."""
        result = await self.db.execute(
            select(SampleDocumentModel).where(
                SampleDocumentModel.id == sample_id,
                SampleDocumentModel.user_id == user_id
            )
        )
        db_sample = result.scalar_one_or_none()

        if db_sample:
            return self._to_entity(db_sample)
        return None

    async def list_by_user(
        self,
        user_id: int,
        document_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Sample]:
        """List all samples for a user with optional filters."""
        query = select(SampleDocumentModel).where(
            SampleDocumentModel.user_id == user_id
        )

        if document_type:
            query = query.where(SampleDocumentModel.document_type == document_type)
        
        if is_active is not None:
            query = query.where(SampleDocumentModel.is_active == is_active)

        query = query.order_by(SampleDocumentModel.created_at.desc())
        
        result = await self.db.execute(query)
        db_samples = result.scalars().all()
        
        return [self._to_entity(s) for s in db_samples]

    async def delete(self, sample_id: str, user_id: int) -> bool:
        """Delete a sample document (hard delete)."""
        result = await self.db.execute(
            delete(SampleDocumentModel).where(
                SampleDocumentModel.id == sample_id,
                SampleDocumentModel.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def get_active_sample(self, user_id: int, document_type: str) -> Optional[Sample]:
        """Get the active sample for a user and document type."""
        result = await self.db.execute(
            select(SampleDocumentModel).where(
                SampleDocumentModel.user_id == user_id,
                SampleDocumentModel.document_type == document_type,
                SampleDocumentModel.is_active == True
            )
        )
        db_sample = result.scalar_one_or_none()

        if db_sample:
            return self._to_entity(db_sample)
        return None

    def _to_entity(self, db_sample: SampleDocumentModel) -> Sample:
        """Convert database model to domain entity."""
        return Sample(
            id=db_sample.id,
            user_id=db_sample.user_id,
            document_type=db_sample.document_type,
            original_filename=db_sample.original_filename,
            full_text=db_sample.full_text,
            writing_style=db_sample.writing_style,
            word_count=db_sample.word_count,
            character_count=db_sample.character_count,
            is_active=db_sample.is_active,
            created_at=db_sample.created_at,
            updated_at=db_sample.updated_at
        )
