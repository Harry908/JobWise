"""Profile API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.dtos.profile_dtos import (
    CreateProfileDTO,
    UpdateProfileDTO,
    ProfileDTO,
    ProfileSummaryDTO,
    AddExperienceDTO,
    UpdateExperienceDTO,
    RemoveExperienceDTO,
    AddEducationDTO,
    UpdateEducationDTO,
    RemoveEducationDTO,
    AddProjectDTO,
    UpdateProjectDTO,
    RemoveProjectDTO,
    ProfileAnalyticsDTO,
)
from ...application.services.profile_service import ProfileService
from ...core.dependencies import get_db_session, get_current_user
from ...domain.entities.user import User
from ...infrastructure.repositories.profile_repository import ProfileRepository

from ...domain.value_objects import PersonalInfo, Experience, Education, Skills, Project, Language, LanguageProficiency, Certification

router = APIRouter(tags=["profiles"])


# Dependency to get profile service
async def get_profile_service(session: AsyncSession = Depends(get_db_session)) -> ProfileService:
    """Get profile service instance."""
    repository = ProfileRepository(session)
    return ProfileService(repository)


@router.post("", response_model=ProfileDTO, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: CreateProfileDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """
    Create a new profile for the current user.

    - **personal_info**: Personal information (required)
    - **professional_summary**: Professional summary (optional)
    - **experiences**: List of work experiences (optional)
    - **education**: List of education records (optional)
    - **skills**: Skills information (optional)
    - **projects**: List of projects (optional)
    """
    try:

        personal_info = PersonalInfo(**profile_data.personal_info.model_dump())

        experiences = [
            Experience(**exp.model_dump())
            for exp in profile_data.experiences
        ] if profile_data.experiences else None

        education = [
            Education(**edu.model_dump())
            for edu in profile_data.education
        ] if profile_data.education else None

        skills = Skills(
            technical_skills=profile_data.skills.technical,
            soft_skills=profile_data.skills.soft,
            languages=[
                Language(name=lang.name, proficiency=LanguageProficiency(lang.proficiency))
                for lang in profile_data.skills.languages
            ],
            certifications=[
                Certification(
                    name=cert.name,
                    issuer=cert.issuer,
                    date_obtained=cert.date_obtained,
                    expiry_date=cert.expiry_date,
                    credential_id=cert.credential_id,
                    verification_url=str(cert.verification_url) if cert.verification_url else None
                )
                for cert in profile_data.skills.certifications
            ]
        ) if profile_data.skills else None

        projects = [
            Project(**proj.model_dump())
            for proj in profile_data.projects
        ] if profile_data.projects else None

        profile = await service.create_profile(
            user_id=current_user.id,
            personal_info=personal_info,
            professional_summary=profile_data.professional_summary,
            experiences=experiences,
            education=education,
            skills=skills,
            projects=projects,
        )

        return ProfileDTO(**profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile"
        )


@router.get("/me", response_model=ProfileDTO)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Get the current user's profile."""
    profile = await service.get_user_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return ProfileDTO(**profile.to_dict())


@router.get("/{profile_id}", response_model=ProfileDTO)
async def get_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Get a profile by ID."""
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Check if user owns this profile
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return ProfileDTO(**profile.to_dict())


@router.put("/{profile_id}", response_model=ProfileDTO)
async def update_profile(
    profile_id: UUID,
    profile_data: UpdateProfileDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Update an existing profile."""
    # Check if profile exists and user owns it
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        # Convert DTOs to domain objects if provided
        from ...domain.value_objects import PersonalInfo, Experience, Education, Skills, Project

        personal_info = None
        if profile_data.personal_info:
            personal_info = PersonalInfo(**profile_data.personal_info.model_dump())

        experiences = None
        if profile_data.experiences:
            experiences = [
                Experience(**exp.model_dump())
                for exp in profile_data.experiences
            ]

        education = None
        if profile_data.education:
            education = [
                Education(**edu.model_dump())
                for edu in profile_data.education
            ]

        skills = None
        if profile_data.skills:
            skills = Skills(
                technical_skills=profile_data.skills.technical,
                soft_skills=profile_data.skills.soft,
                languages=[
                    Language(name=lang.name, proficiency=LanguageProficiency(lang.proficiency))
                    for lang in profile_data.skills.languages
                ],
                certifications=[
                    Certification(
                        name=cert.name,
                        issuer=cert.issuer,
                        date_obtained=cert.date_obtained,
                        expiry_date=cert.expiry_date,
                        credential_id=cert.credential_id,
                        verification_url=str(cert.verification_url) if cert.verification_url else None
                    )
                    for cert in profile_data.skills.certifications
                ]
            )

        projects = None
        if profile_data.projects:
            projects = [
                Project(**proj.model_dump())
                for proj in profile_data.projects
            ]

        updated_profile = await service.update_profile(
            profile_id=profile_id,
            personal_info=personal_info,
            professional_summary=profile_data.professional_summary,
            experiences=experiences,
            education=education,
            skills=skills,
            projects=projects,
        )

        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> None:
    """Delete a profile."""
    # Check if profile exists and user owns it
    profile = await service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        await service.delete_profile(profile_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile"
        )


# Experience management endpoints
@router.post("/{profile_id}/experiences", response_model=ProfileDTO)
async def add_experience(
    profile_id: UUID,
    experience_data: AddExperienceDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Add experience to a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Experience
        experience = Experience(**experience_data.experience.model_dump())

        updated_profile = await service.add_experience(profile_id, experience)
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{profile_id}/experiences", response_model=ProfileDTO)
async def update_experience(
    profile_id: UUID,
    experience_data: UpdateExperienceDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Update experience in a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Experience
        experience = Experience(**experience_data.experience.model_dump())

        updated_profile = await service.update_experience(
            profile_id, experience_data.index, experience
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{profile_id}/experiences", response_model=ProfileDTO)
async def remove_experience(
    profile_id: UUID,
    experience_data: RemoveExperienceDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Remove experience from a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_profile = await service.remove_experience(
            profile_id, experience_data.index
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Education management endpoints
@router.post("/{profile_id}/education", response_model=ProfileDTO)
async def add_education(
    profile_id: UUID,
    education_data: AddEducationDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Add education to a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Education
        education = Education(**education_data.education.model_dump())

        updated_profile = await service.add_education(profile_id, education)
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{profile_id}/education", response_model=ProfileDTO)
async def update_education(
    profile_id: UUID,
    education_data: UpdateEducationDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Update education in a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Education
        education = Education(**education_data.education.model_dump())

        updated_profile = await service.update_education(
            profile_id, education_data.index, education
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{profile_id}/education", response_model=ProfileDTO)
async def remove_education(
    profile_id: UUID,
    education_data: RemoveEducationDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Remove education from a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_profile = await service.remove_education(
            profile_id, education_data.index
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Project management endpoints
@router.post("/{profile_id}/projects", response_model=ProfileDTO)
async def add_project(
    profile_id: UUID,
    project_data: AddProjectDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Add project to a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Project
        project = Project(**project_data.project.model_dump())

        updated_profile = await service.add_project(profile_id, project)
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{profile_id}/projects", response_model=ProfileDTO)
async def update_project(
    profile_id: UUID,
    project_data: UpdateProjectDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Update project in a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        from ...domain.value_objects import Project
        project = Project(**project_data.project.model_dump())

        updated_profile = await service.update_project(
            profile_id, project_data.index, project
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{profile_id}/projects", response_model=ProfileDTO)
async def remove_project(
    profile_id: UUID,
    project_data: RemoveProjectDTO,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileDTO:
    """Remove project from a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_profile = await service.remove_project(
            profile_id, project_data.index
        )
        return ProfileDTO(**updated_profile.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Analytics endpoints
@router.get("/{profile_id}/analytics", response_model=ProfileAnalyticsDTO)
async def get_profile_analytics(
    profile_id: UUID,
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
) -> ProfileAnalyticsDTO:
    """Get analytics for a profile."""
    # Check ownership
    profile = await service.get_profile(profile_id)
    if not profile or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Calculate analytics
    years_experience = await service.calculate_years_experience(profile_id)
    technical_skills = await service.get_technical_skills(profile_id)

    # Count technologies across experiences and projects
    technologies = set()
    for exp in profile.experiences:
        if exp.description:
            # Simple extraction - in real app this would be more sophisticated
            for tech in ['python', 'javascript', 'java', 'react', 'node', 'sql', 'aws', 'docker']:
                if tech.lower() in exp.description.lower():
                    technologies.add(tech)

    for project in profile.projects:
        technologies.update(project.technologies)

    return ProfileAnalyticsDTO(
        total_experiences=len(profile.experiences),
        total_education=len(profile.education),
        total_projects=len(profile.projects),
        technical_skills_count=len(technical_skills),
        soft_skills_count=len(profile.skills.get_all_soft_skills()),
        languages_count=len(profile.skills.get_all_languages()),
        certifications_count=len(profile.skills.get_all_certifications()),
        years_experience=years_experience,
        top_technologies=list(technologies)[:10]  # Top 10 technologies
    )