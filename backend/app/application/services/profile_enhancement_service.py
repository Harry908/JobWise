"""
Profile Enhancement Service - AI-powered enhancement (V3.0).

Uses LLM to enhance professional summaries and experience descriptions
with stronger action verbs, quantification, and impact statements.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import Depends

from app.domain.ports.llm_service import ILLMService, LLMMessage
from app.application.services.prompt_service import PromptService, get_prompt_service
from app.infrastructure.adapters.llm_factory import get_llm_service
from app.core.exceptions import LLMServiceError

logger = logging.getLogger(__name__)


class ProfileEnhancementService:
    """
    Service for AI-powered profile enhancement.
    
    Uses llama-3.3-70b-versatile with anti-fabrication rules.
    """
    
    # Model configuration per 02-AI-PIPELINE.md
    ENHANCEMENT_MODEL = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.3
    MAX_TOKENS = 2048
    
    def __init__(
        self,
        llm_service: ILLMService,
        prompt_service: PromptService
    ):
        """
        Initialize profile enhancement service.
        
        Args:
            llm_service: LLM service for generation
            prompt_service: Prompt template service
        """
        self.llm = llm_service
        self.prompts = prompt_service
    
    async def enhance_profile(
        self,
        professional_summary: str,
        experiences: Optional[List[Dict[str, Any]]] = None,
        projects: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Enhance professional summary and experience descriptions.
        
        Args:
            professional_summary: Original professional summary text
            experiences: List of experience dicts with id, title, company, description
            projects: List of project dicts with id, name, description, technologies
            
        Returns:
            Enhancement result with enhanced texts and metadata
            
        Raises:
            LLMServiceError: Enhancement failed
        """
        try:
            # Prepare template variables
            variables = {
                "professional_summary": professional_summary,
                "experiences": experiences or [],
                "projects": projects or []
            }
            
            # Render prompt template
            prompt = self.prompts.render("profile_enhancement", variables)
            
            # Create LLM messages
            messages = [
                LLMMessage(
                    role="system",
                    content="You are an expert resume writer. Enhance the provided content using strong action verbs and quantifiable impact. DO NOT fabricate any information."
                ),
                LLMMessage(
                    role="user",
                    content=prompt
                )
            ]
            
            # Call LLM
            logger.info(f"Enhancing profile with {len(experiences or [])} experiences and {len(projects or [])} projects")
            
            response = await self.llm.generate(
                messages=messages,
                model=self.ENHANCEMENT_MODEL,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Parse JSON response
            result = self._parse_enhancement_response(response.content)
            
            # Add metadata
            result["enhancement_metadata"] = {
                "model": self.ENHANCEMENT_MODEL,
                "timestamp": datetime.utcnow().isoformat(),
                "temperature": self.TEMPERATURE,
                "tokens_used": response.tokens_used,
                "confidence": 0.85  # Fixed confidence for now
            }
            
            logger.info(f"Enhancement successful: {response.tokens_used} tokens used")
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise LLMServiceError(f"Invalid JSON response from LLM: {str(e)}")
        
        except Exception as e:
            logger.error(f"Profile enhancement failed: {e}")
            raise LLMServiceError(f"Enhancement failed: {str(e)}")
    
    def _parse_enhancement_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured enhancement result.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed enhancement dict
        """
        # Extract JSON from response
        json_text = self._extract_json_from_text(response_text)
        
        # Parse JSON
        data = json.loads(json_text)
        
        # Validate structure
        if "enhanced_professional_summary" not in data:
            raise ValueError("Missing enhanced_professional_summary in response")
        
        # Normalize structure
        return {
            "enhanced_professional_summary": data.get("enhanced_professional_summary", ""),
            "enhanced_experiences": data.get("enhanced_experiences", []),
            "enhanced_projects": data.get("enhanced_projects", [])
        }
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Extract JSON object from LLM response text.
        
        Handles markdown code blocks and other formatting.
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
    
    async def enhance_professional_summary_only(
        self,
        professional_summary: str
    ) -> Dict[str, Any]:
        """
        Enhance only the professional summary.
        
        Simpler version for users who only want summary enhancement.
        
        Args:
            professional_summary: Original summary text
            
        Returns:
            Enhancement result with enhanced summary and metadata
        """
        result = await self.enhance_profile(
            professional_summary=professional_summary,
            experiences=[],
            projects=[]
        )
        
        return {
            "enhanced_professional_summary": result["enhanced_professional_summary"],
            "enhancement_metadata": result["enhancement_metadata"]
        }
    
    async def enhance_experience_only(
        self,
        experience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance a single experience description.
        
        Args:
            experience: Experience dict with id, title, company, description
            
        Returns:
            Enhancement result with enhanced description and metadata
        """
        # Create minimal summary from experience title for context
        summary_context = f"{experience.get('title', 'Professional')} with expertise in the field."
        
        result = await self.enhance_profile(
            professional_summary=summary_context,
            experiences=[experience],
            projects=[]
        )
        
        if result["enhanced_experiences"]:
            return {
                "enhanced_description": result["enhanced_experiences"][0].get("enhanced_description", ""),
                "enhancement_metadata": result["enhancement_metadata"]
            }
        
        return {
            "enhanced_description": experience.get("description", ""),
            "enhancement_metadata": result["enhancement_metadata"]
        }


# FastAPI dependency
def get_profile_enhancement_service(
    llm_service: ILLMService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> ProfileEnhancementService:
    """
    FastAPI dependency for ProfileEnhancementService injection.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(
            service: ProfileEnhancementService = Depends(get_profile_enhancement_service),
            llm: ILLMService = Depends(get_llm_service),
            prompts: PromptService = Depends(get_prompt_service)
        ):
            ...
    """
    return ProfileEnhancementService(
        llm_service=llm_service,
        prompt_service=prompt_service
    )
