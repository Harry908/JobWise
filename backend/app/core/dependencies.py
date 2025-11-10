"""Dependency injection functions for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.auth_service import AuthService
from app.application.services.job_service import JobService
from app.core.security import get_user_id_from_token
from app.core.config import get_settings
from app.infrastructure.database.connection import get_db_session
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.domain.ports.llm_service import ILLMService
from app.infrastructure.adapters.mock_llm_adapter import MockLLMAdapter
# from app.infrastructure.adapters.groq_llm_adapter import GroqLLMAdapter


settings = get_settings()


# Security scheme
security = HTTPBearer()


async def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Get user repository instance."""
    return UserRepository(db)


async def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(user_repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """Get current authenticated user ID from JWT token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        user_id = get_user_id_from_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_job_repository(db: AsyncSession = Depends(get_db_session)) -> JobRepository:
    """Get job repository instance."""
    return JobRepository(db)


async def get_job_service(
    job_repo: JobRepository = Depends(get_job_repository)
) -> JobService:
    """Get job service instance."""
    return JobService(job_repo)


def get_llm_service() -> ILLMService:
    """
    Get LLM service instance (Context7 dependency injection pattern).
    
    Returns:
        ILLMService: Mock adapter for development, Groq adapter for production
    """
    # Use mock adapter for development (no API key needed)
    # Uncomment to use Groq in production:
    # if settings.groq_api_key:
    #     return GroqLLMAdapter()
    return MockLLMAdapter()