# Generation Repository

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, insert, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generation import Generation, GenerationStatus, GenerationResult, DocumentType
from app.infrastructure.database.models import GenerationModel


class GenerationRepository:
    """Repository for generation data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, generation: Generation) -> Generation:
        """Create a new generation."""
        # Convert domain entity to database model
        model = GenerationModel(
            id=generation.id,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            status=generation.status.value,
            created_at=generation.created_at,
            updated_at=generation.updated_at,
            completed_at=generation.completed_at,
            results=[],  # Will be populated when results are added
            error_message=generation.error_message,
            processing_time_seconds=generation.processing_time_seconds,
            pipeline_metadata=generation.pipeline_metadata
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return generation

    async def get_by_id(self, generation_id: str) -> Optional[Generation]:
        """Get generation by ID."""
        query = select(GenerationModel).where(GenerationModel.id == generation_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_by_user_id(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Generation]:
        """Get generations by user ID."""
        # Note: Generation entity doesn't have user_id, so we need to join with profiles
        from app.infrastructure.database.models import MasterProfileModel

        query = (
            select(GenerationModel)
            .join(MasterProfileModel, GenerationModel.profile_id == MasterProfileModel.id)
            .where(MasterProfileModel.user_id == user_id)
            .order_by(GenerationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def count_by_user_id(self, user_id: str) -> int:
        """Count generations by user ID."""
        from app.infrastructure.database.models import MasterProfileModel

        query = (
            select(func.count())
            .select_from(GenerationModel)
            .join(MasterProfileModel, GenerationModel.profile_id == MasterProfileModel.id)
            .where(MasterProfileModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update_status(self, generation_id: str, status: GenerationStatus) -> bool:
        """Update generation status."""
        update_stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status=status.value,
                updated_at=datetime.utcnow()
            )
        )

        if status == GenerationStatus.COMPLETED:
            update_stmt = update_stmt.values(completed_at=datetime.utcnow())
        elif status == GenerationStatus.FAILED:
            update_stmt = update_stmt.values(completed_at=datetime.utcnow())

        result = await self.session.execute(update_stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def update_progress(self, generation_id: str, progress: Dict[str, Any]) -> bool:
        """Update generation progress."""
        update_stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                pipeline_metadata=GenerationModel.pipeline_metadata.op('||')(progress),
                updated_at=datetime.utcnow()
            )
        )

        result = await self.session.execute(update_stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def complete_generation(
        self,
        generation_id: str,
        result_data: Dict[str, Any],
        generation_time: float
    ) -> bool:
        """Complete generation with results."""
        # Create GenerationResult
        result = GenerationResult(
            document_type=DocumentType.RESUME,  # Default to resume for now
            content=result_data.get('content', ''),
            ats_score=result_data.get('ats_score'),
            word_count=len(result_data.get('content', '').split()) if result_data.get('content') else 0,
            generated_at=datetime.utcnow(),
            metadata=result_data.get('metadata', {})
        )

        update_stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status=GenerationStatus.COMPLETED.value,
                results=[result],  # Store as list
                processing_time_seconds=generation_time,
                completed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        result = await self.session.execute(update_stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def fail_generation(self, generation_id: str, error_message: str) -> bool:
        """Mark generation as failed."""
        update_stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status=GenerationStatus.FAILED.value,
                error_message=error_message,
                completed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        result = await self.session.execute(update_stmt)
        await self.session.commit()

        return result.rowcount > 0

    def _model_to_entity(self, model: GenerationModel) -> Generation:
        """Convert database model to domain entity."""
        # Convert results back to GenerationResult objects
        results = []
        if model.results:
            for result_data in model.results:
                if isinstance(result_data, dict):
                    results.append(GenerationResult(**result_data))
                else:
                    results.append(result_data)

        return Generation(
            id=model.id,
            profile_id=model.profile_id,
            job_id=model.job_id or "",  # Handle None case
            status=GenerationStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            results=results,
            error_message=model.error_message,
            processing_time_seconds=model.processing_time_seconds,
            pipeline_metadata=model.pipeline_metadata or {}
        )