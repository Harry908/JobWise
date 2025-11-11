"""Real Groq LLM adapter implementation."""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from groq import Groq
import json
import time
from datetime import datetime

from app.core.config import get_settings
from app.core.exceptions import LLMServiceError, LLMTimeoutError, LLMValidationError, RateLimitError

logger = logging.getLogger(__name__)
settings = get_settings()


class GroqAdapter:
    """Production Groq LLM adapter with error handling and rate limiting."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq adapter.
        
        Args:
            api_key: Groq API key (defaults to environment variable)
            model: Model name to use (default: llama-3.3-70b-versatile for best reasoning)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
        
        self.model = model
        self.client = Groq(api_key=self.api_key)
        
        # Rate limiting - now from settings
        self.requests_per_minute = settings.rate_limit_requests_per_minute  
        self.request_times: List[float] = []
        
        # Retry configuration - now from settings
        self.max_retries = settings.rate_limit_max_retries
        self.base_delay = float(settings.rate_limit_retry_delay)
        
        logger.info(f"GroqAdapter initialized with model: {self.model}")

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.3,  # Updated to match settings default
        max_tokens: int = 1024,
        timeout: float = 30.0,
        **kwargs
    ) -> str:
        """
        Generate text using Groq LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            **kwargs: Additional parameters
            
        Returns:
            Generated text
            
        Raises:
            LLMServiceError: LLM service error
            LLMTimeoutError: Request timeout
            RateLimitError: Rate limit exceeded
            LLMValidationError: Invalid parameters
        """
        try:
            # Validate parameters
            if not prompt or len(prompt.strip()) == 0:
                raise LLMValidationError("Prompt cannot be empty")
            
            if not 0.0 <= temperature <= 1.0:
                raise LLMValidationError("Temperature must be between 0.0 and 1.0")
            
            if max_tokens <= 0:
                raise LLMValidationError("max_tokens must be positive")
            
            # Check rate limits
            await self._check_rate_limit()
            
            # Prepare request
            request_start = time.time()
            
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Making Groq request (attempt {attempt + 1}/{self.max_retries})")
                    
                    # Make the request
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=1,
                        stream=False,
                        **kwargs
                    )
                    
                    # Track request timing
                    request_time = time.time() - request_start
                    self.request_times.append(time.time())
                    
                    # Extract response
                    if not response.choices:
                        raise LLMServiceError("No response choices returned from Groq")
                    
                    content = response.choices[0].message.content
                    if not content:
                        raise LLMServiceError("Empty content returned from Groq")
                    
                    # Log successful request
                    usage = response.usage
                    logger.info(f"Groq request successful: {request_time:.2f}s, "
                               f"tokens: {usage.prompt_tokens}+{usage.completion_tokens}={usage.total_tokens}")
                    
                    return content.strip()
                    
                except Exception as e:
                    if "rate_limit" in str(e).lower() or "429" in str(e):
                        if attempt == self.max_retries - 1:
                            raise RateLimitError(f"Rate limit exceeded after {self.max_retries} attempts")
                        
                        # Exponential backoff for rate limits
                        delay = self.base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, retrying in {delay}s")
                        await asyncio.sleep(delay)
                        continue
                    
                    if time.time() - request_start > timeout:
                        raise LLMTimeoutError(f"Request timeout after {timeout}s")
                    
                    if attempt == self.max_retries - 1:
                        raise LLMServiceError(f"Groq request failed: {str(e)}")
                    
                    # Wait before retry
                    delay = self.base_delay * (1.5 ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
            
        except (LLMServiceError, LLMTimeoutError, RateLimitError, LLMValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in GroqAdapter.generate: {e}")
            raise LLMServiceError(f"Unexpected error: {str(e)}")

    async def generate_structured(
        self,
        prompt: str,
        response_format: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response.
        
        Args:
            prompt: Input prompt
            response_format: Expected JSON schema
            temperature: Sampling temperature (low for consistency)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            LLMServiceError: Generation or parsing failed
        """
        try:
            # Enhance prompt for JSON output
            json_prompt = f"""{prompt}

Please respond with a valid JSON object that matches this schema:
{json.dumps(response_format, indent=2)}

Response (JSON only, no additional text):"""
            
            # Generate response
            response_text = await self.generate(
                prompt=json_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Extract and parse JSON
            json_response = self._extract_json_from_response(response_text)
            
            # Validate structure
            if not isinstance(json_response, dict):
                raise LLMServiceError("Response is not a JSON object")
            
            return json_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            raise LLMServiceError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise LLMServiceError(f"Structured generation failed: {str(e)}")

    async def extract_writing_style(self, cover_letter_text: str) -> Dict[str, Any]:
        """
        Extract writing style preferences from cover letter.
        
        Args:
            cover_letter_text: Cover letter content
            
        Returns:
            Writing style configuration
        """
        try:
            from app.domain.prompts.writing_style_prompts import WritingStylePrompts
            
            # Use the class method to get messages
            messages = WritingStylePrompts.get_extraction_messages(cover_letter_text)
            
            # Extract just the user prompt from messages
            user_message = next(msg for msg in messages if msg["role"] == "user")
            prompt = user_message["content"]
            
            response_format = {
                "writing_style": {
                    "vocabulary_level": "string",
                    "vocabulary_complexity_score": "number",
                    "tone": "string",
                    "formality_level": "number",
                    "sentence_structure": "string",
                    "avg_sentence_length": "string",
                    "active_voice_ratio": "number",
                    "first_person_frequency": "string",
                    "transition_style": "string",
                    "paragraph_length": "string",
                    "closing_style": "string"
                },
                "language_patterns": {
                    "action_verbs": "array of strings",
                    "technical_terms": "array of strings",
                    "connector_phrases": "array of strings",
                    "emphasis_words": "array of strings",
                    "qualification_language": "array of strings"
                },
                "content_approach": {
                    "storytelling_style": "string",
                    "evidence_style": "string",
                    "example_integration": "string",
                    "industry_language_usage": "string"
                }
            }
            
            result = await self.generate_structured(
                prompt=prompt,
                response_format=response_format,
                temperature=0.1,
                max_tokens=800
            )
            
            logger.info("Successfully extracted writing style preferences")
            return result
            
        except Exception as e:
            logger.error(f"Writing style extraction failed: {e}")
            raise LLMServiceError(f"Failed to extract writing style: {str(e)}")

    async def extract_layout_preferences(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract layout preferences from example resume.
        
        Args:
            resume_text: Resume content
            
        Returns:
            Layout configuration
        """
        try:
            from app.domain.prompts.structural_analysis_prompts import StructuralAnalysisPrompts
            
            # Use the class method to get messages
            messages = StructuralAnalysisPrompts.get_extraction_messages(resume_text)
            
            # Extract just the user prompt from messages
            user_message = next(msg for msg in messages if msg["role"] == "user")
            prompt = user_message["content"]
            
            response_format = {
                "layout_preferences": {
                    "section_order": "array of strings",
                    "header_style": "string",
                    "date_format": "string",
                    "location_display": "string",
                    "bullet_style": "string"
                },
                "content_density": {
                    "bullets_per_experience": {
                        "min": "number",
                        "max": "number", 
                        "preferred": "number"
                    },
                    "line_spacing": "string",
                    "section_spacing": "string",
                    "white_space_usage": "string"
                },
                "formatting_patterns": {
                    "emphasis_style": "string",
                    "title_formatting": "string",
                    "company_formatting": "string",
                    "skill_grouping": "string",
                    "contact_integration": "string"
                }
            }
            
            result = await self.generate_structured(
                prompt=prompt,
                response_format=response_format,
                temperature=0.1,
                max_tokens=1000
            )
            
            logger.info("Successfully extracted layout preferences")
            return result
            
        except Exception as e:
            logger.error(f"Layout extraction failed: {e}")
            raise LLMServiceError(f"Failed to extract layout preferences: {str(e)}")

    async def _check_rate_limit(self):
        """Check and enforce rate limits."""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (now - self.request_times[0])
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response text.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Parsed JSON object
        """
        # Try to find JSON in response
        text = response_text.strip()
        
        # Look for JSON block markers
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
        start_idx = -1
        end_idx = -1
        brace_count = 0
        
        for i, char in enumerate(text):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    end_idx = i + 1
                    break
        
        if start_idx != -1 and end_idx != -1:
            json_text = text[start_idx:end_idx]
        else:
            json_text = text
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            # Try to clean up common issues
            json_text = json_text.replace('\n', ' ').replace('\t', ' ')
            json_text = ' '.join(json_text.split())
            return json.loads(json_text)

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model": self.model,
            "provider": "Groq",
            "max_tokens": 32768 if "32768" in self.model else 8192,
            "rate_limit": f"{self.requests_per_minute}/minute",
            "supports_streaming": True,
            "supports_json": True
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        now = time.time()
        recent_requests = [t for t in self.request_times if now - t < 60]
        
        return {
            "requests_last_minute": len(recent_requests),
            "rate_limit": self.requests_per_minute,
            "remaining_requests": max(0, self.requests_per_minute - len(recent_requests)),
            "total_requests": len(self.request_times),
            "model": self.model
        }

    async def generate_resume_content(self, user_data: dict, job_analysis: dict, content_type: str = "resume") -> str:
        """
        Generate resume/cover letter content with enhanced anti-hallucination measures.
        
        Based on 2025 research showing that factual constraints and explicit verification
        reduce hallucination rates from 25%+ to under 10%.
        
        Args:
            user_data: User profile data (skills, experience, education)
            job_analysis: Analyzed job requirements
            content_type: Type of content to generate ("resume" or "cover_letter")
            
        Returns:
            Generated content with fact-checking applied
        """
        # Anti-hallucination prompt engineering based on research
        anti_hallucination_prefix = """CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. ONLY use information explicitly provided in the user data below
2. DO NOT invent, assume, or fabricate any details about the user's background
3. If information is missing, use phrases like "relevant experience" or "applicable skills" instead of inventing specifics
4. Verify each statement against the provided data before including it
5. Focus on truthful representation of actual qualifications
6. Do not add fictional companies, dates, or achievements

FACT-CHECK REQUIREMENT: Before finalizing, verify that every claim can be traced back to the provided user data.

"""
        
        # Construct factual prompt
        user_context = f"""USER PROFILE DATA (USE ONLY THIS INFORMATION):
Name: {user_data.get('full_name', 'User')}
Email: {user_data.get('email', '')}
Phone: {user_data.get('phone', '')}
Location: {user_data.get('location', '')}

SKILLS: {', '.join(user_data.get('skills', []))}

EXPERIENCE:
"""
        
        # Add work experience details
        for exp in user_data.get('work_experience', []):
            user_context += f"- {exp.get('title', 'Position')} at {exp.get('company', 'Company')} ({exp.get('start_date', 'Start')} - {exp.get('end_date', 'End')})\n"
            if exp.get('description'):
                user_context += f"  Description: {exp.get('description')}\n"
        
        # Add education
        user_context += f"\nEDUCATION:\n"
        for edu in user_data.get('education', []):
            user_context += f"- {edu.get('degree', 'Degree')} in {edu.get('field_of_study', 'Field')} from {edu.get('school', 'School')} ({edu.get('graduation_date', 'Year')})\n"
        
        # Add projects if available
        if user_data.get('projects'):
            user_context += f"\nPROJECTS:\n"
            for project in user_data.get('projects', []):
                user_context += f"- {project.get('name', 'Project')}: {project.get('description', 'Description')}\n"
        
        job_context = f"""
JOB REQUIREMENTS TO ADDRESS:
Position: {job_analysis.get('title', 'Target Position')}
Key Skills: {', '.join(job_analysis.get('required_skills', []))}
Experience Level: {job_analysis.get('experience_level', 'Not specified')}
"""
        
        if content_type == "resume":
            task_prompt = """
Generate a professional resume in ATS-friendly format. Structure should include:
1. Contact Information
2. Professional Summary (2-3 lines highlighting relevant experience)
3. Core Skills (only skills from user data that match job requirements)
4. Professional Experience (use actual job titles, companies, and dates provided)
5. Education
6. Projects (if applicable)

FORMAT: Use clear section headers, bullet points, and quantified achievements where possible.
CONSTRAINT: Every detail must come from the user data provided above.
"""
        else:  # cover_letter
            task_prompt = """
Generate a professional cover letter. Structure should include:
1. Header with contact information
2. Greeting to hiring manager
3. Opening paragraph stating interest and brief qualification summary
4. Body paragraph highlighting relevant experience and skills that match job requirements
5. Closing paragraph with call to action
6. Professional signature

TONE: Professional and enthusiastic but not overstated.
CONSTRAINT: Only reference actual experience, skills, and achievements from the user data.
"""
        
        final_prompt = anti_hallucination_prefix + user_context + job_context + task_prompt
        
        # Use low temperature for factual consistency
        return await self.generate(final_prompt, temperature=0.1, max_tokens=3000)