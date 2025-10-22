"""Profile API routes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.profile_service import ProfileService
from app.core.dependencies import get_current_user
from app.core.exceptions import ValidationException, NotFoundError, ForbiddenException
from app.domain.entities.profile import PersonalInfo, Skills
from app.infrastructure.database.connection import get_db_session


# Request/Response models
class PersonalInfoModel(BaseModel):
    """Personal information model."""
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")

    model_config = {
        "json_schema_extra": {
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1-555-123-4567",
                "location": "Seattle, WA",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "website": "https://johndoe.com"
            }
        }
    }


class LanguageModel(BaseModel):
    """Language proficiency model."""
    name: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., pattern=r'^(native|fluent|conversational|basic)$')

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "English",
                "proficiency": "native"
            }
        }
    }


class CertificationModel(BaseModel):
    """Certification model."""
    name: str = Field(..., min_length=1, max_length=200)
    issuer: str = Field(..., min_length=1, max_length=100)
    date_obtained: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    expiry_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    credential_id: Optional[str] = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "AWS Solutions Architect",
                "issuer": "Amazon",
                "date_obtained": "2023-01-01",
                "credential_id": "AWS-123"
            }
        }
    }


class SkillsModel(BaseModel):
    """Skills model."""
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    languages: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "technical": ["Python", "FastAPI", "React"],
                "soft": ["Leadership", "Communication"],
                "languages": [
                    {"name": "English", "proficiency": "native"},
                    {"name": "Spanish", "proficiency": "conversational"}
                ],
                "certifications": [{
                    "name": "AWS Solutions Architect",
                    "issuer": "Amazon",
                    "date_obtained": "2023-01-01",
                    "credential_id": "AWS-123"
                }]
            }
        }
    }


class ExperienceModel(BaseModel):
    """Work experience model."""
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    is_current: bool = Field(False)
    description: Optional[str] = Field(None, max_length=2000)
    achievements: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Senior Developer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2020-01-01",
                "end_date": "2023-01-01",
                "is_current": False,
                "description": "Led development of web applications"
            }
        }
    }


class EducationModel(BaseModel):
    """Education model."""
    institution: str = Field(..., min_length=1, max_length=100)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "institution": "University of Washington",
                "degree": "BS",
                "field_of_study": "Computer Science",
                "start_date": "2016-01-01",
                "end_date": "2020-01-01",
                "gpa": 3.8
            }
        }
    }


class ProjectModel(BaseModel):
    """Project model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = Field(None, max_length=200)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "E-commerce Platform",
                "description": "Full-stack e-commerce solution",
                "technologies": ["React", "Node.js", "PostgreSQL"],
                "url": "https://github.com/user/ecommerce",
                "start_date": "2022-01-01",
                "end_date": "2022-06-01"
            }
        }
    }


class CreateProfileRequest(BaseModel):
    """Profile creation request."""
    personal_info: PersonalInfoModel
    professional_summary: Optional[str] = Field(None, min_length=10, description="Professional summary")
    skills: Optional[SkillsModel] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1-555-123-4567",
                    "location": "Seattle, WA"
                },
                "professional_summary": "Experienced developer with 5+ years...",
                "skills": {
                    "technical": ["Python", "FastAPI"],
                    "soft": ["Leadership"]
                }
            }
        }
    }


class UpdateProfileRequest(BaseModel):
    """Profile update request."""
    personal_info: Optional[PersonalInfoModel] = None
    professional_summary: Optional[str] = Field(None, min_length=10, description="Professional summary")
    skills: Optional[SkillsModel] = None
    experiences: Optional[List[ExperienceModel]] = None
    education: Optional[List[EducationModel]] = None
    projects: Optional[List[ProjectModel]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "professional_summary": "Updated professional summary...",
                "personal_info": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "location": "San Francisco, CA"
                }
            }
        }
    }


class ProfileResponse(BaseModel):
    """Profile response model."""
    id: str
    user_id: int
    personal_info: PersonalInfoModel
    professional_summary: Optional[str]
    skills: SkillsModel
    experiences: List[ExperienceModel] = Field(default_factory=list)
    education: List[EducationModel] = Field(default_factory=list)
    projects: List[ProjectModel] = Field(default_factory=list)
    created_at: str
    updated_at: str


class ProfileListResponse(BaseModel):
    """Profile list response."""
    profiles: List[ProfileResponse]
    total: int
    limit: int
    offset: int


class ProfileAnalyticsResponse(BaseModel):
    """Profile analytics response."""
    completeness: Dict[str, Any]
    statistics: Dict[str, Any]
    recommendations: List[str]


# Router
router = APIRouter(prefix="/api/v1/profiles", tags=["Profiles"])


# Dependency to get profile service
async def get_profile_service(
    db: AsyncSession = Depends(get_db_session)
) -> ProfileService:
    """Get profile service instance."""
    from app.infrastructure.repositories.profile_repository import ProfileRepository

    repo = ProfileRepository(db)
    return ProfileService(repo)


@router.post("", response_model=ProfileResponse, status_code=201)
async def create_profile(
    request: CreateProfileRequest,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create a new profile for the current user."""
    try:
        profile = await profile_service.create_profile(
            user_id=current_user_id,
            personal_info=request.personal_info.model_dump(),
            professional_summary=request.professional_summary,
            skills=request.skills.model_dump() if request.skills else None
        )

        # Convert domain entity to response model
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
            education=[EducationModel(**edu.model_dump()) for edu in profile.education],
            projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=ProfileListResponse)
async def get_user_profiles(
    limit: int = Query(10, ge=1, le=100, description="Number of profiles to return"),
    offset: int = Query(0, ge=0, description="Number of profiles to skip"),
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's profiles with pagination."""
    try:
        profiles = await profile_service.get_user_profiles(
            user_id=current_user_id,
            limit=limit,
            offset=offset
        )

        # Convert domain entities to response models
        profile_responses = []
        for profile in profiles:
            profile_responses.append(ProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
                professional_summary=profile.professional_summary,
                skills=SkillsModel(**profile.skills.model_dump()),
                experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
                education=[EducationModel(**edu.model_dump()) for edu in profile.education],
                projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
                created_at=profile.created_at.isoformat(),
                updated_at=profile.updated_at.isoformat()
            ))

        return ProfileListResponse(
            profiles=profile_responses,
            total=len(profile_responses),  # Simplified - in real app, get from service
            limit=limit,
            offset=offset
        )
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's active profile."""
    print(f"DEBUG: get_my_profile endpoint called with user_id={current_user_id}")
    try:
        profile = await profile_service.get_active_profile(current_user_id)
        print(f"DEBUG: get_active_profile returned: {profile}")
        if not profile:
            raise NotFoundError("No profile found for current user")

        # Convert domain entity to response model
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
            education=[EducationModel(**edu.model_dump()) for edu in profile.education],
            projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except NotFoundError as e:
        print(f"DEBUG: NotFoundError raised: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get a specific profile by ID."""
    try:
        profile = await profile_service.get_profile(
            profile_id=profile_id,
            user_id=current_user_id
        )

        # Convert domain entity to response model
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
            education=[EducationModel(**edu.model_dump()) for edu in profile.education],
            projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    request: UpdateProfileRequest,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update a specific profile."""
    try:
        # Build update data
        update_data = {}
        if request.personal_info:
            update_data["personal_info"] = request.personal_info.model_dump()
        if request.professional_summary is not None:
            update_data["professional_summary"] = request.professional_summary
        if request.skills:
            update_data["skills"] = request.skills.model_dump()
        if request.experiences is not None:
            update_data["experiences"] = [exp.model_dump() for exp in request.experiences]
        if request.education is not None:
            update_data["education"] = [edu.model_dump() for edu in request.education]
        if request.projects is not None:
            update_data["projects"] = [proj.model_dump() for proj in request.projects]

        profile = await profile_service.update_profile(
            profile_id=profile_id,
            user_id=current_user_id,
            **update_data
        )

        # Convert domain entity to response model
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
            education=[EducationModel(**edu.model_dump()) for edu in profile.education],
            projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's active profile."""
    print(f"DEBUG: get_my_profile endpoint called with user_id={current_user_id}")
    try:
        profile = await profile_service.get_active_profile(current_user_id)
        print(f"DEBUG: get_active_profile returned: {profile}")
        if not profile:
            raise NotFoundError("No profile found for current user")

        # Convert domain entity to response model
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=[ExperienceModel(**exp.model_dump()) for exp in profile.experiences],
            education=[EducationModel(**edu.model_dump()) for edu in profile.education],
            projects=[ProjectModel(**proj.model_dump()) for proj in profile.projects],
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except NotFoundError as e:
        print(f"DEBUG: NotFoundError raised: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: str,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete a specific profile."""
    try:
        await profile_service.delete_profile(
            profile_id=profile_id,
            user_id=current_user_id
        )
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}/analytics", response_model=ProfileAnalyticsResponse)
async def get_profile_analytics(
    profile_id: str,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get analytics for a specific profile."""
    try:
        profile = await profile_service.get_profile(
            profile_id=profile_id,
            user_id=current_user_id
        )

        completeness = profile_service._calculate_completeness(profile)
        statistics = profile_service._calculate_statistics(profile)
        recommendations = profile_service._generate_recommendations(profile, completeness)

        return ProfileAnalyticsResponse(
            completeness=completeness,
            statistics=statistics,
            recommendations=recommendations
        )
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")