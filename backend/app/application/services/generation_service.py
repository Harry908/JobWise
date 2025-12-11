"""Generation service for resumes and cover letters."""

from uuid import UUID, uuid4
from typing import Optional, List, Dict
from datetime import datetime
import logging
import json

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
        exp_dict = {str(exp.id): exp for exp in experiences}  # Direct UUID matching
        
        # Debug logging
        logger.info(f"Total experiences available: {len(experiences)}")
        logger.info(f"Experience UUIDs in profile: {[str(exp.id) for exp in experiences]}")
        logger.info(f"Ranked experience UUIDs from ranking: {ranking.ranked_experience_ids[:max_experiences]}")
        
        # Match experiences with UUIDs (no normalization needed with integer mapping)
        ranked_exps = []
        for exp_uuid in ranking.ranked_experience_ids[:max_experiences]:
            if exp_uuid in exp_dict:
                ranked_exps.append(exp_dict[exp_uuid])
            else:
                logger.warning(f"Could not find experience with UUID: {exp_uuid}")
        
        # Fallback: if no ranked experiences matched, use all experiences in original order
        if not ranked_exps and experiences:
            logger.warning("No ranked experiences matched! Using all experiences in original order as fallback")
            ranked_exps = experiences[:max_experiences]
        
        logger.info(f"Successfully matched {len(ranked_exps)} out of {min(max_experiences, len(ranking.ranked_experience_ids))} ranked experiences")
        if len(ranked_exps) < min(max_experiences, len(ranking.ranked_experience_ids)):
            missing_ids = [exp_id for exp_id in ranking.ranked_experience_ids[:max_experiences] if exp_id not in exp_dict]
            logger.warning(f"Missing experience UUIDs: {missing_ids}")
        
        # Get ranked projects
        proj_dict = {str(proj.id): proj for proj in profile.projects}  # Direct UUID matching
        
        # Debug logging
        logger.info(f"Total projects available: {len(profile.projects)}")
        logger.info(f"Project UUIDs in profile: {[str(proj.id) for proj in profile.projects]}")
        logger.info(f"Ranked project UUIDs from ranking: {ranking.ranked_project_ids[:max_projects]}")
        
        # Match projects with UUIDs (no normalization needed with integer mapping)
        ranked_projs = []
        for proj_uuid in ranking.ranked_project_ids[:max_projects]:
            if proj_uuid in proj_dict:
                ranked_projs.append(proj_dict[proj_uuid])
            else:
                logger.warning(f"Could not find project with UUID: {proj_uuid})")
        
        # Fallback: if no ranked projects matched, use all projects in original order
        if not ranked_projs and profile.projects:
            logger.warning("No ranked projects matched! Using all projects in original order as fallback")
            ranked_projs = profile.projects[:max_projects]
        
        logger.info(f"Successfully matched {len(ranked_projs)} out of {min(max_projects, len(ranking.ranked_project_ids))} ranked projects")
        if len(ranked_projs) < min(max_projects, len(ranking.ranked_project_ids)):
            missing_ids = [proj_id for proj_id in ranking.ranked_project_ids[:max_projects] if proj_id not in proj_dict]
            logger.warning(f"Missing project UUIDs: {missing_ids}")
        
        # Build resume text (pure logic, no LLM)
        resume_parts = []
        
        # Header
        resume_parts.append(f"{profile.personal_info.full_name}")
        resume_parts.append(f"{profile.personal_info.location or ''} | {profile.personal_info.email}")
        if profile.personal_info.phone:
            resume_parts[-1] += f" | {profile.personal_info.phone}"
        resume_parts.append("")
        
        # Professional Summary
        if include_summary:
            # Use enhanced summary if available and not empty, otherwise use original
            summary = None
            if profile.enhanced_professional_summary and profile.enhanced_professional_summary.strip():
                summary = profile.enhanced_professional_summary
                logger.info("Using ENHANCED professional summary")
            elif profile.professional_summary and profile.professional_summary.strip():
                summary = profile.professional_summary
                logger.info("Using ORIGINAL professional summary")
            
            if summary:
                resume_parts.append("PROFESSIONAL SUMMARY")
                resume_parts.append(summary)
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
                # Use enhanced description if available and not empty, fallback to original
                description = None
                if exp.enhanced_description and exp.enhanced_description.strip():
                    description = exp.enhanced_description
                    logger.info(f"Using ENHANCED description for experience: {exp.title} at {exp.company}")
                    logger.debug(f"Enhanced description length: {len(exp.enhanced_description)} chars")
                elif exp.description and exp.description.strip():
                    description = exp.description
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
                # Use enhanced description if available and not empty, fallback to original
                description = None
                if proj.enhanced_description and proj.enhanced_description.strip():
                    description = proj.enhanced_description
                    logger.info(f"Using ENHANCED description for project: {proj.name}")
                    logger.debug(f"Enhanced description length: {len(proj.enhanced_description)} chars")
                elif proj.description and proj.description.strip():
                    description = proj.description
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
        
        # Build structured content for export templates
        content_structured = self._build_structured_resume(
            profile=profile,
            ranked_exps=ranked_exps,
            ranked_projs=ranked_projs,
            summary=summary if include_summary else None
        )
        
        # Calculate ATS score using LLM
        ats_result = await self._calculate_ats_score(resume_text, job)
        
        # Create generation entity
        generation = Generation(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            ranking_id=ranking.id,
            document_type=DocumentType.RESUME,
            content_text=resume_text,
            content_structured=json.dumps(content_structured),
            status=GenerationStatus.COMPLETED,
            ats_score=ats_result["score"],
            ats_feedback=ats_result.get("analysis", ""),
            llm_metadata=str(ats_result.get("llm_metadata", {}))
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
        
        # Get ranked experiences and projects with UUID matching
        experiences = await self.profile_repo.get_experiences_by_profile_id(profile.id)
        exp_dict = {str(exp.id): exp for exp in experiences}  # Direct UUID matching
        
        ranked_exps = []
        for exp_uuid in ranking.ranked_experience_ids[:3]:
            if exp_uuid in exp_dict:
                exp = exp_dict[exp_uuid]
                ranked_exps.append({
                    "title": exp.title,
                    "company": exp.company,
                    # Use enhanced description if available and not empty, otherwise use original
                    "description": (
                        exp.enhanced_description 
                        if exp.enhanced_description and exp.enhanced_description.strip()
                        else exp.description or ""
                    )
                })
        
        # Fallback: if no experiences matched, use all experiences
        if not ranked_exps and experiences:
            logger.warning("No experiences matched for cover letter! Using first 3 experiences as fallback")
            for exp in experiences[:3]:
                ranked_exps.append({
                    "title": exp.title,
                    "company": exp.company,
                    "description": (
                        exp.enhanced_description 
                        if exp.enhanced_description and exp.enhanced_description.strip()
                        else exp.description or ""
                    )
                })
        
        proj_dict = {str(proj.id): proj for proj in profile.projects}  # Direct UUID matching
        
        ranked_projs = []
        for proj_uuid in ranking.ranked_project_ids[:2]:
            if proj_uuid in proj_dict:
                proj = proj_dict[proj_uuid]
                ranked_projs.append({
                    "name": proj.name,
                    # Use enhanced description if available and not empty, otherwise use original
                    "description": (
                        proj.enhanced_description
                        if proj.enhanced_description and proj.enhanced_description.strip()
                        else proj.description or ""
                    ),
                    "technologies": proj.technologies or []
                })
        
        # Fallback: if no projects matched, use all projects
        if not ranked_projs and profile.projects:
            logger.warning("No projects matched for cover letter! Using first 2 projects as fallback")
            for proj in profile.projects[:2]:
                ranked_projs.append({
                    "name": proj.name,
                    "description": (
                        proj.enhanced_description
                        if proj.enhanced_description and proj.enhanced_description.strip()
                        else proj.description or ""
                    ),
                    "technologies": proj.technologies or []
                })
        
        # Prepare profile data for LLM
        # Use enhanced summary if available and not empty, otherwise use original
        summary = (
            profile.enhanced_professional_summary
            if profile.enhanced_professional_summary and profile.enhanced_professional_summary.strip()
            else profile.professional_summary or ""
        )
        
        profile_data = {
            "full_name": profile.personal_info.full_name,
            "professional_summary": summary,
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
        
        # Build structured content for export templates
        content_structured = self._build_structured_cover_letter(
            profile=profile,
            cover_letter_text=cover_letter_text,
            company_name=company_name or job.company,
            job_title=job.title
        )
        
        # Calculate ATS score using LLM
        ats_result = await self._calculate_ats_score(cover_letter_text, job)
        
        # Create generation entity
        generation = Generation(
            id=uuid4(),
            user_id=user_id,
            job_id=job_id,
            ranking_id=ranking.id,
            document_type=DocumentType.COVER_LETTER,
            content_text=cover_letter_text,
            content_structured=json.dumps(content_structured),
            status=GenerationStatus.COMPLETED,
            ats_score=ats_result["score"],
            ats_feedback=ats_result.get("analysis", ""),
            llm_metadata=str(ats_result.get("llm_metadata", {}))
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
    
    def _build_structured_resume(self, profile, ranked_exps, ranked_projs, summary) -> Dict:
        """Build structured JSON content for resume export templates."""
        # Calculate total years of experience
        total_years = 0
        if ranked_exps:
            for exp in ranked_exps:
                try:
                    start = datetime.fromisoformat(exp.start_date)
                    end = datetime.fromisoformat(exp.end_date) if exp.end_date else datetime.now()
                    total_years += (end - start).days / 365.25
                except (ValueError, AttributeError):
                    pass
        
        # Build header with ALL personal info fields
        header = {
            "name": profile.personal_info.full_name,
            "title": ranked_exps[0].title if ranked_exps else "Professional",
            "email": profile.personal_info.email,
            "phone": profile.personal_info.phone or "",
            "location": profile.personal_info.location or "",
            "linkedin": profile.personal_info.linkedin or "",
            "github": profile.personal_info.github or "",
            "website": profile.personal_info.website or ""
        }
        
        # Build sections
        sections = []
        
        # Professional Summary
        if summary:
            sections.append({
                "type": "professional_summary",
                "content": summary
            })
        
        # Skills section with ALL categories
        skills_categories = []
        
        # Technical skills
        if profile.skills and profile.skills.technical:
            skills_categories.append({
                "name": "Technical Skills",
                "items": profile.skills.technical
            })
        
        # Soft skills
        if profile.skills and profile.skills.soft:
            skills_categories.append({
                "name": "Soft Skills",
                "items": profile.skills.soft
            })
        
        # Languages
        if profile.skills and profile.skills.languages:
            skills_categories.append({
                "name": "Languages",
                "items": [
                    {
                        "name": lang.name,
                        "proficiency": lang.proficiency
                    }
                    for lang in profile.skills.languages
                ]
            })
        
        # Certifications
        if profile.skills and profile.skills.certifications:
            skills_categories.append({
                "name": "Certifications",
                "items": [
                    {
                        "name": cert.name,
                        "issuer": cert.issuer,
                        "date_obtained": cert.date_obtained,
                        "expiry_date": cert.expiry_date or "",
                        "credential_id": cert.credential_id or ""
                    }
                    for cert in profile.skills.certifications
                ]
            })
        
        if skills_categories:
            sections.append({
                "type": "skills",
                "categories": skills_categories
            })
        
        # Experience section with ALL fields
        if ranked_exps:
            sections.append({
                "type": "experience",
                "entries": [
                    {
                        "id": str(exp.id),
                        "title": exp.title,
                        "company": exp.company,
                        "location": exp.location or "",
                        "start_date": exp.start_date,
                        "end_date": exp.end_date or "Present",
                        "is_current": exp.is_current,
                        "description": exp.enhanced_description or exp.description or "",
                        "bullets": [],  # Could parse from description if needed
                        "achievements": exp.achievements or []
                    }
                    for exp in ranked_exps
                ]
            })
        
        # Projects section with ALL fields
        if ranked_projs:
            sections.append({
                "type": "projects",
                "entries": [
                    {
                        "id": str(proj.id),
                        "name": proj.name,
                        "description": proj.enhanced_description or proj.description or "",
                        "technologies": proj.technologies or [],
                        "url": proj.url or "",
                        "start_date": proj.start_date or "",
                        "end_date": proj.end_date or ""
                    }
                    for proj in ranked_projs
                ]
            })
        
        # Education section with ALL fields
        if profile.education:
            sections.append({
                "type": "education",
                "entries": [
                    {
                        "id": str(edu.id),
                        "degree": edu.degree,
                        "field_of_study": edu.field_of_study,
                        "institution": edu.institution,
                        "start_date": edu.start_date,
                        "end_date": edu.end_date or "",
                        "gpa": edu.gpa or 0.0,
                        "honors": edu.honors or []
                    }
                    for edu in profile.education
                ]
            })
        
        # Metadata
        metadata = {
            "total_years_experience": round(total_years, 1),
            "top_skills": profile.skills.technical[:10] if profile.skills and profile.skills.technical else [],
            "industries": list(set(exp.company for exp in ranked_exps[:5])) if ranked_exps else [],
            "total_projects": len(profile.projects),
            "total_certifications": len(profile.skills.certifications) if profile.skills and profile.skills.certifications else 0
        }
        
        return {
            "header": header,
            "sections": sections,
            "metadata": metadata
        }
    
    def _build_structured_cover_letter(self, profile, cover_letter_text, company_name, job_title) -> Dict:
        """Build structured JSON content for cover letter export templates."""
        # Parse cover letter into paragraphs
        paragraphs = [p.strip() for p in cover_letter_text.split("\n\n") if p.strip()]
        
        # Build header with ALL personal info fields
        header = {
            "name": profile.personal_info.full_name,
            "title": job_title,
            "email": profile.personal_info.email,
            "phone": profile.personal_info.phone or "",
            "location": profile.personal_info.location or "",
            "linkedin": profile.personal_info.linkedin or "",
            "github": profile.personal_info.github or "",
            "website": profile.personal_info.website or ""
        }
        
        # Build sections
        sections = [
            {
                "type": "cover_letter",
                "company": company_name,
                "paragraphs": paragraphs
            }
        ]
        
        # Metadata
        metadata = {
            "word_count": len(cover_letter_text.split()),
            "paragraph_count": len(paragraphs),
            "company": company_name,
            "position": job_title
        }
        
        return {
            "header": header,
            "sections": sections,
            "metadata": metadata
        }
    
    async def _calculate_ats_score(self, text: str, job) -> Dict:
        """Calculate ATS score using LLM analysis."""
        if not job or not job.parsed_keywords:
            return {
                "score": 75.0,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": [],
                "analysis": "Default score - no job keywords available",
                "llm_metadata": {}
            }
        
        job_description = job.description or f"{job.title} at {job.company}"
        
        # Use LLM to calculate ATS score
        return await self.llm.calculate_ats_score(
            document_text=text,
            job_description=job_description,
            job_keywords=job.parsed_keywords
        )
