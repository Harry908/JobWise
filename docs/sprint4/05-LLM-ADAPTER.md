# LLM Adapter - JobWise AI Generation System v3.0

**Version**: 3.0  
**Last Updated**: November 16, 2025  
**Status**: 🎯 **Ready for Implementation**

---

## LLM Adapter Overview

The LLM Adapter pattern enables swappable LLM providers without code changes to business logic. This design allows:
- **Provider flexibility** - Switch between Groq, OpenAI, Claude, local models
- **Unified interface** - All services use same `ILLMService` interface
- **Configuration-driven** - Select provider via environment variables
- **Retry logic** - Automatic retry with exponential backoff
- **Error handling** - Standardized error responses across providers
- **Cost tracking** - Token usage monitoring for budget control

---

## Architecture

### Port and Adapter Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                     │
│  (ProfileEnhancementService, ContentRankingService, etc.)   │
└─────────────────────────┬───────────────────────────────────┘
                          │ depends on
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    ILLMService Interface                     │
│   + generate(prompt, system_msg, temp, tokens) -> Response  │
│   + generate_json(prompt, system_msg) -> dict               │
└─────────────────────────┬───────────────────────────────────┘
                          │ implemented by
              ┌───────────┴───────────┐
              ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │   GroqAdapter    │    │  OpenAIAdapter   │
    │  (llama-3.x)     │    │   (gpt-4, etc)   │
    └──────────────────┘    └──────────────────┘
              ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Groq REST API   │    │ OpenAI REST API  │
    └──────────────────┘    └──────────────────┘
```

---

## ILLMService Interface

### Interface Definition

```python
# backend/app/domain/ports/illm_service.py
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Standard LLM response"""
    text: str
    model: str
    tokens_used: int
    generation_time: float  # seconds
    finish_reason: str  # "stop", "length", "content_filter"
    
@dataclass
class LLMRequest:
    """Standard LLM request"""
    prompt: str
    system_message: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 2000
    model: Optional[str] = None  # Override default model
    response_format: Optional[dict] = None  # {"type": "json_object"} for JSON
    stop_sequences: Optional[list[str]] = None

class ILLMService(ABC):
    """Port interface for LLM services"""
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text completion"""
        pass
    
    @abstractmethod
    async def generate_json(self, request: LLMRequest) -> dict:
        """Generate JSON completion with automatic parsing"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name (groq, openai, anthropic, etc.)"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models"""
        pass
```

---

## Groq Adapter Implementation

### Adapter Class

```python
# backend/app/infrastructure/llm/groq_adapter.py
import httpx
import json
import time
from typing import Optional
from app.domain.ports.illm_service import ILLMService, LLMRequest, LLMResponse
from app.core.config import settings

class GroqAdapter(ILLMService):
    """Adapter for Groq LLM API"""
    
    AVAILABLE_MODELS = [
        "llama-3.1-8b-instant",      # Fast, 8B params, 840 TPS
        "llama-3.3-70b-versatile",   # High-quality, 70B params, 394 TPS
        "llama-3.1-70b-versatile",   # Alternative 70B
        "mixtral-8x7b-32768",        # Mixtral MoE
    ]
    
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text completion via Groq"""
        start_time = time.time()
        
        # Build API request
        api_request = {
            "model": request.model or self.DEFAULT_MODEL,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        # Add optional parameters
        if request.response_format:
            api_request["response_format"] = request.response_format
        if request.stop_sequences:
            api_request["stop"] = request.stop_sequences
        
        # Call API with retry
        response_data = await self._call_with_retry(api_request)
        
        # Extract response
        choice = response_data["choices"][0]
        usage = response_data["usage"]
        
        return LLMResponse(
            text=choice["message"]["content"],
            model=response_data["model"],
            tokens_used=usage["total_tokens"],
            generation_time=time.time() - start_time,
            finish_reason=choice["finish_reason"]
        )
    
    async def generate_json(self, request: LLMRequest) -> dict:
        """Generate JSON completion with automatic parsing"""
        # Force JSON response format
        request.response_format = {"type": "json_object"}
        
        # Generate
        response = await self.generate(request)
        
        # Parse JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}")
    
    def get_provider_name(self) -> str:
        return "groq"
    
    def get_available_models(self) -> list[str]:
        return self.AVAILABLE_MODELS
    
    def _build_messages(self, request: LLMRequest) -> list[dict]:
        """Build messages array for API"""
        messages = []
        
        if request.system_message:
            messages.append({
                "role": "system",
                "content": request.system_message
            })
        
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        return messages
    
    async def _call_with_retry(
        self,
        api_request: dict,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> dict:
        """Call API with exponential backoff retry"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json=api_request
                )
                
                # Check for errors
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit - retry with backoff
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code >= 500:
                    # Server error - retry
                    raise APIError(f"Server error: {response.status_code}")
                else:
                    # Client error - don't retry
                    error_data = response.json()
                    raise APIError(f"API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            
            except (RateLimitError, APIError, httpx.TimeoutException) as e:
                last_error = e
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    raise LLMServiceError(f"LLM API failed after {max_retries} attempts: {last_error}")
        
        raise LLMServiceError(f"Unexpected error: {last_error}")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

# Custom exceptions
class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    pass

class RateLimitError(LLMServiceError):
    """Rate limit exceeded"""
    pass

class APIError(LLMServiceError):
    """API error response"""
    pass
```

---

## OpenAI Adapter Implementation

### Adapter Class

```python
# backend/app/infrastructure/llm/openai_adapter.py
import httpx
import json
import time
from typing import Optional
from app.domain.ports.illm_service import ILLMService, LLMRequest, LLMResponse
from app.core.config import settings

class OpenAIAdapter(ILLMService):
    """Adapter for OpenAI API"""
    
    AVAILABLE_MODELS = [
        "gpt-4-turbo-preview",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    BASE_URL = "https://api.openai.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text completion via OpenAI"""
        start_time = time.time()
        
        # Build API request (similar to Groq)
        api_request = {
            "model": request.model or self.DEFAULT_MODEL,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        
        if request.response_format:
            api_request["response_format"] = request.response_format
        if request.stop_sequences:
            api_request["stop"] = request.stop_sequences
        
        # Call API with retry
        response_data = await self._call_with_retry(api_request)
        
        # Extract response
        choice = response_data["choices"][0]
        usage = response_data["usage"]
        
        return LLMResponse(
            text=choice["message"]["content"],
            model=response_data["model"],
            tokens_used=usage["total_tokens"],
            generation_time=time.time() - start_time,
            finish_reason=choice["finish_reason"]
        )
    
    async def generate_json(self, request: LLMRequest) -> dict:
        """Generate JSON completion"""
        request.response_format = {"type": "json_object"}
        response = await self.generate(request)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}")
    
    def get_provider_name(self) -> str:
        return "openai"
    
    def get_available_models(self) -> list[str]:
        return self.AVAILABLE_MODELS
    
    # _build_messages and _call_with_retry methods similar to GroqAdapter
    # ...
```

---

## Provider Factory

### Factory Pattern

```python
# backend/app/infrastructure/llm/llm_factory.py
from typing import Optional
from app.domain.ports.illm_service import ILLMService
from app.infrastructure.llm.groq_adapter import GroqAdapter
from app.infrastructure.llm.openai_adapter import OpenAIAdapter
from app.core.config import settings

class LLMFactory:
    """Factory for creating LLM service instances"""
    
    _adapters = {
        "groq": GroqAdapter,
        "openai": OpenAIAdapter,
        # Future: "anthropic": AnthropicAdapter,
        # Future: "local": LocalLLMAdapter,
    }
    
    @classmethod
    def create(cls, provider: Optional[str] = None) -> ILLMService:
        """
        Create LLM service instance.
        
        Args:
            provider: Provider name (groq, openai, etc.)
                     If None, uses settings.LLM_PROVIDER
        
        Returns:
            ILLMService instance
        
        Raises:
            ValueError: If provider not supported
        """
        provider_name = provider or settings.LLM_PROVIDER
        
        if provider_name not in cls._adapters:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Available: {available}"
            )
        
        adapter_class = cls._adapters[provider_name]
        return adapter_class()
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: type):
        """Register new adapter (for extensions)"""
        cls._adapters[name] = adapter_class
```

---

## Configuration

### Environment Variables

```bash
# .env
# LLM Provider Configuration
LLM_PROVIDER=groq  # groq | openai | anthropic | local

# Groq API
GROQ_API_KEY=gsk_your_groq_api_key_here

# OpenAI API (optional)
OPENAI_API_KEY=sk-your_openai_api_key_here

# Anthropic API (optional)
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# LLM Settings
LLM_DEFAULT_TEMPERATURE=0.3
LLM_DEFAULT_MAX_TOKENS=2000
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=60
```

### Settings Class

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM Configuration
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    LLM_DEFAULT_TEMPERATURE: float = 0.3
    LLM_DEFAULT_MAX_TOKENS: int = 2000
    LLM_MAX_RETRIES: int = 3
    LLM_TIMEOUT_SECONDS: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Dependency Injection

### FastAPI Dependencies

```python
# backend/app/presentation/api/dependencies.py
from fastapi import Depends
from app.domain.ports.illm_service import ILLMService
from app.infrastructure.llm.llm_factory import LLMFactory

async def get_llm_service() -> ILLMService:
    """Dependency injection for LLM service"""
    service = LLMFactory.create()
    try:
        yield service
    finally:
        # Cleanup if needed
        if hasattr(service, 'close'):
            await service.close()
```

### Service Layer Usage

```python
# backend/app/application/services/profile_enhancement_service.py
from app.domain.ports.illm_service import ILLMService, LLMRequest

class ProfileEnhancementService:
    def __init__(self, llm_service: ILLMService):
        self.llm = llm_service
    
    async def enhance_summary(
        self,
        original_text: str,
        writing_style: dict,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Enhance professional summary"""
        
        # Build request
        request = LLMRequest(
            prompt=self._build_prompt(original_text, writing_style),
            system_message="You are an expert resume writer...",
            temperature=0.4,
            max_tokens=2000
        )
        
        # Generate
        response = await self.llm.generate(request)
        
        return response.text
```

---

## Model Selection Strategy

### Per-Workflow Model Configuration

```python
# backend/app/infrastructure/llm/model_selector.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class ModelConfig:
    """Model configuration for specific workflow"""
    provider: str
    model: str
    temperature: float
    max_tokens: int
    description: str

class ModelSelector:
    """Select optimal model for each workflow"""
    
    WORKFLOW_CONFIGS = {
        "writing_style_extraction": ModelConfig(
            provider="groq",
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1500,
            description="Fast analysis with good JSON parsing"
        ),
        "profile_enhancement": ModelConfig(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=2000,
            description="High-quality text generation"
        ),
        "content_ranking": ModelConfig(
            provider="groq",
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=2500,
            description="Fast ranking with structured output"
        ),
        "cover_letter_generation": ModelConfig(
            provider="groq",
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=3000,
            description="Creative, natural cover letter writing"
        ),
    }
    
    @classmethod
    def get_config(cls, workflow: str) -> ModelConfig:
        """Get model config for workflow"""
        if workflow not in cls.WORKFLOW_CONFIGS:
            raise ValueError(f"Unknown workflow: {workflow}")
        
        return cls.WORKFLOW_CONFIGS[workflow]
    
    @classmethod
    def override_for_testing(cls, workflow: str, model: str):
        """Override model for testing (e.g., use faster/cheaper model)"""
        config = cls.WORKFLOW_CONFIGS[workflow]
        config.model = model
```

### Usage in Services

```python
async def enhance_profile(self, ...):
    # Get optimal model config
    config = ModelSelector.get_config("profile_enhancement")
    
    # Build request with workflow-specific settings
    request = LLMRequest(
        prompt=prompt,
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens
    )
    
    response = await self.llm.generate(request)
```

---

## Error Handling

### Standardized Error Types

```python
# backend/app/domain/exceptions/llm_exceptions.py

class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    pass

class LLMRateLimitError(LLMServiceError):
    """Rate limit exceeded"""
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after}s")

class LLMTimeoutError(LLMServiceError):
    """Request timeout"""
    pass

class LLMContentPolicyError(LLMServiceError):
    """Content policy violation"""
    pass

class LLMInvalidResponseError(LLMServiceError):
    """Invalid response format (e.g., malformed JSON)"""
    pass

class LLMAuthenticationError(LLMServiceError):
    """Authentication failed"""
    pass
```

### API Error Handling

```python
# backend/app/presentation/api/generation.py
from fastapi import HTTPException
from app.domain.exceptions.llm_exceptions import *

@router.post("/profile/enhance")
async def enhance_profile(...):
    try:
        result = await service.enhance_profile(...)
        return result
    
    except LLMRateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail=f"LLM rate limit exceeded. Try again in {e.retry_after}s",
            headers={"Retry-After": str(e.retry_after)}
        )
    
    except LLMTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM request timeout. Please try again."
        )
    
    except LLMContentPolicyError:
        raise HTTPException(
            status_code=400,
            detail="Content violates LLM provider policy"
        )
    
    except LLMInvalidResponseError:
        raise HTTPException(
            status_code=500,
            detail="LLM returned invalid response format"
        )
    
    except LLMServiceError as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM service error: {str(e)}"
        )
```

---

## Token Usage Tracking

### Token Counter

```python
# backend/app/infrastructure/llm/token_tracker.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TokenUsage:
    """Track token usage for cost monitoring"""
    user_id: int
    workflow: str
    provider: str
    model: str
    tokens_used: int
    estimated_cost: float
    timestamp: datetime

class TokenTracker:
    """Track and log token usage"""
    
    # Pricing per 1M tokens (as of Nov 2024)
    PRICING = {
        "groq": {
            "llama-3.1-8b-instant": 0.05,      # $0.05 / 1M tokens
            "llama-3.3-70b-versatile": 0.59,   # $0.59 / 1M tokens
        },
        "openai": {
            "gpt-3.5-turbo": 0.50,
            "gpt-4-turbo-preview": 10.00,
        }
    }
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def log_usage(
        self,
        user_id: int,
        workflow: str,
        provider: str,
        model: str,
        tokens_used: int
    ):
        """Log token usage to database"""
        cost = self._calculate_cost(provider, model, tokens_used)
        
        usage = TokenUsage(
            user_id=user_id,
            workflow=workflow,
            provider=provider,
            model=model,
            tokens_used=tokens_used,
            estimated_cost=cost,
            timestamp=datetime.utcnow()
        )
        
        # Store in database (implement storage logic)
        # await self.db.save(usage)
        
        return usage
    
    def _calculate_cost(self, provider: str, model: str, tokens: int) -> float:
        """Calculate estimated cost"""
        try:
            price_per_million = self.PRICING[provider][model]
            return (tokens / 1_000_000) * price_per_million
        except KeyError:
            return 0.0  # Unknown pricing
    
    async def get_user_usage(self, user_id: int, days: int = 30) -> dict:
        """Get user's token usage summary"""
        # Implement aggregation query
        return {
            "total_tokens": 125000,
            "total_cost": 0.12,
            "workflows": {
                "profile_enhancement": 50000,
                "cover_letter_generation": 75000
            }
        }
```

---

## Testing

### Mock LLM Service

```python
# backend/tests/mocks/mock_llm_service.py
from app.domain.ports.illm_service import ILLMService, LLMRequest, LLMResponse

class MockLLMService(ILLMService):
    """Mock LLM service for testing"""
    
    def __init__(self, responses: dict[str, str] = None):
        """
        Args:
            responses: Dict mapping prompts (or keywords) to mock responses
        """
        self.responses = responses or {}
        self.calls = []  # Track all calls for assertions
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Return mock response"""
        self.calls.append(request)
        
        # Find matching response
        response_text = self._find_response(request.prompt)
        
        return LLMResponse(
            text=response_text,
            model="mock-model",
            tokens_used=len(response_text.split()),
            generation_time=0.1,
            finish_reason="stop"
        )
    
    async def generate_json(self, request: LLMRequest) -> dict:
        """Return mock JSON response"""
        response = await self.generate(request)
        import json
        return json.loads(response.text)
    
    def get_provider_name(self) -> str:
        return "mock"
    
    def get_available_models(self) -> list[str]:
        return ["mock-model"]
    
    def _find_response(self, prompt: str) -> str:
        """Find matching response by keyword"""
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        return "Mock LLM response"
    
    def assert_called_with(self, keyword: str):
        """Assert service was called with prompt containing keyword"""
        for call in self.calls:
            if keyword.lower() in call.prompt.lower():
                return True
        raise AssertionError(f"No calls found with keyword: {keyword}")
```

### Test Example

```python
# backend/tests/test_profile_enhancement_service.py
import pytest
from tests.mocks.mock_llm_service import MockLLMService
from app.application.services.profile_enhancement_service import ProfileEnhancementService

@pytest.mark.asyncio
async def test_enhance_summary():
    # Arrange
    mock_llm = MockLLMService(responses={
        "professional_summary": "Enhanced professional summary text"
    })
    service = ProfileEnhancementService(llm_service=mock_llm)
    
    # Act
    result = await service.enhance_summary(
        original_text="I am a student",
        writing_style={"tone": "professional"}
    )
    
    # Assert
    assert result == "Enhanced professional summary text"
    mock_llm.assert_called_with("professional_summary")
```

---

## Performance Optimization

### Response Caching

```python
# backend/app/infrastructure/llm/caching_llm_service.py
import hashlib
import json
from typing import Optional
from app.domain.ports.illm_service import ILLMService, LLMRequest, LLMResponse

class CachingLLMService(ILLMService):
    """Wrapper that caches LLM responses"""
    
    def __init__(self, base_service: ILLMService, cache_ttl: int = 3600):
        self.base_service = base_service
        self.cache_ttl = cache_ttl
        self.cache = {}  # In production, use Redis
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate with caching"""
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Call base service
        response = await self.base_service.generate(request)
        
        # Cache response
        self.cache[cache_key] = response
        
        return response
    
    def _generate_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key from request"""
        key_data = {
            "prompt": request.prompt,
            "system_message": request.system_message,
            "temperature": request.temperature,
            "model": request.model
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_json.encode()).hexdigest()
    
    # Delegate other methods to base_service
    async def generate_json(self, request: LLMRequest) -> dict:
        return await self.base_service.generate_json(request)
    
    def get_provider_name(self) -> str:
        return self.base_service.get_provider_name()
    
    def get_available_models(self) -> list[str]:
        return self.base_service.get_available_models()
```

---

## Implementation Checklist

### Phase 1: Core Interface
- [ ] Define `ILLMService` interface
- [ ] Create `LLMRequest` and `LLMResponse` dataclasses
- [ ] Implement custom exceptions

### Phase 2: Groq Adapter
- [ ] Implement `GroqAdapter` class
- [ ] Add retry logic with exponential backoff
- [ ] Test with all Groq models
- [ ] Error handling for rate limits

### Phase 3: Provider Factory
- [ ] Implement `LLMFactory` class
- [ ] Configuration via environment variables
- [ ] Dependency injection setup

### Phase 4: Additional Adapters (Optional)
- [ ] Implement `OpenAIAdapter`
- [ ] Implement `AnthropicAdapter`
- [ ] Local model support

### Phase 5: Advanced Features
- [ ] Token usage tracking
- [ ] Response caching
- [ ] Model selection strategy
- [ ] Performance monitoring

### Phase 6: Testing
- [ ] Mock LLM service for unit tests
- [ ] Integration tests with real APIs
- [ ] Load testing
- [ ] Error scenario testing

---

## Next Steps

1. Review adapter design
2. Implement `ILLMService` interface
3. Create `GroqAdapter` with retry logic
4. Set up dependency injection
5. Test with all prompt templates
6. Monitor token usage and costs
7. Ready for full system implementation
