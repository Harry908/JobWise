"""Document domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum


class DocumentType(Enum):
    """Types of generated documents."""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    LINKEDIN_PROFILE = "linkedin_profile"
    PORTFOLIO_SUMMARY = "portfolio_summary"


@dataclass
class Document:
    """Generated document entity."""
    id: str
    generation_id: str
    document_type: DocumentType
    content: str
    file_path: Optional[str]
    ats_score: Optional[float]
    word_count: int
    created_at: datetime
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        id: str,
        generation_id: str,
        document_type: DocumentType,
        content: str,
        file_path: Optional[str] = None,
        ats_score: Optional[float] = None,
        word_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> 'Document':
        """Create a new document."""
        return cls(
            id=id,
            generation_id=generation_id,
            document_type=document_type,
            content=content,
            file_path=file_path,
            ats_score=ats_score,
            word_count=word_count,
            created_at=datetime.utcnow(),
            metadata=metadata or {},
        )

    def update_content(self, content: str) -> None:
        """Update document content."""
        self.content = content
        self.word_count = len(content.split())

    def update_file_path(self, file_path: str) -> None:
        """Update file path."""
        self.file_path = file_path

    def update_ats_score(self, score: float) -> None:
        """Update ATS score."""
        self.ats_score = score

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'generation_id': self.generation_id,
            'document_type': self.document_type.value,
            'content': self.content,
            'file_path': self.file_path,
            'ats_score': self.ats_score,
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
        }