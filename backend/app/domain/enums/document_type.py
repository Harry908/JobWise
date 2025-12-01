"""Document type enumeration."""

from enum import Enum


class DocumentType(str, Enum):
    """Document type for samples and generations."""
    
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
