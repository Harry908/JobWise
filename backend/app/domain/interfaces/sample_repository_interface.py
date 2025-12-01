"""Sample repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.sample_document import SampleDocument
from ..enums.document_type import DocumentType


class SampleRepositoryInterface(ABC):
    """Interface for sample document repository."""
    
    @abstractmethod
    async def create(self, sample: SampleDocument) -> SampleDocument:
        """Create a new sample document."""
        pass
    
    @abstractmethod
    async def get_by_id(self, sample_id: UUID) -> Optional[SampleDocument]:
        """Get sample by ID."""
        pass
    
    @abstractmethod
    async def get_active_by_type(
        self,
        user_id: int,
        document_type: DocumentType
    ) -> Optional[SampleDocument]:
        """Get active sample of a specific type for user."""
        pass
    
    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        document_type: Optional[DocumentType] = None
    ) -> List[SampleDocument]:
        """List all samples for a user."""
        pass
    
    @abstractmethod
    async def update(self, sample: SampleDocument) -> SampleDocument:
        """Update sample document."""
        pass
    
    @abstractmethod
    async def delete(self, sample_id: UUID) -> bool:
        """Delete sample document."""
        pass
    
    @abstractmethod
    async def deactivate_others(
        self,
        user_id: int,
        document_type: DocumentType,
        active_sample_id: UUID
    ) -> None:
        """Deactivate all other samples of same type."""
        pass
