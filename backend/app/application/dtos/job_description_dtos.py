"""Job Description DTOs for simplified CRUD API"""

from typing import List, Optional, Literal
from datetime import datetime

from pydantic import BaseModel, Field, model_validator, ConfigDict


class CreateJobDescriptionRequest(BaseModel):
    """
    Create job description from raw text or structured data.

    The API accepts either:
    1. raw_text: Plain text job posting (will be parsed)
    2. Structured fields: Pre-parsed job data

    If raw_text is provided, it takes precedence and other fields
    are used as fallback/override.
    """

    # Option 1: Raw text (user copy-paste)
    raw_text: Optional[str] = Field(None, max_length=20000, description="Raw job posting text")

    # Option 2: Structured data (or override for raw_text)
    title: Optional[str] = Field(None, max_length=200, description="Job title")
    company: Optional[str] = Field(None, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    description: Optional[str] = Field(None, max_length=10000, description="Job description")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, description="Job benefits")

    # Optional metadata
    job_type: Optional[str] = Field(None, description="Job type (e.g., full-time, part-time)")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary")
    salary_currency: str = Field(default="USD", max_length=3, description="Salary currency code")
    remote_work: Optional[str] = Field(None, description="Remote work policy")

    # Source info
    source: Literal["user_created", "saved_external"] = Field(
        default="user_created",
        description="Source of job (user_created or saved_external)"
    )
    external_id: Optional[str] = Field(None, description="External API job ID")
    external_url: Optional[str] = Field(None, description="Application URL")

    @model_validator(mode='after')
    def validate_data(self):
        """Ensure either raw_text or (title + company + description) provided"""
        if not self.raw_text:
            if not (self.title and self.company and self.description):
                raise ValueError(
                    "Must provide either raw_text OR (title, company, description)"
                )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "description": "User copy-paste example",
                    "value": {
                        "raw_text": """Senior Software Engineer

TechCorp Inc.
San Francisco, CA (Hybrid)

We are seeking a Senior Software Engineer to join our backend team...

Requirements:
- 5+ years Python experience
- FastAPI or Django
- PostgreSQL, Redis

Benefits:
- Competitive salary
- Health insurance
""",
                        "source": "user_created"
                    }
                },
                {
                    "description": "Structured data from external API",
                    "value": {
                        "title": "Senior Software Engineer",
                        "company": "TechCorp Inc.",
                        "location": "San Francisco, CA",
                        "description": "We are seeking...",
                        "requirements": ["5+ years Python", "FastAPI"],
                        "benefits": ["Health insurance", "401k"],
                        "job_type": "full-time",
                        "remote_work": "hybrid",
                        "source": "saved_external",
                        "external_id": "indeed_12345",
                        "external_url": "https://indeed.com/job/12345"
                    }
                }
            ]
        }
    )


class UpdateJobDescriptionRequest(BaseModel):
    """Update job description (all fields optional)"""

    title: Optional[str] = Field(None, max_length=200, description="Job title")
    company: Optional[str] = Field(None, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    description: Optional[str] = Field(None, max_length=10000, description="Job description")
    requirements: Optional[List[str]] = Field(None, description="Job requirements")
    benefits: Optional[List[str]] = Field(None, description="Job benefits")
    job_type: Optional[str] = Field(None, description="Job type")
    experience_level: Optional[str] = Field(None, description="Experience level")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary")
    remote_work: Optional[str] = Field(None, description="Remote work policy")
    status: Optional[Literal["active", "archived"]] = Field(None, description="Job status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Job Title",
                "status": "active"
            }
        }
    )


class JobDescriptionResponse(BaseModel):
    """Job description response"""

    id: str = Field(..., description="Job description ID")
    user_id: str = Field(..., description="Owner user ID")

    # Core fields
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, description="Job benefits")

    # Metadata
    job_type: Optional[str] = Field(None, description="Job type")
    experience_level: Optional[str] = Field(None, description="Experience level")
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    salary_currency: str = Field(default="USD", description="Salary currency")
    remote_work: Optional[str] = Field(None, description="Remote work policy")

    # Source
    source: str = Field(..., description="Source (user_created or saved_external)")
    external_id: Optional[str] = Field(None, description="External API ID")
    external_url: Optional[str] = Field(None, description="Application URL")
    raw_text: Optional[str] = Field(None, description="Original raw text")

    # Status
    status: str = Field(default="active", description="Job status")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "user-uuid-here",
                "title": "Senior Software Engineer",
                "company": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "description": "We are seeking...",
                "requirements": ["5+ years Python", "FastAPI"],
                "benefits": ["Health insurance", "401k"],
                "job_type": "full-time",
                "experience_level": "senior",
                "salary_min": 120000,
                "salary_max": 160000,
                "salary_currency": "USD",
                "remote_work": "hybrid",
                "source": "user_created",
                "external_id": None,
                "external_url": None,
                "raw_text": "Senior Software Engineer...",
                "status": "active",
                "created_at": "2025-10-20T10:00:00Z",
                "updated_at": "2025-10-20T10:00:00Z"
            }
        }
    )


class JobDescriptionListResponse(BaseModel):
    """List of job descriptions with pagination"""

    jobs: List[JobDescriptionResponse] = Field(..., description="List of job descriptions")
    total: int = Field(..., ge=0, description="Total count")
    limit: int = Field(..., ge=1, le=100, description="Items per page")
    offset: int = Field(..., ge=0, description="Pagination offset")
    has_more: bool = Field(..., description="Whether more results exist")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jobs": [],
                "total": 25,
                "limit": 20,
                "offset": 0,
                "has_more": True
            }
        }
    )
