"""Writing style repository implementation."""

import json
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.writing_style import WritingStyle
from app.domain.interfaces.writing_style_repository_interface import WritingStyleRepositoryInterface
from app.infrastructure.database.models import WritingStyleModel


class WritingStyleRepository(WritingStyleRepositoryInterface):
    """Repository for writing style operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, style: WritingStyle) -> WritingStyle:
        """Create a new writing style."""
        model = WritingStyleModel(
            id=str(style.id),
            user_id=style.user_id,
            extracted_style=json.dumps(style.extracted_style),
            sample_document_id=str(style.sample_document_id),
            extraction_date=style.extraction_date,
            llm_metadata=json.dumps(style.llm_metadata) if style.llm_metadata else None
        )
        
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        return style
    
    async def get_by_user(self, user_id: int) -> Optional[WritingStyle]:
        """Get most recent writing style for user."""
        query = select(WritingStyleModel).where(
            WritingStyleModel.user_id == user_id
        ).order_by(WritingStyleModel.extraction_date.desc())
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return WritingStyle(
            id=UUID(model.id),
            user_id=model.user_id,
            extracted_style=json.loads(model.extracted_style),
            sample_document_id=UUID(model.sample_document_id),
            extraction_date=model.extraction_date,
            llm_metadata=model.llm_metadata
        )
    
    async def get_by_sample(self, sample_id: UUID) -> Optional[WritingStyle]:
        """Get writing style extracted from specific sample."""
        query = select(WritingStyleModel).where(
            WritingStyleModel.sample_document_id == str(sample_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return WritingStyle(
            id=UUID(model.id),
            user_id=model.user_id,
            extracted_style=json.loads(model.extracted_style),
            sample_document_id=UUID(model.sample_document_id),
            extraction_date=model.extraction_date,
            llm_metadata=model.llm_metadata
        )
    
    async def delete_by_sample(self, sample_id: UUID) -> bool:
        """Delete writing style associated with sample."""
        query = delete(WritingStyleModel).where(
            WritingStyleModel.sample_document_id == str(sample_id)
        )
        
        result = await self.session.execute(query)
        await self.session.commit()
        
        return result.rowcount > 0
