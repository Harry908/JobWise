"""Layout configuration domain entity."""

from datetime import datetime
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
import uuid


class ContentDensity(BaseModel):
    """Content density preferences."""
    bullets_per_experience_min: int = Field(default=2, ge=1, le=8)
    bullets_per_experience_max: int = Field(default=5, ge=1, le=8)
    bullets_per_experience_preferred: int = Field(default=3, ge=1, le=8)
    line_spacing: Literal["tight", "standard", "loose"] = "standard"
    section_spacing: Literal["minimal", "standard", "generous"] = "standard"
    white_space_usage: Literal["minimal", "balanced", "generous"] = "balanced"


class FormattingPatterns(BaseModel):
    """Formatting pattern preferences."""
    emphasis_style: Literal["bold", "italic", "caps", "underlining", "none"] = "bold"
    title_formatting: Literal["bold", "caps", "italic", "standard"] = "bold"
    company_formatting: Literal["bold", "italic", "standard"] = "bold"
    skill_grouping: Literal["categorized", "listed", "integrated", "highlighted"] = "categorized"
    contact_integration: Literal["header", "sidebar", "footer", "inline"] = "header"


class SectionCharacteristics(BaseModel):
    """Section-specific formatting preferences."""
    summary_style: Literal["paragraph", "bullets", "objectives", "none"] = "paragraph"
    experience_focus: Literal["responsibilities", "achievements", "mixed", "skills"] = "achievements"
    education_detail_level: Literal["minimal", "standard", "detailed", "academic"] = "standard"
    skills_presentation: Literal["categorized", "listed", "integrated", "proficiency"] = "categorized"
    project_integration: Literal["separate", "embedded", "portfolio", "minimal"] = "separate"


class ProfessionalPolish(BaseModel):
    """Professional quality metrics."""
    consistency_level: Literal["basic", "good", "excellent"] = "good"
    ats_optimization: Literal["minimal", "moderate", "high"] = "moderate"
    readability_score: int = Field(default=7, ge=1, le=10)
    visual_hierarchy: Literal["poor", "good", "excellent"] = "good"


class LayoutConfig(BaseModel):
    """Layout and structural configuration extracted from user's example resumes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    
    # Section organization
    section_order: List[str] = Field(default_factory=lambda: [
        "contact", "summary", "experience", "education", "skills", "projects"
    ])
    
    # Header and contact styling
    header_style: Literal["centered", "left-aligned", "two-column", "contact-block", "name-contact"] = "left-aligned"
    date_format: Literal["MM/YYYY", "MM/DD/YYYY", "Month YYYY", "YYYY"] = "MM/YYYY"
    location_display: Literal["city-state", "full-address", "city-only", "remote"] = "city-state"
    
    # Bullet and content styling
    bullet_style: Literal["standard", "achievement", "CAR", "STAR", "numeric"] = "achievement"
    
    # Density and spacing
    content_density: ContentDensity = Field(default_factory=ContentDensity)
    formatting_patterns: FormattingPatterns = Field(default_factory=FormattingPatterns)
    section_characteristics: SectionCharacteristics = Field(default_factory=SectionCharacteristics)
    professional_polish: ProfessionalPolish = Field(default_factory=ProfessionalPolish)
    
    # Source tracking
    source_resume_ids: List[str] = Field(default_factory=list)  # IDs of example resumes used
    extraction_method: Literal["single_resume", "multi_resume_consensus", "user_defined"] = "single_resume"
    consistency_score: float = Field(default=0.0, ge=0.0, le=1.0)  # Across multiple examples
    
    # Metadata
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    user_modifications: List[Dict[str, str]] = Field(default_factory=list)  # Track user changes
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_prompt_context(self) -> str:
        """Convert to string format for LLM prompts."""
        return f"""
Layout Preferences:
- Section Order: {' → '.join(self.section_order)}
- Header Style: {self.header_style}
- Date Format: {self.date_format}
- Location Display: {self.location_display}
- Bullet Style: {self.bullet_style}

Content Density:
- Bullets per Experience: {self.content_density.bullets_per_experience_min}-{self.content_density.bullets_per_experience_max} (preferred: {self.content_density.bullets_per_experience_preferred})
- Spacing: {self.content_density.line_spacing} line spacing, {self.content_density.section_spacing} section spacing
- White Space: {self.content_density.white_space_usage} usage

Formatting Patterns:
- Emphasis: {self.formatting_patterns.emphasis_style}
- Titles: {self.formatting_patterns.title_formatting}
- Companies: {self.formatting_patterns.company_formatting}
- Skills: {self.formatting_patterns.skill_grouping} grouping
- Contact: {self.formatting_patterns.contact_integration} integration

Section Characteristics:
- Summary: {self.section_characteristics.summary_style}
- Experience Focus: {self.section_characteristics.experience_focus}
- Education: {self.section_characteristics.education_detail_level} detail
- Skills: {self.section_characteristics.skills_presentation} presentation
- Projects: {self.section_characteristics.project_integration} integration

Professional Polish:
- Consistency: {self.professional_polish.consistency_level}
- ATS Optimization: {self.professional_polish.ats_optimization}
- Readability: {self.professional_polish.readability_score}/10
- Visual Hierarchy: {self.professional_polish.visual_hierarchy}
"""

    def update_user_preference(self, field_path: str, new_value: str, reason: str = "User modification"):
        """Track user modifications to extracted preferences."""
        modification = {
            "field": field_path,
            "old_value": str(getattr(self, field_path.split('.')[0])),
            "new_value": new_value,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.user_modifications.append(modification)
        self.updated_at = datetime.utcnow()