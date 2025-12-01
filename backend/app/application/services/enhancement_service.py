"""Enhancement service for profile enhancement."""

from typing import Optional
from uuid import UUID

from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.profile_repository import ProfileRepository
from app.application.services.style_extraction_service import StyleExtractionService


class EnhancementService:
    """Service for AI-powered profile enhancement."""
    
    def __init__(
        self,
        llm_adapter: GroqAdapter,
        profile_repo: ProfileRepository,
        style_service: StyleExtractionService
    ):
        self.llm = llm_adapter
        self.profile_repo = profile_repo
        self.style_service = style_service
    
    async def enhance_profile(
        self,
        profile_id: UUID,
        user_id: int,
        custom_prompt: Optional[str] = None
    ) -> dict:
        """Enhance master profile using AI - batch process all content in one LLM call."""
        # Get profile
        profile = await self.profile_repo.get_by_id(str(profile_id))
        if not profile or profile.user_id != user_id:
            raise ValueError("Profile not found")
        
        # Get writing style
        style = await self.style_service.get_user_style(user_id)
        
        # Get all experiences
        experiences = await self.profile_repo.get_experiences_by_profile_id(str(profile_id))
        
        # Prepare profile data for batch enhancement
        profile_data = {
            "professional_summary": profile.professional_summary,
            "experiences": [
                {
                    "id": exp.id,
                    "title": exp.title,
                    "company": exp.company,
                    "description": exp.description
                }
                for exp in experiences if exp.description
            ],
            "projects": [
                {
                    "id": proj.id,
                    "name": proj.name,
                    "description": proj.description
                }
                for proj in profile.projects if proj.description
            ]
        }
        
        # Single LLM call to enhance all content
        result = await self.llm.enhance_profile_batch(profile_data, style)
        enhancements = result["enhancements"]
        
        # Update profile with enhanced content
        experiences_enhanced = 0
        projects_enhanced = 0
        enhanced_summary = None
        
        # Update professional summary
        if "summary" in enhancements:
            enhanced_summary = enhancements["summary"]["enhanced_text"]
            # TODO: Add method to update professional summary if needed
        
        # Update experiences with enhanced descriptions
        for exp in experiences:
            if exp.id in enhancements and enhancements[exp.id]["type"] == "experience":
                enhanced_text = enhancements[exp.id]["enhanced_text"]
                # Update experience in database
                exp.enhanced_description = enhanced_text
                await self.profile_repo.update_experience(
                    profile_id=str(profile_id),
                    experience_id=exp.id,
                    enhanced_description=enhanced_text
                )
                experiences_enhanced += 1
        
        # Update projects with enhanced descriptions
        for proj in profile.projects:
            if proj.id in enhancements and enhancements[proj.id]["type"] == "project":
                enhanced_text = enhancements[proj.id]["enhanced_text"]
                # Update project in database
                proj.enhanced_description = enhanced_text
                await self.profile_repo.update_project(
                    profile_id=str(profile_id),
                    project_id=proj.id,
                    enhanced_description=enhanced_text
                )
                projects_enhanced += 1
        
        return {
            "profile_id": str(profile_id),
            "status": "completed",
            "enhanced_sections": {
                "professional_summary": enhanced_summary,
                "experiences_enhanced": experiences_enhanced,
                "projects_enhanced": projects_enhanced
            },
            "writing_style_used": style,
            "llm_metadata": result["llm_metadata"]
        }
