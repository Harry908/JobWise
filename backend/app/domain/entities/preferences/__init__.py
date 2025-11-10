"""Preference-based generation domain entities."""

from .writing_style_config import WritingStyleConfig, LanguagePatterns, ContentApproach
from .layout_config import LayoutConfig, ContentDensity, FormattingPatterns, SectionCharacteristics, ProfessionalPolish
from .user_generation_profile import UserGenerationProfile, QualityTargets
from .example_resume import ExampleResume, FileMetadata
from .consistency_score import ConsistencyScore, ValidationResult
from .job_type_override import JobTypeOverride

__all__ = [
    "WritingStyleConfig",
    "LanguagePatterns", 
    "ContentApproach",
    "LayoutConfig",
    "ContentDensity",
    "FormattingPatterns",
    "SectionCharacteristics",
    "ProfessionalPolish",
    "UserGenerationProfile",
    "QualityTargets",
    "ExampleResume",
    "FileMetadata",
    "ConsistencyScore",
    "ValidationResult",
    "JobTypeOverride"
]