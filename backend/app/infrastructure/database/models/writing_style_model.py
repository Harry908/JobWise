"""Writing style database model."""

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class WritingStyleModel(Base):
    """Writing style ORM model."""
    
    __tablename__ = "writing_styles"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    extracted_style = Column(Text, nullable=False)  # JSON stored as text
    sample_document_id = Column(String, ForeignKey("sample_documents.id", ondelete="CASCADE"), nullable=False)
    extraction_date = Column(DateTime, default=func.now(), nullable=False)
    llm_metadata = Column(Text, nullable=True)  # Model, tokens, etc.
