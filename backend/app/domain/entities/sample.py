"""Sample document domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class Sample:
    """Sample document domain entity."""
    
    user_id: int
    document_type: str  # 'resume' or 'cover_letter'
    original_filename: str
    full_text: str
    word_count: int
    character_count: int
    id: str = field(default_factory=lambda: str(uuid4()))
    writing_style: Optional[dict] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate sample document fields after initialization."""
        if self.document_type not in ["resume", "cover_letter"]:
            raise ValueError("document_type must be 'resume' or 'cover_letter'")
        
        if not self.original_filename:
            raise ValueError("original_filename is required")
        
        if not self.full_text or not self.full_text.strip():
            raise ValueError("full_text cannot be empty")
        
        if self.word_count < 0:
            raise ValueError("word_count must be non-negative")
        
        if self.character_count < 0:
            raise ValueError("character_count must be non-negative")

    def to_dict(self) -> dict:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "document_type": self.document_type,
            "original_filename": self.original_filename,
            "full_text": self.full_text,
            "writing_style": self.writing_style,
            "word_count": self.word_count,
            "character_count": self.character_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
