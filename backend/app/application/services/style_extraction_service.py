"""Style extraction service."""

from uuid import UUID
from typing import Optional

from app.infrastructure.adapters.llm.groq_adapter import GroqAdapter
from app.infrastructure.repositories.sample_repository import SampleRepository
from app.infrastructure.repositories.writing_style_repository import WritingStyleRepository
from app.domain.entities.writing_style import WritingStyle
from app.domain.enums.document_type import DocumentType


class StyleExtractionService:
    """Service for extracting writing style from samples."""
    
    def __init__(
        self,
        llm_adapter: GroqAdapter,
        sample_repo: SampleRepository,
        style_repo: WritingStyleRepository
    ):
        self.llm = llm_adapter
        self.sample_repo = sample_repo
        self.style_repo = style_repo
    
    async def extract_from_sample(
        self,
        sample_id: UUID,
        user_id: int
    ) -> WritingStyle:
        """Extract writing style from a specific sample."""
        # Get sample
        sample = await self.sample_repo.get_by_id(str(sample_id), user_id)
        if not sample:
            raise ValueError("Sample not found")
        
        # Extract style using LLM
        result = await self.llm.extract_writing_style(sample.full_text)
        
        # Create writing style entity
        style = WritingStyle(
            id=UUID(sample.id),  # Reuse sample ID
            user_id=user_id,
            extracted_style=result["extracted_style"],
            sample_document_id=UUID(sample.id),
            extraction_date=sample.created_at,
            llm_metadata=str(result.get("llm_metadata"))
        )
        
        # Save to database
        await self.style_repo.create(style)
        
        return style
    
    async def get_user_style(
        self,
        user_id: int,
        document_type: DocumentType = DocumentType.COVER_LETTER
    ) -> Optional[dict]:
        """Get user's writing style, extracting from active sample if needed."""
        # Try to get existing style
        existing_style = await self.style_repo.get_by_user(user_id)
        if existing_style:
            return existing_style.extracted_style
        
        # Get active sample
        sample = await self.sample_repo.get_active_sample(user_id, document_type.value)
        if not sample:
            return None
        
        # Extract and return style
        style = await self.extract_from_sample(UUID(sample.id), user_id)
        return style.extracted_style
