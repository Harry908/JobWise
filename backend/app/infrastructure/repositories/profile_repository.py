"""Profile repository for database operations."""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.profile import Profile, Experience, Education, Project
from app.infrastructure.database.models import (
    MasterProfileModel,
    ExperienceModel,
    EducationModel,
    ProjectModel
)


class ProfileRepository:
    """Repository for profile database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: Profile) -> Profile:
        """Create a new profile with all related data."""
        # Create main profile
        profile_model = MasterProfileModel(
            id=profile.id,
            user_id=profile.user_id,
            version=profile.version,
            personal_info=profile.personal_info.model_dump(),
            professional_summary=profile.professional_summary,
            skills=profile.skills.model_dump()
        )

        self.session.add(profile_model)

        # Create experiences
        for exp in profile.experiences:
            exp_model = ExperienceModel(
                id=exp.id,
                profile_id=profile.id,
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                achievements=exp.achievements
            )
            self.session.add(exp_model)

        # Create education
        for edu in profile.education:
            edu_model = EducationModel(
                id=edu.id,
                profile_id=profile.id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                honors=edu.honors
            )
            self.session.add(edu_model)

        # Create projects
        for proj in profile.projects:
            proj_model = ProjectModel(
                id=proj.id,
                profile_id=profile.id,
                name=proj.name,
                description=proj.description,
                technologies=proj.technologies,
                url=proj.url,
                start_date=proj.start_date,
                end_date=proj.end_date
            )
            self.session.add(proj_model)

        await self.session.commit()
        await self.session.refresh(profile_model)

        # Reload with relationships using get_by_id
        created_profile = await self.get_by_id(profile_model.id)
        if not created_profile:
            raise ValueError(f"Failed to retrieve created profile {profile_model.id}")
        return created_profile

    async def get_by_id(self, profile_id: str) -> Optional[Profile]:
        """Get profile by ID with all relationships loaded."""
        stmt = select(MasterProfileModel).where(
            MasterProfileModel.id == profile_id
        ).options(
            selectinload(MasterProfileModel.experiences),
            selectinload(MasterProfileModel.education),
            selectinload(MasterProfileModel.projects)
        )

        result = await self.session.execute(stmt)
        profile_model = result.scalar_one_or_none()

        if not profile_model:
            return None

        return await self._model_to_entity(profile_model)

    async def get_by_user_id(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Profile]:
        """Get all profiles for a user."""
        stmt = select(MasterProfileModel).where(
            MasterProfileModel.user_id == user_id
        ).options(
            selectinload(MasterProfileModel.experiences),
            selectinload(MasterProfileModel.education),
            selectinload(MasterProfileModel.projects)
        ).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        profile_models = result.scalars().all()

        profiles = []
        for model in profile_models:
            profiles.append(await self._model_to_entity(model))

        return profiles

    async def get_active_by_user_id(self, user_id: int) -> Optional[Profile]:
        """Get the most recent profile for a user (by version)."""
        # For now, just get the first profile since users can only have one
        profiles = await self.get_by_user_id(user_id, limit=1, offset=0)
        return profiles[0] if profiles else None

    async def update(self, profile: Profile) -> Profile:
        """Update profile and all related data."""
        # Update main profile
        stmt = update(MasterProfileModel).where(
            MasterProfileModel.id == profile.id
        ).values(
            version=profile.version,
            personal_info=profile.personal_info.model_dump(),
            professional_summary=profile.professional_summary,
            skills=profile.skills.model_dump(),
            updated_at=profile.updated_at
        )
        await self.session.execute(stmt)

        # Delete existing relationships
        await self.session.execute(
            delete(ExperienceModel).where(ExperienceModel.profile_id == profile.id)
        )
        await self.session.execute(
            delete(EducationModel).where(EducationModel.profile_id == profile.id)
        )
        await self.session.execute(
            delete(ProjectModel).where(ProjectModel.profile_id == profile.id)
        )

        # Create new relationships
        for exp in profile.experiences:
            exp_model = ExperienceModel(
                id=exp.id,
                profile_id=profile.id,
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                achievements=exp.achievements
            )
            self.session.add(exp_model)

        for edu in profile.education:
            edu_model = EducationModel(
                id=edu.id,
                profile_id=profile.id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                honors=edu.honors
            )
            self.session.add(edu_model)

        for proj in profile.projects:
            proj_model = ProjectModel(
                id=proj.id,
                profile_id=profile.id,
                name=proj.name,
                description=proj.description,
                technologies=proj.technologies,
                url=proj.url,
                start_date=proj.start_date,
                end_date=proj.end_date
            )
            self.session.add(proj_model)

        await self.session.commit()

        # Return updated profile
        updated_profile = await self.get_by_id(profile.id)
        if not updated_profile:
            raise ValueError(f"Profile {profile.id} not found after update")
        return updated_profile

    async def delete(self, profile_id: str) -> bool:
        """Delete profile and all related data."""
        # Cascade delete will handle related records
        stmt = delete(MasterProfileModel).where(MasterProfileModel.id == profile_id)
        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def exists(self, profile_id: str) -> bool:
        """Check if profile exists."""
        stmt = select(MasterProfileModel.id).where(MasterProfileModel.id == profile_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_by_user_id(self, user_id: int) -> int:
        """Count profiles for a user."""
        from sqlalchemy import func
        stmt = select(func.count(MasterProfileModel.id)).where(
            MasterProfileModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count if count is not None else 0

    async def _model_to_entity(self, profile_model: MasterProfileModel) -> Profile:
        """Convert database model to domain entity."""
        from app.domain.entities.profile import PersonalInfo, Skills

        # Convert experiences
        experiences = []
        for exp_model in profile_model.experiences:
            experiences.append(Experience(
                id=exp_model.id,
                title=exp_model.title,
                company=exp_model.company,
                location=exp_model.location,
                start_date=exp_model.start_date,
                end_date=exp_model.end_date,
                is_current=exp_model.is_current,
                description=exp_model.description,
                achievements=exp_model.achievements or []
            ))

        # Convert education
        education = []
        for edu_model in profile_model.education:
            education.append(Education(
                id=edu_model.id,
                institution=edu_model.institution,
                degree=edu_model.degree,
                field_of_study=edu_model.field_of_study,
                start_date=edu_model.start_date,
                end_date=edu_model.end_date,
                gpa=edu_model.gpa,
                honors=edu_model.honors or []
            ))

        # Convert projects
        projects = []
        for proj_model in profile_model.projects:
            projects.append(Project(
                id=proj_model.id,
                name=proj_model.name,
                description=proj_model.description,
                technologies=proj_model.technologies or [],
                url=proj_model.url,
                start_date=proj_model.start_date,
                end_date=proj_model.end_date
            ))

        return Profile(
            id=profile_model.id,
            user_id=profile_model.user_id,
            personal_info=PersonalInfo(**profile_model.personal_info),
            professional_summary=profile_model.professional_summary,
            experiences=experiences,
            education=education,
            skills=Skills(**profile_model.skills),
            projects=projects,
            version=profile_model.version,
            created_at=profile_model.created_at,
            updated_at=profile_model.updated_at
        )