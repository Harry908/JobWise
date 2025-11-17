"""
Document Generation Service - Cover letter generation (V3.0).

Uses LLM to generate tailored cover letters matching user's writing style
and incorporating job-specific ranked content.
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


class DocumentGenerationService:
    """
    Service for cover letter generation.
    
    Uses llama-3.3-70b-versatile for high-quality generation.
    """
    
    # Model configuration per 02-AI-PIPELINE.md
    GENERATION_MODEL = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.4
    MAX_TOKENS = 2048
    
    def __init__(
        self,
        llm_service: ILLMService,
        prompt_service: PromptService
    ):
        """
        Initialize document generation service.
        
        Args:
            llm_service: LLM service for generation
            prompt_service: Prompt template service
        """
        self.llm = llm_service
        self.prompts = prompt_service
    
    async def generate_cover_letter(
        self,
        job_title: str,
        job_company: str,
        job_description: str,
        user_name: str,
        user_email: str,
        professional_summary: str,
        top_experiences: List[Dict[str, Any]],
        top_projects: List[Dict[str, Any]],
        top_skills: List[str],
        writing_style: Dict[str, Any],
        user_custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate tailored cover letter.
        
        Args:
            job_title: Target job title
            job_company: Target company name
            job_description: Full job description
            user_name: User's full name
            user_email: User's email
            professional_summary: User's professional summary
            top_experiences: Top 3-5 ranked experiences
            top_projects: Top 2-3 ranked projects
            top_skills: Top 10-15 ranked skills
            writing_style: Writing style config from WritingStyleService
            user_custom_prompt: Optional custom instructions
            
        Returns:
            Generated cover letter with metadata
            
        Raises:
            LLMServiceError: Generation failed
        """
        try:
            # Prepare template variables
            variables = {
                "job_title": job_title,
                "job_company": job_company,
                "job_description": job_description,
                "user_name": user_name,
                "user_email": user_email,
                "professional_summary": professional_summary,
                "top_experiences": top_experiences,
                "top_projects": top_projects,
                "top_skills": top_skills,
                "writing_style": writing_style,
                "user_custom_prompt": user_custom_prompt or ""
            }
            
            # Render prompt template
            prompt = self.prompts.render("cover_letter_generation", variables)
            
            # Create LLM messages with anti-fabrication rules
            messages = [
                LLMMessage(
                    role="system",
                    content=(
                        "You are an expert cover letter writer. "
                        "Write a compelling, personalized cover letter that matches the user's writing style. "
                        "CRITICAL RULES:\n"
                        "1. ONLY use information provided in the user profile\n"
                        "2. DO NOT invent, assume, or fabricate any skills, experiences, or achievements\n"
                        "3. Match the user's vocabulary level, tone, and sentence structure\n"
                        "4. Focus on experiences and skills most relevant to this specific job\n"
                        "5. Keep the letter concise (300-400 words)\n"
                        "6. Use a professional but authentic tone"
                    )
                ),
                LLMMessage(
                    role="user",
                    content=prompt
                )
            ]
            
            # Call LLM
            logger.info(f"Generating cover letter for job: {job_title} at {job_company}")
            logger.debug(f"Using {len(top_experiences)} experiences, {len(top_projects)} projects, {len(top_skills)} skills")
            
            response = await self.llm.generate(
                messages=messages,
                model=self.GENERATION_MODEL,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Extract cover letter text
            cover_letter_text = self._extract_cover_letter_text(response.content)
            
            # Build result
            result = {
                "cover_letter_text": cover_letter_text,
                "generation_model_used": self.GENERATION_MODEL,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "tokens_used": response.tokens_used,
                "writing_style_applied": writing_style,
                "confidence": 0.88,  # High confidence for llama-3.3-70b
                "word_count": len(cover_letter_text.split())
            }
            
            logger.info(f"Cover letter generated: {result['word_count']} words, {response.tokens_used} tokens used")
            
            return result
        
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            raise LLMServiceError(f"Generation failed: {str(e)}")
    
    async def generate_resume_text(
        self,
        job_title: str,
        job_description: str,
        professional_summary: str,
        top_experiences: List[Dict[str, Any]],
        top_projects: List[Dict[str, Any]],
        top_skills: List[str],
        writing_style: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate tailored resume text (summary + bullet points).
        
        This is a lighter version focused on rewriting content
        to match job keywords without fabrication.
        
        Args:
            job_title: Target job title
            job_description: Full job description
            professional_summary: User's professional summary
            top_experiences: Top ranked experiences
            top_projects: Top ranked projects
            top_skills: Top ranked skills
            writing_style: Writing style config
            
        Returns:
            Tailored resume content with metadata
        """
        try:
            # Prepare variables
            variables = {
                "job_title": job_title,
                "job_description": job_description,
                "professional_summary": professional_summary,
                "top_experiences": top_experiences,
                "top_projects": top_projects,
                "top_skills": top_skills,
                "writing_style": writing_style
            }
            
            # Render prompt (we'd need a resume_generation template)
            # For now, use inline prompt
            prompt = self._build_resume_prompt(variables)
            
            messages = [
                LLMMessage(
                    role="system",
                    content=(
                        "You are an expert resume writer specializing in ATS optimization. "
                        "Rewrite resume content to highlight relevant experience and skills. "
                        "CRITICAL RULES:\n"
                        "1. ONLY use factual information from the provided profile\n"
                        "2. DO NOT fabricate skills, metrics, or achievements\n"
                        "3. Incorporate relevant keywords from job description naturally\n"
                        "4. Use strong action verbs and quantifiable results when available\n"
                        "5. Match the user's writing style and tone"
                    )
                ),
                LLMMessage(
                    role="user",
                    content=prompt
                )
            ]
            
            logger.info(f"Generating resume text for job: {job_title}")
            
            response = await self.llm.generate(
                messages=messages,
                model=self.GENERATION_MODEL,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS
            )
            
            # Parse response
            result = self._parse_resume_response(response.content)
            
            # Add metadata
            result["generation_model_used"] = self.GENERATION_MODEL
            result["generation_timestamp"] = datetime.utcnow().isoformat()
            result["tokens_used"] = response.tokens_used
            result["writing_style_applied"] = writing_style
            
            logger.info(f"Resume text generated: {response.tokens_used} tokens used")
            
            return result
        
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise LLMServiceError(f"Resume generation failed: {str(e)}")
    
    def _extract_cover_letter_text(self, response_text: str) -> str:
        """
        Extract clean cover letter text from LLM response.
        
        Removes markdown formatting, code blocks, etc.
        """
        text = response_text.strip()
        
        # Remove markdown code blocks
        if "```" in text:
            # Find content between code blocks
            parts = text.split("```")
            # Use the part that's not a language tag
            for i, part in enumerate(parts):
                if i % 2 == 1:  # Inside code block
                    continue
                if len(part.strip()) > 100:  # Likely the cover letter
                    text = part.strip()
                    break
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Here's the cover letter:",
            "Here is the cover letter:",
            "Cover Letter:",
            "COVER LETTER:",
        ]
        for prefix in prefixes_to_remove:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text
    
    def _build_resume_prompt(self, variables: Dict[str, Any]) -> str:
        """Build inline resume generation prompt."""
        return f"""
Generate a tailored resume for this job:

**Job Title:** {variables['job_title']}

**Job Description:**
{variables['job_description']}

**User Profile:**
Professional Summary: {variables['professional_summary']}

Top Experiences:
{json.dumps(variables['top_experiences'], indent=2)}

Top Projects:
{json.dumps(variables['top_projects'], indent=2)}

Top Skills:
{', '.join(variables['top_skills'])}

**Writing Style:**
- Vocabulary Level: {variables['writing_style'].get('vocabulary_level', 'professional')}
- Formality: {variables['writing_style'].get('formality_level', 'formal')}
- Tone: {variables['writing_style'].get('tone', 'professional')}

Generate a tailored professional summary and experience bullet points that incorporate relevant keywords from the job description while maintaining factual accuracy.

Return your response as JSON with this structure:
{{
  "tailored_summary": "...",
  "tailored_experiences": [
    {{
      "experience_id": "...",
      "tailored_description": "...",
      "tailored_bullet_points": ["...", "..."]
    }}
  ],
  "tailored_projects": [
    {{
      "project_id": "...",
      "tailored_description": "..."
    }}
  ]
}}
""".strip()
    
    def _parse_resume_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from resume generation."""
        # Extract JSON
        json_text = self._extract_json_from_text(response_text)
        
        # Parse
        data = json.loads(json_text)
        
        # Validate structure
        return {
            "tailored_summary": data.get("tailored_summary", ""),
            "tailored_experiences": data.get("tailored_experiences", []),
            "tailored_projects": data.get("tailored_projects", [])
        }
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from LLM response."""
        text = text.strip()
        
        # Remove markdown
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
        
        # Find JSON boundaries
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


# FastAPI dependency
def get_document_generation_service(
    llm_service: ILLMService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> DocumentGenerationService:
    """
    FastAPI dependency for DocumentGenerationService injection.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(
            service: DocumentGenerationService = Depends(get_document_generation_service),
            llm: ILLMService = Depends(get_llm_service),
            prompts: PromptService = Depends(get_prompt_service)
        ):
            ...
    """
    return DocumentGenerationService(
        llm_service=llm_service,
        prompt_service=prompt_service
    )
