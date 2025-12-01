"""Job content ranking repository implementation."""

import json
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.job_content_ranking import JobContentRanking
from app.domain.enums.generation_status import GenerationStatus
from app.domain.interfaces.ranking_repository_interface import RankingRepositoryInterface
from app.infrastructure.database.models import JobContentRankingModel


class RankingRepository(RankingRepositoryInterface):
    """Repository for job content ranking operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, ranking: JobContentRanking) -> JobContentRanking:
        """Create a new ranking."""
        model = JobContentRankingModel(
            id=str(ranking.id),
            user_id=ranking.user_id,
            job_id=str(ranking.job_id),
            profile_id=str(ranking.profile_id),
            ranked_experience_ids=json.dumps(ranking.ranked_experience_ids),
            ranked_project_ids=json.dumps(ranking.ranked_project_ids),
            ranking_rationale=ranking.ranking_rationale,
            keyword_matches=json.dumps(ranking.keyword_matches) if ranking.keyword_matches else None,
            relevance_scores=json.dumps(ranking.relevance_scores) if ranking.relevance_scores else None,
            llm_metadata=ranking.llm_metadata,
            status=ranking.status.value,
            created_at=ranking.created_at
        )
        
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        return ranking
    
    async def get_by_id(self, ranking_id: UUID) -> Optional[JobContentRanking]:
        """Get ranking by ID."""
        query = select(JobContentRankingModel).where(
            JobContentRankingModel.id == str(ranking_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return JobContentRanking(
            id=UUID(model.id),
            user_id=model.user_id,
            job_id=UUID(model.job_id),
            profile_id=UUID(model.profile_id),
            ranked_experience_ids=json.loads(model.ranked_experience_ids),
            ranked_project_ids=json.loads(model.ranked_project_ids),
            ranking_rationale=model.ranking_rationale,
            keyword_matches=json.loads(model.keyword_matches) if model.keyword_matches else None,
            relevance_scores=json.loads(model.relevance_scores) if model.relevance_scores else None,
            llm_metadata=model.llm_metadata,
            status=GenerationStatus(model.status),
            created_at=model.created_at
        )
    
    async def get_by_job(
        self,
        user_id: int,
        job_id: UUID
    ) -> Optional[JobContentRanking]:
        """Get ranking for specific job."""
        query = select(JobContentRankingModel).where(
            and_(
                JobContentRankingModel.user_id == user_id,
                JobContentRankingModel.job_id == str(job_id)
            )
        ).order_by(JobContentRankingModel.created_at.desc())
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return JobContentRanking(
            id=UUID(model.id),
            user_id=model.user_id,
            job_id=UUID(model.job_id),
            profile_id=UUID(model.profile_id),
            ranked_experience_ids=json.loads(model.ranked_experience_ids),
            ranked_project_ids=json.loads(model.ranked_project_ids),
            ranking_rationale=model.ranking_rationale,
            keyword_matches=json.loads(model.keyword_matches) if model.keyword_matches else None,
            relevance_scores=json.loads(model.relevance_scores) if model.relevance_scores else None,
            llm_metadata=model.llm_metadata,
            status=GenerationStatus(model.status),
            created_at=model.created_at
        )
    
    async def update(self, ranking: JobContentRanking) -> JobContentRanking:
        """Update ranking."""
        query = select(JobContentRankingModel).where(
            JobContentRankingModel.id == str(ranking.id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ValueError(f"Ranking {ranking.id} not found")
        
        model.status = ranking.status.value
        model.ranking_rationale = ranking.ranking_rationale
        model.keyword_matches = json.dumps(ranking.keyword_matches) if ranking.keyword_matches else None
        model.relevance_scores = json.dumps(ranking.relevance_scores) if ranking.relevance_scores else None
        
        await self.session.commit()
        await self.session.refresh(model)
        
        return ranking
    
    async def delete(self, ranking_id: UUID) -> bool:
        """Delete ranking."""
        query = select(JobContentRankingModel).where(
            JobContentRankingModel.id == str(ranking_id)
        )
        
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        return True
