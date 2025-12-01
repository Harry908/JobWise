"""Writing style repository interface."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.writing_style import WritingStyle


class WritingStyleRepositoryInterface(ABC):
    """Interface for writing style repository."""
    
    @abstractmethod
    async def create(self, style: WritingStyle) -> WritingStyle:
        """Create a new writing style."""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: int) -> Optional[WritingStyle]:
        """Get most recent writing style for user."""
        pass
    
    @abstractmethod
    async def get_by_sample(self, sample_id: UUID) -> Optional[WritingStyle]:
        """Get writing style extracted from specific sample."""
        pass
    
    @abstractmethod
    async def delete_by_sample(self, sample_id: UUID) -> bool:
        """Delete writing style associated with sample."""
        pass
