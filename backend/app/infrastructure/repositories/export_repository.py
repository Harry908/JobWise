"""
Export Repository
Data access layer for exports.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.export import Export
from app.domain.enums.export_format import ExportFormat
from app.domain.enums.template_type import TemplateType
from app.infrastructure.database.models import ExportModel


class ExportRepository:
    """Repository for export database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def create(self, export: Export) -> Export:
        """
        Create a new export record.
        
        Args:
            export: Export entity
        
        Returns:
            Created export entity
        """
        export_model = ExportModel(
            id=export.id,
            user_id=export.user_id,
            generation_id=export.generation_id,
            format=export.format.value,
            template=export.template.value,
            filename=export.filename,
            file_path=export.file_path,
            file_size_bytes=export.file_size_bytes,
            page_count=export.page_count,
            options=export.options,
            metadata=export.metadata,
            download_url=export.download_url,
            expires_at=export.expires_at,
            created_at=export.created_at
        )
        
        self.session.add(export_model)
        await self.session.commit()
        await self.session.refresh(export_model)
        
        return self._to_entity(export_model)
    
    async def get_by_id(self, export_id: str, user_id: int) -> Optional[Export]:
        """
        Get export by ID and user ID.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
        
        Returns:
            Export entity or None
        """
        stmt = select(ExportModel).where(
            ExportModel.id == export_id,
            ExportModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        export_model = result.scalar_one_or_none()
        
        if not export_model:
            return None
        
        return self._to_entity(export_model)
    
    async def list_by_user(
        self,
        user_id: int,
        format: Optional[ExportFormat] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Export]:
        """
        List exports for a user with pagination.
        
        Args:
            user_id: User ID
            format: Optional format filter
            limit: Maximum results
            offset: Pagination offset
        
        Returns:
            List of export entities
        """
        stmt = select(ExportModel).where(ExportModel.user_id == user_id)
        
        if format:
            stmt = stmt.where(ExportModel.format == format.value)
        
        stmt = stmt.order_by(ExportModel.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        export_models = result.scalars().all()
        
        return [self._to_entity(model) for model in export_models]
    
    async def delete(self, export_id: str, user_id: int) -> bool:
        """
        Delete an export.
        
        Args:
            export_id: Export ID
            user_id: User ID (for authorization)
        
        Returns:
            True if deleted, False if not found
        """
        stmt = select(ExportModel).where(
            ExportModel.id == export_id,
            ExportModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        export_model = result.scalar_one_or_none()
        
        if not export_model:
            return False
        
        await self.session.delete(export_model)
        await self.session.commit()
        
        return True
    
    async def cleanup_expired(self) -> int:
        """
        Delete all expired exports.
        
        Returns:
            Number of exports deleted
        """
        stmt = select(ExportModel).where(
            ExportModel.expires_at < datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        expired_models = result.scalars().all()
        
        count = len(expired_models)
        
        for model in expired_models:
            await self.session.delete(model)
        
        await self.session.commit()
        
        return count
    
    def _to_entity(self, model: ExportModel) -> Export:
        """Convert database model to domain entity."""
        return Export(
            id=model.id,
            user_id=model.user_id,
            generation_id=model.generation_id,
            format=ExportFormat(model.format),
            template=TemplateType(model.template),
            filename=model.filename,
            file_path=model.file_path,
            file_size_bytes=model.file_size_bytes,
            page_count=model.page_count,
            options=model.options or {},
            metadata=model.metadata or {},
            download_url=model.download_url,
            expires_at=model.expires_at,
            created_at=model.created_at
        )
