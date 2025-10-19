"""Data transfer objects for profile operations."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator


# Value Object DTOs
class PersonalInfoDTO(BaseModel):
    """DTO for personal information."""
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None


class ExperienceDTO(BaseModel):
    """DTO for work experience."""
    title: str = Field(..., min_length=1, max_length=100)
    company: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = Field(..., min_length=1, max_length=2000)
    achievements: List[str] = Field(default_factory=list)

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('is_current')
    def validate_current_position(cls, v, values):
        if v and 'end_date' in values and values.get('end_date') is not None:
            raise ValueError('current position cannot have end_date')
        return v


class EducationDTO(BaseModel):
    """DTO for education."""
    institution: str = Field(..., min_length=1, max_length=100)
    degree: str = Field(..., min_length=1, max_length=100)
    field_of_study: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: List[str] = Field(default_factory=list)

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


class LanguageDTO(BaseModel):
    """DTO for language proficiency."""
    name: str = Field(..., min_length=1, max_length=50)
    proficiency: str = Field(..., regex=r'^(beginner|intermediate|advanced|native)$')


class CertificationDTO(BaseModel):
    """DTO for certification."""
    name: str = Field(..., min_length=1, max_length=100)
    issuer: str = Field(..., min_length=1, max_length=100)
    date_obtained: date
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = Field(None, max_length=100)
    verification_url: Optional[HttpUrl] = None

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'date_obtained' in values and v < values['date_obtained']:
            raise ValueError('expiry_date must be after date_obtained')
        return v


class SkillsDTO(BaseModel):
    """DTO for skills section."""
    technical: List[str] = Field(default_factory=list)
    soft: List[str] = Field(default_factory=list)
    languages: List[LanguageDTO] = Field(default_factory=list)
    certifications: List[CertificationDTO] = Field(default_factory=list)


class ProjectDTO(BaseModel):
    """DTO for project."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    technologies: List[str] = Field(default_factory=list)
    url: Optional[HttpUrl] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values.get('start_date') and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v


# Profile DTOs
class CreateProfileDTO(BaseModel):
    """DTO for creating a new profile."""
    personal_info: PersonalInfoDTO
    professional_summary: Optional[str] = Field(None, max_length=1000)
    experiences: List[ExperienceDTO] = Field(default_factory=list)
    education: List[EducationDTO] = Field(default_factory=list)
    skills: SkillsDTO = Field(default_factory=SkillsDTO)
    projects: List[ProjectDTO] = Field(default_factory=list)


class UpdateProfileDTO(BaseModel):
    """DTO for updating an existing profile."""
    personal_info: Optional[PersonalInfoDTO] = None
    professional_summary: Optional[str] = Field(None, max_length=1000)
    experiences: Optional[List[ExperienceDTO]] = None
    education: Optional[List[EducationDTO]] = None
    skills: Optional[SkillsDTO] = None
    projects: Optional[List[ProjectDTO]] = None


class ProfileDTO(BaseModel):
    """DTO for profile response."""
    id: UUID
    user_id: UUID
    personal_info: PersonalInfoDTO
    professional_summary: Optional[str]
    experiences: List[ExperienceDTO]
    education: List[EducationDTO]
    skills: SkillsDTO
    projects: List[ProjectDTO]
    version: int
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string

    class Config:
        from_attributes = True


class ProfileSummaryDTO(BaseModel):
    """DTO for profile summary (list view)."""
    id: UUID
    user_id: UUID
    full_name: str
    email: str
    location: Optional[str]
    version: int
    updated_at: str
    years_experience: float


# Experience CRUD DTOs
class AddExperienceDTO(BaseModel):
    """DTO for adding experience."""
    experience: ExperienceDTO


class UpdateExperienceDTO(BaseModel):
    """DTO for updating experience."""
    index: int = Field(..., ge=0)
    experience: ExperienceDTO


class RemoveExperienceDTO(BaseModel):
    """DTO for removing experience."""
    index: int = Field(..., ge=0)


# Education CRUD DTOs
class AddEducationDTO(BaseModel):
    """DTO for adding education."""
    education: EducationDTO


class UpdateEducationDTO(BaseModel):
    """DTO for updating education."""
    index: int = Field(..., ge=0)
    education: EducationDTO


class RemoveEducationDTO(BaseModel):
    """DTO for removing education."""
    index: int = Field(..., ge=0)


# Project CRUD DTOs
class AddProjectDTO(BaseModel):
    """DTO for adding project."""
    project: ProjectDTO


class UpdateProjectDTO(BaseModel):
    """DTO for updating project."""
    index: int = Field(..., ge=0)
    project: ProjectDTO


class RemoveProjectDTO(BaseModel):
    """DTO for removing project."""
    index: int = Field(..., ge=0)


# Analytics DTOs
class ProfileAnalyticsDTO(BaseModel):
    """DTO for profile analytics."""
    total_experiences: int
    total_education: int
    total_projects: int
    technical_skills_count: int
    soft_skills_count: int
    languages_count: int
    certifications_count: int
    years_experience: float
    top_technologies: List[str]