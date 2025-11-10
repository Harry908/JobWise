"""Generation API DTOs (Request/Response models)."""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# Request DTOs
class GenerationOptionsDTO(BaseModel):
    """Generation options request model."""
    template: Literal["modern", "classic", "creative"] = Field(default="modern")
    length: Literal["one_page", "two_page"] = Field(default="one_page")
    focus_areas: List[str] = Field(default_factory=list, max_length=5)
    include_cover_letter: bool = Field(default=False)
    custom_instructions: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template": "modern",
                "length": "one_page",
                "focus_areas": ["backend_development", "leadership"],
                "include_cover_letter": False,
                "custom_instructions": "Emphasize cloud architecture experience"
            }
        }
    )


class GenerateResumeRequest(BaseModel):
    """Request to generate resume."""
    profile_id: str = Field(..., description="Profile ID to use for generation")
    job_id: str = Field(..., description="Job ID to tailor resume for")
    options: Optional[GenerationOptionsDTO] = Field(None, description="Generation options")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_id": "job-550e8400-e29b-41d4-a716-446655440001",
                "options": {
                    "template": "modern",
                    "length": "one_page"
                }
            }
        }
    )


class GenerateCoverLetterRequest(BaseModel):
    """Request to generate cover letter."""
    profile_id: str = Field(..., description="Profile ID to use for generation")
    job_id: str = Field(..., description="Job ID to tailor cover letter for")
    options: Optional[GenerationOptionsDTO] = Field(None, description="Generation options")


class RegenerateRequest(BaseModel):
    """Request to regenerate with new options."""
    options: Optional[GenerationOptionsDTO] = Field(None, description="Updated generation options")


# Response DTOs
class GenerationProgressDTO(BaseModel):
    """Progress tracking response."""
    current_stage: int = Field(..., ge=0, le=5)
    total_stages: int = Field(default=5)
    percentage: int = Field(..., ge=0, le=100)
    stage_name: Optional[str] = None
    stage_description: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_stage": 2,
                "total_stages": 5,
                "percentage": 40,
                "stage_name": "Profile Compilation",
                "stage_description": "Scoring profile content by relevance"
            }
        }
    )


class GenerationResultDTO(BaseModel):
    """Generation result response."""
    document_id: str
    ats_score: float = Field(..., ge=0.0, le=1.0)
    match_percentage: int = Field(..., ge=0, le=100)
    keyword_coverage: float = Field(..., ge=0.0, le=1.0)
    keywords_matched: Optional[int] = None
    keywords_total: Optional[int] = None
    pdf_url: str
    recommendations: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "doc-550e8400-e29b-41d4-a716-446655440000",
                "ats_score": 0.87,
                "match_percentage": 82,
                "keyword_coverage": 0.91,
                "keywords_matched": 15,
                "keywords_total": 18,
                "pdf_url": "/api/v1/documents/doc-550e8400-e29b-41d4-a716-446655440000/download",
                "recommendations": [
                    "Add AWS certification to skills",
                    "Quantify team size in leadership experience"
                ]
            }
        }
    )


class GenerationResponse(BaseModel):
    """Generation response model."""
    id: str = Field(..., description="Generation ID (note: 'id' not 'generation_id')")
    status: Literal["pending", "generating", "completed", "failed", "cancelled"]
    progress: GenerationProgressDTO
    profile_id: str
    job_id: str
    document_type: Literal["resume", "cover_letter"] = "resume"
    result: Optional[GenerationResultDTO] = None
    error_message: Optional[str] = None
    tokens_used: int = Field(default=0, ge=0)
    generation_time: Optional[float] = Field(None, ge=0)
    estimated_completion: Optional[str] = None  # ISO datetime string
    created_at: str  # ISO datetime string
    started_at: Optional[str] = None  # ISO datetime string
    completed_at: Optional[str] = None  # ISO datetime string
    updated_at: Optional[str] = None  # ISO datetime string

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "gen-550e8400-e29b-41d4-a716-446655440000",
                "status": "generating",
                "progress": {
                    "current_stage": 2,
                    "total_stages": 5,
                    "percentage": 40,
                    "stage_name": "Profile Compilation",
                    "stage_description": "Scoring profile content by relevance"
                },
                "profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "job_id": "job-550e8400-e29b-41d4-a716-446655440001",
                "document_type": "resume",
                "tokens_used": 3500,
                "estimated_completion": "2025-11-07T10:30:30Z",
                "created_at": "2025-11-07T10:30:00Z",
                "updated_at": "2025-11-07T10:30:20Z"
            }
        }
    )


class GenerationDetailResultResponse(BaseModel):
    """Detailed generation result with content."""
    id: str
    document_id: str
    document_type: Literal["resume", "cover_letter"]
    content: Dict[str, str] = Field(..., description="Content in multiple formats (text, html, markdown)")
    ats_score: float = Field(..., ge=0.0, le=1.0)
    match_percentage: int = Field(..., ge=0, le=100)
    keyword_coverage: float = Field(..., ge=0.0, le=1.0)
    keywords_matched: int
    keywords_total: int
    pdf_url: str
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")


class GenerationListItemDTO(BaseModel):
    """Generation list item (summary view)."""
    id: str
    status: Literal["pending", "generating", "completed", "failed", "cancelled"]
    document_type: Literal["resume", "cover_letter"]
    job_title: str
    company: str
    ats_score: Optional[float] = None
    created_at: str  # ISO datetime string
    completed_at: Optional[str] = None  # ISO datetime string


class PaginationDTO(BaseModel):
    """Pagination metadata."""
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class GenerationListResponse(BaseModel):
    """Response for list of generations."""
    generations: List[GenerationListItemDTO]
    pagination: PaginationDTO
    statistics: Dict[str, Any] = Field(default_factory=dict)


class TemplateDTO(BaseModel):
    """Template information."""
    id: str
    name: str
    description: str
    preview_url: str
    recommended_for: List[str]
    ats_friendly: bool


class TemplateListResponse(BaseModel):
    """Response for list of templates."""
    templates: List[TemplateDTO]
