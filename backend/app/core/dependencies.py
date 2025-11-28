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
from app.infrastructure.adapters.groq_llm_service import GroqLLMService


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
    Get LLM service instance using Groq with API key from environment.
    
    Returns:
        ILLMService: GroqLLMService with API key from settings
        
    Raises:
        ValueError: If no API key is configured
    """
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is required but not configured. "
            "Please set GROQ_API_KEY in your .env file to use the generation features."
        )
    
    try:
        # Use Groq service with API key from settings
        return GroqLLMService(api_key=settings.groq_api_key)
    except Exception as e:
        # Log error and re-raise with helpful message
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize Groq service: {e}")
        raise ValueError(f"Failed to initialize Groq LLM service: {e}. Please check your GROQ_API_KEY.")


# ==================== V3 API Service Dependencies ====================

async def get_writing_style_service(
    db: AsyncSession = Depends(get_db_session)
) -> "WritingStyleService":
    """Get writing style service instance with database session."""
    from app.application.services.writing_style_service import WritingStyleService
    return WritingStyleService(db)


async def get_profile_enhancement_service(
    db: AsyncSession = Depends(get_db_session)
) -> "ProfileEnhancementService":
    """Get profile enhancement service instance."""
    from app.application.services.profile_enhancement_service import ProfileEnhancementService
    return ProfileEnhancementService(db)


async def get_content_ranking_service(
    db: AsyncSession = Depends(get_db_session)
) -> "ContentRankingService":
    """Get content ranking service instance."""
    from app.application.services.content_ranking_service import ContentRankingService
    return ContentRankingService(db)


async def get_document_generation_service(
    db: AsyncSession = Depends(get_db_session)
) -> "DocumentGenerationService":
    """Get document generation service instance."""
    from app.application.services.document_generation_service import DocumentGenerationService
    return DocumentGenerationService(db)