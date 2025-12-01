"""Generation service for resumes and cover letters."""

from uuid import UUID, uuid4
from typing import Optional, List
import logging

from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.generation_repository import GenerationRepository
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.infrastructure.repositories.job_repository import JobRepository
from app.application.services.ranking_service import RankingService
from app.application.services.style_extraction_service import StyleExtractionService
from app.domain.entities.generation import Generation
from app.domain.enums.document_type import DocumentType
from app.domain.enums.generation_status import GenerationStatus

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating resumes and cover letters."""
    
    def __init__(
        self,
        llm_adapter: GroqAdapter,
        generation_repo: GenerationRepository,
        profile_repo: ProfileRepository,
        job_repo: JobRepository,
        ranking_service: RankingService,
        style_service: StyleExtractionService
    ):
        self.llm = llm_adapter
        self.generation_repo = generation_repo
        self.profile_repo = profile_repo
        self.job_repo = job_repo
        self.ranking_service = ranking_service
        self.style_service = style_service
    
    async def generate_resume(
        self,
        user_id: int,
        job_id: UUID,
        max_experiences: int = 5,
        max_projects: int = 3,
        include_summary: bool = True,
        custom_prompt: Optional[str] = None
    ) -> Generation:
        """Generate resume for a specific job (no LLM, fast compilation)."""
        # Get or create ranking
        ranking = await self.ranking_service.get_ranking_for_job(user_id, job_id)
        if not ranking:
            ranking = await self.ranking_service.create_ranking(user_id, job_id)
        
        # Get profile
        profile = await self.profile_repo.get_active_by_user_id(user_id)
        if not profile:
            raise ValueError("No profile found")
        
        # Get job for reference
        job = await self.job_repo.get_by_id(str(job_id))
        
        # Get ranked experiences
        experiences = await self.profile_repo.get_experiences_by_profile_id(profile.id)
        exp_dict = {exp.id: exp for exp in experiences}
        ranked_exps = [
            exp_dict[exp_id] 
            for exp_id in ranking.ranked_experience_ids[:max_experiences]
            if exp_id in exp_dict
        ]
        
        # Get ranked projects
        proj_dict = {proj.id: proj for proj in profile.projects}
        ranked_projs = [
            proj_dict[proj_id]
            for proj_id in ranking.ranked_project_ids[:max_projects]
            if proj_id in proj_dict
        ]
        
        # Build resume text (pure logic, no LLM)
        resume_parts = []
        
        # Header
        resume_parts.append(f"{profile.personal_info.full_name}")
        resume_parts.append(f"{profile.personal_info.location or ''} | {profile.personal_info.email}")
        if profile.personal_info.phone:
            resume_parts[-1] += f" | {profile.personal_info.phone}"
        resume_parts.append("")
        
        # Professional Summary
        if include_summary and profile.professional_summary:
            resume_parts.append("PROFESSIONAL SUMMARY")
            resume_parts.append(profile.professional_summary)
            resume_parts.append("")
        
        # Technical Skills
        if profile.skills and profile.skills.technical:
            resume_parts.append("TECHNICAL SKILLS")
            resume_parts.append(", ".join(profile.skills.technical[:20]))
            resume_parts.append("")
        
        # Professional Experience
        if ranked_exps:
            resume_parts.append("PROFESSIONAL EXPERIENCE")
            resume_parts.append("")
            for exp in ranked_exps:
                resume_parts.append(f"{exp.title} | {exp.company} | {exp.location or ''}")
                resume_parts.append(f"{exp.start_date} - {exp.end_date or 'Present'}")
                # Use enhanced description if available, fallback to original
                description = exp.enhanced_description or exp.description
                if exp.enhanced_description:
                    logger.info(f"Using ENHANCED description for experience: {exp.title} at {exp.company}")
                    logger.debug(f"Enhanced description length: {len(exp.enhanced_description)} chars")
                elif exp.description:
                    logger.info(f"Using ORIGINAL description for experience: {exp.title} at {exp.company}")
                else:
                    logger.warning(f"No description available for experience: {exp.title} at {exp.company}")
                if description:
                    resume_parts.append(description)
                if exp.achievements:
                    for achievement in exp.achievements:
                        resume_parts.append(f"• {achievement}")
                resume_parts.append("")
        
        # Projects
        if ranked_projs:
            resume_parts.append("PROJECTS")
            resume_parts.append("")
            for proj in ranked_projs:
                resume_parts.append(f"{proj.name}")
                # Use enhanced description if available, fallback to original
                description = proj.enhanced_description or proj.description
                if proj.enhanced_description:
                    logger.info(f"Using ENHANCED description for project: {proj.name}")
                    logger.debug(f"Enhanced description length: {len(proj.enhanced_description)} chars")
                elif proj.description:
                    logger.info(f"Using ORIGINAL description for project: {proj.name}")
                else:
                    logger.warning(f"No description available for project: {proj.name}")
                if description:
                    resume_parts.append(description)
                if proj.technologies:
                    resume_parts.append(f"Technologies: {', '.join(proj.technologies)}")
                if proj.url:
                    resume_parts.append(f"URL: {proj.url}")
                resume_parts.append("")
        
        # Education
        if profile.education:
            resume_parts.append("EDUCATION")
            resume_parts.append("")
            for edu in profile.education[:2]:  # Top 2
                resume_parts.append(f"{edu.degree} in {edu.field_of_study}")
                resume_parts.append(f"{edu.institution} | {edu.start_date} - {edu.end_date}")
                if edu.gpa:
                    resume_parts.append(f"GPA: {edu.gpa}")
                resume_parts.append("")
        
        resume_text = "\n".join(resume_parts)
        
        # Calculate simple ATS score (keyword matching)
        ats_score = self._calculate_ats_score(resume_text, job)
        
        # Create generation entity
        generation = Generation(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            ranking_id=ranking.id,
            document_type=DocumentType.RESUME,
            content_text=resume_text,
            status=GenerationStatus.COMPLETED,
            ats_score=ats_score,
            ats_feedback=f"Resume contains {len(ranked_exps)} experiences and {len(ranked_projs)} projects.",
            llm_metadata='{"note": "Pure logic compilation, no LLM used"}'
        )
        
        # Save generation
        await self.generation_repo.create(generation)
        
        return generation
    
    async def generate_cover_letter(
        self,
        user_id: int,
        job_id: UUID,
        company_name: Optional[str] = None,
        hiring_manager_name: Optional[str] = None,
        max_paragraphs: int = 4,
        custom_prompt: Optional[str] = None
    ) -> Generation:
        """Generate cover letter for a specific job (LLM-powered)."""
        # Get or create ranking
        ranking = await self.ranking_service.get_ranking_for_job(user_id, job_id)
        if not ranking:
            ranking = await self.ranking_service.create_ranking(user_id, job_id)
        
        # Get profile
        profile = await self.profile_repo.get_active_by_user_id(user_id)
        if not profile:
            raise ValueError("No profile found")
        
        # Get job
        job = await self.job_repo.get_by_id(str(job_id))
        if not job:
            raise ValueError("Job not found")
        
        # Get writing style
        style = await self.style_service.get_user_style(user_id)
        
        # Get ranked experiences and projects
        experiences = await self.profile_repo.get_experiences_by_profile_id(profile.id)
        exp_dict = {exp.id: exp for exp in experiences}
        ranked_exps = [
            {
                "title": exp_dict[exp_id].title,
                "company": exp_dict[exp_id].company,
                "description": exp_dict[exp_id].description or ""
            }
            for exp_id in ranking.ranked_experience_ids[:3]
            if exp_id in exp_dict
        ]
        
        proj_dict = {proj.id: proj for proj in profile.projects}
        ranked_projs = [
            {
                "name": proj_dict[proj_id].name,
                "description": proj_dict[proj_id].description or "",
                "technologies": proj_dict[proj_id].technologies or []
            }
            for proj_id in ranking.ranked_project_ids[:2]
            if proj_id in proj_dict
        ]
        
        # Prepare profile data for LLM
        profile_data = {
            "full_name": profile.personal_info.full_name,
            "professional_summary": profile.professional_summary or "",
            "experiences": ranked_exps,
            "projects": ranked_projs
        }
        
        # Generate cover letter using LLM
        job_description = job.description or f"{job.title} at {job.company}"
        cover_letter_text = await self.llm.generate_cover_letter(
            job_description=job_description,
            profile_data=profile_data,
            writing_style=style,
            company_name=company_name or job.company,
            hiring_manager=hiring_manager_name,
            max_paragraphs=max_paragraphs
        )
        
        # Calculate ATS score
        ats_score = self._calculate_ats_score(cover_letter_text, job)
        
        # Create generation entity
        generation = Generation(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            ranking_id=ranking.id,
            document_type=DocumentType.COVER_LETTER,
            content_text=cover_letter_text,
            status=GenerationStatus.COMPLETED,
            ats_score=ats_score,
            ats_feedback=f"Cover letter generated with {len(cover_letter_text.split())} words.",
            llm_metadata='{"model": "llama-3.3-70b-versatile"}'
        )
        
        # Save generation
        await self.generation_repo.create(generation)
        
        return generation
    
    async def get_generation_history(
        self,
        user_id: int,
        document_type: Optional[DocumentType] = None,
        job_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Generation]:
        """Get generation history for user."""
        return await self.generation_repo.list_by_user(
            user_id=user_id,
            document_type=document_type,
            job_id=job_id,
            limit=limit,
            offset=offset
        )
    
    def _calculate_ats_score(self, text: str, job) -> float:
        """Calculate simple ATS score based on keyword matching."""
        if not job or not job.parsed_keywords:
            return 75.0  # Default score
        
        text_lower = text.lower()
        matched_keywords = sum(1 for keyword in job.parsed_keywords if keyword.lower() in text_lower)
        total_keywords = len(job.parsed_keywords)
        
        if total_keywords == 0:
            return 75.0
        
        score = (matched_keywords / total_keywords) * 100
        return min(max(score, 50.0), 95.0)  # Clamp between 50-95
