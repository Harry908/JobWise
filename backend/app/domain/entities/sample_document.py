"""Sample document entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..enums.document_type import DocumentType


@dataclass
class SampleDocument:
    """Sample document entity (resume or cover letter)."""
    
    id: UUID
    user_id: int
    document_type: DocumentType
    content_text: str
    filename: str
    is_active: bool
    upload_date: datetime
    last_used_date: Optional[datetime] = None
    word_count: Optional[int] = None
    metadata: Optional[dict] = None
    
    def activate(self) -> None:
        """Mark sample as active."""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Mark sample as inactive."""
        self.is_active = False
    
    def update_last_used(self) -> None:
        """Update last used timestamp."""
        self.last_used_date = datetime.utcnow()
