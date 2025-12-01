"""Writing style entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class WritingStyle:
    """Extracted writing style from sample documents."""
    
    id: UUID
    user_id: int
    extracted_style: dict  # JSON with tone, vocabulary, structure analysis
    sample_document_id: UUID
    extraction_date: datetime
    llm_metadata: Optional[str] = None  # Model, tokens, etc.
    
    @property
    def tone(self) -> Optional[str]:
        """Get tone from extracted style."""
        return self.extracted_style.get("tone")
    
    @property
    def vocabulary_level(self) -> Optional[str]:
        """Get vocabulary level from extracted style."""
        return self.extracted_style.get("vocabulary_level")
