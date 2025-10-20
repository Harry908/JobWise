"""FastAPI dependency injection functions."""

from typing import Optional, AsyncGenerator
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.entities.user import User
from ..core.exceptions import AuthenticationException
from ..core.security import verify_token
from ..infrastructure.database.connection import get_database_session_dependency
from ..infrastructure.database.repositories import RepositoryFactory


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async for session in get_database_session_dependency():
        yield session


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Dependency to get current user ID from JWT token."""
    if not credentials:
        raise AuthenticationException("Authentication credentials not provided")

    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        return token_data.user_id

    except AuthenticationException:
        raise


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    """Dependency to get current user entity from JWT token."""
    try:
        # Get user repository
        repo_factory = RepositoryFactory(session)
        user_repo = repo_factory.create_user_repository()

        # Get user by ID
        user_model = await user_repo.get_by_id(user_id)
        if not user_model:
            raise AuthenticationException("User not found")

        if not user_model.is_active:
            raise AuthenticationException("User account is deactivated")

        # Convert UserModel to User entity
        from uuid import UUID
        user = User(
            id=UUID(user_model.id),
            email=user_model.email,
            hashed_password=user_model.password_hash,  # Map password_hash to hashed_password
            full_name=f"{user_model.first_name or ''} {user_model.last_name or ''}".strip(),  # Combine first/last name
            is_active=user_model.is_active,
            is_verified=user_model.is_verified,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login_at=user_model.last_active_at  # Map last_active_at to last_login_at
        )

        return user

    except Exception as e:
        raise AuthenticationException(f"Failed to get user: {str(e)}")