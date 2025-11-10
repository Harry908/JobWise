"""Repository for user generation profile database operations."""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.domain.entities.preferences.user_generation_profile import UserGenerationProfile
from app.infrastructure.database.models import UserGenerationProfileModel
from app.core.exceptions import DatabaseException

logger = logging.getLogger(__name__)


class UserGenerationProfileRepository:
    """Repository for user generation profile operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, profile: UserGenerationProfile) -> UserGenerationProfile:
        """
        Create a new user generation profile.
        
        Args:
            profile: UserGenerationProfile entity
            
        Returns:
            Created profile with ID
            
        Raises:
            DatabaseException: Creation failed
        """
        try:
            # Convert entity to model
            profile_model = UserGenerationProfileModel(
                user_id=profile.user_id,
                writing_style_config_id=profile.writing_style_config_id,
                layout_config_id=profile.layout_config_id,
                is_active=profile.is_active,
                is_complete=profile.is_complete,
                setup_stage=profile.setup_stage,
                quality_targets=profile.quality_targets.dict() if profile.quality_targets else {},
                job_type_overrides=profile.job_type_overrides,
                generations_count=profile.generations_count,
                successful_generations=profile.successful_generations,
                user_satisfaction_scores=profile.user_satisfaction_scores,
                preference_learning_enabled=profile.preference_learning_enabled,
                auto_update_from_feedback=profile.auto_update_from_feedback,
                last_feedback_learning=profile.last_feedback_learning,
                preferred_templates=profile.preferred_templates,
                industry_focus=profile.industry_focus,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
                last_generation_at=profile.last_generation_at
            )
            
            self.db.add(profile_model)
            await self.db.commit()
            await self.db.refresh(profile_model)
            
            # Convert back to entity
            return self._model_to_entity(profile_model)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user generation profile: {e}")
            raise DatabaseException(f"Failed to create profile: {str(e)}")

    async def get_by_user_id(self, user_id: int) -> Optional[UserGenerationProfile]:
        """
        Get active user generation profile by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserGenerationProfile if found, None otherwise
        """
        try:
            query = select(UserGenerationProfileModel).where(
                UserGenerationProfileModel.user_id == user_id,
                UserGenerationProfileModel.is_active == True
            ).options(
                selectinload(UserGenerationProfileModel.writing_style_config),
                selectinload(UserGenerationProfileModel.layout_config),
                selectinload(UserGenerationProfileModel.example_resumes)
            )
            
            result = await self.db.execute(query)
            profile_model = result.scalar_one_or_none()
            
            if profile_model:
                return self._model_to_entity(profile_model)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user generation profile for user {user_id}: {e}")
            raise DatabaseException(f"Failed to get profile: {str(e)}")

    async def get_by_id(self, profile_id: int) -> Optional[UserGenerationProfile]:
        """
        Get user generation profile by ID.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            UserGenerationProfile if found, None otherwise
        """
        try:
            query = select(UserGenerationProfileModel).where(
                UserGenerationProfileModel.id == profile_id
            ).options(
                selectinload(UserGenerationProfileModel.writing_style_config),
                selectinload(UserGenerationProfileModel.layout_config),
                selectinload(UserGenerationProfileModel.example_resumes)
            )
            
            result = await self.db.execute(query)
            profile_model = result.scalar_one_or_none()
            
            if profile_model:
                return self._model_to_entity(profile_model)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user generation profile {profile_id}: {e}")
            raise DatabaseException(f"Failed to get profile: {str(e)}")

    async def update(self, profile: UserGenerationProfile) -> UserGenerationProfile:
        """
        Update user generation profile.
        
        Args:
            profile: Updated profile entity
            
        Returns:
            Updated profile
            
        Raises:
            DatabaseException: Update failed
        """
        try:
            query = update(UserGenerationProfileModel).where(
                UserGenerationProfileModel.id == int(profile.id)
            ).values(
                writing_style_config_id=profile.writing_style_config_id,
                layout_config_id=profile.layout_config_id,
                is_active=profile.is_active,
                is_complete=profile.is_complete,
                setup_stage=profile.setup_stage,
                quality_targets=profile.quality_targets.dict() if profile.quality_targets else {},
                job_type_overrides=profile.job_type_overrides,
                generations_count=profile.generations_count,
                successful_generations=profile.successful_generations,
                user_satisfaction_scores=profile.user_satisfaction_scores,
                preference_learning_enabled=profile.preference_learning_enabled,
                auto_update_from_feedback=profile.auto_update_from_feedback,
                last_feedback_learning=profile.last_feedback_learning,
                preferred_templates=profile.preferred_templates,
                industry_focus=profile.industry_focus,
                updated_at=profile.updated_at,
                last_generation_at=profile.last_generation_at
            )
            
            await self.db.execute(query)
            await self.db.commit()
            
            # Fetch updated profile
            updated_profile = await self.get_by_id(int(profile.id))
            if not updated_profile:
                raise DatabaseException(f"Profile {profile.id} not found after update")
            return updated_profile
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user generation profile {profile.id}: {e}")
            raise DatabaseException(f"Failed to update profile: {str(e)}")

    async def deactivate_current_profile(self, user_id: int) -> bool:
        """
        Deactivate current active profile for user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if profile was deactivated
        """
        try:
            query = update(UserGenerationProfileModel).where(
                UserGenerationProfileModel.user_id == user_id,
                UserGenerationProfileModel.is_active == True
            ).values(
                is_active=False,
                updated_at=datetime.now()
            )
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to deactivate profile for user {user_id}: {e}")
            raise DatabaseException(f"Failed to deactivate profile: {str(e)}")

    async def list_by_user(self, user_id: int, include_inactive: bool = False) -> List[UserGenerationProfile]:
        """
        List all user generation profiles for a user.
        
        Args:
            user_id: User ID
            include_inactive: Whether to include inactive profiles
            
        Returns:
            List of user profiles
        """
        try:
            query = select(UserGenerationProfileModel).where(
                UserGenerationProfileModel.user_id == user_id
            ).options(
                selectinload(UserGenerationProfileModel.writing_style_config),
                selectinload(UserGenerationProfileModel.layout_config),
                selectinload(UserGenerationProfileModel.example_resumes)
            )
            
            if not include_inactive:
                query = query.where(UserGenerationProfileModel.is_active == True)
            
            query = query.order_by(UserGenerationProfileModel.last_updated.desc())
            
            result = await self.db.execute(query)
            profile_models = result.scalars().all()
            
            return [self._model_to_entity(model) for model in profile_models]
            
        except Exception as e:
            logger.error(f"Failed to list profiles for user {user_id}: {e}")
            raise DatabaseException(f"Failed to list profiles: {str(e)}")

    async def delete(self, profile_id: int) -> bool:
        """
        Delete user generation profile.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            True if profile was deleted
        """
        try:
            query = delete(UserGenerationProfileModel).where(
                UserGenerationProfileModel.id == profile_id
            )
            
            result = await self.db.execute(query)
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete profile {profile_id}: {e}")
            raise DatabaseException(f"Failed to delete profile: {str(e)}")

    def _model_to_entity(self, model: UserGenerationProfileModel) -> UserGenerationProfile:
        """
        Convert database model to entity.
        
        Args:
            model: Database model
            
        Returns:
            UserGenerationProfile entity
        """
        from app.domain.entities.preferences.user_generation_profile import QualityTargets
        
        # Convert quality targets from dict to object
        quality_targets = QualityTargets()
        if model.quality_targets:
            for key, value in model.quality_targets.items():
                if hasattr(quality_targets, key):
                    setattr(quality_targets, key, value)
        
        return UserGenerationProfile(
            id=str(model.id),
            user_id=model.user_id,
            writing_style_config_id=model.writing_style_config_id,
            layout_config_id=model.layout_config_id,
            is_active=model.is_active,
            is_complete=model.is_complete,
            setup_stage=model.setup_stage,
            quality_targets=quality_targets,
            job_type_overrides=model.job_type_overrides or {},
            generations_count=model.generations_count,
            successful_generations=model.successful_generations,
            user_satisfaction_scores=model.user_satisfaction_scores or [],
            preference_learning_enabled=model.preference_learning_enabled,
            auto_update_from_feedback=model.auto_update_from_feedback,
            last_feedback_learning=model.last_feedback_learning,
            preferred_templates=model.preferred_templates or ["modern"],
            industry_focus=model.industry_focus,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_generation_at=model.last_generation_at
        )