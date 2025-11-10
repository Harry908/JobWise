"""Job type override domain entity."""

from datetime import datetime
from typing import Dict, Optional, Literal, Any
from pydantic import BaseModel, Field
import uuid


class JobTypeOverride(BaseModel):
    """Job-type specific preference overrides learned from user feedback."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    user_generation_profile_id: str
    
    # Job type identification
    job_type: str  # "software_engineer", "data_scientist", "product_manager", etc.
    industry_sector: Optional[str] = None  # "technology", "finance", "healthcare", etc.
    seniority_level: Optional[str] = None  # "entry", "mid", "senior", "lead", "executive"
    
    # Override configurations
    writing_style_overrides: Dict[str, Any] = Field(default_factory=dict)
    layout_overrides: Dict[str, Any] = Field(default_factory=dict)
    quality_target_overrides: Dict[str, Any] = Field(default_factory=dict)
    
    # Learning and confidence metrics
    learning_source: Literal["user_feedback", "edit_analysis", "a_b_testing", "manual"] = "user_feedback"
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    applications_count: int = Field(default=0)  # How many times applied
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)  # User satisfaction when applied
    
    # Specific override examples
    keyword_emphasis_boost: Optional[float] = Field(None, ge=1.0, le=3.0)  # Multiplier for certain keywords
    section_reordering: Optional[Dict[str, int]] = None  # Custom section order
    tone_adjustment: Optional[int] = Field(None, ge=-3, le=3)  # Tone shift from base
    
    # Activation conditions
    is_active: bool = Field(default=True)
    auto_apply: bool = Field(default=True)  # Automatically apply when job type matches
    requires_user_confirmation: bool = Field(default=False)
    
    # Usage tracking
    last_applied_at: Optional[datetime] = None
    last_updated_from_feedback: Optional[datetime] = None
    user_approval_status: Literal["pending", "approved", "rejected", "needs_review"] = "pending"
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_job_type_key(self) -> str:
        """Get standardized job type key for matching."""
        parts = [self.job_type]
        if self.seniority_level:
            parts.append(self.seniority_level)
        if self.industry_sector:
            parts.append(self.industry_sector)
        return "_".join(parts).lower()
    
    def apply_overrides(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply overrides to base configuration."""
        result = base_config.copy()
        
        # Apply writing style overrides
        if "writing_style" in result and self.writing_style_overrides:
            result["writing_style"].update(self.writing_style_overrides)
        
        # Apply layout overrides
        if "layout" in result and self.layout_overrides:
            result["layout"].update(self.layout_overrides)
        
        # Apply quality target overrides
        if "quality_targets" in result and self.quality_target_overrides:
            result["quality_targets"].update(self.quality_target_overrides)
        
        # Apply specific adjustments
        if self.tone_adjustment is not None and "writing_style" in result:
            current_formality = result["writing_style"].get("formality_level", 5)
            new_formality = max(1, min(10, current_formality + self.tone_adjustment))
            result["writing_style"]["formality_level"] = new_formality
        
        if self.keyword_emphasis_boost is not None:
            result["keyword_emphasis_multiplier"] = self.keyword_emphasis_boost
        
        if self.section_reordering:
            result["section_order_override"] = self.section_reordering
        
        return result
    
    def record_application(self, successful: bool = True):
        """Record that this override was applied."""
        self.applications_count += 1
        self.last_applied_at = datetime.utcnow()
        
        # Update success rate
        if self.applications_count == 1:
            self.success_rate = 1.0 if successful else 0.0
        else:
            # Exponential moving average with more weight on recent applications
            alpha = 0.3
            new_value = 1.0 if successful else 0.0
            self.success_rate = alpha * new_value + (1 - alpha) * self.success_rate
        
        self.updated_at = datetime.utcnow()
    
    def update_from_feedback(self, feedback_data: Dict[str, Any]):
        """Update override based on user feedback or edit analysis."""
        # Extract specific feedback types
        if "tone_too_formal" in feedback_data and feedback_data["tone_too_formal"]:
            self.tone_adjustment = max(-3, (self.tone_adjustment or 0) - 1)
        
        if "tone_too_casual" in feedback_data and feedback_data["tone_too_casual"]:
            self.tone_adjustment = min(3, (self.tone_adjustment or 0) + 1)
        
        if "emphasize_keywords" in feedback_data:
            keywords = feedback_data["emphasize_keywords"]
            if keywords and isinstance(keywords, list):
                self.keyword_emphasis_boost = min(3.0, (self.keyword_emphasis_boost or 1.0) + 0.2)
        
        # Update learning metadata
        self.last_updated_from_feedback = datetime.utcnow()
        self.confidence_score = min(1.0, self.confidence_score + 0.1)  # Gradual confidence increase
        self.updated_at = datetime.utcnow()
    
    def should_apply_to_job(self, job_type: str, seniority: Optional[str] = None, industry: Optional[str] = None) -> bool:
        """Check if this override should apply to a specific job."""
        if not self.is_active or not self.auto_apply:
            return False
        
        # Check job type match
        if self.job_type.lower() != job_type.lower():
            return False
        
        # Check seniority match (if specified)
        if self.seniority_level and seniority:
            if self.seniority_level.lower() != seniority.lower():
                return False
        
        # Check industry match (if specified)
        if self.industry_sector and industry:
            if self.industry_sector.lower() != industry.lower():
                return False
        
        # Check confidence threshold
        if self.confidence_score < 0.3:
            return False
        
        return True
    
    def get_effectiveness_metrics(self) -> Dict[str, Any]:
        """Get metrics on override effectiveness."""
        return {
            "applications_count": self.applications_count,
            "success_rate": self.success_rate,
            "confidence_score": self.confidence_score,
            "is_effective": self.success_rate >= 0.7 and self.applications_count >= 3,
            "needs_more_data": self.applications_count < 5,
            "last_applied": self.last_applied_at.isoformat() if self.last_applied_at else None,
            "approval_status": self.user_approval_status
        }