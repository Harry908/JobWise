"""User generation profile domain entity."""

from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
import uuid


class QualityTargets(BaseModel):
    """Quality targets and preferences."""
    target_ats_score: float = Field(default=0.85, ge=0.0, le=1.0)
    min_keyword_coverage: float = Field(default=0.75, ge=0.0, le=1.0)
    max_keyword_density: float = Field(default=0.03, ge=0.01, le=0.1)  # 3% max
    preferred_length_pages: int = Field(default=1, ge=1, le=3)
    quality_over_speed: bool = Field(default=True)
    include_soft_skills: bool = Field(default=True)
    emphasize_achievements: bool = Field(default=True)


class UserGenerationProfile(BaseModel):
    """Complete user generation profile combining writing style and layout preferences."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    
    # Profile status
    is_active: bool = Field(default=True)
    is_complete: bool = Field(default=False)  # Both writing style and layout configs present
    setup_stage: Literal["not_started", "cover_letter_uploaded", "examples_uploaded", "preferences_extracted", "completed"] = "not_started"
    
    # Associated configurations
    writing_style_config_id: Optional[str] = None
    layout_config_id: Optional[str] = None
    
    # Quality and generation preferences
    quality_targets: QualityTargets = Field(default_factory=QualityTargets)
    
    # Job-type specific overrides
    job_type_overrides: Dict[str, Dict] = Field(default_factory=dict)  # job_type -> config overrides
    
    # Experience and learning
    generations_count: int = Field(default=0)
    successful_generations: int = Field(default=0)
    user_satisfaction_scores: List[float] = Field(default_factory=list)  # 1.0-5.0 scale
    
    # Continuous improvement tracking
    preference_learning_enabled: bool = Field(default=True)
    auto_update_from_feedback: bool = Field(default=True)
    last_feedback_learning: Optional[datetime] = None
    
    # Template and style preferences
    preferred_templates: List[str] = Field(default_factory=lambda: ["modern"])
    industry_focus: Optional[str] = None  # "technology", "finance", etc.
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_generation_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def is_ready_for_generation(self) -> bool:
        """Check if profile is complete enough for generation."""
        return (
            self.writing_style_config_id is not None and
            self.layout_config_id is not None and
            self.is_active
        )
    
    def get_completion_percentage(self) -> int:
        """Get profile completion percentage."""
        completion_factors = [
            self.writing_style_config_id is not None,  # 50%
            self.layout_config_id is not None,  # 40%
            len(self.preferred_templates) > 0,  # 5%
            self.industry_focus is not None,  # 5%
        ]
        weights = [50, 40, 5, 5]
        
        completed_weight = sum(weight for factor, weight in zip(completion_factors, weights) if factor)
        return min(100, completed_weight)
    
    def update_quality_targets(self, **kwargs):
        """Update quality targets with new values."""
        for key, value in kwargs.items():
            if hasattr(self.quality_targets, key):
                setattr(self.quality_targets, key, value)
        self.updated_at = datetime.utcnow()
    
    def record_generation_feedback(self, satisfaction_score: float, generation_successful: bool = True):
        """Record user feedback for continuous improvement."""
        self.generations_count += 1
        if generation_successful:
            self.successful_generations += 1
        
        if 1.0 <= satisfaction_score <= 5.0:
            self.user_satisfaction_scores.append(satisfaction_score)
            # Keep only last 20 scores
            if len(self.user_satisfaction_scores) > 20:
                self.user_satisfaction_scores = self.user_satisfaction_scores[-20:]
        
        self.last_generation_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def get_average_satisfaction(self) -> Optional[float]:
        """Get average user satisfaction score."""
        if not self.user_satisfaction_scores:
            return None
        return sum(self.user_satisfaction_scores) / len(self.user_satisfaction_scores)
    
    def get_success_rate(self) -> float:
        """Get generation success rate."""
        if self.generations_count == 0:
            return 0.0
        return self.successful_generations / self.generations_count
    
    def add_job_type_override(self, job_type: str, overrides: Dict):
        """Add job-type specific preference overrides."""
        self.job_type_overrides[job_type] = {
            **overrides,
            "created_at": datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def get_effective_preferences(self, job_type: Optional[str] = None) -> Dict:
        """Get effective preferences including any job-type overrides."""
        base_preferences = {
            "quality_targets": self.quality_targets.dict(),
            "preferred_templates": self.preferred_templates,
            "industry_focus": self.industry_focus
        }
        
        if job_type and job_type in self.job_type_overrides:
            # Apply overrides
            overrides = self.job_type_overrides[job_type]
            for key, value in overrides.items():
                if key != "created_at":
                    base_preferences[key] = value
        
        return base_preferences