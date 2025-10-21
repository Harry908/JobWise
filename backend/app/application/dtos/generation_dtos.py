# Generation DTOs

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class GenerationStatus(str, Enum):
    """Generation status enumeration."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentType(str, Enum):
    """Document type enumeration."""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"


class GenerationOptions(BaseModel):
    """Options for generation customization."""
    template: Optional[str] = Field(None, description="Resume template to use")
    length: Optional[str] = Field(None, description="Document length preference")
    focus_areas: Optional[List[str]] = Field(default_factory=list, description="Areas to emphasize")
    include_cover_letter: Optional[bool] = Field(False, description="Generate cover letter too")
    custom_instructions: Optional[str] = Field(None, description="Custom generation instructions")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "template": "modern",
                "length": "one_page",
                "focus_areas": ["backend_development", "leadership"],
                "include_cover_letter": True,
                "custom_instructions": "Emphasize cloud architecture experience"
            }
        }
    )


class ResumeGenerationRequest(BaseModel):
    """Request to start resume generation."""
    profile_id: str = Field(..., description="Profile ID to use for generation")
    job_id: str = Field(..., description="Job ID to tailor resume for")
    options: Optional[GenerationOptions] = Field(None, description="Generation options")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profile_id": "profile-uuid",
                "job_id": "job-uuid",
                "options": {
                    "template": "modern",
                    "focus_areas": ["backend_development"],
                    "include_cover_letter": True
                }
            }
        }
    )


class CoverLetterGenerationRequest(BaseModel):
    """Request to start cover letter generation."""
    profile_id: str = Field(..., description="Profile ID to use for generation")
    job_id: str = Field(..., description="Job ID to tailor cover letter for")
    options: Optional[GenerationOptions] = Field(None, description="Generation options")


class GenerationProgress(BaseModel):
    """Progress information for ongoing generation."""
    current_stage: int = Field(..., description="Current pipeline stage (1-5)")
    total_stages: int = Field(5, description="Total number of stages")
    percentage: int = Field(..., ge=0, le=100, description="Completion percentage")
    stage_name: Optional[str] = Field(None, description="Name of current stage")
    stage_description: Optional[str] = Field(None, description="Description of current stage")

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


class GenerationResult(BaseModel):
    """Result of completed generation."""
    document_id: str = Field(..., description="Generated document ID")
    ats_score: float = Field(..., ge=0.0, le=1.0, description="ATS compatibility score")
    match_percentage: int = Field(..., ge=0, le=100, description="Job match percentage")
    keyword_coverage: float = Field(..., ge=0.0, le=1.0, description="Keyword coverage ratio")
    pdf_url: str = Field(..., description="URL to download PDF")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": "doc-uuid",
                "ats_score": 0.87,
                "match_percentage": 82,
                "keyword_coverage": 0.91,
                "pdf_url": "/api/v1/documents/doc-uuid/download",
                "recommendations": [
                    "Add AWS certification to skills",
                    "Quantify team size in leadership experience"
                ]
            }
        }
    )


class GenerationDTO(BaseModel):
    """Complete generation information."""
    generation_id: str = Field(..., description="Generation unique identifier")
    status: GenerationStatus = Field(..., description="Current generation status")
    progress: Optional[GenerationProgress] = Field(None, description="Progress if in progress")
    result: Optional[GenerationResult] = Field(None, description="Result if completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    profile_id: str = Field(..., description="Profile ID used")
    job_id: str = Field(..., description="Job ID used")
    tokens_used: int = Field(0, description="Tokens consumed")
    generation_time: Optional[float] = Field(None, description="Time taken in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generation_id": "gen-uuid",
                "status": "completed",
                "progress": None,
                "result": {
                    "document_id": "doc-uuid",
                    "ats_score": 0.87,
                    "match_percentage": 82,
                    "keyword_coverage": 0.91,
                    "pdf_url": "/api/v1/documents/doc-uuid/download",
                    "recommendations": []
                },
                "profile_id": "profile-uuid",
                "job_id": "job-uuid",
                "tokens_used": 7850,
                "generation_time": 5.2,
                "created_at": "2025-10-21T10:30:00Z",
                "completed_at": "2025-10-21T10:30:05Z"
            }
        }
    )


class GenerationSummaryDTO(BaseModel):
    """Summary of generation for listing."""
    generation_id: str = Field(..., description="Generation ID")
    status: GenerationStatus = Field(..., description="Generation status")
    document_type: DocumentType = Field(..., description="Type of document generated")
    job_title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    ats_score: Optional[float] = Field(None, description="ATS score if completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generation_id": "gen-uuid",
                "status": "completed",
                "document_type": "resume",
                "job_title": "Senior Python Developer",
                "company": "TechCorp",
                "ats_score": 0.87,
                "created_at": "2025-10-21T10:30:00Z",
                "completed_at": "2025-10-21T10:30:05Z"
            }
        }
    )


class GenerationListResponse(BaseModel):
    """Response for listing generations."""
    generations: List[GenerationSummaryDTO] = Field(..., description="List of generations")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    statistics: Dict[str, Any] = Field(..., description="Generation statistics")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generations": [],
                "pagination": {
                    "total": 25,
                    "limit": 20,
                    "offset": 0,
                    "has_next": True,
                    "has_previous": False
                },
                "statistics": {
                    "total_generations": 25,
                    "completed": 22,
                    "failed": 2,
                    "in_progress": 1,
                    "average_ats_score": 0.84
                }
            }
        }
    )


class RegenerateRequest(BaseModel):
    """Request to regenerate with updated options."""
    options: Optional[GenerationOptions] = Field(None, description="Updated generation options")


class GenerationResultContent(BaseModel):
    """Content of generated document."""
    generation_id: str = Field(..., description="Generation ID")
    document_id: str = Field(..., description="Document ID")
    document_type: DocumentType = Field(..., description="Document type")
    content: Dict[str, Any] = Field(..., description="Document content in multiple formats")
    ats_score: float = Field(..., description="ATS score")
    match_percentage: int = Field(..., description="Match percentage")
    keyword_coverage: float = Field(..., description="Keyword coverage")
    keywords_matched: int = Field(..., description="Number of keywords matched")
    keywords_total: int = Field(..., description="Total keywords")
    pdf_url: str = Field(..., description="PDF download URL")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generation_id": "gen-uuid",
                "document_id": "doc-uuid",
                "document_type": "resume",
                "content": {
                    "text": "John Doe\nSoftware Engineer\n...",
                    "html": "<html>...</html>",
                    "markdown": "# John Doe\n..."
                },
                "ats_score": 0.87,
                "match_percentage": 82,
                "keyword_coverage": 0.91,
                "keywords_matched": 15,
                "keywords_total": 18,
                "pdf_url": "/api/v1/documents/doc-uuid/download",
                "recommendations": [],
                "metadata": {
                    "template": "modern",
                    "tokens_used": 7850,
                    "generation_time": 5.2
                }
            }
        }
    )


class ResumeTemplateDTO(BaseModel):
    """Resume template information."""
    id: str = Field(..., description="Template ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    preview_url: Optional[str] = Field(None, description="Preview image URL")
    recommended_for: List[str] = Field(default_factory=list, description="Recommended use cases")
    ats_friendly: bool = Field(True, description="ATS compatibility")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "modern",
                "name": "Modern",
                "description": "Clean, contemporary design",
                "preview_url": "/templates/modern/preview.png",
                "recommended_for": ["tech", "startup"],
                "ats_friendly": True
            }
        }
    )


class TemplatesResponse(BaseModel):
    """Response containing available templates."""
    templates: List[ResumeTemplateDTO] = Field(..., description="Available templates")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "templates": [
                    {
                        "id": "modern",
                        "name": "Modern",
                        "description": "Clean, contemporary design",
                        "recommended_for": ["tech", "startup"],
                        "ats_friendly": True
                    }
                ]
            }
        }
    )