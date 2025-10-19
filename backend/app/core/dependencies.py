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
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        if not user.is_active:
            raise AuthenticationException("User account is deactivated")

        return user

    except Exception as e:
        raise AuthenticationException(f"Failed to get user: {str(e)}")