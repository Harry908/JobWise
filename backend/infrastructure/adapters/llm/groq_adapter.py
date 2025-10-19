"""
Groq LLM Adapter Implementation

This adapter integrates Groq's ultra-fast inference API with our universal LLM service port.
Groq specializes in high-speed inference using their custom LPU (Language Processing Unit) hardware.

Key Features:
- Ultra-fast inference (500+ tokens/sec)
- Cost-effective pricing
- OpenAI-compatible API
- Multiple model support (Llama, Mixtral, Gemma)
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import groq
from groq import Groq

from ...domain.ports.llm_service_port import LLMServicePort
from ...domain.value_objects.llm_request import LLMRequest
from ...domain.value_objects.llm_response import LLMResponse
from ...domain.value_objects.token_usage import TokenUsage
from ...domain.value_objects.model_capabilities import ModelCapabilities
from ...domain.value_objects.rate_limit_info import RateLimitInfo
from ...domain.value_objects.cost_estimate import CostEstimate
from ...core.exceptions import LLMProviderException, RateLimitException
from ...core.logging import get_logger

logger = get_logger(__name__)


class GroqAdapter(LLMServicePort):
    """
    Groq LLM adapter for ultra-fast inference.
    
    Groq's LPU (Language Processing Unit) architecture enables:
    - 10-20x faster inference than traditional GPU-based systems
    - Lower latency for real-time applications
    - Cost-effective pricing with predictable costs
    """
    
    # Groq model configurations
    GROQ_MODELS = {
        "llama3-70b-8192": {
            "max_tokens": 8192,
            "context_window": 8192,
            "speed": 300,  # tokens/sec
            "cost_per_1k_input": 0.00059,
            "cost_per_1k_output": 0.00079,
        },
        "llama3-8b-8192": {
            "max_tokens": 8192,
            "context_window": 8192,
            "speed": 500,  # tokens/sec
            "cost_per_1k_input": 0.00005,
            "cost_per_1k_output": 0.00008,
        },
        "mixtral-8x7b-32768": {
            "max_tokens": 32768,
            "context_window": 32768,
            "speed": 400,  # tokens/sec
            "cost_per_1k_input": 0.00024,
            "cost_per_1k_output": 0.00024,
        },
        "gemma-7b-it": {
            "max_tokens": 8192,
            "context_window": 8192,
            "speed": 350,  # tokens/sec
            "cost_per_1k_input": 0.00007,
            "cost_per_1k_output": 0.00007,
        },
        "llama3-3-70b-versatile": {
            "max_tokens": 131072,
            "context_window": 131072,
            "speed": 280,  # tokens/sec
            "cost_per_1k_input": 0.00059,
            "cost_per_1k_output": 0.00079,
        }
    }
    
    def __init__(
        self,
        api_key: str,
        default_model: str = "llama3-70b-8192",
        max_retries: int = 3,
        timeout: float = 60.0,
        speed_priority: bool = True,
        **kwargs
    ):
        """
        Initialize Groq adapter.
        
        Args:
            api_key: Groq API key
            default_model: Default model to use
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
            speed_priority: Whether to prioritize speed over other factors
        """
        self.client = Groq(api_key=api_key)
        self.default_model = default_model
        self.max_retries = max_retries
        self.timeout = timeout
        self.speed_priority = speed_priority
        
        # Rate limiting tracking
        self._request_times: List[datetime] = []
        self._rate_limit_per_minute = 30  # Free tier limit
        
        logger.info(f"Groq adapter initialized with model: {default_model}")
    
    async def generate_completion(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using Groq's ultra-fast inference.
        
        Args:
            request: LLM request with prompt and parameters
            
        Returns:
            LLM response with generated content and metadata
        """
        start_time = datetime.now()
        
        try:
            # Check rate limits
            await self._check_rate_limits()
            
            # Prepare Groq request
            groq_request = self._map_to_groq_format(request)
            
            # Make request with retries
            groq_response = await self._make_request_with_retries(groq_request)
            
            # Parse response
            response = self._parse_groq_response(groq_response, start_time)
            
            logger.info(
                f"Groq completion generated in {response.latency_ms}ms "
                f"with {response.tokens_used.total_tokens} tokens"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Groq completion failed: {e}")
            raise LLMProviderException(f"Groq request failed: {str(e)}") from e
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Groq uses similar tokenization to OpenAI for most models.
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        return max(1, len(text) // 4)
    
    def get_model_capabilities(self) -> ModelCapabilities:
        """Get capabilities of the current model."""
        model_config = self.GROQ_MODELS.get(self.default_model, {})
        
        return ModelCapabilities(
            model_name=self.default_model,
            provider="groq",
            max_tokens=model_config.get("max_tokens", 8192),
            context_window=model_config.get("context_window", 8192),
            supports_streaming=True,
            supports_function_calling=False,  # Not yet supported by Groq
            supports_vision=False,
            max_requests_per_minute=self._rate_limit_per_minute,
            average_latency_ms=50,  # Ultra-fast inference
            tokens_per_second=model_config.get("speed", 300),
        )
    
    def get_rate_limits(self) -> RateLimitInfo:
        """Get current rate limit information."""
        recent_requests = [
            t for t in self._request_times 
            if (datetime.now() - t).total_seconds() < 60
        ]
        
        return RateLimitInfo(
            requests_per_minute=len(recent_requests),
            max_requests_per_minute=self._rate_limit_per_minute,
            reset_time=datetime.now(),
            remaining_requests=max(0, self._rate_limit_per_minute - len(recent_requests))
        )
    
    def calculate_cost(self, request: LLMRequest) -> CostEstimate:
        """Calculate estimated cost for the request."""
        model_config = self.GROQ_MODELS.get(request.model or self.default_model, {})
        
        input_tokens = len(request.prompt) // 4  # Rough estimation
        max_output_tokens = request.max_tokens or 1000
        
        input_cost = input_tokens * model_config.get("cost_per_1k_input", 0.0005) / 1000
        max_output_cost = max_output_tokens * model_config.get("cost_per_1k_output", 0.0008) / 1000
        
        return CostEstimate(
            estimated_cost=input_cost + max_output_cost,
            input_cost=input_cost,
            output_cost=max_output_cost,
            currency="USD",
            provider="groq"
        )
    
    def validate_response(self, response: LLMResponse) -> bool:
        """Validate response quality and completeness."""
        return (
            response.content is not None and
            len(response.content.strip()) > 0 and
            response.tokens_used.total_tokens > 0 and
            response.finish_reason in ["stop", "length"]
        )
    
    def _map_to_groq_format(self, request: LLMRequest) -> Dict[str, Any]:
        """Map universal LLM request to Groq API format."""
        messages = []
        
        # Add system message if provided
        if request.system_message:
            messages.append({
                "role": "system",
                "content": request.system_message
            })
        
        # Add user prompt
        messages.append({
            "role": "user", 
            "content": request.prompt
        })
        
        groq_request = {
            "model": request.model or self.default_model,
            "messages": messages,
            "max_tokens": min(request.max_tokens or 4000, 4000),
            "temperature": request.temperature or 0.7,
            "top_p": getattr(request, 'top_p', 1.0),
            "stream": False,  # Non-streaming for now
        }
        
        # Add stop sequences if provided
        if hasattr(request, 'stop') and request.stop:
            groq_request["stop"] = request.stop
        
        return groq_request
    
    async def _make_request_with_retries(self, groq_request: Dict[str, Any]) -> Any:
        """Make request to Groq API with exponential backoff retries."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Track request time for rate limiting
                self._request_times.append(datetime.now())
                
                # Make synchronous call (Groq SDK doesn't have async support yet)
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(**groq_request)
                )
                
                return response
                
            except groq.RateLimitError as e:
                logger.warning(f"Groq rate limit hit on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise RateLimitException(f"Groq rate limit exceeded: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                last_exception = e
                
            except groq.APIError as e:
                logger.error(f"Groq API error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise LLMProviderException(f"Groq API error: {str(e)}")
                await asyncio.sleep(1)
                last_exception = e
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                last_exception = e
                if attempt == self.max_retries - 1:
                    break
                await asyncio.sleep(1)
        
        raise LLMProviderException(f"Groq request failed after {self.max_retries} attempts: {str(last_exception)}")
    
    def _parse_groq_response(self, groq_response: Any, start_time: datetime) -> LLMResponse:
        """Parse Groq API response to universal format."""
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        choice = groq_response.choices[0]
        usage = groq_response.usage
        
        # Calculate cost
        model_config = self.GROQ_MODELS.get(groq_response.model, {})
        input_cost = usage.prompt_tokens * model_config.get("cost_per_1k_input", 0.0005) / 1000
        output_cost = usage.completion_tokens * model_config.get("cost_per_1k_output", 0.0008) / 1000
        total_cost = input_cost + output_cost
        
        return LLMResponse(
            content=choice.message.content,
            tokens_used=TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens
            ),
            model_used=groq_response.model,
            finish_reason=choice.finish_reason,
            cost=total_cost,
            latency_ms=latency_ms,
            metadata={
                "provider": "groq",
                "system_fingerprint": getattr(groq_response, "system_fingerprint", None),
                "created": groq_response.created,
                "speed_tokens_per_sec": usage.completion_tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
                "lpu_processing": True,  # Indicates LPU hardware was used
            }
        )
    
    async def _check_rate_limits(self) -> None:
        """Check and enforce rate limits."""
        now = datetime.now()
        
        # Clean up old request times (older than 1 minute)
        self._request_times = [
            t for t in self._request_times 
            if (now - t).total_seconds() < 60
        ]
        
        # Check if we're at the rate limit
        if len(self._request_times) >= self._rate_limit_per_minute:
            oldest_request = min(self._request_times)
            wait_time = 60 - (now - oldest_request).total_seconds()
            
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.2f}s")
                raise RateLimitException(
                    f"Groq rate limit exceeded. Wait {wait_time:.2f} seconds."
                )
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the Groq provider."""
        return {
            "provider": "groq",
            "description": "Ultra-fast LLM inference using custom LPU hardware",
            "supported_models": list(self.GROQ_MODELS.keys()),
            "key_features": [
                "Ultra-fast inference (500+ tokens/sec)",
                "Custom LPU hardware acceleration", 
                "Cost-effective pricing",
                "Low latency for real-time applications",
                "OpenAI-compatible API"
            ],
            "best_use_cases": [
                "Real-time chatbots",
                "Interactive AI applications",
                "High-throughput text generation",
                "Cost-sensitive applications",
                "Speed-critical workflows"
            ],
            "current_model": self.default_model,
            "speed_priority": self.speed_priority,
        }