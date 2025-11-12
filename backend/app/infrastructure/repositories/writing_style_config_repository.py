"""Repository for writing style configuration operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from app.infrastructure.database.models import WritingStyleConfigModel


class WritingStyleConfigRepository:
    """Repository for writing style configuration database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, config_data: dict) -> WritingStyleConfigModel:
        """
        Create a new writing style configuration.
        
        Args:
            config_data: Dictionary with configuration data
            
        Returns:
            Created WritingStyleConfigModel
        """
        config_model = WritingStyleConfigModel(**config_data)
        self.db.add(config_model)
        await self.db.commit()
        await self.db.refresh(config_model)
        return config_model
    
    async def get_by_id(self, config_id: str) -> Optional[WritingStyleConfigModel]:
        """
        Get writing style configuration by ID.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            WritingStyleConfigModel or None
        """
        result = await self.db.execute(
            select(WritingStyleConfigModel).where(
                WritingStyleConfigModel.id == config_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> Optional[WritingStyleConfigModel]:
        """
        Get the most recent writing style configuration for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            WritingStyleConfigModel or None
        """
        result = await self.db.execute(
            select(WritingStyleConfigModel)
            .where(WritingStyleConfigModel.user_id == user_id)
            .order_by(WritingStyleConfigModel.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update(self, config_id: str, updates: dict) -> Optional[WritingStyleConfigModel]:
        """
        Update writing style configuration.
        
        Args:
            config_id: Configuration ID
            updates: Dictionary with fields to update
            
        Returns:
            Updated WritingStyleConfigModel or None
        """
        updates['updated_at'] = datetime.utcnow()
        
        await self.db.execute(
            update(WritingStyleConfigModel)
            .where(WritingStyleConfigModel.id == config_id)
            .values(**updates)
        )
        await self.db.commit()
        
        return await self.get_by_id(config_id)
    
    async def delete(self, config_id: str, user_id: int) -> bool:
        """
        Delete writing style configuration.
        
        Args:
            config_id: Configuration ID
            user_id: User ID (for authorization check)
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.db.execute(
            delete(WritingStyleConfigModel)
            .where(
                WritingStyleConfigModel.id == config_id,
                WritingStyleConfigModel.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def exists(self, config_id: str) -> bool:
        """
        Check if configuration exists.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if exists, False otherwise
        """
        result = await self.db.execute(
            select(WritingStyleConfigModel.id)
            .where(WritingStyleConfigModel.id == config_id)
        )
        return result.scalar_one_or_none() is not None
