"""Generation repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.generation import Generation
from ..enums.document_type import DocumentType


class GenerationRepositoryInterface(ABC):
    """Interface for generation repository."""
    
    @abstractmethod
    async def create(self, generation: Generation) -> Generation:
        """Create a new generation."""
        pass
    
    @abstractmethod
    async def get_by_id(self, generation_id: UUID) -> Optional[Generation]:
        """Get generation by ID."""
        pass
    
    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        document_type: Optional[DocumentType] = None,
        job_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Generation]:
        """List generations for a user with pagination."""
        pass
    
    @abstractmethod
    async def update(self, generation: Generation) -> Generation:
        """Update generation."""
        pass
    
    @abstractmethod
    async def delete(self, generation_id: UUID) -> bool:
        """Delete generation."""
        pass
