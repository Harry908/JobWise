"""Repository for layout configuration operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime

from app.infrastructure.database.models import LayoutConfigModel


class LayoutConfigRepository:
    """Repository for layout configuration database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db
    
    async def create(self, config_data: dict) -> LayoutConfigModel:
        """
        Create a new layout configuration.
        
        Args:
            config_data: Dictionary with configuration data
            
        Returns:
            Created LayoutConfigModel
        """
        config_model = LayoutConfigModel(**config_data)
        self.db.add(config_model)
        await self.db.commit()
        await self.db.refresh(config_model)
        return config_model
    
    async def get_by_id(self, config_id: str) -> Optional[LayoutConfigModel]:
        """
        Get layout configuration by ID.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            LayoutConfigModel or None
        """
        result = await self.db.execute(
            select(LayoutConfigModel).where(
                LayoutConfigModel.id == config_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> Optional[LayoutConfigModel]:
        """
        Get the most recent layout configuration for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            LayoutConfigModel or None
        """
        result = await self.db.execute(
            select(LayoutConfigModel)
            .where(LayoutConfigModel.user_id == user_id)
            .order_by(LayoutConfigModel.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update(self, config_id: str, updates: dict) -> Optional[LayoutConfigModel]:
        """
        Update layout configuration.
        
        Args:
            config_id: Configuration ID
            updates: Dictionary with fields to update
            
        Returns:
            Updated LayoutConfigModel or None
        """
        updates['updated_at'] = datetime.utcnow()
        
        await self.db.execute(
            update(LayoutConfigModel)
            .where(LayoutConfigModel.id == config_id)
            .values(**updates)
        )
        await self.db.commit()
        
        return await self.get_by_id(config_id)
    
    async def delete(self, config_id: str, user_id: int) -> bool:
        """
        Delete layout configuration.
        
        Args:
            config_id: Configuration ID
            user_id: User ID (for authorization check)
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.db.execute(
            delete(LayoutConfigModel)
            .where(
                LayoutConfigModel.id == config_id,
                LayoutConfigModel.user_id == user_id
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
            select(LayoutConfigModel.id)
            .where(LayoutConfigModel.id == config_id)
        )
        return result.scalar_one_or_none() is not None
