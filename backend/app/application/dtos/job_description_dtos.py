"""Data transfer objects for job description operations."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator, ConfigDict


# Value Object DTOs
class JobDescriptionMetadataDTO(BaseModel):
    """DTO for job description metadata."""
    keywords: List[str] = Field(default_factory=list)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    experience_level: str = Field(default="", max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    remote_policy: Optional[str] = Field(None, max_length=50)
    salary_range_min: Optional[int] = Field(None, ge=0)
    salary_range_max: Optional[int] = Field(None, ge=0)
    salary_currency: str = Field(default="USD", max_length=3)
    location: Optional[str] = Field(None, max_length=200)
    created_from_url: Optional[HttpUrl] = None

    @validator('salary_range_max')
    def validate_salary_range(cls, v, values):
        if v is not None and values.get('salary_range_min') is not None:
            if v < values['salary_range_min']:
                raise ValueError('salary_range_max must be greater than or equal to salary_range_min')
        return v


# Job Description DTOs
class CreateJobDescriptionDTO(BaseModel):
    """DTO for creating a new job description."""
    title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    requirements: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    source: str = Field(default="manual", pattern=r'^(manual|scraped|uploaded)$')
    metadata: Optional[JobDescriptionMetadataDTO] = None
    created_from_url: Optional[HttpUrl] = None


class UpdateJobDescriptionDTO(BaseModel):
    """DTO for updating an existing job description."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    metadata: Optional[JobDescriptionMetadataDTO] = None


class JobDescriptionDTO(BaseModel):
    """DTO for job description response."""
    id: UUID
    user_id: UUID
    title: str
    company: str
    description: str
    requirements: List[str]
    benefits: List[str]
    status: str
    source: str
    metadata: JobDescriptionMetadataDTO
    version: int
    created_at: str  # ISO format datetime string
    updated_at: str  # ISO format datetime string

    model_config = ConfigDict(from_attributes=True)

class JobDescriptionSummaryDTO(BaseModel):
    """DTO for job description summary (list view)."""
    id: UUID
    user_id: UUID
    title: str
    company: str
    status: str
    version: int
    created_at: str
    updated_at: str
    keywords_count: int
    technical_skills_count: int
    requirements_count: int


# CRUD Operation DTOs
class ParseJobDescriptionDTO(BaseModel):
    """DTO for parsing job description."""
    pass  # No additional fields needed


class ActivateJobDescriptionDTO(BaseModel):
    """DTO for activating job description."""
    pass  # No additional fields needed


class ArchiveJobDescriptionDTO(BaseModel):
    """DTO for archiving job description."""
    pass  # No additional fields needed


# Search and Filter DTOs
class JobDescriptionSearchDTO(BaseModel):
    """DTO for job description search parameters."""
    query: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern=r'^(draft|active|archived)$')
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class JobDescriptionListDTO(BaseModel):
    """DTO for job description list response."""
    items: List[JobDescriptionSummaryDTO]
    total: int
    limit: int
    offset: int


# Analytics DTOs
class JobDescriptionAnalyticsDTO(BaseModel):
    """DTO for job description analytics."""
    total_job_descriptions: int
    active_job_descriptions: int
    draft_job_descriptions: int
    archived_job_descriptions: int
    average_keywords_per_description: float
    average_technical_skills_per_description: float
    average_requirements_per_description: float
    most_common_technical_skills: List[str]
    most_common_industries: List[str]
    experience_level_distribution: dict  # e.g., {"entry": 5, "mid": 10, "senior": 8}