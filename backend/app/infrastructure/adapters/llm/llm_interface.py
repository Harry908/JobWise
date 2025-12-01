"""LLM interface for AI operations."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class LLMInterface(ABC):
    """Abstract interface for LLM adapters."""
    
    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """
        Generate completion from LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Additional model-specific parameters
            
        Returns:
            Dict with 'content', 'tokens', 'model', 'processing_time'
        """
        pass
    
    @abstractmethod
    async def extract_writing_style(self, sample_text: str) -> Dict:
        """Extract writing style from sample text."""
        pass
    
    @abstractmethod
    async def enhance_text(self, text: str, style: Optional[Dict] = None) -> str:
        """Enhance text using optional writing style."""
        pass
    
    @abstractmethod
    async def rank_content(
        self,
        job_description: str,
        experiences: list,
        projects: list
    ) -> Dict:
        """Rank content by relevance to job."""
        pass
    
    @abstractmethod
    async def generate_cover_letter(
        self,
        job_description: str,
        profile_data: Dict,
        writing_style: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Generate personalized cover letter."""
        pass
