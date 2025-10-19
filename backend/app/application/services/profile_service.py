"""Profile service for business logic operations."""

from typing import List, Optional
from uuid import UUID

from ...domain.entities.profile import MasterProfile
from ...domain.value_objects import PersonalInfo, Experience, Education, Skills, Project
from ...infrastructure.repositories.profile_repository import ProfileRepository


class ProfileService:
    """Service for profile business logic operations."""

    def __init__(self, profile_repository: ProfileRepository):
        self.repository = profile_repository

    async def create_profile(
        self,
        user_id: UUID,
        personal_info: PersonalInfo,
        professional_summary: Optional[str] = None,
        experiences: Optional[List[Experience]] = None,
        education: Optional[List[Education]] = None,
        skills: Optional[Skills] = None,
        projects: Optional[List[Project]] = None,
    ) -> MasterProfile:
        """Create a new profile for a user."""
        # Check if user already has a profile
        existing_profile = await self.repository.get_by_user_id(user_id)
        if existing_profile:
            raise ValueError("User already has a profile")

        # Create new profile
        profile = MasterProfile.create(
            user_id=user_id,
            personal_info=personal_info,
            professional_summary=professional_summary,
            experiences=experiences,
            education=education,
            skills=skills,
            projects=projects,
        )

        # Save to repository
        return await self.repository.create(profile)

    async def get_profile(self, profile_id: UUID) -> Optional[MasterProfile]:
        """Get profile by ID."""
        return await self.repository.get_by_id(profile_id)

    async def get_user_profile(self, user_id: UUID) -> Optional[MasterProfile]:
        """Get profile for a specific user."""
        return await self.repository.get_by_user_id(user_id)

    async def update_profile(
        self,
        profile_id: UUID,
        personal_info: Optional[PersonalInfo] = None,
        professional_summary: Optional[str] = None,
        experiences: Optional[List[Experience]] = None,
        education: Optional[List[Education]] = None,
        skills: Optional[Skills] = None,
        projects: Optional[List[Project]] = None,
    ) -> MasterProfile:
        """Update an existing profile."""
        # Get existing profile
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Update fields if provided
        if personal_info is not None:
            profile.update_personal_info(personal_info)

        if professional_summary is not None:
            profile.update_professional_summary(professional_summary)

        if experiences is not None:
            # Replace all experiences
            profile.experiences = experiences
            profile.updated_at = profile.updated_at  # This will trigger version update
            profile.version += 1

        if education is not None:
            # Replace all education
            profile.education = education
            profile.updated_at = profile.updated_at
            profile.version += 1

        if skills is not None:
            profile.update_skills(skills)

        if projects is not None:
            # Replace all projects
            profile.projects = projects
            profile.updated_at = profile.updated_at
            profile.version += 1

        # Save updated profile
        return await self.repository.update(profile)

    async def delete_profile(self, profile_id: UUID) -> bool:
        """Delete a profile."""
        # Check if profile exists
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        # Delete profile
        return await self.repository.delete(profile_id)

    async def add_experience(self, profile_id: UUID, experience: Experience) -> MasterProfile:
        """Add experience to a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.add_experience(experience)
        return await self.repository.update(profile)

    async def update_experience(self, profile_id: UUID, index: int, experience: Experience) -> MasterProfile:
        """Update experience in a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.update_experience(index, experience)
        return await self.repository.update(profile)

    async def remove_experience(self, profile_id: UUID, index: int) -> MasterProfile:
        """Remove experience from a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.remove_experience(index)
        return await self.repository.update(profile)

    async def add_education(self, profile_id: UUID, education: Education) -> MasterProfile:
        """Add education to a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.add_education(education)
        return await self.repository.update(profile)

    async def update_education(self, profile_id: UUID, index: int, education: Education) -> MasterProfile:
        """Update education in a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.update_education(index, education)
        return await self.repository.update(profile)

    async def remove_education(self, profile_id: UUID, index: int) -> MasterProfile:
        """Remove education from a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.remove_education(index)
        return await self.repository.update(profile)

    async def add_project(self, profile_id: UUID, project: Project) -> MasterProfile:
        """Add project to a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.add_project(project)
        return await self.repository.update(profile)

    async def update_project(self, profile_id: UUID, index: int, project: Project) -> MasterProfile:
        """Update project in a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.update_project(index, project)
        return await self.repository.update(profile)

    async def remove_project(self, profile_id: UUID, index: int) -> MasterProfile:
        """Remove project from a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        profile.remove_project(index)
        return await self.repository.update(profile)

    async def get_relevant_experiences(self, profile_id: UUID, keywords: List[str]) -> List[Experience]:
        """Get experiences relevant to keywords."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        return profile.get_relevant_experiences(keywords)

    async def get_technical_skills(self, profile_id: UUID) -> List[str]:
        """Get all technical skills from a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        return profile.get_technical_skills()

    async def calculate_years_experience(self, profile_id: UUID) -> float:
        """Calculate total years of experience for a profile."""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise ValueError("Profile not found")

        return profile.calculate_years_experience()