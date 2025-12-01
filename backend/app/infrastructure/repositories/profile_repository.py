"""Profile repository for database operations."""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from app.domain.entities.profile import Profile, Experience, Education, Project
from app.infrastructure.database.models import (
    MasterProfileModel,
    ExperienceModel,
    EducationModel,
    ProjectModel
)

logger = logging.getLogger(__name__)


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
            personal_info=profile.personal_info.model_dump(),
            professional_summary=profile.professional_summary,
            skills=profile.skills.model_dump(),
            custom_fields=profile.custom_fields
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
                enhanced_description=proj.enhanced_description,
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
            personal_info=profile.personal_info.model_dump(),
            professional_summary=profile.professional_summary,
            skills=profile.skills.model_dump(),
            custom_fields=profile.custom_fields,
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

    async def create_experiences_bulk(self, profile_id: str, experiences: List[Experience]) -> List[Experience]:
        """Create multiple experiences for a profile."""
        # Get all existing experiences for this profile
        stmt = select(ExperienceModel).where(ExperienceModel.profile_id == profile_id)
        result = await self.session.execute(stmt)
        existing_experiences = result.scalars().all()
        
        # Build set of existing content signatures (title, company, start_date)
        existing_signatures = set()
        for existing in existing_experiences:
            signature = (existing.title, existing.company, existing.start_date)
            existing_signatures.add(signature)
        
        # Only add experiences that don't already exist based on content
        created_experiences = []
        for exp in experiences:
            signature = (exp.title, exp.company, exp.start_date)
            if signature not in existing_signatures:
                if exp.enhanced_description:
                    logger.info(f"Creating experience with ENHANCED description: {exp.title} at {exp.company}")
                    logger.debug(f"Enhanced description preview: {exp.enhanced_description[:100]}...")
                exp_model = ExperienceModel(
                    id=exp.id,
                    profile_id=profile_id,
                    title=exp.title,
                    company=exp.company,
                    location=exp.location,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=exp.is_current,
                    description=exp.description,
                    enhanced_description=exp.enhanced_description,
                    achievements=exp.achievements
                )
                self.session.add(exp_model)
                created_experiences.append(exp)

        if created_experiences:
            await self.session.commit()
        return created_experiences

    async def get_experiences_by_profile_id(self, profile_id: str, limit: int = 50, offset: int = 0) -> List[Experience]:
        """Get experiences for a profile."""
        stmt = select(ExperienceModel).where(
            ExperienceModel.profile_id == profile_id
        ).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        exp_models = result.scalars().all()

        experiences = []
        for exp_model in exp_models:
            experiences.append(Experience(
                id=exp_model.id,
                title=exp_model.title,
                company=exp_model.company,
                location=exp_model.location,
                start_date=exp_model.start_date,
                end_date=exp_model.end_date,
                is_current=exp_model.is_current,
                description=exp_model.description,
                enhanced_description=exp_model.enhanced_description,
                achievements=exp_model.achievements or []
            ))

        return experiences

    async def update_experiences_bulk(self, profile_id: str, experiences: List[Experience]) -> List[Experience]:
        """Update multiple experiences for a profile."""
        for exp in experiences:
            stmt = update(ExperienceModel).where(
                ExperienceModel.id == exp.id,
                ExperienceModel.profile_id == profile_id
            ).values(
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                enhanced_description=exp.enhanced_description,
                achievements=exp.achievements
            )
            await self.session.execute(stmt)

        await self.session.commit()
        return experiences

    async def delete_experiences_bulk(self, profile_id: str, experience_ids: List[str]) -> int:
        """Delete multiple experiences for a profile."""
        stmt = delete(ExperienceModel).where(
            ExperienceModel.id.in_(experience_ids),
            ExperienceModel.profile_id == profile_id
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def create_education_bulk(self, profile_id: str, education_list: List[Education]) -> List[Education]:
        """Create multiple education entries for a profile."""
        # Get all existing education entries for this profile
        stmt = select(EducationModel).where(EducationModel.profile_id == profile_id)
        result = await self.session.execute(stmt)
        existing_education = result.scalars().all()
        
        # Build set of existing content signatures (institution, degree, field_of_study)
        existing_signatures = set()
        for existing in existing_education:
            signature = (existing.institution, existing.degree, existing.field_of_study)
            existing_signatures.add(signature)
        
        # Only add education entries that don't already exist based on content
        created_education = []
        for edu in education_list:
            signature = (edu.institution, edu.degree, edu.field_of_study)
            if signature not in existing_signatures:
                edu_model = EducationModel(
                    id=edu.id,
                    profile_id=profile_id,
                    institution=edu.institution,
                    degree=edu.degree,
                    field_of_study=edu.field_of_study,
                    start_date=edu.start_date,
                    end_date=edu.end_date,
                    gpa=edu.gpa,
                    honors=edu.honors
                )
                self.session.add(edu_model)
                created_education.append(edu)

        if created_education:
            await self.session.commit()
        return created_education

    async def update_education_bulk(self, profile_id: str, education_list: List[Education]) -> List[Education]:
        """Update multiple education entries for a profile."""
        for edu in education_list:
            stmt = update(EducationModel).where(
                EducationModel.id == edu.id,
                EducationModel.profile_id == profile_id
            ).values(
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                honors=edu.honors
            )
            await self.session.execute(stmt)

        await self.session.commit()
        return education_list

    async def delete_education_bulk(self, profile_id: str, education_ids: List[str]) -> int:
        """Delete multiple education entries for a profile."""
        stmt = delete(EducationModel).where(
            EducationModel.id.in_(education_ids),
            EducationModel.profile_id == profile_id
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def create_projects_bulk(self, profile_id: str, projects: List[Project]) -> List[Project]:
        """Create multiple projects for a profile."""
        # Get all existing projects for this profile
        stmt = select(ProjectModel).where(ProjectModel.profile_id == profile_id)
        result = await self.session.execute(stmt)
        existing_projects = result.scalars().all()
        
        # Build set of existing content signatures (name, first 100 chars of description)
        existing_signatures = set()
        for existing in existing_projects:
            # Use name and description prefix to identify duplicates
            desc_prefix = (existing.description or "")[:100]
            signature = (existing.name, desc_prefix)
            existing_signatures.add(signature)
        
        # Only add projects that don't already exist based on content
        created_projects = []
        for proj in projects:
            desc_prefix = (proj.description or "")[:100]
            signature = (proj.name, desc_prefix)
            if signature not in existing_signatures:
                if proj.enhanced_description:
                    logger.info(f"Creating project with ENHANCED description: {proj.name}")
                    logger.debug(f"Enhanced description preview: {proj.enhanced_description[:100]}...")
                proj_model = ProjectModel(
                    id=proj.id,
                    profile_id=profile_id,
                    name=proj.name,
                    description=proj.description,
                    enhanced_description=proj.enhanced_description,
                    technologies=proj.technologies,
                    url=proj.url,
                    start_date=proj.start_date,
                    end_date=proj.end_date
                )
                self.session.add(proj_model)
                created_projects.append(proj)

        if created_projects:
            await self.session.commit()
        return created_projects

    async def update_projects_bulk(self, profile_id: str, projects: List[Project]) -> List[Project]:
        """Update multiple projects for a profile."""
        for proj in projects:
            stmt = update(ProjectModel).where(
                ProjectModel.id == proj.id,
                ProjectModel.profile_id == profile_id
            ).values(
                name=proj.name,
                description=proj.description,
                enhanced_description=proj.enhanced_description,
                technologies=proj.technologies,
                url=proj.url,
                start_date=proj.start_date,
                end_date=proj.end_date
            )
            await self.session.execute(stmt)

        await self.session.commit()
        return projects

    async def delete_projects_bulk(self, profile_id: str, project_ids: List[str]) -> int:
        """Delete multiple projects for a profile."""
        stmt = delete(ProjectModel).where(
            ProjectModel.id.in_(project_ids),
            ProjectModel.profile_id == profile_id
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

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
                enhanced_description=exp_model.enhanced_description,
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
                enhanced_description=proj_model.enhanced_description,
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
            custom_fields=profile_model.custom_fields or {},
            created_at=profile_model.created_at,
            updated_at=profile_model.updated_at
        )