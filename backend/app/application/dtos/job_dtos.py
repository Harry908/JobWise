# Job DTOs

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator
from pydantic.types import constr


class SalaryRangeDTO(BaseModel):
    """Salary range DTO"""
    min: int = Field(..., ge=0, description="Minimum salary")
    max: int = Field(..., ge=0, description="Maximum salary")
    currency: str = Field(default="USD", description="Currency code")

    @field_validator('max')
    @classmethod
    def max_greater_than_min(cls, v, info):
        if info.data and 'min' in info.data and v < info.data['min']:
            raise ValueError('max must be greater than or equal to min')
        return v


class JobSummaryDTO(BaseModel):
    """Job summary for list views"""
    id: str = Field(..., description="Job unique identifier")
    title: str = Field(..., max_length=200, description="Job title")
    company: str = Field(..., max_length=100, description="Company name")
    location: str = Field(..., max_length=100, description="Job location")
    job_type: str = Field(..., pattern="^(full-time|part-time|contract|freelance)$", description="Job type")
    experience_level: str = Field(..., pattern="^(entry|mid|senior)$", description="Experience level")
    salary_range: Optional[SalaryRangeDTO] = Field(None, description="Salary range")
    posted_date: datetime = Field(..., description="Job posting date")
    remote_work_policy: str = Field(..., pattern="^(remote|hybrid|onsite)$", description="Remote work policy")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Job tags")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Senior Python Backend Developer",
                "company": "TechCorp Solutions",
                "location": "Seattle, WA",
                "job_type": "full-time",
                "experience_level": "senior",
                "salary_range": {
                    "min": 120000,
                    "max": 160000,
                    "currency": "USD"
                },
                "posted_date": "2024-10-15T10:00:00Z",
                "remote_work_policy": "hybrid",
                "tags": ["python", "fastapi", "postgresql"]
            }
        }


class JobDTO(BaseModel):
    """Complete job details DTO"""
    id: str = Field(..., description="Job unique identifier")
    title: str = Field(..., max_length=200, description="Job title")
    company: str = Field(..., max_length=100, description="Company name")
    location: str = Field(..., max_length=100, description="Job location")
    job_type: str = Field(..., pattern="^(full-time|part-time|contract|freelance)$", description="Job type")
    experience_level: str = Field(..., pattern="^(entry|mid|senior)$", description="Experience level")
    salary_range: Optional[SalaryRangeDTO] = Field(None, description="Salary range")
    description: str = Field(..., max_length=5000, description="Job description")
    requirements: List[str] = Field(default_factory=list, max_items=20, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, max_items=20, description="Job benefits")
    posted_date: datetime = Field(..., description="Job posting date")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    company_size: str = Field(..., pattern="^(1-10|10-50|50-200|200-500|500-1000|1000\\+)$", description="Company size range")
    industry: str = Field(..., max_length=50, description="Industry")
    remote_work_policy: str = Field(..., pattern="^(remote|hybrid|onsite)$", description="Remote work policy")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Job tags")

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Senior Python Backend Developer",
                "company": "TechCorp Solutions",
                "location": "Seattle, WA",
                "job_type": "full-time",
                "experience_level": "senior",
                "salary_range": {
                    "min": 120000,
                    "max": 160000,
                    "currency": "USD"
                },
                "description": "We are seeking a Senior Python Backend Developer...",
                "requirements": [
                    "5+ years of Python development experience",
                    "Strong knowledge of FastAPI or Django"
                ],
                "benefits": [
                    "Competitive salary and equity package",
                    "Health, dental, and vision insurance"
                ],
                "posted_date": "2024-10-15T10:00:00Z",
                "application_deadline": "2024-11-15T23:59:59Z",
                "company_size": "500-1000",
                "industry": "Technology",
                "remote_work_policy": "hybrid",
                "tags": ["python", "fastapi", "postgresql"]
            }
        }


class JobSearchRequestDTO(BaseModel):
    """Job search request DTO"""
    query: Optional[str] = Field(None, max_length=100, description="Search query (keywords)")
    location: Optional[str] = Field(None, max_length=100, description="Location filter")
    job_type: Optional[str] = Field(None, pattern="^(full-time|part-time|contract|freelance)$", description="Job type filter")
    experience_level: Optional[str] = Field(None, pattern="^(entry|mid|senior)$", description="Experience level filter")
    remote_work_policy: Optional[str] = Field(None, pattern="^(remote|hybrid|onsite)$", description="Remote work policy filter")
    industry: Optional[str] = Field(None, max_length=50, description="Industry filter")
    company_size: Optional[str] = Field(None, pattern="^(1-10|10-50|50-200|200-500|500-1000|1000\\+)$", description="Company size filter")
    tags: Optional[List[str]] = Field(None, max_items=10, description="Tag filters")
    min_salary: Optional[int] = Field(None, ge=0, description="Minimum salary filter")
    max_salary: Optional[int] = Field(None, ge=0, description="Maximum salary filter")
    limit: int = Field(default=20, ge=1, le=100, description="Results per page")
    offset: int = Field(default=0, ge=0, description="Pagination offset")

    class Config:
        schema_extra = {
            "example": {
                "query": "python backend",
                "location": "Seattle",
                "job_type": "full-time",
                "experience_level": "senior",
                "remote_work_policy": "hybrid",
                "industry": "Technology",
                "tags": ["python", "fastapi"],
                "min_salary": 100000,
                "max_salary": 150000,
                "limit": 20,
                "offset": 0
            }
        }


class JobSearchResponseDTO(BaseModel):
    """Job search response DTO"""
    jobs: List[JobSummaryDTO] = Field(..., description="List of jobs")
    total_count: int = Field(..., ge=0, description="Total number of matching jobs")
    limit: int = Field(..., ge=1, le=100, description="Results per page")
    offset: int = Field(..., ge=0, description="Pagination offset")
    has_more: bool = Field(..., description="Whether there are more results")

    class Config:
        schema_extra = {
            "example": {
                "jobs": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "title": "Senior Python Backend Developer",
                        "company": "TechCorp Solutions",
                        "location": "Seattle, WA",
                        "job_type": "full-time",
                        "experience_level": "senior",
                        "salary_range": {
                            "min": 120000,
                            "max": 160000,
                            "currency": "USD"
                        },
                        "posted_date": "2024-10-15T10:00:00Z",
                        "remote_work_policy": "hybrid",
                        "tags": ["python", "fastapi", "postgresql"]
                    }
                ],
                "total_count": 1,
                "limit": 20,
                "offset": 0,
                "has_more": False
            }
        }


class JobFiltersDTO(BaseModel):
    """Available job filters DTO"""
    job_types: List[str] = Field(..., description="Available job types")
    experience_levels: List[str] = Field(..., description="Available experience levels")
    remote_work_policies: List[str] = Field(..., description="Available remote work policies")
    industries: List[str] = Field(..., description="Available industries")
    company_sizes: List[str] = Field(..., description="Available company sizes")
    locations: List[str] = Field(..., description="Available locations")
    tags: List[str] = Field(..., description="Available tags")
    salary_ranges: Dict[str, Any] = Field(..., description="Salary range statistics")

    class Config:
        schema_extra = {
            "example": {
                "job_types": ["full-time", "part-time", "contract"],
                "experience_levels": ["entry", "mid", "senior"],
                "remote_work_policies": ["remote", "hybrid", "onsite"],
                "industries": ["Technology", "Healthcare", "Finance"],
                "company_sizes": ["1-10", "10-50", "50-200", "200-500"],
                "locations": ["Seattle, WA", "San Francisco, CA", "New York, NY"],
                "tags": ["python", "javascript", "react", "aws"],
                "salary_ranges": {
                    "min": 50000,
                    "max": 200000,
                    "average": 110000
                }
            }
        }