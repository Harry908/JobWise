"""Mock LLM adapter for testing (Context7 pattern)."""

import asyncio
import logging
from typing import List, Optional

from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class MockLLMAdapter(ILLMService):
    """Mock LLM adapter with realistic timing (no external calls)."""
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate mock completion with realistic timing.
        
        Args:
            messages: List of conversation messages
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0-1.0)
            
        Returns:
            LLMResponse with mock content
        """
        # Simulate processing time
        if "8b" in model:
            await asyncio.sleep(1)  # Fast model
        else:
            await asyncio.sleep(2)  # Slower model
        
        # Generate mock content based on last user message
        user_messages = [msg for msg in messages if msg.role == "user"]
        last_user_msg = user_messages[-1].content if user_messages else ""
        
        # Mock different responses based on content
        if "analyze" in last_user_msg.lower() or "extract" in last_user_msg.lower():
            mock_content = """## Job Analysis
**Required Skills:**
- Python (5 years)
- FastAPI
- SQLAlchemy
- Docker

**Nice to Have:**
- AWS
- Kubernetes

**Experience Level:** Senior (5-8 years)
**Work Mode:** Hybrid"""
        
        elif "generate" in last_user_msg.lower() or "resume" in last_user_msg.lower():
            mock_content = """## Professional Summary
Results-driven Senior Backend Engineer with 8+ years of experience building scalable APIs and AI-powered systems. Expert in Python, FastAPI, and SQLAlchemy with proven track record in delivering high-performance applications.

## Technical Skills
- **Languages:** Python, SQL
- **Frameworks:** FastAPI, SQLAlchemy, Flask
- **Tools:** Docker, Git, AWS
- **Databases:** PostgreSQL, SQLite, Redis

## Professional Experience

### Senior Backend Engineer | TechCorp
*Jan 2020 - Present*
- Designed and implemented RESTful APIs serving 1M+ requests/day using FastAPI
- Reduced API response time by 40% through query optimization and caching strategies
- Led team of 4 engineers in microservices architecture migration

### Backend Engineer | StartupXYZ
*Jun 2017 - Dec 2019*
- Built scalable backend services using Python and PostgreSQL
- Implemented CI/CD pipelines reducing deployment time by 60%
- Collaborated with frontend team on API contract design"""
        
        else:
            mock_content = "Mock LLM response generated successfully."
        
        logger.info(f"Mock LLM generation: model={model}, messages={len(messages)}")
        
        return LLMResponse(
            content=mock_content,
            model=model,
            tokens_used=len(mock_content) // 4,  # Approximate token count
            finish_reason="stop"
        )
