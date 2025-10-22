"""Profile service for business logic and validation."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.exceptions import ValidationException, NotFoundError, ForbiddenException
from app.domain.entities.profile import Profile, PersonalInfo, Skills, Experience, Education, Project
from app.infrastructure.repositories.profile_repository import ProfileRepository


class ProfileService:
    """Profile service handling business logic and validation."""

    def __init__(self, profile_repository: ProfileRepository):
        self.profile_repository = profile_repository

    async def create_profile(
        self,
        user_id: int,
        personal_info: Dict[str, Any],
        professional_summary: Optional[str] = None,
        experiences: Optional[List[Dict[str, Any]]] = None,
        education: Optional[List[Dict[str, Any]]] = None,
        skills: Optional[Dict[str, Any]] = None,
        projects: Optional[List[Dict[str, Any]]] = None
    ) -> Profile:
        """Create a new profile for a user."""
        # Validate that user doesn't already have a profile
        existing_profiles = await self.profile_repository.get_by_user_id(user_id)
        if existing_profiles:
            raise ValidationException("User already has a profile. Use update instead.")

        # Create domain entities
        try:
            personal_info_obj = PersonalInfo(**personal_info)
            skills_obj = Skills(**skills) if skills else Skills()

            # Convert experiences
            experiences_list = []
            if experiences:
                from app.domain.entities.profile import Experience
                for exp_data in experiences:
                    experiences_list.append(Experience(**exp_data))

            # Convert education
            education_list = []
            if education:
                from app.domain.entities.profile import Education
                for edu_data in education:
                    education_list.append(Education(**edu_data))

            # Convert projects
            projects_list = []
            if projects:
                from app.domain.entities.profile import Project
                for proj_data in projects:
                    projects_list.append(Project(**proj_data))

        except Exception as e:
            raise ValidationException(f"Invalid profile data: {str(e)}")

        # Create profile
        profile = Profile(
            user_id=user_id,
            personal_info=personal_info_obj,
            professional_summary=professional_summary,
            experiences=experiences_list,
            education=education_list,
            skills=skills_obj,
            projects=projects_list
        )

        return await self.profile_repository.create(profile)

    async def get_profile(self, profile_id: str, user_id: int) -> Profile:
        """Get a profile by ID with ownership verification."""
        profile = await self.profile_repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundError("Profile not found")

        if profile.user_id != user_id:
            raise ForbiddenException("Access denied: profile belongs to another user")

        return profile

    async def get_user_profiles(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Profile]:
        """Get all profiles for a user."""
        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        if offset < 0:
            raise ValidationException("Offset must be non-negative")

        return await self.profile_repository.get_by_user_id(user_id, limit, offset)

    async def get_active_profile(self, user_id: int) -> Optional[Profile]:
        """Get the active (latest version) profile for a user."""
        profiles = await self.get_user_profiles(user_id, limit=1, offset=0)
        return profiles[0] if profiles else None

    async def update_profile(
        self,
        profile_id: str,
        user_id: int,
        personal_info: Optional[Dict[str, Any]] = None,
        professional_summary: Optional[str] = None,
        experiences: Optional[List[Dict[str, Any]]] = None,
        education: Optional[List[Dict[str, Any]]] = None,
        skills: Optional[Dict[str, Any]] = None,
        projects: Optional[List[Dict[str, Any]]] = None
    ) -> Profile:
        """Update an existing profile."""
        # Get existing profile
        existing_profile = await self.get_profile(profile_id, user_id)

        # Update fields if provided
        if personal_info:
            try:
                existing_profile.personal_info = PersonalInfo(**personal_info)
            except Exception as e:
                raise ValidationException(f"Invalid personal info: {str(e)}")

        if professional_summary is not None:
            existing_profile.professional_summary = professional_summary

        if skills:
            try:
                existing_profile.skills = Skills(**skills)
            except Exception as e:
                raise ValidationException(f"Invalid skills data: {str(e)}")

        # Update experiences
        if experiences is not None:
            experiences_list = []
            try:
                from app.domain.entities.profile import Experience
                for exp_data in experiences:
                    experiences_list.append(Experience(**exp_data))
                existing_profile.experiences = experiences_list
            except Exception as e:
                raise ValidationException(f"Invalid experiences data: {str(e)}")

        # Update education
        if education is not None:
            education_list = []
            try:
                from app.domain.entities.profile import Education
                for edu_data in education:
                    education_list.append(Education(**edu_data))
                existing_profile.education = education_list
            except Exception as e:
                raise ValidationException(f"Invalid education data: {str(e)}")

        # Update projects
        if projects is not None:
            projects_list = []
            try:
                from app.domain.entities.profile import Project
                for proj_data in projects:
                    projects_list.append(Project(**proj_data))
                existing_profile.projects = projects_list
            except Exception as e:
                raise ValidationException(f"Invalid projects data: {str(e)}")

        # Increment version and update timestamp
        existing_profile.increment_version()

        return await self.profile_repository.update(existing_profile)

    async def delete_profile(self, profile_id: str, user_id: int) -> None:
        """Delete a profile with ownership verification."""
        # Verify ownership
        await self.get_profile(profile_id, user_id)

        # Delete
        deleted = await self.profile_repository.delete(profile_id)
        if not deleted:
            raise NotFoundError("Profile not found")

    async def get_profile_analytics(self, profile_id: str, user_id: int) -> Dict[str, Any]:
        """Get profile completeness and quality metrics."""
        profile = await self.get_profile(profile_id, user_id)

        # Calculate completeness scores
        completeness = self._calculate_completeness(profile)

        # Calculate statistics
        statistics = self._calculate_statistics(profile)

        # Generate recommendations
        recommendations = self._generate_recommendations(profile, completeness)

        return {
            "profile_id": profile_id,
            "completeness": completeness,
            "statistics": statistics,
            "recommendations": recommendations
        }

    async def create_experiences_bulk(
        self,
        profile_id: str,
        user_id: int,
        experiences_data: List[Dict[str, Any]]
    ) -> List[Experience]:
        """Create multiple experiences for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        experiences = []
        try:
            for exp_data in experiences_data:
                # Remove id if it's None (for creation, id should be auto-generated)
                if "id" in exp_data and exp_data["id"] is None:
                    del exp_data["id"]
                experience = Experience(**exp_data)
                experiences.append(experience)
        except Exception as e:
            raise ValidationException(f"Invalid experience data: {str(e)}")

        return await self.profile_repository.create_experiences_bulk(profile_id, experiences)

    async def get_experiences(self, profile_id: str, user_id: int, limit: int = 50, offset: int = 0) -> List[Experience]:
        """Get experiences for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        if limit < 1 or limit > 100:
            raise ValidationException("Limit must be between 1 and 100")
        if offset < 0:
            raise ValidationException("Offset must be non-negative")

        return await self.profile_repository.get_experiences_by_profile_id(profile_id, limit, offset)

    async def update_experiences_bulk(
        self,
        profile_id: str,
        user_id: int,
        experiences_data: List[Dict[str, Any]]
    ) -> List[Experience]:
        """Update multiple experiences for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        experiences = []
        try:
            for exp_data in experiences_data:
                if "id" not in exp_data:
                    raise ValidationException("Experience ID is required for updates")
                experience = Experience(**exp_data)
                experiences.append(experience)
        except Exception as e:
            raise ValidationException(f"Invalid experience data: {str(e)}")

        return await self.profile_repository.update_experiences_bulk(profile_id, experiences)

    async def delete_experiences_bulk(
        self,
        profile_id: str,
        user_id: int,
        experience_ids: List[str]
    ) -> int:
        """Delete multiple experiences for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        return await self.profile_repository.delete_experiences_bulk(profile_id, experience_ids)

    async def create_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_data: List[Dict[str, Any]]
    ) -> List[Education]:
        """Create multiple education entries for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        education_list = []
        try:
            for edu_data in education_data:
                # Remove id if it's None (for creation, id should be auto-generated)
                if "id" in edu_data and edu_data["id"] is None:
                    del edu_data["id"]
                education = Education(**edu_data)
                education_list.append(education)
        except Exception as e:
            raise ValidationException(f"Invalid education data: {str(e)}")

        return await self.profile_repository.create_education_bulk(profile_id, education_list)

    async def update_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_data: List[Dict[str, Any]]
    ) -> List[Education]:
        """Update multiple education entries for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        education_list = []
        try:
            for edu_data in education_data:
                if "id" not in edu_data:
                    raise ValidationException("Education ID is required for updates")
                education = Education(**edu_data)
                education_list.append(education)
        except Exception as e:
            raise ValidationException(f"Invalid education data: {str(e)}")

        return await self.profile_repository.update_education_bulk(profile_id, education_list)

    async def delete_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_ids: List[str]
    ) -> int:
        """Delete multiple education entries for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        return await self.profile_repository.delete_education_bulk(profile_id, education_ids)

    async def create_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        projects_data: List[Dict[str, Any]]
    ) -> List[Project]:
        """Create multiple projects for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        projects = []
        try:
            for proj_data in projects_data:
                # Remove id if it's None (for creation, id should be auto-generated)
                if "id" in proj_data and proj_data["id"] is None:
                    del proj_data["id"]
                project = Project(**proj_data)
                projects.append(project)
        except Exception as e:
            raise ValidationException(f"Invalid project data: {str(e)}")

        return await self.profile_repository.create_projects_bulk(profile_id, projects)

    async def update_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        projects_data: List[Dict[str, Any]]
    ) -> List[Project]:
        """Update multiple projects for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        projects = []
        try:
            for proj_data in projects_data:
                if "id" not in proj_data:
                    raise ValidationException("Project ID is required for updates")
                project = Project(**proj_data)
                projects.append(project)
        except Exception as e:
            raise ValidationException(f"Invalid project data: {str(e)}")

        return await self.profile_repository.update_projects_bulk(profile_id, projects)

    async def delete_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        project_ids: List[str]
    ) -> int:
        """Delete multiple projects for a profile."""
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        return await self.profile_repository.delete_projects_bulk(profile_id, project_ids)

    async def get_skills(self, profile_id: str, user_id: int) -> Dict[str, Any]:
        """Get skills for a profile."""
        profile = await self.get_profile(profile_id, user_id)
        return profile.skills.model_dump()

    async def update_skills(
        self,
        profile_id: str,
        user_id: int,
        skills_data: Dict[str, Any]
    ) -> Skills:
        """Update all skills for a profile."""
        profile = await self.get_profile(profile_id, user_id)

        try:
            new_skills = Skills(**skills_data)
            profile.skills = new_skills
            updated_profile = await self.profile_repository.update(profile)
            return updated_profile.skills
        except Exception as e:
            raise ValidationException(f"Invalid skills data: {str(e)}")

    async def add_technical_skills(
        self,
        profile_id: str,
        user_id: int,
        skills: List[str]
    ) -> Skills:
        """Add technical skills to a profile."""
        profile = await self.get_profile(profile_id, user_id)

        # Add new skills without duplicates
        existing_skills = set(profile.skills.technical)
        new_skills = existing_skills.union(set(skills))
        profile.skills.technical = list(new_skills)

        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.skills

    async def remove_technical_skills(
        self,
        profile_id: str,
        user_id: int,
        skills: List[str]
    ) -> Skills:
        """Remove technical skills from a profile."""
        profile = await self.get_profile(profile_id, user_id)

        # Remove specified skills
        skills_to_remove = set(skills)
        profile.skills.technical = [s for s in profile.skills.technical if s not in skills_to_remove]

        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.skills

    async def add_soft_skills(
        self,
        profile_id: str,
        user_id: int,
        skills: List[str]
    ) -> Skills:
        """Add soft skills to a profile."""
        profile = await self.get_profile(profile_id, user_id)

        # Add new skills without duplicates
        existing_skills = set(profile.skills.soft)
        new_skills = existing_skills.union(set(skills))
        profile.skills.soft = list(new_skills)

        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.skills

    async def remove_soft_skills(
        self,
        profile_id: str,
        user_id: int,
        skills: List[str]
    ) -> Skills:
        """Remove soft skills from a profile."""
        profile = await self.get_profile(profile_id, user_id)

        # Remove specified skills
        skills_to_remove = set(skills)
        profile.skills.soft = [s for s in profile.skills.soft if s not in skills_to_remove]

        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.skills

    async def update_custom_fields(
        self,
        profile_id: str,
        user_id: int,
        fields: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add or update custom fields for a profile."""
        profile = await self.get_profile(profile_id, user_id)

        # Update custom fields
        if not hasattr(profile, 'custom_fields') or profile.custom_fields is None:
            profile.custom_fields = {}

        for field in fields:
            profile.custom_fields[field["key"]] = field["value"]

        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.custom_fields or {}

    async def get_custom_fields(self, profile_id: str, user_id: int) -> Dict[str, Any]:
        """Get custom fields for a profile."""
        profile = await self.get_profile(profile_id, user_id)
        return profile.custom_fields or {}

    async def update_custom_fields_full(
        self,
        profile_id: str,
        user_id: int,
        custom_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update all custom fields for a profile (full replacement)."""
        profile = await self.get_profile(profile_id, user_id)
        profile.custom_fields = custom_fields
        updated_profile = await self.profile_repository.update(profile)
        return updated_profile.custom_fields or {}

    def _calculate_completeness(self, profile: Profile) -> Dict[str, Any]:
        """Calculate profile completeness percentage."""
        overall_score = 0
        section_scores = {}

        # Personal info completeness (weight: 20%)
        personal_fields = ['full_name', 'email', 'phone', 'location']
        personal_completed = sum(1 for field in personal_fields
                               if getattr(profile.personal_info, field, None))
        personal_score = (personal_completed / len(personal_fields)) * 100
        section_scores['personal_info'] = int(personal_score)
        overall_score += personal_score * 0.2

        # Professional summary (weight: 15%)
        summary_score = 100 if profile.professional_summary and len(profile.professional_summary.strip()) > 50 else 0
        section_scores['professional_summary'] = summary_score
        overall_score += summary_score * 0.15

        # Experiences (weight: 25%)
        if profile.experiences:
            exp_score = min(len(profile.experiences) * 20, 100)  # Max 5 experiences for 100%
        else:
            exp_score = 0
        section_scores['experiences'] = exp_score
        overall_score += exp_score * 0.25

        # Education (weight: 15%)
        if profile.education:
            edu_score = min(len(profile.education) * 50, 100)  # Max 2 education entries for 100%
        else:
            edu_score = 0
        section_scores['education'] = edu_score
        overall_score += edu_score * 0.15

        # Skills (weight: 15%)
        skills_score = 0
        if profile.skills.technical:
            skills_score += 40
        if profile.skills.soft:
            skills_score += 30
        if profile.skills.languages:
            skills_score += 20
        if profile.skills.certifications:
            skills_score += 10
        skills_score = min(skills_score, 100)
        section_scores['skills'] = skills_score
        overall_score += skills_score * 0.15

        # Projects (weight: 10%)
        if profile.projects:
            proj_score = min(len(profile.projects) * 25, 100)  # Max 4 projects for 100%
        else:
            proj_score = 0
        section_scores['projects'] = proj_score
        overall_score += proj_score * 0.1

        return {
            "overall": int(overall_score),
            **section_scores
        }

    def _calculate_statistics(self, profile: Profile) -> Dict[str, Any]:
        """Calculate profile statistics."""
        # Count experiences
        total_experiences = len(profile.experiences)

        # Calculate years of experience
        years_experience = 0.0
        if profile.experiences:
            current_year = datetime.utcnow().year
            for exp in profile.experiences:
                start_year = int(exp.start_date[:4])
                if exp.end_date:
                    end_year = int(exp.end_date[:4])
                else:
                    end_year = current_year
                years_experience += max(0, end_year - start_year)

        return {
            "total_experiences": total_experiences,
            "total_education": len(profile.education),
            "total_skills": len(profile.skills.technical) + len(profile.skills.soft),
            "total_projects": len(profile.projects),
            "years_of_experience": round(years_experience, 1)
        }

    def _generate_recommendations(self, profile: Profile, completeness: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if completeness['personal_info'] < 100:
            recommendations.append("Complete your personal information (phone, location)")

        if completeness['professional_summary'] < 100:
            recommendations.append("Add a detailed professional summary (aim for 50+ words)")

        if completeness['experiences'] < 80:
            recommendations.append("Add more work experience entries")

        if completeness['education'] < 100:
            recommendations.append("Add your education background")

        if completeness['skills'] < 70:
            recommendations.append("Add technical skills, soft skills, and languages")

        if completeness['projects'] < 50:
            recommendations.append("Add portfolio projects with descriptions and technologies")

        return recommendations