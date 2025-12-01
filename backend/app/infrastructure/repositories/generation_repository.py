"""Generation repository implementation."""

import json
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.generation import Generation
from app.domain.enums.document_type import DocumentType
from app.domain.enums.generation_status import GenerationStatus
from app.domain.interfaces.generation_repository_interface import GenerationRepositoryInterface
from app.infrastructure.database.models import GenerationModel


class GenerationRepository(GenerationRepositoryInterface):
    """Repository for generation operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, generation: Generation) -> Generation:
        """Create a new generation."""
        model = GenerationModel(
            id=str(generation.id),
            user_id=generation.user_id,
            job_id=str(generation.job_id),
            ranking_id=str(generation.ranking_id) if generation.ranking_id else None,
            document_type=generation.document_type.value,
            content_text=generation.content_text,
            status=generation.status.value,
            ats_score=generation.ats_score,
            ats_feedback=generation.ats_feedback,
            llm_metadata=generation.llm_metadata,
            created_at=generation.created_at
        )
        
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        return generation
    
    async def get_by_id(self, generation_id: UUID) -> Optional[Generation]:
        """Get generation by ID."""
        query = select(GenerationModel).where(
            GenerationModel.id == str(generation_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return Generation(
            id=UUID(model.id),
            user_id=model.user_id,
            job_id=UUID(model.job_id),
            ranking_id=UUID(model.ranking_id) if model.ranking_id else None,
            document_type=DocumentType(model.document_type),
            content_text=model.content_text,
            status=GenerationStatus(model.status),
            ats_score=model.ats_score,
            ats_feedback=model.ats_feedback,
            llm_metadata=model.llm_metadata,
            created_at=model.created_at
        )
    
    async def list_by_user(
        self,
        user_id: int,
        document_type: Optional[DocumentType] = None,
        job_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Generation]:
        """List generations for a user with pagination."""
        query = select(GenerationModel).where(GenerationModel.user_id == user_id)
        
        if document_type:
            query = query.where(GenerationModel.document_type == document_type.value)
        
        if job_id:
            query = query.where(GenerationModel.job_id == str(job_id))
        
        query = query.order_by(GenerationModel.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        return [
            Generation(
                id=UUID(model.id),
                user_id=model.user_id,
                job_id=UUID(model.job_id),
                ranking_id=UUID(model.ranking_id) if model.ranking_id else None,
                document_type=DocumentType(model.document_type),
                content_text=model.content_text,
                status=GenerationStatus(model.status),
                ats_score=model.ats_score,
                ats_feedback=model.ats_feedback,
                llm_metadata=model.llm_metadata,
                created_at=model.created_at
            )
            for model in models
        ]
    
    async def update(self, generation: Generation) -> Generation:
        """Update generation."""
        query = select(GenerationModel).where(
            GenerationModel.id == str(generation.id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Generation {generation.id} not found")
        
        model.content_text = generation.content_text
        model.status = generation.status.value
        model.ats_score = generation.ats_score
        model.ats_feedback = generation.ats_feedback
        model.llm_metadata = generation.llm_metadata
        
        await self.session.commit()
        await self.session.refresh(model)
        
        return generation
    
    async def delete(self, generation_id: UUID) -> bool:
        """Delete generation."""
        query = select(GenerationModel).where(
            GenerationModel.id == str(generation_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
