"""Job Analyzer Stage - Stage 1 of the AI generation pipeline."""

import json
import logging
from typing import Dict, Any

from openai import AsyncOpenAI

from ..ai_orchestrator import PipelineStageInterface, PipelineStage, PipelineContext, StageError


logger = logging.getLogger(__name__)


class JobAnalyzerStage(PipelineStageInterface):
    """Stage 1: Analyze job posting to extract requirements and keywords."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    @property
    def stage(self) -> PipelineStage:
        return PipelineStage.ANALYZING_JOB

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Analyze the job posting to extract key requirements and insights."""
        try:
            # Extract job details
            job_analysis = await self._analyze_job_posting(context.job)

            # Update context metadata
            context.update_metadata('job_analysis', job_analysis)
            context.update_metadata('stage_1_completed', True)

            logger.info(f"Job analysis completed for job {context.job.id}")
            return context

        except Exception as e:
            logger.error(f"Job analysis failed: {str(e)}")
            raise StageError(self.stage, f"Failed to analyze job posting: {str(e)}", e)

    async def _analyze_job_posting(self, job) -> Dict[str, Any]:
        """Use AI to analyze the job posting and extract structured information."""
        prompt = f"""
        Analyze this job posting and extract key information in JSON format:

        Job Title: {job.title}
        Company: {job.company}
        Description: {job.description}
        Requirements: {', '.join(job.requirements)}

        Please provide a JSON response with the following structure:
        {{
            "key_responsibilities": ["list of 3-5 main responsibilities"],
            "required_skills": {{
                "technical": ["list of technical skills"],
                "soft": ["list of soft skills"]
            }},
            "experience_level": "entry|mid|senior|lead|executive",
            "industry_keywords": ["list of industry-specific keywords"],
            "ats_keywords": ["list of keywords likely used in ATS systems"],
            "job_type_analysis": "analysis of whether this is individual contributor, management, etc.",
            "cultural_indicators": ["list of cultural or company values mentioned"],
            "compensation_signals": "analysis of compensation hints or requirements",
            "urgency_level": "high|medium|low based on posting language",
            "competition_level": "high|medium|low based on requirements specificity"
        }}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert job market analyst. Analyze job postings and extract structured information that would be valuable for resume optimization and job matching."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            # Parse JSON response
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {content}")
                # Return a basic structure if JSON parsing fails
                return {
                    "key_responsibilities": ["Unable to parse responsibilities"],
                    "required_skills": {"technical": [], "soft": []},
                    "experience_level": "unknown",
                    "industry_keywords": job.extract_keywords()[:10],  # Fallback to basic extraction
                    "ats_keywords": job.extract_keywords()[:15],
                    "job_type_analysis": "unknown",
                    "cultural_indicators": [],
                    "compensation_signals": "unknown",
                    "urgency_level": "medium",
                    "competition_level": "medium",
                    "parsing_error": str(e)
                }

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Return fallback analysis
            return {
                "key_responsibilities": ["Analysis unavailable"],
                "required_skills": {
                    "technical": job.get_technical_requirements(),
                    "soft": job.get_soft_skills_requirements()
                },
                "experience_level": job.experience_level.value,
                "industry_keywords": job.extract_keywords()[:10],
                "ats_keywords": job.extract_keywords()[:15],
                "job_type_analysis": "unknown",
                "cultural_indicators": [],
                "compensation_signals": "unknown",
                "urgency_level": "medium",
                "competition_level": "medium",
                "error": str(e)
            }