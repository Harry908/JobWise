"""Consistency score domain entity."""

from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import uuid


class ValidationResult(BaseModel):
    """Individual validation result component."""
    category: str  # "writing_style", "structure", "quality", "ats"
    score: float = Field(..., ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0)


class ConsistencyScore(BaseModel):
    """Consistency score tracking for generated content validation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    generation_id: str  # Associated generation
    
    # Validation components
    writing_style_consistency: ValidationResult
    structural_consistency: ValidationResult
    quality_assessment: ValidationResult
    ats_optimization: ValidationResult
    content_accuracy: ValidationResult
    
    # Overall metrics
    overall_consistency_score: float = Field(..., ge=0.0, le=1.0)
    meets_quality_standards: bool = Field(default=False)
    validation_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Comparison data
    compared_against: List[str] = Field(default_factory=list)  # Example resume IDs used
    user_preferences_applied: Dict[str, str] = Field(default_factory=dict)
    
    # Improvement tracking
    improvement_areas: List[str] = Field(default_factory=list)
    critical_issues: List[str] = Field(default_factory=list)
    minor_issues: List[str] = Field(default_factory=list)
    
    # User feedback correlation
    user_satisfaction_predicted: Optional[float] = Field(None, ge=1.0, le=5.0)
    user_satisfaction_actual: Optional[float] = Field(None, ge=1.0, le=5.0)
    feedback_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0)  # How accurate was prediction
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_overall_grade(self) -> str:
        """Get letter grade based on overall score."""
        score = self.overall_consistency_score
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def get_priority_improvements(self, limit: int = 3) -> List[Dict[str, str]]:
        """Get prioritized improvement recommendations."""
        all_issues = []
        
        # Collect issues from all validation components
        components = [
            ("writing_style", self.writing_style_consistency),
            ("structural", self.structural_consistency),
            ("quality", self.quality_assessment),
            ("ats", self.ats_optimization),
            ("accuracy", self.content_accuracy)
        ]
        
        for component_name, validation in components:
            for rec in validation.recommendations[:2]:  # Top 2 per component
                priority = "high" if validation.score < 0.6 else "medium" if validation.score < 0.8 else "low"
                all_issues.append({
                    "category": component_name,
                    "recommendation": rec,
                    "priority": priority,
                    "impact_score": 1.0 - validation.score
                })
        
        # Sort by impact and return top items
        sorted_issues = sorted(all_issues, key=lambda x: x["impact_score"], reverse=True)
        return sorted_issues[:limit]
    
    def update_user_feedback(self, actual_satisfaction: float):
        """Update with actual user feedback."""
        self.user_satisfaction_actual = actual_satisfaction
        
        if self.user_satisfaction_predicted is not None:
            # Calculate prediction accuracy
            diff = abs(self.user_satisfaction_predicted - actual_satisfaction)
            max_diff = 4.0  # Max possible difference (5.0 - 1.0)
            self.feedback_accuracy = 1.0 - (diff / max_diff)
    
    def is_generation_ready(self) -> bool:
        """Check if generation meets minimum quality standards."""
        return (
            self.overall_consistency_score >= 0.7 and
            self.content_accuracy.score >= 0.9 and  # High accuracy requirement
            len(self.critical_issues) == 0
        )
    
    def get_validation_summary(self) -> Dict[str, str]:
        """Get human-readable validation summary."""
        grade = self.get_overall_grade()
        status = "✅ Ready" if self.meets_quality_standards else "⚠️ Needs Improvement"
        
        return {
            "grade": grade,
            "status": status,
            "overall_score": f"{self.overall_consistency_score:.1%}",
            "top_strength": self._get_top_strength(),
            "top_weakness": self._get_top_weakness(),
            "critical_issues_count": str(len(self.critical_issues)),
            "minor_issues_count": str(len(self.minor_issues))
        }
    
    def _get_top_strength(self) -> str:
        """Identify the strongest validation component."""
        components = [
            ("Writing Style", self.writing_style_consistency.score),
            ("Structure", self.structural_consistency.score),
            ("Quality", self.quality_assessment.score),
            ("ATS Optimization", self.ats_optimization.score),
            ("Content Accuracy", self.content_accuracy.score)
        ]
        
        best_component = max(components, key=lambda x: x[1])
        return f"{best_component[0]} ({best_component[1]:.1%})"
    
    def _get_top_weakness(self) -> str:
        """Identify the weakest validation component."""
        components = [
            ("Writing Style", self.writing_style_consistency.score),
            ("Structure", self.structural_consistency.score),
            ("Quality", self.quality_assessment.score),
            ("ATS Optimization", self.ats_optimization.score),
            ("Content Accuracy", self.content_accuracy.score)
        ]
        
        worst_component = min(components, key=lambda x: x[1])
        return f"{worst_component[0]} ({worst_component[1]:.1%})"