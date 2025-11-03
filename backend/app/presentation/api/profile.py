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
    """Experience model for API responses and requests."""
    id: str = Field(..., description="Unique experience ID")
    title: str = Field(..., min_length=1, max_length=100, description="Job title")
    company: str = Field(..., min_length=1, max_length=100, description="Company name")
    location: Optional[str] = Field(None, max_length=100, description="Job location")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    is_current: bool = Field(False, description="Is this current position")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "exp_123",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "is_current": False,
                "description": "Led development of scalable web applications",
                "achievements": ["Increased performance by 40%", "Mentored 5 junior developers"]
            }
        }
    }


class EducationModel(BaseModel):
    """Education model."""
    id: Optional[str] = Field(None, description="Unique education ID (auto-generated if not provided)")
    institution: str = Field(..., min_length=1, max_length=100)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "edu_123",
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
    id: Optional[str] = Field(None, description="Unique project ID (auto-generated if not provided)")
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = Field(None, max_length=200)
    start_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    end_date: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "proj_123",
                "name": "E-commerce Platform",
                "description": "Full-stack e-commerce solution",
                "technologies": ["React", "Node.js", "PostgreSQL"],
                "url": "https://github.com/user/ecommerce",
                "start_date": "2022-01-01",
                "end_date": "2022-06-01"
            }
        }
    }


class CustomFieldModel(BaseModel):
    """Custom field model."""
    key: str = Field(..., min_length=1, max_length=50, description="Custom field key")
    value: Any = Field(..., description="Custom field value")

    model_config = {
        "json_schema_extra": {
            "example": {
                "key": "hobbies",
                "value": ["reading", "gaming", "photography"]
            }
        }
    }


class CustomFieldsRequest(BaseModel):
    """Custom fields request model."""
    fields: List[CustomFieldModel] = Field(..., description="List of custom fields to add/update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "fields": [
                    {"key": "hobbies", "value": ["reading", "gaming"]},
                    {"key": "achievements", "value": ["Employee of the Month", "Hackathon Winner"]}
                ]
            }
        }
    }


class CreateProfileRequest(BaseModel):
    """Profile creation request."""
    personal_info: PersonalInfoModel
    professional_summary: Optional[str] = Field(None, min_length=10, description="Professional summary")
    skills: Optional[SkillsModel] = None
    experiences: Optional[List[ExperienceModel]] = None
    education: Optional[List[EducationModel]] = None
    projects: Optional[List[ProjectModel]] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields")

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
                },
                "experiences": [{
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "description": "Led development team"
                }],
                "education": [{
                    "institution": "University of Washington",
                    "degree": "BS",
                    "field_of_study": "Computer Science",
                    "start_date": "2016-01-01",
                    "end_date": "2020-01-01"
                }],
                "projects": [{
                    "name": "E-commerce Platform",
                    "description": "Full-stack solution",
                    "technologies": ["React", "Node.js"],
                    "start_date": "2022-01-01"
                }],
                "custom_fields": {
                    "hobbies": ["reading", "gaming"],
                    "achievements": ["Employee of the Month"]
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
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom user-defined fields")
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


# Bulk operations models
class ExperienceCreateModel(BaseModel):
    """Experience model for creation (id is optional)."""
    id: Optional[str] = Field(None, description="Unique experience ID (auto-generated if not provided)")
    title: str = Field(..., min_length=1, max_length=100, description="Job title")
    company: str = Field(..., min_length=1, max_length=100, description="Company name")
    location: Optional[str] = Field(None, max_length=100, description="Job location")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    is_current: bool = Field(False, description="Is this current position")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    achievements: List[str] = Field(default_factory=list, description="Key achievements")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "is_current": False,
                "description": "Led development of scalable web applications",
                "achievements": ["Increased performance by 40%", "Mentored 5 junior developers"]
            }
        }
    }


# Duplicate ExperienceModel removed - using the one defined earlier


class EducationCreateModel(BaseModel):
    """Education model for creation (id is optional)."""
    id: Optional[str] = Field(None, description="Unique education ID (auto-generated if not provided)")
    institution: str = Field(..., min_length=1, max_length=100, description="Institution name")
    degree: str = Field(..., min_length=1, max_length=100, description="Degree earned")
    field_of_study: str = Field(..., min_length=1, max_length=100, description="Field of study")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA (0.0-4.0)")
    honors: List[str] = Field(default_factory=list, description="Honors and awards")

    model_config = {
        "json_schema_extra": {
            "example": {
                "institution": "University of Washington",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "start_date": "2016-09-01",
                "end_date": "2020-06-01",
                "gpa": 3.8,
                "honors": ["Summa Cum Laude", "Dean's List"]
            }
        }
    }


# Removed duplicate EducationModel - using the unified one above


class ProjectCreateModel(BaseModel):
    """Project model for creation (id is optional)."""
    id: Optional[str] = Field(None, description="Unique project ID (auto-generated if not provided)")
    name: str = Field(..., min_length=1, max_length=100, description="Project name")
    description: str = Field(..., min_length=1, max_length=500, description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "E-commerce Platform",
                "description": "Built a scalable e-commerce platform handling 10k+ transactions daily",
                "technologies": ["Python", "FastAPI", "PostgreSQL", "Redis"],
                "url": "https://github.com/user/ecommerce",
                "start_date": "2022-01-01",
                "end_date": "2022-06-01"
            }
        }
    }


# Removed duplicate ProjectModel - using the unified one above


class BulkCreateExperiencesRequest(BaseModel):
    """Request model for bulk creating experiences."""
    experiences: List[ExperienceModel] = Field(..., description="List of experiences to create")


class BulkUpdateExperiencesRequest(BaseModel):
    """Request model for bulk updating experiences."""
    experiences: List[ExperienceModel] = Field(..., description="List of experiences to update")


class BulkDeleteExperiencesRequest(BaseModel):
    """Request model for bulk deleting experiences."""
    experience_ids: List[str] = Field(..., description="List of experience IDs to delete")


class BulkCreateEducationRequest(BaseModel):
    """Request model for bulk creating education."""
    education: List[EducationModel] = Field(..., description="List of education entries to create")


class BulkUpdateEducationRequest(BaseModel):
    """Request model for bulk updating education."""
    education: List[EducationModel] = Field(..., description="List of education entries to update")


class BulkDeleteEducationRequest(BaseModel):
    """Request model for bulk deleting education."""
    education_ids: List[str] = Field(..., description="List of education IDs to delete")


class BulkCreateProjectsRequest(BaseModel):
    """Request model for bulk creating projects."""
    projects: List[ProjectModel] = Field(..., description="List of projects to create")


class BulkUpdateProjectsRequest(BaseModel):
    """Request model for bulk updating projects."""
    projects: List[ProjectModel] = Field(..., description="List of projects to update")


class BulkDeleteProjectsRequest(BaseModel):
    """Request model for bulk deleting projects."""
    project_ids: List[str] = Field(..., description="List of project IDs to delete")


class SkillsResponse(BaseModel):
    """Skills response model."""
    technical: List[str]
    soft: List[str]
    languages: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]


# Removed duplicate CustomFieldModel - using the one defined above


class UpdateCustomFieldsRequest(BaseModel):
    """Request model for updating custom fields."""
    fields: List[CustomFieldModel] = Field(..., description="List of custom fields to add/update")


class BulkResponse(BaseModel):
    """Generic bulk operation response."""
    count: int = Field(..., description="Number of items processed")
    message: str = Field(..., description="Operation result message")


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
            skills=request.skills.model_dump() if request.skills else None,
            experiences=[exp.model_dump() for exp in request.experiences] if request.experiences else [],
            education=[edu.model_dump() for edu in request.education] if request.education else [],
            projects=[proj.model_dump() for proj in request.projects] if request.projects else []
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
        experiences_list = []
        for exp in profile.experiences:
            exp_data = exp.model_dump()
            print(f"DEBUG: Converting experience: {exp_data}")
            experiences_list.append(ExperienceModel(**exp_data))
        
        return ProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
            professional_summary=profile.professional_summary,
            skills=SkillsModel(**profile.skills.model_dump()),
            experiences=experiences_list,
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
        print(f"DEBUG: Received profile update request for profile_id={profile_id}")
        print(f"DEBUG: Request data: {request.model_dump()}")
        
        # Build update data
        update_data = {}
        if request.personal_info:
            update_data["personal_info"] = request.personal_info.model_dump()
        if request.professional_summary is not None:
            update_data["professional_summary"] = request.professional_summary
        if request.skills:
            update_data["skills"] = request.skills.model_dump()
        if request.experiences is not None:
            print(f"DEBUG: Processing {len(request.experiences)} experiences")
            experiences_data = [exp.model_dump() for exp in request.experiences]
            print(f"DEBUG: Experience data: {experiences_data}")
            update_data["experiences"] = experiences_data
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
        try:
            print(f"DEBUG: Converting profile to response model")
            print(f"DEBUG: Profile has {len(profile.experiences)} experiences, {len(profile.education)} education, {len(profile.projects)} projects")
            
            # Convert experiences with error checking
            experiences_list = []
            for i, exp in enumerate(profile.experiences):
                exp_data = exp.model_dump()
                print(f"DEBUG: Experience {i} data: {exp_data}")
                experiences_list.append(ExperienceModel(**exp_data))
            
            # Convert education with error checking  
            education_list = []
            for i, edu in enumerate(profile.education):
                edu_data = edu.model_dump()
                print(f"DEBUG: Education {i} data: {edu_data}")
                education_list.append(EducationModel(**edu_data))
            
            # Convert projects with error checking
            projects_list = []
            for i, proj in enumerate(profile.projects):
                proj_data = proj.model_dump()
                print(f"DEBUG: Project {i} data: {proj_data}")
                projects_list.append(ProjectModel(**proj_data))
            
            response = ProfileResponse(
                id=profile.id,
                user_id=profile.user_id,
                personal_info=PersonalInfoModel(**profile.personal_info.model_dump()),
                professional_summary=profile.professional_summary,
                skills=SkillsModel(**profile.skills.model_dump()),
                experiences=experiences_list,
                education=education_list,
                projects=projects_list,
                created_at=profile.created_at.isoformat(),
                updated_at=profile.updated_at.isoformat()
            )
            print(f"DEBUG: Profile response created successfully")
            return response
        except Exception as e:
            print(f"DEBUG: Error converting profile to response: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            raise HTTPException(status_code=500, detail=f"Error serializing profile response: {str(e)}")
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
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


# Bulk operations routes
@router.post("/{profile_id}/experiences", status_code=201)
async def create_experiences_bulk(
    profile_id: str,
    experiences: List[ExperienceCreateModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create multiple experiences for a profile."""
    try:
        experiences_data = [exp.model_dump() for exp in experiences]
        created_experiences = await profile_service.create_experiences_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            experiences_data=experiences_data
        )
        return [ExperienceModel(**exp.model_dump()) for exp in created_experiences]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}/experiences")
async def get_experiences(
    profile_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get experiences for a profile."""
    try:
        experiences = await profile_service.get_experiences(
            profile_id=profile_id,
            user_id=current_user_id,
            limit=limit,
            offset=offset
        )
        return {
            "experiences": [ExperienceModel(**exp.model_dump()) for exp in experiences],
            "pagination": {
                "total": len(experiences),  # Simplified - in real app, get from service
                "limit": limit,
                "offset": offset
            }
        }
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}/experiences")
async def update_experiences_bulk(
    profile_id: str,
    experiences: List[ExperienceModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update multiple experiences for a profile."""
    try:
        experiences_data = [exp.model_dump() for exp in experiences]
        updated_experiences = await profile_service.update_experiences_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            experiences_data=experiences_data
        )
        return [ExperienceModel(**exp.model_dump()) for exp in updated_experiences]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}/experiences", status_code=204)
async def delete_experiences_bulk(
    profile_id: str,
    request: BulkDeleteExperiencesRequest,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete multiple experiences for a profile."""
    try:
        deleted_count = await profile_service.delete_experiences_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            experience_ids=request.experience_ids
        )
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/education", status_code=201)
async def create_education_bulk(
    profile_id: str,
    education: List[EducationCreateModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create multiple education entries for a profile."""
    try:
        education_data = [edu.model_dump() for edu in education]
        created_education = await profile_service.create_education_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            education_data=education_data
        )
        return [EducationModel(**edu.model_dump()) for edu in created_education]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}/education")
async def update_education_bulk(
    profile_id: str,
    education: List[EducationModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update multiple education entries for a profile."""
    try:
        education_data = [edu.model_dump() for edu in education]
        updated_education = await profile_service.update_education_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            education_data=education_data
        )
        return [EducationModel(**edu.model_dump()) for edu in updated_education]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}/education")
async def delete_education_bulk(
    profile_id: str,
    education_ids: List[str],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete multiple education entries for a profile."""
    try:
        deleted_count = await profile_service.delete_education_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            education_ids=education_ids
        )
        return {"message": f"Deleted {deleted_count} education entries successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/projects", status_code=201)
async def create_projects_bulk(
    profile_id: str,
    projects: List[ProjectCreateModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Create multiple projects for a profile."""
    try:
        projects_data = [proj.model_dump() for proj in projects]
        created_projects = await profile_service.create_projects_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            projects_data=projects_data
        )
        return [ProjectModel(**proj.model_dump()) for proj in created_projects]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}/projects")
async def update_projects_bulk(
    profile_id: str,
    projects: List[ProjectModel],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update multiple projects for a profile."""
    try:
        projects_data = [proj.model_dump() for proj in projects]
        updated_projects = await profile_service.update_projects_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            projects_data=projects_data
        )
        return [ProjectModel(**proj.model_dump()) for proj in updated_projects]
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}/projects")
async def delete_projects_bulk(
    profile_id: str,
    project_ids: List[str],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Delete multiple projects for a profile."""
    try:
        deleted_count = await profile_service.delete_projects_bulk(
            profile_id=profile_id,
            user_id=current_user_id,
            project_ids=project_ids
        )
        return {"message": f"Deleted {deleted_count} projects successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}/skills", response_model=SkillsResponse)
async def get_skills(
    profile_id: str,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get skills for a profile."""
    try:
        skills = await profile_service.get_skills(
            profile_id=profile_id,
            user_id=current_user_id
        )
        return SkillsResponse(**skills)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}/skills")
async def update_skills(
    profile_id: str,
    skills: SkillsModel,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update all skills for a profile."""
    try:
        updated_skills = await profile_service.update_skills(
            profile_id=profile_id,
            user_id=current_user_id,
            skills_data=skills.model_dump()
        )
        return {"message": "Skills updated successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/skills/technical")
async def add_technical_skills(
    profile_id: str,
    skills: Dict[str, List[str]],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Add technical skills to a profile."""
    try:
        updated_skills = await profile_service.add_technical_skills(
            profile_id=profile_id,
            user_id=current_user_id,
            skills=skills["skills"]
        )
        return {"message": f"{len(skills['skills'])} technical skills added successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}/skills/technical")
async def remove_technical_skills(
    profile_id: str,
    skills: Dict[str, List[str]],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Remove technical skills from a profile."""
    try:
        updated_skills = await profile_service.remove_technical_skills(
            profile_id=profile_id,
            user_id=current_user_id,
            skills=skills["skills"]
        )
        return {"message": f"{len(skills['skills'])} technical skills removed successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/skills/soft")
async def add_soft_skills(
    profile_id: str,
    skills: Dict[str, List[str]],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Add soft skills to a profile."""
    try:
        updated_skills = await profile_service.add_soft_skills(
            profile_id=profile_id,
            user_id=current_user_id,
            skills=skills["skills"]
        )
        return {"message": f"{len(skills['skills'])} soft skills added successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{profile_id}/skills/soft")
async def remove_soft_skills(
    profile_id: str,
    skills: Dict[str, List[str]],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Remove soft skills from a profile."""
    try:
        updated_skills = await profile_service.remove_soft_skills(
            profile_id=profile_id,
            user_id=current_user_id,
            skills=skills["skills"]
        )
        return {"message": f"{len(skills['skills'])} soft skills removed successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{profile_id}/custom-fields")
async def get_custom_fields(
    profile_id: str,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get custom fields for a profile."""
    try:
        custom_fields = await profile_service.get_custom_fields(
            profile_id=profile_id,
            user_id=current_user_id
        )
        return custom_fields
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{profile_id}/custom-fields", status_code=201)
async def add_custom_fields(
    profile_id: str,
    request: CustomFieldsRequest,
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Add or update custom fields for a profile."""
    try:
        fields_data = [{"key": field.key, "value": field.value} for field in request.fields]
        updated_fields = await profile_service.update_custom_fields(
            profile_id=profile_id,
            user_id=current_user_id,
            fields=fields_data
        )
        return {
            "message": f"Successfully updated {len(request.fields)} custom fields",
            "updated_fields": list(updated_fields.keys())
        }
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{profile_id}/custom-fields")
async def update_custom_fields(
    profile_id: str,
    custom_fields: Dict[str, Any],
    current_user_id: int = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update all custom fields for a profile (full replacement)."""
    try:
        updated_fields = await profile_service.update_custom_fields_full(
            profile_id=profile_id,
            user_id=current_user_id,
            custom_fields=custom_fields
        )
        return updated_fields
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForbiddenException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValidationException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")