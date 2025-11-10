"""LLM service port interface (Context7 pattern)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LLMMessage:
    """LLM message structure."""
    
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM response structure."""
    
    content: str
    model: str
    tokens_used: int
    finish_reason: str


class ILLMService(ABC):
    """Port interface for LLM service (dependency inversion principle)."""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate completion from LLM.
        
        Args:
            messages: List of conversation messages
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0-1.0)
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            LLMServiceError: Base LLM error
            RateLimitError: Rate limit exceeded
            LLMTimeoutError: Request timeout
            LLMValidationError: Invalid parameters
        """
        pass
