"""Universal LLM service port - abstract interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMRequest:
    """Request model for LLM operations."""
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None


@dataclass
class LLMResponse:
    """Response model for LLM operations."""
    content: str
    tokens_used: int
    model: str
    finish_reason: str


class LLMServicePort(ABC):
    """Abstract interface for LLM services."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using LLM."""
        pass

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the LLM service is healthy."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass