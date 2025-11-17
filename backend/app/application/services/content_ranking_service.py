"""
Content Ranking Service - Job-specific content ranking (V3.0).

Uses LLM to rank experiences, projects, and skills by relevance
to a specific job posting.
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


class ContentRankingService:
    """
    Service for job-specific content ranking.
    
    Uses llama-3.1-8b-instant for fast ranking (5-8s target).
    """
    
    # Model configuration per 02-AI-PIPELINE.md
    RANKING_MODEL = "llama-3.1-8b-instant"
    TEMPERATURE = 0.2
    MAX_TOKENS = 1024
    
    def __init__(
        self,
        llm_service: ILLMService,
        prompt_service: PromptService
    ):
        """
        Initialize content ranking service.
        
        Args:
            llm_service: LLM service for generation
            prompt_service: Prompt template service
        """
        self.llm = llm_service
        self.prompts = prompt_service
    
    async def rank_content(
        self,
        job_title: str,
        job_company: str,
        job_description: str,
        experiences: List[Dict[str, Any]],
        projects: List[Dict[str, Any]],
        skills: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Rank user's content by relevance to job.
        
        Args:
            job_title: Target job title
            job_company: Target company name
            job_description: Full job description text
            experiences: List of experience dicts
            projects: List of project dicts
            skills: Dict of skill categories to skill lists
            
        Returns:
            Ranking result with ranked UUID arrays and explanations
            
        Raises:
            LLMServiceError: Ranking failed
        """
        try:
            # Prepare template variables
            variables = {
                "job_title": job_title,
                "job_company": job_company,
                "job_description": job_description,
                "experiences": experiences,
                "projects": projects,
                "skills": skills
            }
            
            # Render prompt template
            prompt = self.prompts.render("content_ranking", variables)
            
            # Create LLM messages
            messages = [
                LLMMessage(
                    role="system",
                    content="You are an expert at analyzing job descriptions and ranking resume content by relevance. Focus on keyword matches, required skills, and experience alignment."
                ),
                LLMMessage(
                    role="user",
                    content=prompt
                )
            ]
            
            # Call LLM
            logger.info(f"Ranking content for job: {job_title} at {job_company}")
            logger.debug(f"Analyzing {len(experiences)} experiences, {len(projects)} projects, {sum(len(v) for v in skills.values())} skills")
            
            response = await self.llm.generate(
                messages=messages,
                model=self.RANKING_MODEL,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Parse JSON response
            result = self._parse_ranking_response(response.content)
            
            # Add metadata
            result["ranking_model_used"] = self.RANKING_MODEL
            result["ranking_timestamp"] = datetime.utcnow().isoformat()
            result["tokens_used"] = response.tokens_used
            
            # Validate confidence score
            if "ranking_confidence_score" not in result or not isinstance(result["ranking_confidence_score"], (int, float)):
                result["ranking_confidence_score"] = 0.75  # Default confidence
            
            logger.info(f"Ranking successful: {response.tokens_used} tokens used, confidence={result.get('ranking_confidence_score', 0)}")
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise LLMServiceError(f"Invalid JSON response from LLM: {str(e)}")
        
        except Exception as e:
            logger.error(f"Content ranking failed: {e}")
            raise LLMServiceError(f"Ranking failed: {str(e)}")
    
    def _parse_ranking_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured ranking result.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed ranking dict
        """
        # Extract JSON from response
        json_text = self._extract_json_from_text(response_text)
        
        # Parse JSON
        data = json.loads(json_text)
        
        # Validate required fields
        required_fields = ["ranked_experience_ids", "ranked_project_ids", "ranked_skill_ids"]
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing {field} in ranking response, using empty list")
                data[field] = []
        
        # Ensure all are lists
        for field in required_fields:
            if not isinstance(data[field], list):
                data[field] = []
        
        # Normalize structure
        return {
            "ranked_experience_ids": data.get("ranked_experience_ids", []),
            "ranked_project_ids": data.get("ranked_project_ids", []),
            "ranked_skill_ids": data.get("ranked_skill_ids", []),
            "ranking_confidence_score": data.get("ranking_confidence_score", 0.75),
            "ranking_explanations": data.get("ranking_explanations", {})
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
    
    def apply_user_override(
        self,
        ranking: Dict[str, Any],
        user_overrides: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Apply user manual overrides to ranking.
        
        Args:
            ranking: Original ranking result
            user_overrides: Dict with manual rankings (ranked_experience_ids, etc.)
            
        Returns:
            Updated ranking with user modifications
        """
        updated_ranking = ranking.copy()
        
        # Apply overrides
        if "ranked_experience_ids" in user_overrides:
            updated_ranking["ranked_experience_ids"] = user_overrides["ranked_experience_ids"]
            updated_ranking["user_modified"] = True
            updated_ranking["user_override_timestamp"] = datetime.utcnow().isoformat()
        
        if "ranked_project_ids" in user_overrides:
            updated_ranking["ranked_project_ids"] = user_overrides["ranked_project_ids"]
            updated_ranking["user_modified"] = True
            updated_ranking["user_override_timestamp"] = datetime.utcnow().isoformat()
        
        if "ranked_skill_ids" in user_overrides:
            updated_ranking["ranked_skill_ids"] = user_overrides["ranked_skill_ids"]
            updated_ranking["user_modified"] = True
            updated_ranking["user_override_timestamp"] = datetime.utcnow().isoformat()
        
        return updated_ranking


# FastAPI dependency
def get_content_ranking_service(
    llm_service: ILLMService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> ContentRankingService:
    """
    FastAPI dependency for ContentRankingService injection.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(
            service: ContentRankingService = Depends(get_content_ranking_service),
            llm: ILLMService = Depends(get_llm_service),
            prompts: PromptService = Depends(get_prompt_service)
        ):
            ...
    """
    return ContentRankingService(
        llm_service=llm_service,
        prompt_service=prompt_service
    )
