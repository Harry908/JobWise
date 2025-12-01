"""Job content ranking repository interface."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.job_content_ranking import JobContentRanking


class RankingRepositoryInterface(ABC):
    """Interface for job content ranking repository."""
    
    @abstractmethod
    async def create(self, ranking: JobContentRanking) -> JobContentRanking:
        """Create a new ranking."""
        pass
    
    @abstractmethod
    async def get_by_id(self, ranking_id: UUID) -> Optional[JobContentRanking]:
        """Get ranking by ID."""
        pass
    
    @abstractmethod
    async def get_by_job(
        self,
        user_id: int,
        job_id: UUID
    ) -> Optional[JobContentRanking]:
        """Get ranking for specific job."""
        pass
    
    @abstractmethod
    async def update(self, ranking: JobContentRanking) -> JobContentRanking:
        """Update ranking."""
        pass
    
    @abstractmethod
    async def delete(self, ranking_id: UUID) -> bool:
        """Delete ranking."""
        pass
