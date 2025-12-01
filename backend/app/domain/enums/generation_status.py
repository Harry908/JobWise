"""Generation status enumeration."""

from enum import Enum


class GenerationStatus(str, Enum):
    """Status for AI generation operations."""
    
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
