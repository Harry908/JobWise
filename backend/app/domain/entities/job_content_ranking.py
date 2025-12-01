"""Job content ranking entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from ..enums.generation_status import GenerationStatus


@dataclass
class JobContentRanking:
    """Content ranking for a specific job."""
    
    id: UUID
    user_id: int
    job_id: UUID
    profile_id: UUID
    ranked_experience_ids: List[str]
    ranked_project_ids: List[str]
    ranking_rationale: Optional[str] = None
    keyword_matches: Optional[dict] = None
    relevance_scores: Optional[dict] = None
    llm_metadata: Optional[str] = None
    status: GenerationStatus = GenerationStatus.COMPLETED
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def get_top_experiences(self, limit: int = 5) -> List[str]:
        """Get top N ranked experiences."""
        return self.ranked_experience_ids[:limit]
    
    def get_top_projects(self, limit: int = 3) -> List[str]:
        """Get top N ranked projects."""
        return self.ranked_project_ids[:limit]
