"""Generation repository for database operations."""

import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, update, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generation import (
    Generation,
    GenerationOptions,
    GenerationResult
)
from app.infrastructure.database.models import GenerationModel


class GenerationRepository:
    """Repository for generation database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, generation: Generation) -> Generation:
        """Create a new generation."""
        # Convert options and result to JSON strings
        options_json = generation.options.model_dump_json() if generation.options else None
        result_json = generation.result.model_dump_json() if generation.result else None

        generation_model = GenerationModel(
            id=generation.id,
            user_id=generation.user_id,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            document_type=generation.document_type,
            status=generation.status,
            current_stage=generation.current_stage,
            total_stages=generation.total_stages,
            stage_name=generation.stage_name,
            stage_description=generation.stage_description,
            error_message=generation.error_message,
            options=options_json,
            result=result_json,
            tokens_used=generation.tokens_used,
            generation_time=generation.generation_time,
            created_at=generation.created_at,
            started_at=generation.started_at,
            completed_at=generation.completed_at,
            updated_at=generation.updated_at
        )

        self.session.add(generation_model)
        await self.session.commit()
        await self.session.refresh(generation_model)

        return await self._model_to_entity(generation_model)

    async def get_by_id(self, generation_id: str) -> Optional[Generation]:
        """Get generation by ID."""
        stmt = select(GenerationModel).where(GenerationModel.id == generation_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return await self._model_to_entity(model)

    async def get_by_user_id(
        self,
        user_id: int,
        job_id: Optional[str] = None,
        status: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Generation], int]:
        """Get generations for a user with optional filters."""
        # Build query
        conditions = [GenerationModel.user_id == user_id]
        if job_id:
            conditions.append(GenerationModel.job_id == job_id)
        if status:
            conditions.append(GenerationModel.status == status)
        if document_type:
            conditions.append(GenerationModel.document_type == document_type)

        # Get total count
        count_stmt = select(func.count(GenerationModel.id)).where(and_(*conditions))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = (
            select(GenerationModel)
            .where(and_(*conditions))
            .order_by(GenerationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        generations = [await self._model_to_entity(model) for model in models]
        return generations, total

    async def update_status(
        self,
        generation_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Generation]:
        """Update generation status."""
        stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status=status,
                error_message=error_message,
                updated_at=datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get_by_id(generation_id)

    async def update_stage(
        self,
        generation_id: str,
        current_stage: int,
        stage_name: Optional[str],
        stage_description: Optional[str],
        tokens_used: int = 0
    ) -> Optional[Generation]:
        """Update generation stage progress."""
        stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                current_stage=current_stage,
                stage_name=stage_name,
                stage_description=stage_description,
                tokens_used=tokens_used,
                status="generating" if current_stage > 0 and current_stage < 2 else "pending",
                started_at=datetime.utcnow() if current_stage == 1 else GenerationModel.started_at,
                updated_at=datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get_by_id(generation_id)

    async def set_completed(
        self,
        generation_id: str,
        result: GenerationResult,
        tokens_used: int,
        generation_time: float
    ) -> Optional[Generation]:
        """Mark generation as completed with result."""
        result_json = result.model_dump_json()

        stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status="completed",
                result=result_json,
                tokens_used=tokens_used,
                generation_time=generation_time,
                completed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.get_by_id(generation_id)

    async def set_failed(
        self,
        generation_id: str,
        error_message: str,
        tokens_used: int = 0
    ) -> Optional[Generation]:
        """Mark generation as failed."""
        return await self.update_status(generation_id, "failed", error_message)

    async def delete(self, generation_id: str) -> bool:
        """Delete generation."""
        stmt = delete(GenerationModel).where(GenerationModel.id == generation_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def exists(self, generation_id: str) -> bool:
        """Check if generation exists."""
        stmt = select(GenerationModel.id).where(GenerationModel.id == generation_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_recent_by_user(self, user_id: int, hours: int = 1) -> int:
        """Count generations by user in the last N hours (for rate limiting)."""
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        stmt = select(func.count(GenerationModel.id)).where(
            and_(
                GenerationModel.user_id == user_id,
                GenerationModel.created_at >= cutoff_time
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count if count is not None else 0

    async def get_statistics_by_user(self, user_id: int) -> dict:
        """Get generation statistics for a user."""
        # Total generations
        total_stmt = select(func.count(GenerationModel.id)).where(
            GenerationModel.user_id == user_id
        )
        total_result = await self.session.execute(total_stmt)
        total_generations = total_result.scalar() or 0

        # Count by status
        completed_stmt = select(func.count(GenerationModel.id)).where(
            and_(
                GenerationModel.user_id == user_id,
                GenerationModel.status == "completed"
            )
        )
        completed_result = await self.session.execute(completed_stmt)
        completed = completed_result.scalar() or 0

        failed_stmt = select(func.count(GenerationModel.id)).where(
            and_(
                GenerationModel.user_id == user_id,
                GenerationModel.status == "failed"
            )
        )
        failed_result = await self.session.execute(failed_stmt)
        failed = failed_result.scalar() or 0

        in_progress_stmt = select(func.count(GenerationModel.id)).where(
            and_(
                GenerationModel.user_id == user_id,
                GenerationModel.status.in_(["pending", "generating"])
            )
        )
        in_progress_result = await self.session.execute(in_progress_stmt)
        in_progress = in_progress_result.scalar() or 0

        # Average ATS score (from completed generations with results)
        # Note: This is a simplified version; a proper implementation would parse JSON
        average_ats_score = 0.0  # TODO: Calculate from result JSON

        return {
            "total_generations": total_generations,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "average_ats_score": average_ats_score
        }

    async def _model_to_entity(self, model: GenerationModel) -> Generation:
        """Convert database model to domain entity."""
        # Parse options
        options = None
        if model.options:
            try:
                options_dict = json.loads(model.options)
                options = GenerationOptions(**options_dict)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        # Parse result
        result = None
        if model.result:
            try:
                result_dict = json.loads(model.result)
                result = GenerationResult(**result_dict)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        return Generation(
            id=model.id,
            user_id=model.user_id,
            profile_id=model.profile_id,
            job_id=model.job_id,
            document_type=model.document_type,
            status=model.status,
            current_stage=model.current_stage,
            total_stages=model.total_stages,
            stage_name=model.stage_name,
            stage_description=model.stage_description,
            error_message=model.error_message,
            options=options,
            result=result,
            tokens_used=model.tokens_used,
            generation_time=model.generation_time,
            created_at=model.created_at,
            started_at=model.started_at,
            completed_at=model.completed_at,
            updated_at=model.updated_at
        )
