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
        print(f"DEBUG: ProfileService creating profile for user {user_id}")
        
        # Validate that user doesn't already have a profile
        existing_profiles = await self.profile_repository.get_by_user_id(user_id)
        if existing_profiles:
            print(f"DEBUG: User {user_id} already has a profile")
            raise ValidationException("User already has a profile. Use update instead.")

        # Create domain entities
        try:
            print(f"DEBUG: Processing personal info: {personal_info}")
            personal_info_obj = PersonalInfo(**personal_info)
            skills_obj = Skills(**skills) if skills else Skills()

            # Convert experiences
            experiences_list = []
            if experiences:
                from app.domain.entities.profile import Experience
                print(f"DEBUG: Creating {len(experiences)} experiences")
                for i, exp_data in enumerate(experiences):
                    print(f"DEBUG: Processing experience {i}: {exp_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in exp_data and (exp_data['id'] is None or exp_data['id'] == ''):
                        del exp_data['id']
                    experiences_list.append(Experience(**exp_data))
                print(f"DEBUG: Successfully created {len(experiences_list)} experiences")

            # Convert education
            education_list = []
            if education:
                from app.domain.entities.profile import Education
                print(f"DEBUG: Creating {len(education)} education entries")
                for i, edu_data in enumerate(education):
                    print(f"DEBUG: Processing education {i}: {edu_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in edu_data and (edu_data['id'] is None or edu_data['id'] == ''):
                        del edu_data['id']
                    education_list.append(Education(**edu_data))
                print(f"DEBUG: Successfully created {len(education_list)} education entries")

            # Convert projects
            projects_list = []
            if projects:
                from app.domain.entities.profile import Project
                print(f"DEBUG: Creating {len(projects)} projects")
                for i, proj_data in enumerate(projects):
                    print(f"DEBUG: Processing project {i}: {proj_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in proj_data and (proj_data['id'] is None or proj_data['id'] == ''):
                        del proj_data['id']
                    projects_list.append(Project(**proj_data))
                print(f"DEBUG: Successfully created {len(projects_list)} projects")

        except Exception as e:
            print(f"DEBUG: Error creating profile entities: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid profile data: {str(e)}")

        # Create profile
        print(f"DEBUG: Creating profile object for user {user_id}")
        profile = Profile(
            user_id=user_id,
            personal_info=personal_info_obj,
            professional_summary=professional_summary,
            experiences=experiences_list,
            education=education_list,
            skills=skills_obj,
            projects=projects_list
        )

        print(f"DEBUG: About to create profile in repository")
        try:
            created_profile = await self.profile_repository.create(profile)
            print(f"DEBUG: Profile created successfully in repository with ID: {created_profile.id}")
            return created_profile
        except Exception as e:
            print(f"DEBUG: Repository create failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

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
        enhanced_professional_summary: Optional[str] = None,
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
                print(f"DEBUG: ProfileService updating personal info: {personal_info}")
                existing_profile.personal_info = PersonalInfo(**personal_info)
                print(f"DEBUG: Successfully updated personal info")
            except Exception as e:
                print(f"DEBUG: Error processing personal info: {str(e)}")
                print(f"DEBUG: Error type: {type(e)}")
                raise ValidationException(f"Invalid personal info: {str(e)}")

        if professional_summary is not None:
            print(f"DEBUG: ProfileService updating professional summary (length: {len(professional_summary) if professional_summary else 0})")
            existing_profile.professional_summary = professional_summary

        if enhanced_professional_summary is not None:
            print(f"DEBUG: ProfileService updating enhanced professional summary (length: {len(enhanced_professional_summary) if enhanced_professional_summary else 0})")
            existing_profile.enhanced_professional_summary = enhanced_professional_summary

        if skills:
            try:
                print(f"DEBUG: ProfileService updating skills: {skills}")
                existing_profile.skills = Skills(**skills)
                print(f"DEBUG: Successfully updated skills")
            except Exception as e:
                print(f"DEBUG: Error processing skills: {str(e)}")
                print(f"DEBUG: Error type: {type(e)}")
                raise ValidationException(f"Invalid skills data: {str(e)}")

        # Update experiences
        if experiences is not None:
            experiences_list = []
            try:
                from app.domain.entities.profile import Experience
                print(f"DEBUG: ProfileService updating {len(experiences)} experiences")
                
                for i, exp_data in enumerate(experiences):
                    print(f"DEBUG: Processing experience {i}: {exp_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in exp_data and (exp_data['id'] is None or exp_data['id'] == ''):
                        del exp_data['id']
                    experiences_list.append(Experience(**exp_data))
                existing_profile.experiences = experiences_list
                print(f"DEBUG: Successfully processed {len(experiences_list)} experiences")
            except Exception as e:
                print(f"DEBUG: Error processing experiences: {str(e)}")
                print(f"DEBUG: Error type: {type(e)}")
                raise ValidationException(f"Invalid experiences data: {str(e)}")

        # Update education
        if education is not None:
            education_list = []
            try:
                from app.domain.entities.profile import Education
                print(f"DEBUG: ProfileService updating {len(education)} education entries")
                
                for i, edu_data in enumerate(education):
                    print(f"DEBUG: Processing education {i}: {edu_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in edu_data and (edu_data['id'] is None or edu_data['id'] == ''):
                        del edu_data['id']
                    education_list.append(Education(**edu_data))
                existing_profile.education = education_list
                print(f"DEBUG: Successfully processed {len(education_list)} education entries")
            except Exception as e:
                print(f"DEBUG: Error processing education: {str(e)}")
                print(f"DEBUG: Error type: {type(e)}")
                raise ValidationException(f"Invalid education data: {str(e)}")

        # Update projects
        if projects is not None:
            projects_list = []
            try:
                from app.domain.entities.profile import Project
                print(f"DEBUG: ProfileService updating {len(projects)} projects")
                
                for i, proj_data in enumerate(projects):
                    print(f"DEBUG: Processing project {i}: {proj_data}")
                    # Remove None or empty string id to let default_factory generate UUID
                    if 'id' in proj_data and (proj_data['id'] is None or proj_data['id'] == ''):
                        del proj_data['id']
                    projects_list.append(Project(**proj_data))
                existing_profile.projects = projects_list
                print(f"DEBUG: Successfully processed {len(projects_list)} projects")
            except Exception as e:
                print(f"DEBUG: Error processing projects: {str(e)}")
                print(f"DEBUG: Error type: {type(e)}")
                raise ValidationException(f"Invalid projects data: {str(e)}")

        # Update timestamp
        existing_profile.updated_at = datetime.utcnow()

        print(f"DEBUG: About to update profile in repository")
        try:
            updated_profile = await self.profile_repository.update(existing_profile)
            print(f"DEBUG: Profile updated successfully in repository")
            return updated_profile
        except Exception as e:
            print(f"DEBUG: Repository update failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

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
        print(f"DEBUG: ProfileService creating {len(experiences_data)} experiences for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        experiences = []
        try:
            for i, exp_data in enumerate(experiences_data):
                print(f"DEBUG: Processing bulk experience {i}: {exp_data}")
                # Remove None id to let default_factory generate UUID
                if 'id' in exp_data and exp_data['id'] is None:
                    del exp_data['id']
                experience = Experience(**exp_data)
                experiences.append(experience)
            print(f"DEBUG: Successfully processed {len(experiences)} experiences for bulk creation")
        except Exception as e:
            print(f"DEBUG: Error processing bulk experiences: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid experience data: {str(e)}")

        try:
            result = await self.profile_repository.create_experiences_bulk(profile_id, experiences)
            print(f"DEBUG: Successfully created {len(result)} experiences in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk create experiences failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

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
        print(f"DEBUG: ProfileService updating {len(experiences_data)} experiences for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        experiences = []
        try:
            for i, exp_data in enumerate(experiences_data):
                print(f"DEBUG: Processing bulk experience update {i}: {exp_data}")
                if "id" not in exp_data:
                    raise ValidationException("Experience ID is required for updates")
                experience = Experience(**exp_data)
                experiences.append(experience)
            print(f"DEBUG: Successfully processed {len(experiences)} experiences for bulk update")
        except Exception as e:
            print(f"DEBUG: Error processing bulk experience updates: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid experience data: {str(e)}")

        try:
            result = await self.profile_repository.update_experiences_bulk(profile_id, experiences)
            print(f"DEBUG: Successfully updated {len(result)} experiences in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk update experiences failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def delete_experiences_bulk(
        self,
        profile_id: str,
        user_id: int,
        experience_ids: List[str]
    ) -> int:
        """Delete multiple experiences for a profile."""
        print(f"DEBUG: ProfileService deleting {len(experience_ids)} experiences for profile {profile_id}: {experience_ids}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        try:
            result = await self.profile_repository.delete_experiences_bulk(profile_id, experience_ids)
            print(f"DEBUG: Successfully deleted {result} experiences from repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk delete experiences failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def create_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_data: List[Dict[str, Any]]
    ) -> List[Education]:
        """Create multiple education entries for a profile."""
        print(f"DEBUG: ProfileService creating {len(education_data)} education entries for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        education_list = []
        try:
            for i, edu_data in enumerate(education_data):
                print(f"DEBUG: Processing bulk education {i}: {edu_data}")
                # Remove None id to let default_factory generate UUID
                if 'id' in edu_data and edu_data['id'] is None:
                    del edu_data['id']
                education = Education(**edu_data)
                education_list.append(education)
            print(f"DEBUG: Successfully processed {len(education_list)} education entries for bulk creation")
        except Exception as e:
            print(f"DEBUG: Error processing bulk education: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid education data: {str(e)}")

        try:
            result = await self.profile_repository.create_education_bulk(profile_id, education_list)
            print(f"DEBUG: Successfully created {len(result)} education entries in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk create education failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def update_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_data: List[Dict[str, Any]]
    ) -> List[Education]:
        """Update multiple education entries for a profile."""
        print(f"DEBUG: ProfileService updating {len(education_data)} education entries for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        education_list = []
        try:
            for i, edu_data in enumerate(education_data):
                print(f"DEBUG: Processing bulk education update {i}: {edu_data}")
                if "id" not in edu_data:
                    raise ValidationException("Education ID is required for updates")
                education = Education(**edu_data)
                education_list.append(education)
            print(f"DEBUG: Successfully processed {len(education_list)} education entries for bulk update")
        except Exception as e:
            print(f"DEBUG: Error processing bulk education updates: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid education data: {str(e)}")

        try:
            result = await self.profile_repository.update_education_bulk(profile_id, education_list)
            print(f"DEBUG: Successfully updated {len(result)} education entries in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk update education failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def delete_education_bulk(
        self,
        profile_id: str,
        user_id: int,
        education_ids: List[str]
    ) -> int:
        """Delete multiple education entries for a profile."""
        print(f"DEBUG: ProfileService deleting {len(education_ids)} education entries for profile {profile_id}: {education_ids}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        try:
            result = await self.profile_repository.delete_education_bulk(profile_id, education_ids)
            print(f"DEBUG: Successfully deleted {result} education entries from repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk delete education failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def create_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        projects_data: List[Dict[str, Any]]
    ) -> List[Project]:
        """Create multiple projects for a profile."""
        print(f"DEBUG: ProfileService creating {len(projects_data)} projects for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        projects = []
        try:
            for i, proj_data in enumerate(projects_data):
                print(f"DEBUG: Processing bulk project {i}: {proj_data}")
                # Remove None id to let default_factory generate UUID
                if 'id' in proj_data and proj_data['id'] is None:
                    del proj_data['id']
                project = Project(**proj_data)
                projects.append(project)
            print(f"DEBUG: Successfully processed {len(projects)} projects for bulk creation")
        except Exception as e:
            print(f"DEBUG: Error processing bulk projects: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid project data: {str(e)}")

        try:
            result = await self.profile_repository.create_projects_bulk(profile_id, projects)
            print(f"DEBUG: Successfully created {len(result)} projects in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk create projects failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def update_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        projects_data: List[Dict[str, Any]]
    ) -> List[Project]:
        """Update multiple projects for a profile."""
        print(f"DEBUG: ProfileService updating {len(projects_data)} projects for profile {profile_id}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        projects = []
        try:
            for i, proj_data in enumerate(projects_data):
                print(f"DEBUG: Processing bulk project update {i}: {proj_data}")
                if "id" not in proj_data:
                    raise ValidationException("Project ID is required for updates")
                project = Project(**proj_data)
                projects.append(project)
            print(f"DEBUG: Successfully processed {len(projects)} projects for bulk update")
        except Exception as e:
            print(f"DEBUG: Error processing bulk project updates: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise ValidationException(f"Invalid project data: {str(e)}")

        try:
            result = await self.profile_repository.update_projects_bulk(profile_id, projects)
            print(f"DEBUG: Successfully updated {len(result)} projects in repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk update projects failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

    async def delete_projects_bulk(
        self,
        profile_id: str,
        user_id: int,
        project_ids: List[str]
    ) -> int:
        """Delete multiple projects for a profile."""
        print(f"DEBUG: ProfileService deleting {len(project_ids)} projects for profile {profile_id}: {project_ids}")
        
        # Verify profile ownership
        await self.get_profile(profile_id, user_id)

        try:
            result = await self.profile_repository.delete_projects_bulk(profile_id, project_ids)
            print(f"DEBUG: Successfully deleted {result} projects from repository")
            return result
        except Exception as e:
            print(f"DEBUG: Repository bulk delete projects failed: {str(e)}")
            print(f"DEBUG: Repository error type: {type(e)}")
            raise

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
        print(f"DEBUG: ProfileService updating skills for profile {profile_id}: {skills_data}")
        
        profile = await self.get_profile(profile_id, user_id)

        try:
            new_skills = Skills(**skills_data)
            profile.skills = new_skills
            print(f"DEBUG: Skills validation successful, updating profile")
            updated_profile = await self.profile_repository.update(profile)
            print(f"DEBUG: Successfully updated skills in repository")
            return updated_profile.skills
        except Exception as e:
            print(f"DEBUG: Error updating skills: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
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