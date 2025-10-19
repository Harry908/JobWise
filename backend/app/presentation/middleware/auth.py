"""Authentication middleware for JWT token validation."""

from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.exceptions import AuthenticationException
from ...core.security import verify_token, get_user_id_from_token
from ...infrastructure.database.connection import get_database_session_dependency
from ...infrastructure.database.repositories import RepositoryFactory


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Dependency to get current user ID from JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify token
        token_data = verify_token(credentials.credentials)

        # Return user ID
        return token_data.user_id

    except AuthenticationException as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Optional dependency to get current user ID (doesn't fail if no token)."""
    if not credentials:
        return None

    try:
        # Verify token
        token_data = verify_token(credentials.credentials)
        return token_data.user_id

    except AuthenticationException:
        return None


async def get_current_user_repository(
    session: AsyncSession = Depends(get_database_session_dependency)
) -> RepositoryFactory:
    """Dependency to get user repository for authenticated user."""
    # Create repository factory
    repo_factory = RepositoryFactory(session)

    # Get current user ID from token
    user_id = await get_current_user_id()

    # Verify user exists and is active
    user_repo = repo_factory.create_user_repository()
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is deactivated")

    return repo_factory


async def require_verified_user(
    session: AsyncSession = Depends(get_database_session_dependency)
) -> str:
    """Dependency that requires user to be verified."""
    # Get current user ID
    user_id = await get_current_user_id()

    # Check user verification status
    user_repo = RepositoryFactory(session).create_user_repository()
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Account verification required"
        )

    return user_id


# Admin role check (for future use)
async def require_admin_user(
    user_id: str = Depends(get_current_user_id)
) -> str:
    """Dependency that requires admin privileges."""
    # For now, this is a placeholder
    # In the future, this would check user roles/permissions
    return user_id


# Utility functions for manual token validation
def validate_token_manual(token: str) -> Optional[str]:
    """Manually validate JWT token and return user ID."""
    try:
        token_data = verify_token(token)
        return token_data.user_id
    except AuthenticationException:
        return None


def get_token_from_header(authorization_header: str) -> Optional[str]:
    """Extract token from Authorization header."""
    if not authorization_header:
        return None

    try:
        scheme, token = authorization_header.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None