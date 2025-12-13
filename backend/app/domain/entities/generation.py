"""Generation entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..enums.document_type import DocumentType
from ..enums.generation_status import GenerationStatus


@dataclass
class Generation:
    """Generated document (resume or cover letter)."""
    
    id: UUID
    user_id: int
    job_id: UUID
    ranking_id: Optional[UUID]
    document_type: DocumentType
    content_text: str
    status: GenerationStatus
    content_structured: Optional[str] = None
    ats_score: Optional[float] = None
    ats_feedback: Optional[str] = None
    llm_metadata: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def mark_completed(self, content: str, ats_score: float = None) -> None:
        """Mark generation as completed."""
        self.status = GenerationStatus.COMPLETED
        self.content_text = content
        if ats_score is not None:
            self.ats_score = ats_score
    
    def mark_failed(self) -> None:
        """Mark generation as failed."""
        self.status = GenerationStatus.FAILED
