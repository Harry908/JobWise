"""Profile repository for data access operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.profile import MasterProfile
from ...domain.value_objects import (
    PersonalInfo, Experience, Education, Skills, Project, 
    Language, LanguageProficiency, Certification
)
from ...infrastructure.database.models import (
    MasterProfileModel,
    ExperienceModel,
    EducationModel,
    SkillModel,
    LanguageModel,
    CertificationModel,
    ProjectModel
)


class ProfileRepository:
    """Repository for profile data access operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: MasterProfile) -> MasterProfile:
        """Create a new profile."""
        # Create the profile model
        profile_model = MasterProfileModel(
            user_id=str(profile.user_id),  # Convert UUID to string
            full_name=profile.personal_info.full_name,
            email=profile.personal_info.email,
            phone=profile.personal_info.phone,
            location=profile.personal_info.location,
            linkedin=profile.personal_info.linkedin,
            github=profile.personal_info.github,
            website=profile.personal_info.website,
            professional_summary=profile.professional_summary,
            version=profile.version
        )
        
        self.session.add(profile_model)
        await self.session.flush()  # Get the ID
        
        # Update the profile entity with the database-generated ID
        profile.id = UUID(profile_model.id)
        
        # Add related entities
        await self._add_experiences(profile_model.id, profile.experiences)
        await self._add_education(profile_model.id, profile.education)
        await self._add_skills(profile_model.id, profile.skills)
        await self._add_languages(profile_model.id, profile.skills)
        await self._add_certifications(profile_model.id, profile.skills)
        await self._add_projects(profile_model.id, profile.projects)
        
        await self.session.commit()
        return profile

    async def get_by_id(self, profile_id: UUID) -> Optional[MasterProfile]:
        """Get profile by ID."""
        query = select(MasterProfileModel).where(
            MasterProfileModel.id == str(profile_id),
            MasterProfileModel.is_active == True
        )
        result = await self.session.execute(query)
        profile_model = result.scalar_one_or_none()
        
        if not profile_model:
            return None
            
        return await self._model_to_entity(profile_model)

    async def get_by_user_id(self, user_id: UUID) -> Optional[MasterProfile]:
        """Get profile by user ID."""
        query = select(MasterProfileModel).where(
            MasterProfileModel.user_id == str(user_id),
            MasterProfileModel.is_active == True
        )
        result = await self.session.execute(query)
        profile_model = result.scalar_one_or_none()
        
        if not profile_model:
            return None
            
        return await self._model_to_entity(profile_model)

    async def update(self, profile: MasterProfile) -> MasterProfile:
        """Update an existing profile."""
        # Update main profile
        update_stmt = (
            update(MasterProfileModel)
            .where(MasterProfileModel.id == str(profile.id))
            .values(
                full_name=profile.personal_info.full_name,
                email=profile.personal_info.email,
                phone=profile.personal_info.phone,
                location=profile.personal_info.location,
                linkedin=profile.personal_info.linkedin,
                github=profile.personal_info.github,
                website=profile.personal_info.website,
                professional_summary=profile.professional_summary,
                version=profile.version
            )
        )
        await self.session.execute(update_stmt)
        
        # Update related entities (delete and recreate for simplicity)
        await self._delete_related_entities(str(profile.id))
        await self._add_experiences(str(profile.id), profile.experiences)
        await self._add_education(str(profile.id), profile.education)
        await self._add_skills(str(profile.id), profile.skills)
        await self._add_languages(str(profile.id), profile.skills)
        await self._add_certifications(str(profile.id), profile.skills)
        await self._add_projects(str(profile.id), profile.projects)
        
        await self.session.commit()
        return profile

    async def delete(self, profile_id: UUID) -> bool:
        """Delete a profile by ID."""
        # Soft delete by setting is_active to False
        update_stmt = (
            update(MasterProfileModel)
            .where(MasterProfileModel.id == str(profile_id))
            .values(is_active=False)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return True  # Assume success for soft delete

    async def list_by_user_id(self, user_id: UUID) -> List[MasterProfile]:
        """List all profiles for a user."""
        query = select(MasterProfileModel).where(MasterProfileModel.user_id == str(user_id))
        result = await self.session.execute(query)
        profile_models = result.scalars().all()
        
        profiles = []
        for profile_model in profile_models:
            profile = await self._model_to_entity(profile_model)
            if profile:
                profiles.append(profile)
        
        return profiles

    async def exists(self, profile_id: UUID) -> bool:
        """Check if profile exists."""
        query = select(MasterProfileModel.id).where(
            MasterProfileModel.id == str(profile_id),
            MasterProfileModel.is_active == True
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def _model_to_entity(self, profile_model: MasterProfileModel) -> MasterProfile:
        """Convert database model to domain entity."""
        from ...domain.value_objects import PersonalInfo, Experience, Education, Skills, Project, Language, LanguageProficiency, Certification
        
        # Load related data
        experiences = await self._get_experiences(profile_model.id)
        education = await self._get_education(profile_model.id)
        skills = await self._get_skills(profile_model.id)
        languages = await self._get_languages(profile_model.id)
        certifications = await self._get_certifications(profile_model.id)
        projects = await self._get_projects(profile_model.id)
        
        # Create personal info
        personal_info = PersonalInfo(
            full_name=profile_model.full_name,
            email=profile_model.email,
            phone=profile_model.phone,
            location=profile_model.location,
            linkedin=profile_model.linkedin,
            github=profile_model.github,
            website=profile_model.website
        )
        
        return MasterProfile(
            id=UUID(profile_model.id),
            user_id=UUID(profile_model.user_id),
            personal_info=personal_info,
            professional_summary=profile_model.professional_summary,
            experiences=experiences,
            education=education,
            skills=skills,
            projects=projects,
            version=profile_model.version,
            created_at=profile_model.created_at,
            updated_at=profile_model.updated_at
        )

    async def _add_experiences(self, profile_id: str, experiences: Optional[List[Experience]]):
        """Add experiences to profile."""
        if not experiences:
            return
            
        for exp in experiences:
            exp_model = ExperienceModel(
                profile_id=profile_id,
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description
            )
            self.session.add(exp_model)

    async def _add_education(self, profile_id: str, education: Optional[List[Education]]):
        """Add education to profile."""
        if not education:
            return
            
        for edu in education:
            edu_model = EducationModel(
                profile_id=profile_id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa
            )
            self.session.add(edu_model)

    async def _add_skills(self, profile_id: str, skills):
        """Add skills to profile."""
        from ...domain.value_objects import SkillCategory
        
        if not skills or not hasattr(skills, 'technical_skills'):
            return
            
        for skill_name in skills.technical_skills:
            skill_model = SkillModel(
                profile_id=profile_id,
                name=skill_name,
                category=SkillCategory.TECHNICAL
            )
            self.session.add(skill_model)
            
        for skill_name in skills.soft_skills:
            skill_model = SkillModel(
                profile_id=profile_id,
                name=skill_name,
                category=SkillCategory.SOFT
            )
            self.session.add(skill_model)

    async def _add_languages(self, profile_id: str, skills):
        """Add languages to profile."""
        if not skills or not hasattr(skills, 'languages'):
            return
            
        for lang in skills.languages:
            lang_model = LanguageModel(
                profile_id=profile_id,
                name=lang.name,
                proficiency=lang.proficiency.value
            )
            self.session.add(lang_model)

    async def _add_certifications(self, profile_id: str, skills):
        """Add certifications to profile."""
        if not skills or not hasattr(skills, 'certifications'):
            return
            
        for cert in skills.certifications:
            cert_model = CertificationModel(
                profile_id=profile_id,
                name=cert.name,
                issuer=cert.issuer,
                date_obtained=cert.date_obtained,
                expiry_date=cert.expiry_date,
                credential_id=cert.credential_id,
                verification_url=cert.verification_url
            )
            self.session.add(cert_model)

    async def _add_projects(self, profile_id: str, projects: Optional[List[Project]]):
        """Add projects to profile."""
        if not projects:
            return
            
        for proj in projects:
            proj_model = ProjectModel(
                profile_id=profile_id,
                name=proj.name,
                description=proj.description,
                technologies=proj.technologies,
                url=proj.url,
                start_date=proj.start_date,
                end_date=proj.end_date
            )
            self.session.add(proj_model)

    async def _get_experiences(self, profile_id: str) -> List[Experience]:
        """Get experiences for profile."""
        from ...domain.value_objects import Experience
        
        query = select(ExperienceModel).where(ExperienceModel.profile_id == profile_id)
        result = await self.session.execute(query)
        exp_models = result.scalars().all()
        
        return [
            Experience(
                title=exp.title,
                company=exp.company,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                is_current=exp.is_current,
                description=exp.description,
                achievements=exp.achievements
            )
            for exp in exp_models
        ]

    async def _get_education(self, profile_id: str) -> List[Education]:
        """Get education for profile."""
        from ...domain.value_objects import Education
        
        query = select(EducationModel).where(EducationModel.profile_id == profile_id)
        result = await self.session.execute(query)
        edu_models = result.scalars().all()
        
        return [
            Education(
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                honors=edu.honors
            )
            for edu in edu_models
        ]

    async def _get_skills(self, profile_id: str):
        """Get skills for profile."""
        from ...domain.value_objects import Skills, Language, LanguageProficiency, Certification, SkillCategory
        
        query = select(SkillModel).where(SkillModel.profile_id == profile_id)
        result = await self.session.execute(query)
        skill_models = result.scalars().all()
        
        technical_skills = [s.name for s in skill_models if s.category == SkillCategory.TECHNICAL]
        soft_skills = [s.name for s in skill_models if s.category == SkillCategory.SOFT]
        
        # Get languages and certifications
        languages = await self._get_languages(profile_id)
        certifications = await self._get_certifications(profile_id)
        
        return Skills(
            technical_skills=technical_skills,
            soft_skills=soft_skills,
            languages=languages,
            certifications=certifications
        )

    async def _get_languages(self, profile_id: str) -> List[Language]:
        """Get languages for profile."""
        from ...domain.value_objects import Language, LanguageProficiency
        
        query = select(LanguageModel).where(LanguageModel.profile_id == profile_id)
        result = await self.session.execute(query)
        lang_models = result.scalars().all()
        
        return [
            Language(
                name=lang.name,
                proficiency=LanguageProficiency(lang.proficiency)
            )
            for lang in lang_models
        ]

    async def _get_certifications(self, profile_id: str) -> List[Certification]:
        """Get certifications for profile."""
        from ...domain.value_objects import Certification
        
        query = select(CertificationModel).where(CertificationModel.profile_id == profile_id)
        result = await self.session.execute(query)
        cert_models = result.scalars().all()
        
        return [
            Certification(
                name=cert.name,
                issuer=cert.issuer,
                date_obtained=cert.date_obtained,
                expiry_date=cert.expiry_date,
                credential_id=cert.credential_id,
                verification_url=cert.verification_url
            )
            for cert in cert_models
        ]

    async def _get_projects(self, profile_id: str) -> List[Project]:
        """Get projects for profile."""
        from ...domain.value_objects import Project
        
        query = select(ProjectModel).where(ProjectModel.profile_id == profile_id)
        result = await self.session.execute(query)
        proj_models = result.scalars().all()
        
        return [
            Project(
                name=proj.name,
                description=proj.description,
                technologies=proj.technologies,
                url=proj.url,
                start_date=proj.start_date,
                end_date=proj.end_date
            )
            for proj in proj_models
        ]

    async def _delete_related_entities(self, profile_id: str):
        """Delete all related entities for a profile."""
        # Delete in order to avoid foreign key constraints
        await self.session.execute(delete(ExperienceModel).where(ExperienceModel.profile_id == profile_id))
        await self.session.execute(delete(EducationModel).where(EducationModel.profile_id == profile_id))
        await self.session.execute(delete(SkillModel).where(SkillModel.profile_id == profile_id))
        await self.session.execute(delete(LanguageModel).where(LanguageModel.profile_id == profile_id))
        await self.session.execute(delete(CertificationModel).where(CertificationModel.profile_id == profile_id))
        await self.session.execute(delete(ProjectModel).where(ProjectModel.profile_id == profile_id))