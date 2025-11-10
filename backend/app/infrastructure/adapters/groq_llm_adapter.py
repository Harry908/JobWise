"""Groq LLM adapter implementation (Context7 AsyncGroq pattern)."""

import logging
from typing import List, Optional

from groq import AsyncGroq
from groq import (
    RateLimitError as GroqRateLimitError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError
)

from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse
from app.core.exceptions import (
    LLMServiceError,
    RateLimitError,
    LLMTimeoutError,
    LLMValidationError
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqLLMAdapter(ILLMService):
    """Groq LLM adapter using AsyncGroq client (Context7 async pattern)."""
    
    def __init__(self, api_key: Optional[str] = None, timeout: Optional[int] = None):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key (defaults to settings.groq_api_key)
            timeout: Request timeout in seconds (defaults to settings.groq_timeout)
        """
        self.api_key = api_key or settings.groq_api_key
        self.timeout = timeout or settings.groq_timeout
        
        if not self.api_key:
            raise LLMValidationError("GROQ_API_KEY not configured")
        
        self.client = AsyncGroq(
            api_key=self.api_key,
            timeout=self.timeout
        )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate completion using Groq API (Context7 error handling pattern).
        
        Args:
            messages: List of conversation messages
            model: Model identifier (e.g., "llama-3.1-8b-instant")
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0-1.0)
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            RateLimitError: Rate limit exceeded
            LLMTimeoutError: Request timeout
            LLMValidationError: Invalid parameters
            LLMServiceError: Other service errors
        """
        try:
            # Convert domain messages to Groq format
            groq_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Call Groq API (async pattern from Context7)
            completion = await self.client.chat.completions.create(
                model=model,
                messages=groq_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract response
            choice = completion.choices[0]
            content = choice.message.content
            
            logger.info(
                f"LLM generation successful: model={model}, "
                f"tokens={completion.usage.total_tokens}"
            )
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=completion.usage.total_tokens,
                finish_reason=choice.finish_reason
            )
            
        except GroqRateLimitError as e:
            logger.warning(f"Groq rate limit exceeded: {e}")
            raise RateLimitError(f"Groq rate limit exceeded: {str(e)}")
        
        except APITimeoutError as e:
            logger.error(f"Groq timeout: {e}")
            raise LLMTimeoutError(f"Groq request timeout: {str(e)}")
        
        except BadRequestError as e:
            logger.error(f"Invalid Groq request: {e}")
            raise LLMValidationError(f"Invalid parameters: {str(e)}")
        
        except APIConnectionError as e:
            logger.error(f"Groq connection failed: {e}")
            raise LLMServiceError(f"Connection failed: {str(e)}")
        
        except Exception as e:
            logger.exception("Unexpected Groq error")
            raise LLMServiceError(f"Unexpected error: {str(e)}")
