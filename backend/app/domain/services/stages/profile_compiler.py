"""Profile Compiler Stage - Stage 2 of the AI generation pipeline."""

import json
import logging
from typing import Dict, Any, List

from openai import AsyncOpenAI

from ..ai_orchestrator import PipelineStageInterface, PipelineStage, PipelineContext, StageError


logger = logging.getLogger(__name__)


class ProfileCompilerStage(PipelineStageInterface):
    """Stage 2: Compile and score user profile against job requirements."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    @property
    def stage(self) -> PipelineStage:
        return PipelineStage.COMPILING_PROFILE

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Compile user profile and score it against job requirements."""
        try:
            # Get job analysis from previous stage
            job_analysis = context.metadata.get('job_analysis', {})

            # Compile and score profile
            profile_compilation = await self._compile_profile(context.profile, job_analysis, context.job)

            # Update context metadata
            context.update_metadata('profile_compilation', profile_compilation)
            context.update_metadata('stage_2_completed', True)

            logger.info(f"Profile compilation completed for profile {context.profile.id}")
            return context

        except Exception as e:
            logger.error(f"Profile compilation failed: {str(e)}")
            raise StageError(self.stage, f"Failed to compile profile: {str(e)}", e)

    async def _compile_profile(self, profile, job_analysis: Dict[str, Any], job) -> Dict[str, Any]:
        """Compile profile data and score relevance to the job."""
        # Extract profile information
        profile_data = self._extract_profile_data(profile)

        prompt = f"""
        Analyze this user profile against the job requirements and provide a detailed scoring and compilation in JSON format:

        JOB ANALYSIS:
        {json.dumps(job_analysis, indent=2)}

        USER PROFILE:
        {json.dumps(profile_data, indent=2)}

        Please provide a JSON response with the following structure:
        {{
            "overall_match_score": 0.0-1.0,
            "skill_match_scores": {{
                "technical_match": 0.0-1.0,
                "soft_skills_match": 0.0-1.0,
                "experience_match": 0.0-1.0
            }},
            "key_strengths": ["list of 3-5 main strengths for this job"],
            "skill_gaps": ["list of skills that should be highlighted or acquired"],
            "experience_relevance": ["list of most relevant experiences"],
            "recommended_focus_areas": ["sections to emphasize in resume/cover letter"],
            "keyword_alignment_score": 0.0-1.0,
            "experience_level_alignment": "overqualified|well-matched|underqualified",
            "cultural_fit_indicators": ["aspects that align with job culture"],
            "tailoring_recommendations": {{
                "resume_highlights": ["specific achievements to emphasize"],
                "cover_letter_angles": ["key points to address"],
                "additional_skills_to_mention": ["skills not in profile but relevant"]
            }},
            "ats_optimization_score": 0.0-1.0,
            "confidence_level": 0.0-1.0
        }}
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career counselor and resume optimization specialist. Analyze candidate profiles against job requirements and provide detailed scoring and recommendations for resume tailoring."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            # Parse JSON response
            try:
                compilation = json.loads(content)
                return compilation
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {content}")
                return self._create_fallback_compilation(profile_data, job_analysis)

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return self._create_fallback_compilation(profile_data, job_analysis)

    def _extract_profile_data(self, profile) -> Dict[str, Any]:
        """Extract relevant profile data for analysis."""
        return {
            "personal_info": {
                "name": profile.personal_info.full_name,
                "location": profile.personal_info.location,
                "years_experience": profile.calculate_years_experience()
            },
            "professional_summary": profile.professional_summary,
            "experiences": [
                {
                    "title": exp.title,
                    "company": exp.company,
                    "duration": f"{exp.start_date.year}-{exp.end_date.year if exp.end_date else 'Present'}",
                    "description": exp.description,
                    "achievements": exp.achievements
                }
                for exp in profile.experiences
            ],
            "education": [
                {
                    "degree": edu.degree,
                    "field": edu.field_of_study,
                    "institution": edu.institution,
                    "gpa": edu.gpa
                }
                for edu in profile.education
            ],
            "skills": {
                "technical": profile.get_technical_skills(),
                "soft": profile.skills.get_all_soft_skills(),
                "certifications": [cert.name for cert in profile.skills.get_all_certifications()]
            },
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies
                }
                for proj in profile.projects
            ]
        }

    def _create_fallback_compilation(self, profile_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic compilation when AI analysis fails."""
        return {
            "overall_match_score": 0.5,
            "skill_match_scores": {
                "technical_match": 0.5,
                "soft_skills_match": 0.5,
                "experience_match": 0.5
            },
            "key_strengths": ["Experience in the field", "Technical skills"],
            "skill_gaps": ["Job-specific technologies"],
            "experience_relevance": [exp["title"] for exp in profile_data["experiences"][:2]],
            "recommended_focus_areas": ["Technical skills", "Relevant experience"],
            "keyword_alignment_score": 0.5,
            "experience_level_alignment": "well-matched",
            "cultural_fit_indicators": ["Professional experience"],
            "tailoring_recommendations": {
                "resume_highlights": ["Key achievements"],
                "cover_letter_angles": ["Career goals"],
                "additional_skills_to_mention": []
            },
            "ats_optimization_score": 0.5,
            "confidence_level": 0.3,
            "fallback_reason": "AI analysis unavailable"
        }