"""Job content ranking database model."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class JobContentRankingModel(Base):
    """Job content ranking ORM model."""
    
    __tablename__ = "job_content_rankings"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(String, ForeignKey("master_profiles.id", ondelete="CASCADE"), nullable=False)
    ranked_experience_ids = Column(Text, nullable=False)  # JSON array
    ranked_project_ids = Column(Text, nullable=False)  # JSON array
    ranking_rationale = Column(Text, nullable=True)
    keyword_matches = Column(Text, nullable=True)  # JSON
    relevance_scores = Column(Text, nullable=True)  # JSON
    llm_metadata = Column(Text, nullable=True)
    status = Column(String, default="completed", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
