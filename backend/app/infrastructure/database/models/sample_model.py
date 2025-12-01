"""Sample document database model."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class SampleDocumentModel(Base):
    """Sample document ORM model."""
    
    __tablename__ = "sample_documents"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type = Column(String, nullable=False)  # resume, cover_letter
    content_text = Column(Text, nullable=False)
    filename = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    upload_date = Column(DateTime, default=func.now(), nullable=False)
    last_used_date = Column(DateTime, nullable=True)
    word_count = Column(Integer, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON stored as text
