"""Document Generator Stage - Stage 3 of the AI generation pipeline."""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from openai import AsyncOpenAI

from ..ai_orchestrator import PipelineStageInterface, PipelineStage, PipelineContext, StageError
from ...entities.generation import GenerationResult, DocumentType


logger = logging.getLogger(__name__)


class DocumentGeneratorStage(PipelineStageInterface):
    """Stage 3: Generate tailored resume and cover letter documents."""

    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    @property
    def stage(self) -> PipelineStage:
        return PipelineStage.GENERATING_DOCUMENTS

    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Generate tailored resume and cover letter."""
        try:
            # Get analysis data from previous stages
            job_analysis = context.metadata.get('job_analysis', {})
            profile_compilation = context.metadata.get('profile_compilation', {})

            # Generate documents
            documents = await self._generate_documents(
                context.profile,
                context.job,
                job_analysis,
                profile_compilation
            )

            # Add results to generation
            for doc_result in documents:
                context.generation.add_result(doc_result)

            # Update context metadata
            context.update_metadata('generated_documents', len(documents))
            context.update_metadata('stage_3_completed', True)

            logger.info(f"Document generation completed for generation {context.generation.id}")
            return context

        except Exception as e:
            logger.error(f"Document generation failed: {str(e)}")
            raise StageError(self.stage, f"Failed to generate documents: {str(e)}", e)

    async def _generate_documents(
        self,
        profile,
        job,
        job_analysis: Dict[str, Any],
        profile_compilation: Dict[str, Any]
    ) -> List[GenerationResult]:
        """Generate resume and cover letter using AI."""
        documents = []

        # Generate resume
        resume_result = await self._generate_resume(profile, job, job_analysis, profile_compilation)
        documents.append(resume_result)

        # Generate cover letter
        cover_letter_result = await self._generate_cover_letter(profile, job, job_analysis, profile_compilation)
        documents.append(cover_letter_result)

        return documents

    async def _generate_resume(
        self,
        profile,
        job,
        job_analysis: Dict[str, Any],
        profile_compilation: Dict[str, Any]
    ) -> GenerationResult:
        """Generate a tailored resume."""
        profile_data = self._extract_profile_data(profile)

        prompt = f"""
        Create a professional resume tailored for this job application. Use the analysis data to optimize content and keywords.

        JOB DETAILS:
        Title: {job.title}
        Company: {job.company}
        Description: {job.description}

        JOB ANALYSIS:
        {json.dumps(job_analysis, indent=2)}

        PROFILE COMPILATION:
        {json.dumps(profile_compilation, indent=2)}

        CANDIDATE PROFILE:
        {json.dumps(profile_data, indent=2)}

        REQUIREMENTS:
        1. Optimize for ATS systems using keywords from job analysis
        2. Highlight relevant experience and skills based on compilation recommendations
        3. Keep resume to 1-2 pages (approximately 800-1200 words)
        4. Use professional formatting with clear sections
        5. Quantify achievements where possible
        6. Tailor professional summary to the specific job
        7. Focus on accomplishments that match job requirements

        Generate the resume content in a clean, professional format.
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer and career counselor. Create highly effective, ATS-optimized resumes that highlight relevant experience and skills for specific job applications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            # Calculate basic metrics
            word_count = len(content.split())
            ats_score = self._estimate_ats_score(content, job_analysis)

            return GenerationResult(
                document_type=DocumentType.RESUME,
                content=content,
                ats_score=ats_score,
                word_count=word_count,
                generated_at=datetime.utcnow(),
                metadata={
                    'model': 'gpt-4o',
                    'temperature': 0.3,
                    'optimization_focus': 'ATS and relevance'
                }
            )

        except Exception as e:
            logger.error(f"Resume generation failed: {str(e)}")
            # Return basic resume structure
            basic_resume = self._create_basic_resume(profile, job)
            return GenerationResult(
                document_type=DocumentType.RESUME,
                content=basic_resume,
                ats_score=0.3,
                word_count=len(basic_resume.split()),
                generated_at=datetime.utcnow(),
                metadata={'error': str(e), 'fallback': True}
            )

    async def _generate_cover_letter(
        self,
        profile,
        job,
        job_analysis: Dict[str, Any],
        profile_compilation: Dict[str, Any]
    ) -> GenerationResult:
        """Generate a tailored cover letter."""
        profile_data = self._extract_profile_data(profile)

        prompt = f"""
        Create a compelling cover letter tailored for this job application.

        JOB DETAILS:
        Title: {job.title}
        Company: {job.company}
        Description: {job.description}

        JOB ANALYSIS:
        {json.dumps(job_analysis, indent=2)}

        PROFILE COMPILATION:
        {json.dumps(profile_compilation, indent=2)}

        CANDIDATE PROFILE:
        {json.dumps(profile_data, indent=2)}

        REQUIREMENTS:
        1. Address the hiring manager by name if possible (use "Hiring Manager" if not known)
        2. Keep to 3-4 paragraphs (300-500 words)
        3. Show knowledge of the company and role
        4. Highlight relevant achievements and skills
        5. Explain why you're interested in this specific role/company
        6. Include a call to action
        7. Use professional, enthusiastic tone

        Focus on the tailoring recommendations from the profile compilation.
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cover letter writer. Create personalized, compelling cover letters that address specific job requirements and showcase candidate fit."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=1000,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            word_count = len(content.split())

            return GenerationResult(
                document_type=DocumentType.COVER_LETTER,
                content=content,
                ats_score=None,  # Cover letters aren't typically ATS-scored
                word_count=word_count,
                generated_at=datetime.utcnow(),
                metadata={
                    'model': 'gpt-4o',
                    'temperature': 0.4,
                    'focus': 'personalization and fit'
                }
            )

        except Exception as e:
            logger.error(f"Cover letter generation failed: {str(e)}")
            basic_cover_letter = self._create_basic_cover_letter(profile, job)
            return GenerationResult(
                document_type=DocumentType.COVER_LETTER,
                content=basic_cover_letter,
                ats_score=None,
                word_count=len(basic_cover_letter.split()),
                generated_at=datetime.utcnow(),
                metadata={'error': str(e), 'fallback': True}
            )

    def _extract_profile_data(self, profile) -> Dict[str, Any]:
        """Extract profile data for document generation."""
        return {
            "name": profile.personal_info.full_name,
            "summary": profile.professional_summary,
            "contact": {
                "email": profile.personal_info.email,
                "phone": profile.personal_info.phone,
                "location": profile.personal_info.location,
                "linkedin": profile.personal_info.linkedin
            },
            "experience": [
                {
                    "title": exp.title,
                    "company": exp.company,
                    "location": exp.location,
                    "dates": f"{exp.start_date.strftime('%B %Y')} - {'Present' if exp.is_current else exp.end_date.strftime('%B %Y')}",
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
                    "dates": f"{edu.start_date.strftime('%B %Y')} - {edu.end_date.strftime('%B %Y') if edu.end_date else 'Present'}",
                    "gpa": f"GPA: {edu.gpa}" if edu.gpa else None
                }
                for edu in profile.education
            ],
            "skills": profile.get_technical_skills() + profile.skills.get_all_soft_skills(),
            "certifications": [cert.name for cert in profile.skills.get_all_certifications()]
        }

    def _estimate_ats_score(self, content: str, job_analysis: Dict[str, Any]) -> float:
        """Estimate ATS compatibility score."""
        ats_keywords = set(job_analysis.get('ats_keywords', []))
        content_words = set(content.lower().split())

        matched_keywords = ats_keywords.intersection(content_words)
        score = len(matched_keywords) / len(ats_keywords) if ats_keywords else 0.5

        return min(1.0, score)

    def _create_basic_resume(self, profile, job) -> str:
        """Create a basic resume structure when AI generation fails."""
        return f"""
{profile.personal_info.full_name}
{profile.personal_info.email} | {profile.personal_info.phone or 'N/A'}
{profile.personal_info.location or 'N/A'}

PROFESSIONAL SUMMARY
{profile.professional_summary or 'Experienced professional seeking opportunities in ' + job.title}

EXPERIENCE
{chr(10).join([f'{exp.title} at {exp.company} ({exp.start_date.year}-{"Present" if exp.is_current else exp.end_date.year})' for exp in profile.experiences])}

EDUCATION
{chr(10).join([f'{edu.degree} in {edu.field_of_study}, {edu.institution}' for edu in profile.education])}

SKILLS
{', '.join(profile.get_technical_skills())}
"""

    def _create_basic_cover_letter(self, profile, job) -> str:
        """Create a basic cover letter when AI generation fails."""
        return f"""
Dear Hiring Manager,

I am writing to express my interest in the {job.title} position at {job.company}. With my background in {', '.join(profile.get_technical_skills()[:3])}, I am excited about the opportunity to contribute to your team.

{profile.professional_summary or 'I bring valuable experience and skills to this role.'}

I would welcome the opportunity to discuss how my experience aligns with {job.company}'s needs.

Best regards,
{profile.personal_info.full_name}
"""