"""Pydantic schemas for AI Generation API."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# Enhancement Schemas
class EnhanceProfileRequest(BaseModel):
    """Request to enhance profile."""
    profile_id: UUID
    custom_prompt: Optional[str] = Field(None, max_length=500)


class EnhanceProfileResponse(BaseModel):
    """Response for profile enhancement."""
    profile_id: UUID
    status: str
    enhanced_sections: Dict[str, Any]
    writing_style_used: Optional[Dict[str, Any]] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Ranking Schemas
class CreateRankingRequest(BaseModel):
    """Request to create ranking."""
    job_id: UUID
    custom_prompt: Optional[str] = Field(None, max_length=500)


class RankingResponse(BaseModel):
    """Response for ranking."""
    id: UUID
    user_id: int
    job_id: UUID
    ranked_experience_ids: List[str]
    ranked_project_ids: List[str]
    ranking_rationale: Optional[str] = None
    keyword_matches: Optional[Dict[str, int]] = None
    relevance_scores: Optional[Dict[str, float]] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime


# Generation Schemas
class GenerateResumeRequest(BaseModel):
    """Request to generate resume."""
    job_id: UUID
    max_experiences: int = Field(default=5, ge=1, le=10)
    max_projects: int = Field(default=3, ge=0)
    include_summary: bool = True
    custom_prompt: Optional[str] = Field(None, max_length=500)


class GenerateCoverLetterRequest(BaseModel):
    """Request to generate cover letter."""
    job_id: UUID
    company_name: Optional[str] = None
    hiring_manager_name: Optional[str] = None
    max_paragraphs: int = Field(default=4, ge=3, le=6)
    custom_prompt: Optional[str] = Field(None, max_length=500)


class GenerationResponse(BaseModel):
    """Response for generation."""
    generation_id: UUID
    job_id: UUID
    document_type: str
    status: str
    content_text: str
    content_structured: Optional[str] = None
    ats_score: Optional[float] = None
    ats_feedback: Optional[str] = None
    llm_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class GenerationHistoryResponse(BaseModel):
    """Response for generation history."""
    generations: List[GenerationResponse]
    total: int
    limit: int
    offset: int
