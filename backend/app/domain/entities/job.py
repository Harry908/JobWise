"""Job domain entity."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Job domain entity representing a job description."""
    
    id: str = Field(..., description="UUID of the job")
    user_id: Optional[int] = Field(None, description="Owner user ID (nullable for external jobs)")
    source: str = Field(..., description="Job source: user_created, indeed, linkedin, mock, etc.")
    title: str = Field(..., min_length=1, max_length=200, description="Job title")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    description: Optional[str] = Field(None, max_length=10000, description="Full job description")
    raw_text: Optional[str] = Field(None, max_length=15000, description="Original pasted text")
    parsed_keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, description="Job benefits")
    salary_range: Optional[str] = Field(None, description="Salary range")
    remote: bool = Field(default=False, description="Remote position flag")
    status: str = Field(default="active", description="Job status: active, archived, draft")
    application_status: str = Field(default="not_applied", description="Application status: not_applied, preparing, applied, interviewing, offer_received, rejected, accepted, withdrawn")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "job_123",
                "user_id": 1,
                "source": "user_created",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "Seattle, WA",
                "description": "We are looking for...",
                "raw_text": "Senior Python Developer at Tech Corp...",
                "parsed_keywords": ["python", "fastapi", "aws"],
                "requirements": ["5+ years Python", "AWS experience"],
                "benefits": ["Health insurance", "Remote work"],
                "salary_range": "120000-180000",
                "remote": True,
                "status": "active",
                "application_status": "not_applied",
                "created_at": "2025-11-02T10:00:00Z",
                "updated_at": "2025-11-02T10:00:00Z"
            }
        }
    }
