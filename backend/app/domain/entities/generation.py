"""Generation domain entities."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid


class GenerationProgress(BaseModel):
    """Progress tracking for generation pipeline."""
    current_stage: int = Field(default=0, ge=0, le=2)  # Updated to 2-stage pipeline
    total_stages: int = Field(default=2)  # Updated to 2-stage pipeline
    percentage: int = Field(default=0, ge=0, le=100)
    stage_name: Optional[str] = None
    stage_description: Optional[str] = None


class GenerationOptions(BaseModel):
    """Options for generation customization."""
    template: Literal["modern", "classic", "creative"] = "modern"
    length: Literal["one_page", "two_page"] = "one_page"
    focus_areas: List[str] = Field(default_factory=list, max_length=5)
    include_cover_letter: bool = False
    custom_instructions: Optional[str] = Field(None, max_length=500)


class GenerationResult(BaseModel):
    """Result of completed generation."""
    document_id: str
    ats_score: float = Field(..., ge=0.0, le=1.0)
    match_percentage: int = Field(..., ge=0, le=100)
    keyword_coverage: float = Field(..., ge=0.0, le=1.0)
    keywords_matched: Optional[int] = None
    keywords_total: Optional[int] = None
    pdf_url: str
    recommendations: List[str] = Field(default_factory=list)
    content: Optional[Dict[str, str]] = None  # text, html, markdown


class Generation(BaseModel):
    """Generation domain entity."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    profile_id: str
    job_id: str
    document_type: Literal["resume", "cover_letter"] = "resume"
    status: Literal["pending", "generating", "completed", "failed", "cancelled"] = "pending"
    current_stage: int = Field(default=0, ge=0, le=2)  # Updated to 2-stage pipeline
    total_stages: int = Field(default=2)  # Updated to 2-stage pipeline
    stage_name: Optional[str] = None
    stage_description: Optional[str] = None
    error_message: Optional[str] = None
    options: Optional[GenerationOptions] = None
    result: Optional[GenerationResult] = None
    tokens_used: int = Field(default=0, ge=0)
    generation_time: Optional[float] = Field(None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_progress(self) -> GenerationProgress:
        """Calculate progress based on current stage (2-stage pipeline)."""
        # Stage weights: [40, 60] - simplified 2-stage pipeline
        stage_weights = [40, 60]

        if self.current_stage == 0:
            percentage = 0
        elif self.current_stage >= 2:
            percentage = 100
        else:
            percentage = sum(stage_weights[:self.current_stage])

        return GenerationProgress(
            current_stage=self.current_stage,
            total_stages=self.total_stages,
            percentage=percentage,
            stage_name=self.stage_name,
            stage_description=self.stage_description
        )

    def is_processing(self) -> bool:
        """Check if generation is in progress."""
        return self.status in ["pending", "generating"]

    def is_complete(self) -> bool:
        """Check if generation is completed."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """Check if generation failed."""
        return self.status == "failed"

    def can_cancel(self) -> bool:
        """Check if generation can be cancelled."""
        return self.is_processing()
