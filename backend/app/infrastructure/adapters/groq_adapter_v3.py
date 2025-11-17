"""
V3.0 Groq LLM Adapter using httpx.AsyncClient with retry logic.

Implements ILLMService interface per 05-LLM-ADAPTER.md design.
Uses httpx AsyncClient patterns from context7 documentation.
"""

import asyncio
import json
import logging
import os
from typing import List, Optional, Dict, Any
import httpx
from datetime import datetime

from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse
from app.core.exceptions import (
    LLMServiceError,
    LLMTimeoutError,
    LLMValidationError,
    RateLimitError
)

logger = logging.getLogger(__name__)


class GroqAdapterV3(ILLMService):
    """
    V3.0 Groq adapter using httpx.AsyncClient with retry logic.
    
    Implements exponential backoff, timeout configuration, and connection pooling
    per context7 best practices from /encode/httpx documentation.
    """
    
    # Groq API constants
    API_BASE_URL = "https://api.groq.com/openai/v1"
    CHAT_COMPLETIONS_ENDPOINT = "/chat/completions"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Groq adapter with httpx AsyncClient.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            retry_delay: Base delay for exponential backoff (seconds)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key required. Set GROQ_API_KEY environment variable.")
        
        # Timeout configuration per context7 httpx patterns
        self.timeout = httpx.Timeout(
            connect=10.0,  # Connection timeout
            read=timeout,  # Read timeout
            write=10.0,    # Write timeout
            pool=5.0       # Pool timeout
        )
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Create transport with retry (context7 HTTPTransport pattern)
        # Note: httpx.HTTPTransport(retries=N) handles connection-level retries
        transport = httpx.AsyncHTTPTransport(retries=1)
        
        # Create AsyncClient with configuration
        self.client = httpx.AsyncClient(
            base_url=self.API_BASE_URL,
            timeout=self.timeout,
            transport=transport,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info("GroqAdapterV3 initialized with httpx.AsyncClient")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate completion from Groq API with retry logic.
        
        Implements exponential backoff per context7 best practices.
        
        Args:
            messages: List of conversation messages
            model: Groq model identifier (e.g., "llama-3.3-70b-versatile")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            LLMResponse with generated content
            
        Raises:
            LLMValidationError: Invalid parameters
            RateLimitError: Rate limit exceeded
            LLMTimeoutError: Request timeout
            LLMServiceError: Other errors
        """
        # Validate parameters
        if not messages:
            raise LLMValidationError("Messages list cannot be empty")
        
        if not 0.0 <= temperature <= 2.0:
            raise LLMValidationError("Temperature must be between 0.0 and 2.0")
        
        if max_tokens is not None and max_tokens <= 0:
            raise LLMValidationError("max_tokens must be positive")
        
        # Build request payload
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        # Retry loop with exponential backoff
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Groq request attempt {attempt + 1}/{self.max_retries}")
                
                # Make API request
                response = await self.client.post(
                    self.CHAT_COMPLETIONS_ENDPOINT,
                    json=payload
                )
                
                # Handle HTTP errors
                if response.status_code == 429:
                    raise RateLimitError("Groq rate limit exceeded")
                elif response.status_code == 408:
                    raise LLMTimeoutError("Groq request timeout")
                elif response.status_code >= 400:
                    error_detail = response.text[:200]
                    raise LLMServiceError(f"Groq API error {response.status_code}: {error_detail}")
                
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                
                if "choices" not in data or not data["choices"]:
                    raise LLMServiceError("No choices in Groq response")
                
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content", "")
                
                if not content:
                    raise LLMServiceError("Empty content in Groq response")
                
                # Extract metadata
                usage = data.get("usage", {})
                tokens_used = usage.get("total_tokens", 0)
                finish_reason = choice.get("finish_reason", "unknown")
                
                logger.info(f"Groq request successful: model={model}, tokens={tokens_used}")
                
                return LLMResponse(
                    content=content,
                    model=model,
                    tokens_used=tokens_used,
                    finish_reason=finish_reason
                )
            
            except httpx.TimeoutException as e:
                last_exception = LLMTimeoutError(f"Request timeout: {str(e)}")
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
            
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    last_exception = RateLimitError("Rate limit exceeded")
                    logger.warning(f"Rate limit on attempt {attempt + 1}")
                else:
                    last_exception = LLMServiceError(f"HTTP error {e.response.status_code}: {str(e)}")
                    logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
            
            except (RateLimitError, LLMTimeoutError, LLMServiceError) as e:
                last_exception = e
                logger.warning(f"LLM error on attempt {attempt + 1}: {e}")
            
            except Exception as e:
                last_exception = LLMServiceError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
        
        # All retries failed
        logger.error(f"All {self.max_retries} attempts failed")
        raise last_exception or LLMServiceError("All retry attempts failed")
    
    async def generate_json(
        self,
        messages: List[LLMMessage],
        model: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            messages: List of conversation messages
            model: Groq model identifier
            response_schema: Expected JSON schema
            temperature: Sampling temperature (low for consistency)
            
        Returns:
            Parsed JSON object
            
        Raises:
            LLMServiceError: Generation or parsing failed
        """
        # Add JSON schema instruction to last user message
        schema_instruction = f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(response_schema, indent=2)}"
        
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[-1].role == "user":
            enhanced_messages[-1] = LLMMessage(
                role="user",
                content=enhanced_messages[-1].content + schema_instruction
            )
        
        # Generate response
        response = await self.generate(
            messages=enhanced_messages,
            model=model,
            temperature=temperature,
            max_tokens=2048
        )
        
        # Parse JSON from response
        try:
            json_text = self._extract_json_from_text(response.content)
            parsed = json.loads(json_text)
            
            if not isinstance(parsed, dict):
                raise LLMServiceError("Response is not a JSON object")
            
            return parsed
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Raw response: {response.content[:500]}")
            raise LLMServiceError(f"Invalid JSON response: {str(e)}")
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Extract JSON object from LLM response text.
        
        Handles common patterns like ```json blocks.
        """
        text = text.strip()
        
        # Remove markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        
        # Find JSON object boundaries
        start_idx = text.find("{")
        if start_idx == -1:
            return text
        
        brace_count = 0
        for i in range(start_idx, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[start_idx:i + 1]
        
        return text[start_idx:]
    
    async def close(self):
        """Close the httpx AsyncClient connection pool."""
        await self.client.aclose()
        logger.info("GroqAdapterV3 client closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
