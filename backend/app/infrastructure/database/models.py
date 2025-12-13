"""Database models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float, JSON
from sqlalchemy.dialects.sqlite import INTEGER
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserModel(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MasterProfileModel(Base):
    """Master profile database model."""
    __tablename__ = "master_profiles"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)

    # Personal info stored as JSON
    personal_info = Column(JSON, nullable=False)

    # Professional summary
    professional_summary = Column(Text)
    
    # V3.0 ENHANCEMENT: AI-enhanced professional summary
    enhanced_professional_summary = Column(Text)  # AI-polished version
    enhancement_metadata = Column(JSON, default=dict)  # {"model": "llama-3.3-70b", "timestamp": "...", "confidence": 0.92}

    # Skills stored as JSON (technical, soft, languages, certifications)
    skills = Column(JSON, nullable=False)

    # Custom fields stored as JSON (achievements, hobbies, interests, etc.)
    custom_fields = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="profiles")
    experiences = relationship("ExperienceModel", backref="profile", cascade="all, delete-orphan")
    education = relationship("EducationModel", backref="profile", cascade="all, delete-orphan")
    projects = relationship("ProjectModel", backref="profile", cascade="all, delete-orphan")


class ExperienceModel(Base):
    """Work experience database model."""
    __tablename__ = "experiences"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String)  # ISO date string, null for current
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    achievements = Column(JSON)  # List of achievement strings
    
    # V3.0 ENHANCEMENT: AI-enhanced description
    enhanced_description = Column(Text)  # AI-polished version with stronger action verbs, quantification
    enhancement_metadata = Column(JSON, default=dict)  # {"model": "llama-3.3-70b", "timestamp": "...", "improvements": ["added metrics", "stronger verbs"]}


class EducationModel(Base):
    """Education database model."""
    __tablename__ = "education"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(String, nullable=False)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String, nullable=False)  # ISO date string
    gpa = Column(Float)
    honors = Column(JSON)  # List of honor strings


class ProjectModel(Base):
    """Project database model."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)  # UUID as string
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    technologies = Column(JSON)  # List of technology strings
    url = Column(String)
    start_date = Column(String, nullable=False)  # ISO date string
    end_date = Column(String)  # ISO date string
    
    # V3.0 ENHANCEMENT: AI-enhanced description
    enhanced_description = Column(Text)  # AI-polished version with technical depth, impact metrics
    enhancement_metadata = Column(JSON, default=dict)  # {"model": "llama-3.3-70b", "timestamp": "...", "improvements": ["added impact", "technical details"]}


class JobModel(Base):
    """Job database model."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=True, index=True)
    source = Column(String, nullable=False, index=True)  # user_created, indeed, linkedin, mock, etc.
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200))
    description = Column(Text)
    raw_text = Column(Text)
    parsed_keywords = Column(JSON)  # List of keyword strings
    requirements = Column(JSON)  # List of requirement strings
    benefits = Column(JSON)  # List of benefit strings
    salary_range = Column(String)
    remote = Column(Boolean, default=False)
    employment_type = Column(String, default="full_time")  # full_time, part_time, contract, temporary, internship
    status = Column(String, default="active", index=True)  # active, archived, draft
    application_status = Column(String, default="not_applied", index=True)  # Application progress tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="jobs")


class SampleDocumentModel(Base):
    """Sample document database model for writing style extraction."""
    __tablename__ = "sample_documents"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False, index=True)  # 'resume' or 'cover_letter'
    original_filename = Column(String, nullable=False)
    full_text = Column(Text, nullable=False)  # Full document text for AI analysis
    writing_style = Column(JSON)  # AI-derived style analysis (populated by generation API)
    word_count = Column(INTEGER)
    character_count = Column(INTEGER)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="sample_documents")


class WritingStyleModel(Base):
    """Writing style extracted from sample documents."""
    __tablename__ = "writing_styles"
    
    id = Column(String, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    extracted_style = Column(JSON, nullable=False)  # Tone, vocabulary, structure analysis
    sample_document_id = Column(String, ForeignKey("sample_documents.id"), nullable=False)
    extraction_date = Column(DateTime, default=datetime.utcnow)
    llm_metadata = Column(JSON)  # Model, tokens, etc.
    
    # Relationships
    user = relationship("UserModel", backref="writing_styles")


class JobContentRankingModel(Base):
    """Job-specific content ranking."""
    __tablename__ = "job_content_rankings"
    
    id = Column(String, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False)
    ranked_experience_ids = Column(JSON, nullable=False)  # Ordered list of experience IDs
    ranked_project_ids = Column(JSON, nullable=False)  # Ordered list of project IDs
    ranking_rationale = Column(Text)
    keyword_matches = Column(JSON)
    relevance_scores = Column(JSON)
    llm_metadata = Column(JSON)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", backref="content_rankings")
    job = relationship("JobModel", backref="content_rankings")


class GenerationModel(Base):
    """Generated documents (resumes and cover letters)."""
    __tablename__ = "generations"
    
    id = Column(String, primary_key=True)
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    ranking_id = Column(String, ForeignKey("job_content_rankings.id"), nullable=True)
    document_type = Column(String, nullable=False)  # resume, cover_letter
    content_text = Column(Text, nullable=False)
    content_structured = Column(Text, nullable=True)  # JSON string for export templates
    status = Column(String, default="pending")
    ats_score = Column(Float)
    ats_feedback = Column(Text)
    llm_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", backref="generations")
    job = relationship("JobModel", backref="generations")


class ExportModel(Base):
    """Export database model for document exports (PDF/DOCX/ZIP)."""
    __tablename__ = "exports"
    
    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    generation_id = Column(String, ForeignKey("generations.id"), nullable=True, index=True)  # Null for batch exports
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True, index=True)  # Denormalized for filtering
    format = Column(String, nullable=False, index=True)  # pdf, docx, zip
    template = Column(String, nullable=False)  # modern, classic, creative, ats_optimized
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # S3 key: exports/{user_id}/{export_id}.{format}
    file_size_bytes = Column(INTEGER, nullable=False)
    page_count = Column(INTEGER)  # For PDFs only
    options = Column(JSON, default=dict)  # Template customization options
    export_metadata = Column(JSON, default=dict)  # Additional metadata (generation_type, generation_ids for batch, etc.)
    download_url = Column(String)  # Presigned S3 URL (regenerated on access)
    expires_at = Column(DateTime, nullable=False)  # 30 days from creation
    local_cache_path = Column(String)  # Mobile local cache path
    cache_expires_at = Column(DateTime)  # Local cache expiration (7 days)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("UserModel", backref="exports")
    generation = relationship("GenerationModel", backref="exports")
    job = relationship("JobModel", backref="exports")


# Removed PromptTemplateModel - prompts are now stored in source code