"""Template type enum."""

from enum import Enum


class TemplateType(Enum):
    """Available export templates."""
    
    MODERN = "modern"
    CLASSIC = "classic"
    CREATIVE = "creative"
    ATS_OPTIMIZED = "ats-optimized"
