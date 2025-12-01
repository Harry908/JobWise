"""Generation database model."""

from sqlalchemy import Column, String, Integer, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class GenerationModel(Base):
    """Generation ORM model."""
    
    __tablename__ = "generations"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    ranking_id = Column(String, ForeignKey("job_content_rankings.id", ondelete="SET NULL"), nullable=True)
    document_type = Column(String, nullable=False)  # resume, cover_letter
    content_text = Column(Text, nullable=False)
    status = Column(String, default="pending", nullable=False)
    ats_score = Column(Float, nullable=True)
    ats_feedback = Column(Text, nullable=True)
    llm_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
