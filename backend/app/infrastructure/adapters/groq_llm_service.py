"""Groq LLM Service implementing the domain port interface."""

import asyncio
import logging
import os
import time
import json
from typing import List, Optional, Dict, Any, cast
from groq import Groq

from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse
from app.core.exceptions import LLMServiceError, LLMTimeoutError, LLMValidationError, RateLimitError

logger = logging.getLogger(__name__)


class GroqLLMService(ILLMService):
    """Groq LLM service implementing the domain port interface."""
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq LLM service.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY environment variable)
            default_model: Default model to use
        """
        # Load from environment if not provided
        # Try multiple sources: parameter > environment variable > settings
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        
        # If still no key, try loading from settings (in case dotenv wasn't loaded)
        if not self.api_key:
            try:
                from app.core.config import get_settings
                settings = get_settings()
                self.api_key = settings.groq_api_key
            except Exception as e:
                logger.warning(f"Could not load settings: {e}")
        
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        logger.debug(f"Initializing Groq service with API key: {self.api_key[:10]}...")
        
        self.default_model = default_model
        
        # Initialize Groq client with minimal configuration
        try:
            # Initialize with just the API key - no other parameters
            self.client = Groq(api_key=self.api_key)
            logger.debug("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Groq client initialization failed: {e}")
            raise ValueError(f"Failed to initialize Groq client: {e}. Please check your API key.")
        
        # Rate limiting
        self.requests_per_minute = 30  # Groq free tier limit
        self.request_times: List[float] = []
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0
        
        logger.info(f"GroqLLMService initialized with default model: {self.default_model}")

    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate completion from LLM using the domain interface.
        
        Args:
            messages: List of conversation messages
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0-1.0)
            
        Returns:
            LLMResponse with generated content
        """
        try:
            # Validate parameters
            if not messages:
                raise LLMValidationError("Messages cannot be empty")
            
            if not 0.0 <= temperature <= 1.0:
                raise LLMValidationError("Temperature must be between 0.0 and 1.0")
            
            if max_tokens is not None and max_tokens <= 0:
                raise LLMValidationError("max_tokens must be positive")
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Convert domain messages to Groq format
            groq_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Use provided model or default
            model_to_use = model or self.default_model
            
            # Make the synchronous request in thread pool for async compatibility
            def make_request():
                try:
                    return self.client.chat.completions.create(
                        model=model_to_use,
                        messages=cast(Any, groq_messages),  # Type cast for API compatibility
                        temperature=temperature,
                        max_tokens=max_tokens or 2048,
                        top_p=1,
                        stream=False
                    )
                except Exception as e:
                    # Convert Groq exceptions to our domain exceptions
                    if "rate_limit" in str(e).lower():
                        raise RateLimitError(f"Groq rate limit exceeded: {str(e)}")
                    elif "timeout" in str(e).lower():
                        raise LLMTimeoutError(f"Groq request timeout: {str(e)}")
                    else:
                        raise LLMServiceError(f"Groq API error: {str(e)}")
            
            # Run in thread pool with retries
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Making Groq request (attempt {attempt + 1}/{self.max_retries})")
                    
                    # Run synchronous request in thread pool 
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, make_request)
                    
                    # Track request for rate limiting
                    self.request_times.append(time.time())
                    
                    # Extract response data
                    content = response.choices[0].message.content or ""
                    finish_reason = response.choices[0].finish_reason or "stop"
                    tokens_used = response.usage.total_tokens if response.usage and response.usage.total_tokens else 0
                    
                    logger.debug(f"Groq request successful: {tokens_used} tokens used")
                    
                    return LLMResponse(
                        content=content,
                        model=model_to_use,
                        tokens_used=tokens_used,
                        finish_reason=finish_reason
                    )
                    
                except (RateLimitError, LLMTimeoutError, LLMServiceError) as e:
                    # These are our domain exceptions, check if we should retry
                    if attempt == self.max_retries - 1:
                        # Last attempt, re-raise
                        raise
                    
                    # Wait before retry with exponential backoff
                    wait_time = self.base_delay * (2 ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    # Unexpected error
                    if attempt == self.max_retries - 1:
                        raise LLMServiceError(f"Unexpected Groq API error: {str(e)}")
                    
                    # Wait before retry
                    wait_time = self.base_delay * (2 ** attempt)
                    logger.warning(f"Unexpected error (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
            
        except (LLMServiceError, RateLimitError, LLMTimeoutError, LLMValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap any other errors
            raise LLMServiceError(f"Unexpected error in Groq LLM service: {str(e)}")
        
        # This should never be reached due to exception handling above
        raise LLMServiceError("Unexpected end of function")

    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()
        
        # Clean old requests (older than 60 seconds)
        self.request_times = [
            req_time for req_time in self.request_times 
            if current_time - req_time < 60
        ]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.requests_per_minute:
            oldest_request = min(self.request_times)
            sleep_time = 60 - (current_time - oldest_request)
            
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                raise RateLimitError(f"Rate limit exceeded. Try again in {sleep_time:.1f} seconds.")

    # Additional convenience methods for specific use cases
    async def generate_structured(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        temperature: float = 0.3,
        max_tokens: int = 2048,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured response using JSON mode.
        
        Args:
            prompt: Input prompt
            response_format: Expected JSON structure
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            model: Model to use (optional)
            
        Returns:
            Parsed JSON response
        """
        try:
            # Enhance prompt with JSON instructions
            json_prompt = f"""
{prompt}

IMPORTANT: Respond with valid JSON matching this exact structure:
{json.dumps(response_format, indent=2)}

Ensure your response is valid JSON and follows the schema exactly.
"""
            
            messages = [LLMMessage(role="user", content=json_prompt)]
            
            response = await self.generate(
                messages=messages,
                model=model or self.default_model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Parse JSON response
            try:
                parsed_response = json.loads(response.content)
                logger.debug("Successfully parsed structured response")
                return parsed_response
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                # Try to extract JSON from the response
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:-3].strip()
                elif content.startswith("```"):
                    content = content[3:-3].strip()
                
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    raise LLMValidationError(f"LLM did not return valid JSON: {response.content[:200]}")
                    
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise

    async def generate_resume_content(
        self,
        user_data: Dict[str, Any],
        job_analysis: Dict[str, Any],
        content_type: str = "resume"
    ) -> str:
        """
        Generate resume content using optimized prompts.
        
        Args:
            user_data: User profile data
            job_analysis: Job analysis results
            content_type: Type of content to generate
            
        Returns:
            Generated resume content as text
        """
        try:
            resume_prompt = f"""
You are a professional resume writer creating a tailored {content_type} for this candidate.

CANDIDATE PROFILE:
{json.dumps(user_data, indent=2)}

JOB ANALYSIS:
{json.dumps(job_analysis, indent=2)}

INSTRUCTIONS:
1. Create a professional {content_type} that highlights the candidate's most relevant experience
2. Emphasize skills and experience that match the job requirements
3. Use action verbs and quantify achievements where possible
4. Ensure ATS-friendly formatting
5. Keep language professional and engaging
6. Only use information provided in the candidate profile - do not fabricate anything

Generate a complete {content_type} in plain text format with clear sections.
"""
            
            messages = [LLMMessage(role="user", content=resume_prompt)]
            
            response = await self.generate(
                messages=messages,
                model="llama-3.3-70b-versatile",  # Use best model for content generation
                max_tokens=3000,
                temperature=0.4  # Balanced creativity and consistency
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Resume content generation failed: {e}")
            raise