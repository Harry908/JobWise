# Groq LLM Architecture Design Document

**Version**: 1.0  
**Status**: 🎯 **Design Ready** (Ready for Sprint 4 Implementation)  
**Last Updated**: November 10, 2025

## Executive Summary

This document outlines the architecture for integrating Groq's ultra-fast LLM inference service into JobWise's resume generation pipeline. Groq provides 10x-100x faster inference speeds compared to traditional LLM providers while maintaining competitive pricing, making it ideal for the 2-stage generation pipeline targeting <8s total generation time.

**Terminology Note**: See `docs/TERMINOLOGY_CLARIFICATION.md` for definitions of:
- **Master Profile** (✅ Implemented): User's manually entered career data  
- **Sample Resume** (⚠️ Backend Only): Uploaded file for layout extraction
- **Sample Cover Letter** (⚠️ Backend Only): Uploaded file for writing style extraction
- **Selected Job** (✅ Implemented): Target job posting for tailoring

**Key Benefits**:
- **Speed**: 280-1000 tokens/second (vs 20-50 TPS for OpenAI)
- **Cost**: $0.59/$0.79 per 1M tokens (input/output) for Llama 3.3 70B
- **Free Tier**: 30 RPM, 14,400 RPD, 40,000 TPM (sufficient for MVP testing)
- **Async Support**: Native Python async/await with `AsyncGroq` client
- **OpenAI Compatible**: Drop-in replacement for OpenAI SDK patterns

## Architecture Overview

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    JobWise Backend                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Generation Pipeline (2 Stages)             │    │
│  │                                                     │    │
│  │  Stage 1: Analysis & Matching (3s, 2500 tokens)   │    │
│  │           ↓ GroqLLMAdapter                        │    │
│  │  Stage 2: Generation & Validation (5s, 2500 tkns) │    │
│  │           ↓ GroqLLMAdapter                        │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │    Domain Port: ILLMService (Abstract Interface)  │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↑                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Infrastructure Adapter: GroqLLMAdapter            │    │
│  │  - AsyncGroq client initialization                │    │
│  │  - API key management (env variables)             │    │
│  │  - Error handling & retry logic                   │    │
│  │  - Rate limit management                          │    │
│  │  - Token usage tracking                           │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
└──────────────────────────┼───────────────────────────────────┘
                           ↓
              ┌────────────────────────┐
              │   Groq Cloud API       │
              │   (console.groq.com)   │
              │                        │
              │  • llama-3.3-70b      │
              │  • mixtral-8x7b       │
              │  • Rate: 280-560 TPS  │
              │  • Free Tier: 30 RPM  │
              └────────────────────────┘
```

## Technology Stack

### Core Dependencies

```toml
# requirements.txt (to be added in Sprint 4)
groq==0.33.0           # Official Groq Python SDK (latest stable)
python-dotenv==1.0.0   # Environment variable management (existing)
pydantic==2.x          # Data validation (existing)
asyncio                # Async support (stdlib)
```

### Python Requirements
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.11+ (current project version)

## Model Selection Strategy

### Recommended Models for Resume Generation (2025 Pricing)

| Model | Speed (TPS) | Cost (Input/Output per 1M) | Context Window | Use Case |
|-------|-------------|---------------------------|----------------|----------|
| **llama-3.3-70b-versatile** | 394 | $0.59 / $0.79 | 128K / 32K | **Primary**: High-quality resume generation, excellent at reasoning, instruction following, tool use |
| **llama-4-scout-17bx16e** | 594 | $0.11 / $0.34 | 128K / 32K | **Emerging**: New Llama 4 model, faster than 70B with competitive quality for mid-complexity tasks |
| **llama-3.1-8b-instant** | 840 | $0.05 / $0.08 | 128K / 128K | **Fallback**: Fast, cost-effective for simpler tasks (keyword extraction, classification) |
| **gpt-oss-120b** | 500 | $0.15 / $0.75 | 128K / 32K | **Alternative**: Enhanced instruction following, best for complex reasoning tasks |
| **mixtral-8x7b-32768** | 480 | $0.24 / $0.24 | 32K / 32K | **Legacy**: Good balance of speed and quality (consider upgrading to Llama 4 Scout) |

### Model Configuration by Pipeline Stage

```python
# Stage 1: Analysis & Matching (speed-optimized)
STAGE1_MODEL = "llama-3.1-8b-instant"  # Fast keyword extraction, profile matching
STAGE1_MAX_TOKENS = 2500
STAGE1_TEMPERATURE = 0.2  # Low for highly deterministic classification tasks

# Stage 2: Generation & Validation (quality-optimized)
STAGE2_MODEL = "llama-3.3-70b-versatile"  # High-quality resume generation
# Alternative: "llama-4-scout-17bx16e" for faster execution with moderate quality
STAGE2_MAX_TOKENS = 2500
STAGE2_TEMPERATURE = 0.4  # Moderate for creative but grounded content
```

**Rationale**:
- **Stage 1**: Uses faster 8B model (840 TPS) for structured analysis tasks (keyword extraction, relevance scoring). Target: <2s execution (1.5s p50 achievable).
- **Stage 2**: Uses advanced 70B model (394 TPS) for nuanced resume generation requiring strong instruction following and anti-fabrication adherence. Target: <6s execution (5s p50 achievable).
  - **Alternative**: Llama 4 Scout (594 TPS) reduces Stage 2 to ~3.5s with acceptable quality trade-off for high-volume scenarios.
- **Combined**: Achieves quality where needed while maintaining <8s total pipeline time (p50: ~6.5s with 70B, ~5s with Scout).

## API Integration Architecture

### Domain Layer: Port Interface

**File**: `backend/app/domain/ports/llm_service.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    """LLM message structure"""
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    """LLM generation response"""
    content: str
    model: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    generation_time: float  # seconds

class ILLMService(ABC):
    """
    Port interface for LLM service interactions.
    Implementations: GroqLLMAdapter, MockLLMAdapter, OpenAILLMAdapter
    """
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from LLM.
        
        Args:
            messages: Conversation history (system, user, assistant)
            model: Model identifier (e.g., "llama-3.3-70b-versatile")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with content and metadata
        
        Raises:
            LLMServiceError: On API errors
            RateLimitError: On rate limit exceeded
            TimeoutError: On request timeout
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream generation from LLM (for future real-time UI updates).
        
        Yields:
            String chunks of generated content
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if LLM service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        pass
```

### Infrastructure Layer: Groq Adapter

**File**: `backend/app/infrastructure/adapters/groq_llm_adapter.py`

```python
import os
import time
import logging
import httpx
from typing import List, AsyncIterator, Optional
from groq import AsyncGroq
import groq

from app.domain.ports.llm_service import (
    ILLMService, 
    LLMMessage, 
    LLMResponse
)
from app.core.exceptions import (
    LLMServiceError,
    RateLimitError,
    LLMTimeoutError
)

logger = logging.getLogger(__name__)

class GroqLLMAdapter(ILLMService):
    """
    Groq LLM service adapter implementation (2025 best practices).
    
    Features:
    - Async API calls with AsyncGroq client (groq-python v0.33.0+)
    - Granular timeout control (connect, read, write)
    - Automatic retry with exponential backoff
    - Comprehensive error handling (RateLimitError, APIConnectionError, etc.)
    - Rate limit handling (30 RPM free tier)
    - Token usage tracking with x_groq metadata
    - JSON mode support for structured outputs
    - Prompt caching for cost optimization
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[httpx.Timeout] = None,
        max_retries: int = 3
    ):
        """
        Initialize Groq adapter with 2025 SDK best practices.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
            timeout: httpx.Timeout object for granular control or float for simple timeout
            max_retries: Maximum retry attempts on transient errors
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Granular timeout configuration (2025 best practice)
        if timeout is None:
            timeout = httpx.Timeout(
                connect=5.0,   # Connection timeout
                read=30.0,     # Read timeout (generous for LLM responses)
                write=5.0,     # Write timeout
                pool=5.0       # Pool timeout
            )
        
        self.client = AsyncGroq(
            api_key=self.api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        
        self.timeout = timeout
        self.max_retries = max_retries
        
        logger.info(
            f"GroqLLMAdapter initialized with granular timeouts "
            f"(connect=5s, read=30s, write=5s, max_retries={max_retries})"
        )
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        json_mode: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion using Groq API with 2025 best practices.
        
        Features:
        - Comprehensive error handling (all groq exception types)
        - JSON mode for structured outputs
        - x_groq metadata extraction for token usage
        - Automatic caching detection
        
        Args:
            messages: List of LLMMessage objects
            model: Model identifier (e.g., "llama-3.3-70b-versatile")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            json_mode: Enable JSON output mode (2025 feature)
            **kwargs: Additional Groq API parameters
        
        Returns:
            LLMResponse with content, token usage, and metadata
        
        Raises:
            RateLimitError: 429 status (exceeded 30 RPM or 40K TPM)
            LLMTimeoutError: Request timeout
            LLMServiceError: Other API errors
        """
        start_time = time.time()
        
        try:
            # Convert LLMMessage to Groq format
            groq_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            logger.debug(
                f"Groq API call: model={model}, max_tokens={max_tokens}, "
                f"temperature={temperature}, json_mode={json_mode}, "
                f"messages={len(groq_messages)}"
            )
            
            # Prepare request parameters (2025 SDK syntax)
            request_params = {
                "messages": groq_messages,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            
            # Enable JSON mode if requested (2025 feature)
            if json_mode:
                request_params["response_format"] = {"type": "json_object"}
            
            # Make async API call with comprehensive error handling
            response = await self.client.chat.completions.create(**request_params)
            
            # Extract response data
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Extract token usage from x_groq metadata (2025 SDK pattern)
            tokens_used = response.usage.total_tokens if response.usage else 0
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            
            # Check if prompt caching was used (2025 feature detection)
            cache_hit = False
            if hasattr(response, 'x_groq') and response.x_groq:
                # Groq indicates cache hits in metadata (if available in future SDK versions)
                cache_hit = getattr(response.x_groq, 'cache_hit', False)
            
            generation_time = time.time() - start_time
            
            logger.info(
                f"Groq generation successful: {tokens_used} tokens "
                f"({prompt_tokens} prompt + {completion_tokens} completion) "
                f"in {generation_time:.2f}s (cache_hit: {cache_hit})"
            )
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=finish_reason,
                generation_time=generation_time
            )
        
        # Comprehensive error handling (2025 best practices)
        except groq.RateLimitError as e:
            error_msg = f"Groq rate limit exceeded (429): {str(e)}"
            logger.error(error_msg)
            logger.error(f"Status: {e.status_code}, Response: {e.response}")
            raise RateLimitError(error_msg) from e
        
        except groq.APIConnectionError as e:
            error_msg = f"Groq API connection failed: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Underlying cause: {e.__cause__}")
            raise LLMServiceError(error_msg) from e
        
        except groq.AuthenticationError as e:
            error_msg = f"Groq authentication failed (401): Check API key"
            logger.error(error_msg)
            raise LLMServiceError(error_msg) from e
        
        except groq.PermissionDeniedError as e:
            error_msg = f"Groq permission denied (403): Insufficient permissions"
            logger.error(error_msg)
            raise LLMServiceError(error_msg) from e
        
        except groq.NotFoundError as e:
            error_msg = f"Groq resource not found (404): Invalid model or endpoint"
            logger.error(error_msg)
            raise LLMServiceError(error_msg) from e
        
        except groq.UnprocessableEntityError as e:
            error_msg = f"Groq invalid request (422): {str(e)}"
            logger.error(error_msg)
            logger.error("Check request parameters (messages, model, tokens)")
            raise LLMServiceError(error_msg) from e
        
        except groq.InternalServerError as e:
            error_msg = f"Groq server error (500+): {str(e)}"
            logger.error(error_msg)
            logger.warning("Retry recommended for transient server errors")
            raise LLMServiceError(error_msg) from e
        
        except groq.APIStatusError as e:
            error_msg = f"Groq API error ({e.status_code}): {str(e)}"
            logger.error(error_msg)
            logger.error(f"Response: {e.response}")
            raise LLMServiceError(error_msg) from e
        
        except groq.APIError as e:
            error_msg = f"Groq general API error: {str(e)}"
            logger.error(error_msg)
            raise LLMServiceError(error_msg) from e
        
        except asyncio.TimeoutError as e:
            error_msg = f"Groq request timeout after {self.timeout}s"
            logger.error(error_msg)
            raise LLMTimeoutError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Unexpected error in Groq adapter: {str(e)}"
            logger.exception(error_msg)
            raise LLMServiceError(error_msg) from e
                top_p=kwargs.get("top_p", 1.0),
                stop=kwargs.get("stop"),
                stream=False
            )
            
            generation_time = time.time() - start_time
            
            # Extract response data
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            
            # Extract token usage
            usage = response.usage
            tokens_used = usage.total_tokens
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            
            logger.info(
                f"Groq generation successful: model={model}, "
                f"tokens={tokens_used}, time={generation_time:.2f}s, "
                f"TPS={completion_tokens/generation_time:.0f}"
            )
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=finish_reason,
                generation_time=generation_time
            )
        
        except groq.RateLimitError as e:
            logger.error(f"Groq rate limit exceeded: {e}")
            raise RateLimitError(
                f"Rate limit exceeded. Free tier: 30 RPM, 14,400 RPD. "
                f"Status: {e.status_code}"
            ) from e
        
        except groq.APIConnectionError as e:
            logger.error(f"Groq connection error: {e.__cause__}")
            raise LLMServiceError(
                f"Failed to connect to Groq API: {e.__cause__}"
            ) from e
        
        except groq.APITimeoutError as e:
            logger.error(f"Groq timeout after {self.timeout}s")
            raise LLMTimeoutError(
                f"Groq API timeout after {self.timeout}s"
            ) from e
        
        except groq.AuthenticationError as e:
            logger.error(f"Groq authentication failed: {e}")
            raise LLMServiceError(
                "Invalid Groq API key. Check GROQ_API_KEY environment variable."
            ) from e
        
        except groq.APIStatusError as e:
            logger.error(
                f"Groq API error: status={e.status_code}, "
                f"response={e.response}"
            )
            raise LLMServiceError(
                f"Groq API error {e.status_code}: {e.response}"
            ) from e
        
        except Exception as e:
            logger.exception("Unexpected error in Groq generation")
            raise LLMServiceError(
                f"Unexpected error: {str(e)}"
            ) from e
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream generation from Groq API.
        
        Future enhancement for real-time UI updates.
        """
        try:
            groq_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            stream = await self.client.chat.completions.create(
                messages=groq_messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                delta_content = chunk.choices[0].delta.content
                if delta_content:
                    yield delta_content
        
        except Exception as e:
            logger.exception("Error in Groq streaming")
            raise LLMServiceError(f"Streaming error: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """
        Check Groq API availability.
        
        Makes minimal API call to verify service health.
        """
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": "ping"}],
                model="llama-3.1-8b-instant",  # Use fastest model
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            return False
```

### Exception Definitions

**File**: `backend/app/core/exceptions.py` (additions)

```python
class LLMServiceError(Exception):
    """Base exception for LLM service errors"""
    pass

class RateLimitError(LLMServiceError):
    """Raised when API rate limit is exceeded"""
    pass

class LLMTimeoutError(LLMServiceError):
    """Raised when LLM request times out"""
    pass

class LLMValidationError(LLMServiceError):
    """Raised when LLM output fails validation"""
    pass
```

## Configuration Management

### Environment Variables

**File**: `backend/.env` (additions)

```bash
# Groq LLM Configuration
GROQ_API_KEY=gsk_your_api_key_here
GROQ_TIMEOUT=30.0
GROQ_MAX_RETRIES=3

# Model Selection (environment-specific)
LLM_STAGE1_MODEL=llama-3.1-8b-instant
LLM_STAGE2_MODEL=llama-3.3-70b-versatile

# Token Budgets
LLM_STAGE1_MAX_TOKENS=2500
LLM_STAGE2_MAX_TOKENS=2500

# Temperature Settings
LLM_STAGE1_TEMPERATURE=0.3  # Deterministic analysis
LLM_STAGE2_TEMPERATURE=0.5  # Balanced generation
```

### Configuration Class

**File**: `backend/app/core/config.py` (additions)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Groq LLM Settings
    groq_api_key: str
    groq_timeout: float = 30.0
    groq_max_retries: int = 3
    
    # Model Configuration
    llm_stage1_model: str = "llama-3.1-8b-instant"
    llm_stage2_model: str = "llama-3.3-70b-versatile"
    
    # Token Budgets
    llm_stage1_max_tokens: int = 2500
    llm_stage2_max_tokens: int = 2500
    
    # Temperature
    llm_stage1_temperature: float = 0.3
    llm_stage2_temperature: float = 0.5
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Service Integration

### Dependency Injection Pattern

**File**: `backend/app/core/dependencies.py` (additions)

```python
from typing import Annotated
from fastapi import Depends

from app.infrastructure.adapters.groq_llm_adapter import GroqLLMAdapter
from app.domain.ports.llm_service import ILLMService
from app.core.config import settings

async def get_llm_service() -> ILLMService:
    """
    Dependency injection for LLM service.
    
    Returns GroqLLMAdapter in production.
    Can be swapped with MockLLMAdapter for testing.
    """
    return GroqLLMAdapter(
        api_key=settings.groq_api_key,
        timeout=settings.groq_timeout,
        max_retries=settings.groq_max_retries
    )

# Type alias for injection
LLMServiceDep = Annotated[ILLMService, Depends(get_llm_service)]
```

### Generation Service Usage

**File**: `backend/app/application/services/generation_service.py` (example)

```python
from app.domain.ports.llm_service import ILLMService, LLMMessage

class GenerationService:
    def __init__(self, llm_service: ILLMService):
        self.llm = llm_service
    
    async def stage1_analysis_matching(
        self,
        job_description: str,
        user_profile: dict
    ) -> dict:
        """
        Stage 1: Job analysis and profile content matching.
        """
        # Build prompt with anti-fabrication rules
        messages = [
            LLMMessage(
                role="system",
                content=self._build_stage1_system_prompt()
            ),
            LLMMessage(
                role="user",
                content=f"Job Description:\n{job_description}\n\n"
                        f"User Profile:\n{json.dumps(user_profile, indent=2)}"
            )
        ]
        
        # Call LLM via port interface
        response = await self.llm.generate(
            messages=messages,
            model=settings.llm_stage1_model,
            max_tokens=settings.llm_stage1_max_tokens,
            temperature=settings.llm_stage1_temperature
        )
        
        # Parse and return structured analysis
        return self._parse_stage1_response(response.content)
    
    async def stage2_generation_validation(
        self,
        ranked_content: dict,
        job_analysis: dict,
        example_resume_structure: Optional[str] = None
    ) -> dict:
        """
        Stage 2: Resume generation with validation.
        """
        # Build prompt with anti-fabrication constraints
        messages = [
            LLMMessage(
                role="system",
                content=self._build_stage2_system_prompt()
            ),
            LLMMessage(
                role="user",
                content=self._build_stage2_user_prompt(
                    ranked_content,
                    job_analysis,
                    example_resume_structure
                )
            )
        ]
        
        # Call LLM via port interface
        response = await self.llm.generate(
            messages=messages,
            model=settings.llm_stage2_model,
            max_tokens=settings.llm_stage2_max_tokens,
            temperature=settings.llm_stage2_temperature
        )
        
        # Validate and return generated resume
        return self._parse_and_validate_stage2_response(response.content)
```

## Prompt Engineering Strategy (2025 Best Practices)

### Anti-Fabrication System Prompts

**2025 Enhancements**:
1. **Front-loading Critical Rules**: Place constraints at the very beginning (highest impact on LLM interpretation)
2. **Structured Output Mode**: Use JSON mode with explicit schema validation
3. **Chain-of-Thought Prompting**: Break complex tasks into intermediate reasoning steps
4. **Temperature Control**: 0.1-0.3 for deterministic tasks, 0.4-0.6 for creative content
5. **Adaptive Fact-Verification**: Cross-reference generated content against source material
6. **Strong System Intent**: Clear role assignment and task boundaries

#### Stage 1: Analysis & Matching (Enhanced 2025)

```python
STAGE1_SYSTEM_PROMPT = """CRITICAL CONSTRAINTS (DO NOT VIOLATE):
- ANALYSIS ONLY - Do not generate any new content
- EXACT MATCHING - Only reference skills/experiences explicitly in user's profile
- STRUCTURED OUTPUT - Return valid JSON matching the schema below
- NO ASSUMPTIONS - If information is missing, mark as null/empty

YOUR ROLE: You are a resume content analyzer. Your task is to:
1. Extract job requirements (keywords, skills, seniority level)
2. Score user's experiences/projects by relevance (0.0-1.0 scale)
3. Rank content for resume inclusion (highest scores first)
4. Identify gaps between job requirements and user's profile

CHAIN OF THOUGHT REASONING:
Step 1: Parse job description → extract keywords and requirements
Step 2: For each user experience/project → calculate relevance score based on keyword overlap
Step 3: Rank all content by relevance score (descending)
Step 4: Identify required skills missing from user's profile

OUTPUT SCHEMA (STRICT JSON):
{
  "job_requirements": {
    "keywords": ["keyword1", "keyword2"],  // Exact keywords from job description
    "required_skills": ["skill1", "skill2"],  // Technical and soft skills required
    "seniority_level": "junior|mid|senior|lead",
    "years_experience": integer or null
  },
  "ranked_experiences": [
    {
      "id": "experience_uuid_from_user_profile",  // MUST exist in user's data
      "relevance_score": 0.0-1.0,  // Keyword match percentage
      "matching_keywords": ["keyword1"],  // Only keywords present in both job and experience
      "reason": "Brief explanation for relevance score"
    }
  ],
  "ranked_projects": [...],  // Same structure as experiences
  "recommended_skills": ["skill1"],  // ONLY skills user already has that match job
  "missing_skills": ["skill2"]  // Job requirements user lacks
}

VALIDATION: Before returning, verify:
1. All IDs reference actual user content (no fabrication)
2. All scores are between 0.0 and 1.0
3. matching_keywords exist in both job description and user content
4. recommended_skills are subset of user's existing skills
"""

#### Stage 2: Generation & Validation (Enhanced 2025)

```python
STAGE2_SYSTEM_PROMPT = """CRITICAL CONSTRAINTS (PLACE AT TOP - HIGHEST PRIORITY):
1. ZERO FABRICATION - Use ONLY content from provided ranked experiences/projects
2. SOURCE TRACING - Every resume bullet MUST map to a source content ID
3. EXACT SKILLS - Use ONLY skills from recommended_skills list
4. STRICT VALIDATION - Self-check output against source material before returning
5. STRUCTURED OUTPUT - Return valid JSON with content + validation metadata

YOUR ROLE: Professional resume writer creating ATS-optimized, tailored resumes.

TASK DECOMPOSITION (Chain-of-Thought):
Step 1: Review ranked content → select top 3-5 experiences/projects
Step 2: For each selected item → rewrite bullets to emphasize job-relevant keywords
Step 3: Extract skills → filter to only recommended_skills
Step 4: Generate professional summary → synthesize from selected experiences
Step 5: VALIDATE → cross-reference every sentence against source material
Step 6: Calculate ATS score → keyword coverage and formatting compliance

ANTI-FABRICATION RULES:
- Work Experience:
  * Company names: Use EXACT company from source (no variations)
  * Dates: Use EXACT dates from source (no approximations)
  * Achievements: Rewrite from source achievements ONLY (no new metrics)
  * Technologies: Use ONLY technologies mentioned in source

- Skills Section:
  * Technical skills: ONLY from recommended_skills
  * If job requires skill user lacks → ADD to missing_skills, DO NOT add to resume

- Projects Section:
  * Project names: EXACT from source
  * Descriptions: Derived from source descriptions ONLY
  * Technologies: ONLY those listed in source project

- Professional Summary:
  * Synthesize from actual experiences (no generic statements)
  * Years of experience: Calculate from source dates
  * Specializations: Derived from actual project/work history

QUALITY TARGETS:
- ATS Score: ≥85% (keyword density 10-15%)
- Keyword Coverage: ≥80% of job requirements (from available user content)
- One-page format preferred (unless >7 years experience)

OUTPUT SCHEMA (STRICT JSON):
{
  "resume": {
    "text": "Full resume in Markdown format",
    "html": "<p>HTML-formatted resume</p>",
    "sections": {
      "professional_summary": "2-3 sentence summary",
      "experience": [
        {
          "company": "Exact company name from source",
          "title": "Exact title from source",
          "dates": "MM/YYYY - MM/YYYY (exact from source)",
          "bullets": [
            {
              "text": "Achievement bullet",
              "source_id": "exp-uuid-123",  // Traceability
              "keywords_emphasized": ["Python", "API"]
            }
          ]
        }
      ],
      "education": [...],  // From user profile ONLY
      "skills": {
        "technical": [],  // Subset of recommended_skills
        "soft": []  // From source if mentioned
      },
      "projects": [...]  // From ranked_projects ONLY
    }
  },
  "validation": {
    "fabrication_check": "passed|failed",
    "fabrication_details": "If failed, explain what was fabricated",
    "content_mapping": [
      {
        "resume_text": "Exact sentence from generated resume",
        "source_id": "exp-uuid or proj-uuid",
        "source_text": "Original text from user profile",
        "confidence": 0.0-1.0  // Similarity to source (1.0 = exact match)
      }
    ],
    "missing_skills": ["Docker", "Kubernetes"],  // Job requirements user lacks
    "ats_score": 0.87,  // Keyword density and formatting compliance
    "keyword_coverage": 0.82,  // Percentage of job keywords in resume
    "adaptive_verification": {
      "cross_references_checked": 12,  // Number of fact-checks performed
      "mismatches_found": 0  // Any discrepancies between resume and source
    }
  }
}

ERROR HANDLING:
If user profile lacks sufficient relevant content for this job:
{
  "error": "insufficient_profile_content",
  "details": "User has no relevant experience for [specific job requirement]",
  "suggestions": ["Add projects demonstrating X", "Include coursework in Y"]
}

FINAL VALIDATION CHECKLIST (Before returning):
✓ All companies/titles/dates match source exactly
✓ All achievements derive from source content
✓ All skills are in recommended_skills list
✓ Every resume bullet maps to a source_id
✓ fabrication_check = "passed"
✓ ATS score ≥ 0.85 (if achievable with user's content)
"""
```

**Usage Example with JSON Mode**:
```python
# Stage 2 generation with enforced JSON output
response = await llm.generate(
    messages=[
        LLMMessage(role="system", content=STAGE2_SYSTEM_PROMPT),
        LLMMessage(role="user", content=user_prompt)
    ],
    model="llama-3.3-70b-versatile",
    temperature=0.2,  # Low for deterministic, factual output
    json_mode=True,  # Enforce JSON schema compliance
    max_tokens=2500
)

# Parse and validate JSON output
import json
result = json.loads(response.content)
assert result["validation"]["fabrication_check"] == "passed", "Fabrication detected!"
```

## Rate Limiting & Cost Management

### Free Tier Constraints

**Groq Free Tier Limits** (as of November 2025):
- **30 requests per minute (RPM)**
- **14,400 requests per day (RPD)**
- **40,000 tokens per minute (TPM)**

### Cost Optimization Features (2025)

**1. Prompt Caching (50% Discount)**
- Cache frequently used prompts (system messages, example resumes)
- **Savings**: 50% reduction on cached input tokens
- **Use Case**: Reuse system prompt and example resume structure across all generations
- **Implementation**: Same input prefix triggers cache hit automatically
- **Estimated Impact**: ~30% total cost reduction (system prompt typically 40% of input)

```python
# System prompt is cached after first use
CACHED_SYSTEM_PROMPT = """You are a professional resume writer..."""

async def generate_with_caching(self, user_content: str):
    messages = [
        {"role": "system", "content": CACHED_SYSTEM_PROMPT},  # Cached (50% discount after first call)
        {"role": "user", "content": user_content}  # Not cached (full price)
    ]
    # Groq automatically detects and applies cache discount
    response = await self.client.chat.completions.create(...)
```

**2. Batch API (50% Discount)**
- Process multiple generations asynchronously
- **Savings**: 50% reduction on all tokens (input + output)
- **Use Case**: Bulk generation for multiple jobs, A/B testing, regeneration workflows
- **Trade-off**: 24-hour completion window (not suitable for real-time UX)
- **Estimated Impact**: 50% cost reduction for batch jobs

```python
# Batch API for non-urgent bulk generations
async def create_batch_generation(self, job_ids: List[str]):
    batch_requests = [
        {
            "custom_id": f"gen-{job_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {...}
        }
        for job_id in job_ids
    ]
    # Returns batch_id, results delivered within 24 hours
    batch = await self.client.batches.create(...)
```

### MVP Usage Estimation

**Per Generation (2 stages)**:
- Stage 1: 1 request, ~2500 tokens
- Stage 2: 1 request, ~2500 tokens
- **Total**: 2 requests, ~5000 tokens

**Free Tier Capacity**:
- **Per minute**: 15 generations (30 RPM / 2 requests per gen)
- **Per day**: 7,200 generations (14,400 RPD / 2)
- **Token limit**: 8 generations/min (40K TPM / 5K tokens per gen)
- **Effective limit**: 8 generations/minute (token-constrained)

**MVP Sufficiency**: Free tier supports 480 generations/hour, far exceeding MVP testing needs (estimated 10-50 generations/day).

### Rate Limit Handling Strategy

```python
class RateLimitHandler:
    """
    Manages Groq API rate limits with exponential backoff.
    """
    
    def __init__(self):
        self.request_count = 0
        self.token_count = 0
        self.window_start = time.time()
        self.window_duration = 60  # 1 minute window
    
    async def check_rate_limit(self, estimated_tokens: int):
        """
        Check if request would exceed rate limits.
        
        Implements token bucket algorithm with time-based window reset.
        """
        now = time.time()
        
        # Reset window if expired
        if now - self.window_start > self.window_duration:
            self.request_count = 0
            self.token_count = 0
            self.window_start = now
        
        # Check limits
        if self.request_count >= 30:  # RPM limit
            wait_time = self.window_duration - (now - self.window_start)
            logger.warning(f"RPM limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            return await self.check_rate_limit(estimated_tokens)
        
        if self.token_count + estimated_tokens > 40000:  # TPM limit
            wait_time = self.window_duration - (now - self.window_start)
            logger.warning(f"TPM limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            return await self.check_rate_limit(estimated_tokens)
        
        # Update counters
        self.request_count += 1
        self.token_count += estimated_tokens
        
        return True
```

### Cost Estimation

**Model Pricing** (Llama 3.3 70B):
- Input: $0.59 per 1M tokens
- Output: $0.79 per 1M tokens

**Per Generation Cost (Without Optimizations)**:
- Stage 1: 1500 input + 1000 output = (1500 × $0.59 + 1000 × $0.79) / 1M = **$0.0018**
- Stage 2: 1500 input + 1000 output = (1500 × $0.59 + 1000 × $0.79) / 1M = **$0.0018**
- **Total per generation**: **$0.0036** (~$0.004)

**Per Generation Cost (With Prompt Caching)**:
- Stage 1: System prompt cached (600 tokens × 50% discount) + user input (900 tokens) + output (1000 tokens)
  - Cost: (600 × $0.295 + 900 × $0.59 + 1000 × $0.79) / 1M = **$0.0013**
- Stage 2: Same caching pattern = **$0.0013**
- **Total per generation**: **$0.0026** (~$0.003) - **28% savings**

**Per Generation Cost (Batch API for Bulk Jobs)**:
- 50% discount on all tokens
- **Total per generation**: **$0.0018** (~$0.002) - **50% savings**

**Monthly Cost Projection (With Caching)**:
- 1,000 generations/month: **$2.60** (was $3.60)
- 10,000 generations/month: **$26.00** (was $36.00)
- 100,000 generations/month: **$260.00** (was $360.00)

**vs Original Estimate** ($0.10 per generation with GPT-4o-mini):
- **97% cost reduction** without optimizations ($0.004 vs $0.10)
- **98% cost reduction** with caching ($0.003 vs $0.10)
- **98.5% cost reduction** with batch API ($0.002 vs $0.10)
- Groq with caching is **33x cheaper** while maintaining quality

## Error Handling & Resilience

### Retry Strategy

```python
class RetryConfig:
    """Exponential backoff configuration"""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd

async def retry_with_backoff(
    func,
    *args,
    config: RetryConfig = RetryConfig(),
    **kwargs
):
    """
    Execute function with exponential backoff retry.
    
    Retries on:
    - APIConnectionError
    - RateLimitError
    - InternalServerError (500+)
    
    Does NOT retry on:
    - AuthenticationError
    - ValidationError
    - 400-level errors (except 429)
    """
    for attempt in range(config.max_retries):
        try:
            return await func(*args, **kwargs)
        
        except (groq.APIConnectionError, groq.RateLimitError) as e:
            if attempt == config.max_retries - 1:
                raise
            
            # Calculate backoff delay
            delay = min(
                config.base_delay * (config.exponential_base ** attempt),
                config.max_delay
            )
            
            # Add jitter
            if config.jitter:
                delay *= (0.5 + random.random())
            
            logger.warning(
                f"Retry {attempt + 1}/{config.max_retries} after {delay:.1f}s: {e}"
            )
            await asyncio.sleep(delay)
        
        except groq.APIStatusError as e:
            # Only retry 500+ errors
            if e.status_code >= 500:
                if attempt == config.max_retries - 1:
                    raise
                delay = config.base_delay * (config.exponential_base ** attempt)
                await asyncio.sleep(delay)
            else:
                raise  # Don't retry 4xx errors
```

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Service failing, reject requests immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"
    
    async def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise LLMServiceError("Circuit breaker OPEN: service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful request"""
        self.failure_count = 0
        
        if self.state == "HALF_OPEN":
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = "CLOSED"
                self.success_count = 0
                logger.info("Circuit breaker CLOSED: service recovered")
    
    def _on_failure(self):
        """Handle failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.success_count = 0
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(
                f"Circuit breaker OPEN: {self.failure_count} consecutive failures"
            )
```

## Testing Strategy

### Unit Tests

**File**: `backend/tests/unit/test_groq_llm_adapter.py`

```python
import pytest
from unittest.mock import AsyncMock, patch
from groq import AsyncGroq

from app.infrastructure.adapters.groq_llm_adapter import GroqLLMAdapter
from app.domain.ports.llm_service import LLMMessage

@pytest.mark.asyncio
async def test_groq_adapter_generation_success():
    """Test successful LLM generation"""
    adapter = GroqLLMAdapter(api_key="test-key")
    
    # Mock Groq response
    mock_response = AsyncMock()
    mock_response.choices = [
        AsyncMock(
            message=AsyncMock(content="Generated resume content"),
            finish_reason="stop"
        )
    ]
    mock_response.usage = AsyncMock(
        total_tokens=1500,
        prompt_tokens=500,
        completion_tokens=1000
    )
    
    with patch.object(adapter.client.chat.completions, 'create', return_value=mock_response):
        messages = [
            LLMMessage(role="system", content="You are a resume writer"),
            LLMMessage(role="user", content="Generate resume")
        ]
        
        response = await adapter.generate(
            messages=messages,
            model="llama-3.3-70b-versatile",
            max_tokens=2000
        )
        
        assert response.content == "Generated resume content"
        assert response.tokens_used == 1500
        assert response.finish_reason == "stop"

@pytest.mark.asyncio
async def test_groq_adapter_rate_limit_error():
    """Test rate limit error handling"""
    adapter = GroqLLMAdapter(api_key="test-key")
    
    with patch.object(
        adapter.client.chat.completions,
        'create',
        side_effect=groq.RateLimitError("Rate limit exceeded", response=None, body=None)
    ):
        with pytest.raises(RateLimitError):
            await adapter.generate(
                messages=[LLMMessage(role="user", content="test")],
                model="llama-3.3-70b-versatile"
            )
```

### Integration Tests

**File**: `backend/tests/integration/test_groq_api_live.py`

```python
import pytest
import os

from app.infrastructure.adapters.groq_llm_adapter import GroqLLMAdapter
from app.domain.ports.llm_service import LLMMessage

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set"
)
@pytest.mark.asyncio
async def test_groq_live_api_generation():
    """Test live Groq API call"""
    adapter = GroqLLMAdapter()
    
    messages = [
        LLMMessage(role="system", content="You are a helpful assistant"),
        LLMMessage(role="user", content="Say 'test successful' in 2 words")
    ]
    
    response = await adapter.generate(
        messages=messages,
        model="llama-3.1-8b-instant",
        max_tokens=10,
        temperature=0.0
    )
    
    assert response.content is not None
    assert response.tokens_used > 0
    assert response.generation_time > 0
    print(f"Live API test: {response.content} ({response.tokens_used} tokens, {response.generation_time:.2f}s)")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_groq_health_check():
    """Test Groq service health check"""
    adapter = GroqLLMAdapter()
    is_healthy = await adapter.health_check()
    assert is_healthy is True
```

### Mock Adapter for Testing

**File**: `backend/app/infrastructure/adapters/mock_llm_adapter.py`

```python
import asyncio
from typing import List, AsyncIterator

from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse

class MockLLMAdapter(ILLMService):
    """
    Mock LLM adapter for testing without API calls.
    
    Returns realistic mock responses with configurable delays.
    """
    
    def __init__(self, response_delay: float = 0.5):
        self.response_delay = response_delay
        self.call_count = 0
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Return mock response after simulated delay"""
        await asyncio.sleep(self.response_delay)
        self.call_count += 1
        
        # Generate mock content based on stage
        if "analyze" in messages[-1].content.lower():
            content = self._mock_stage1_response()
        else:
            content = self._mock_stage2_response()
        
        return LLMResponse(
            content=content,
            model=model,
            tokens_used=1500,
            prompt_tokens=500,
            completion_tokens=1000,
            finish_reason="stop",
            generation_time=self.response_delay
        )
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream mock response"""
        mock_chunks = ["Mock ", "streaming ", "response"]
        for chunk in mock_chunks:
            await asyncio.sleep(0.1)
            yield chunk
    
    async def health_check(self) -> bool:
        """Always healthy in mock"""
        return True
    
    def _mock_stage1_response(self) -> str:
        """Mock job analysis response"""
        return """{
            "job_requirements": {
                "keywords": ["python", "fastapi", "sql"],
                "required_skills": ["backend development"],
                "seniority_level": "mid"
            },
            "ranked_experiences": [
                {
                    "id": "exp-1",
                    "relevance_score": 0.95,
                    "matching_keywords": ["python", "fastapi"]
                }
            ]
        }"""
    
    def _mock_stage2_response(self) -> str:
        """Mock resume generation response"""
        return """{
            "resume": {
                "text": "# John Doe\\n\\n## Software Engineer\\n\\nExperienced backend developer..."
            },
            "validation": {
                "fabrication_check": "passed",
                "ats_score": 0.87
            }
        }"""
```

## Monitoring & Observability

### Logging Strategy

```python
# Configure structured logging for LLM calls
import logging
import json

logger = logging.getLogger("groq_llm")
logger.setLevel(logging.INFO)

# Log format with structured data
class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName
        }
        
        # Add custom fields
        if hasattr(record, "tokens_used"):
            log_data["tokens_used"] = record.tokens_used
        if hasattr(record, "generation_time"):
            log_data["generation_time"] = record.generation_time
        if hasattr(record, "model"):
            log_data["model"] = record.model
        
        return json.dumps(log_data)
```

### Metrics Tracking

```python
class LLMMetricsTracker:
    """Track LLM usage metrics for monitoring"""
    
    def __init__(self):
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.error_count = 0
        self.generation_times = []
    
    def record_generation(self, response: LLMResponse, model: str):
        """Record successful generation metrics"""
        self.total_requests += 1
        self.total_tokens += response.tokens_used
        self.generation_times.append(response.generation_time)
        
        # Calculate cost
        if model == "llama-3.3-70b-versatile":
            cost = (
                response.prompt_tokens * 0.59 / 1_000_000 +
                response.completion_tokens * 0.79 / 1_000_000
            )
            self.total_cost += cost
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.error_count += 1
    
    def get_summary(self) -> dict:
        """Get metrics summary"""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.total_requests, 1),
            "avg_generation_time": sum(self.generation_times) / len(self.generation_times) if self.generation_times else 0,
            "p95_generation_time": sorted(self.generation_times)[int(len(self.generation_times) * 0.95)] if self.generation_times else 0
        }
```

## Security Considerations

### API Key Management

1. **Environment Variables**: Store `GROQ_API_KEY` in `.env`, never in code
2. **Key Rotation**: Support key rotation without service restart
3. **Access Control**: Limit key permissions to chat completions only
4. **Monitoring**: Alert on unusual API usage patterns

### Input Validation

```python
def validate_llm_input(messages: List[LLMMessage]) -> None:
    """Validate LLM inputs before API call"""
    
    # Prevent prompt injection
    for msg in messages:
        if len(msg.content) > 50000:  # Max content length
            raise ValueError("Message content exceeds maximum length")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "ignore previous instructions",
            "disregard all prior",
            "forget everything"
        ]
        
        content_lower = msg.content.lower()
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                logger.warning(f"Potential prompt injection detected: {pattern}")
                # Optionally sanitize or reject
```

### Output Sanitization

```python
def sanitize_llm_output(content: str) -> str:
    """Sanitize LLM output before storing/displaying"""
    
    # Remove potential malicious content
    content = content.strip()
    
    # Remove excessive whitespace
    content = " ".join(content.split())
    
    # Validate JSON structure if expected
    if content.startswith("{"):
        try:
            json.loads(content)
        except json.JSONDecodeError:
            raise LLMValidationError("Invalid JSON output from LLM")
    
    return content
```

## Migration Path from Mock to Groq

### Phase 1: Parallel Implementation (Sprint 4 Week 1)
1. Implement `GroqLLMAdapter` alongside existing `MockLLMAdapter`
2. Add feature flag: `USE_GROQ_LLM=false` (default to mock)
3. Add integration tests with live API
4. Document Groq API key setup

### Phase 2: Testing & Validation (Sprint 4 Week 2)
1. Enable Groq for development environment
2. Compare outputs: Groq vs Mock
3. Validate anti-fabrication measures
4. Performance benchmarking (target <8s)

### Phase 3: Gradual Rollout (Sprint 4 Week 3)
1. Enable Groq for 10% of production traffic
2. Monitor error rates, latency, costs
3. Adjust prompts based on output quality
4. Increase to 50%, then 100%

### Phase 4: Mock Deprecation (Sprint 5)
1. Remove feature flag
2. Keep `MockLLMAdapter` for testing only
3. Update documentation
4. Final cost/performance validation

## Performance Targets

| Metric | Target | Groq Expected | Status |
|--------|--------|---------------|--------|
| Stage 1 Latency (p50) | <3s | 1-2s (8B model @ 560 TPS) | ✅ Achievable |
| Stage 2 Latency (p50) | <6s | 3-4s (70B model @ 280 TPS) | ✅ Achievable |
| Total Pipeline (p50) | <8s | 4-6s | ✅ Exceeds target |
| Total Pipeline (p95) | <10s | 6-8s | ✅ Exceeds target |
| Cost per Generation | <$0.10 | $0.004 | ✅ 25x better |
| Token Budget | <5000 | 5000 | ✅ On target |
| Error Rate | <1% | TBD | 🔄 To monitor |
| Fabrication Rate | 0% | 0% | 🎯 Enforced by prompts |

## Appendix

### Groq Model Comparison

| Model | Parameters | Speed (TPS) | Cost (Input/Output) | Context | Best For |
|-------|-----------|-------------|---------------------|---------|----------|
| llama-3.3-70b-versatile | 70B | 280 | $0.59/$0.79 | 131K/32K | High-quality generation, reasoning, instruction following |
| llama-3.1-8b-instant | 8B | 560 | $0.05/$0.08 | 131K/131K | Fast analysis, structured extraction |
| mixtral-8x7b-32768 | 8x7B | 480 | $0.24/$0.24 | 32K/32K | Balanced speed/quality |

### Useful Resources

- **Groq Console**: https://console.groq.com
- **Python SDK GitHub**: https://github.com/groq/groq-python
- **API Documentation**: https://console.groq.com/docs
- **Model Cards**: https://console.groq.com/docs/models
- **Pricing**: https://groq.com/pricing

### Glossary

- **TPS**: Tokens Per Second - inference speed metric
- **TPM**: Tokens Per Minute - rate limit metric
- **RPM**: Requests Per Minute - rate limit metric
- **RPD**: Requests Per Day - rate limit metric
- **ATS**: Applicant Tracking System
- **LLM**: Large Language Model
- **Circuit Breaker**: Failure isolation pattern
- **Exponential Backoff**: Retry delay strategy

---

**Document Status**: Ready for implementation in Sprint 4. All architectural decisions documented. Integration points defined. Testing strategy outlined.
