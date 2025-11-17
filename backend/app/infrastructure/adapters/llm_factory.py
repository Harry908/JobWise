"""
LLM Factory for dependency injection (V3.0).

Provides centralized LLM service creation with FastAPI dependency injection.
"""

import logging
from typing import Optional, AsyncGenerator, Any
from functools import lru_cache

from app.domain.ports.llm_service import ILLMService
from app.infrastructure.adapters.groq_adapter_v3 import GroqAdapterV3
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM service instances.
    
    Supports dependency injection and service swapping.
    """
    
    @staticmethod
    def create_groq_adapter(
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3
    ) -> ILLMService:
        """
        Create Groq LLM adapter instance.
        
        Args:
            api_key: Groq API key (defaults to environment variable)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            ILLMService implementation
        """
        return GroqAdapterV3(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )


@lru_cache()
def get_llm_service() -> ILLMService:
    """
    FastAPI dependency for LLM service injection.
    
    Usage in endpoint:
        @app.post("/endpoint")
        async def endpoint(llm: ILLMService = Depends(get_llm_service)):
            ...
    
    Returns:
        ILLMService instance (cached singleton)
    """
    settings = get_settings()
    logger.info("Creating LLM service: GroqAdapterV3")
    
    return LLMFactory.create_groq_adapter(
        api_key=settings.groq_api_key,
        timeout=settings.groq_timeout,
        max_retries=settings.groq_max_retries
    )


async def get_llm_service_async() -> AsyncGenerator[ILLMService, Any]:
    """
    Async dependency for LLM service with cleanup.
    
    Usage in endpoint:
        @app.post("/endpoint")
        async def endpoint(llm: ILLMService = Depends(get_llm_service_async)):
            ...
    
    Yields:
        ILLMService instance with automatic cleanup
    """
    llm = get_llm_service()
    try:
        yield llm
    finally:
        # Cleanup if adapter supports it
        if hasattr(llm, 'close'):
            await getattr(llm, 'close')()  # type: ignore
