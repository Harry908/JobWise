"""User repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.database.models import UserModel


class UserRepository:
    """Repository for user data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        # Update user with database ID
        user.id = model.id
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def update(self, user: User) -> User:
        """Update an existing user."""
        query = select(UserModel).where(UserModel.id == user.id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            raise ValueError(f"User with id {user.id} not found")

        # Update model fields
        setattr(model, 'password_hash', user.password_hash)
        setattr(model, 'full_name', user.full_name)
        setattr(model, 'is_active', user.is_active)
        setattr(model, 'is_verified', user.is_verified)
        setattr(model, 'updated_at', user.updated_at)

        await self.session.commit()
        await self.session.refresh(model)

        return user