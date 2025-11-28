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


class GenerationModel(Base):
    """Generation database model for AI document generation tracking."""
    __tablename__ = "generations"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    profile_id = Column(String, ForeignKey("master_profiles.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    document_type = Column(String, nullable=False)  # 'resume', 'cover_letter'
    status = Column(String, default="pending", index=True)  # 'pending', 'generating', 'completed', 'failed', 'cancelled'
    current_stage = Column(Integer, default=0)  # 0-2 (2-stage pipeline)
    total_stages = Column(Integer, default=2)  # Updated to 2-stage pipeline
    stage_name = Column(String)
    stage_description = Column(Text)
    error_message = Column(Text)
    options = Column(Text)  # JSON stored as TEXT
    result = Column(Text)  # JSON stored as TEXT
    tokens_used = Column(Integer, default=0)
    generation_time = Column(Float)  # Seconds
    
    # V3.0 ENHANCEMENT: User-provided custom instructions
    user_custom_prompt = Column(Text)  # Optional user instructions like "Emphasize leadership" or "Highlight Python skills"
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="generations")
    profile = relationship("MasterProfileModel", backref="generations")
    job = relationship("JobModel", backref="generations")


# V3.0 Models - Text-Only Sample Storage & Job-Specific Ranking














# ============================================================
# V3.0 Models - Text-Only Sample Storage & Job-Specific Ranking
# ============================================================


class WritingStyleModel(Base):
    """User's extracted writing style from cover letter analysis (v3.0)."""
    __tablename__ = "writing_styles"

    # Primary identification
    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Writing style analysis results
    extracted_style = Column(JSON, nullable=False)  # Complete style analysis JSON
    
    # Extraction metadata
    extraction_status = Column(String, default="pending", nullable=False)  # pending, completed, failed
    extraction_model = Column(String)  # Model/method used for extraction
    extraction_timestamp = Column(DateTime)
    extraction_confidence = Column(Float)  # 0.0-1.0 confidence score
    
    # Source tracking
    source_sample_id = Column(String, ForeignKey("sample_documents.id"))  # Which sample was used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", backref="writing_style")
    source_sample = relationship("SampleDocumentModel", backref="derived_writing_styles")


class SampleDocumentModel(Base):
    """Text-only storage for user-uploaded sample resumes/cover letters (v3.0)."""
    __tablename__ = "sample_documents"

    # Primary identification
    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    
    # Document classification
    document_type = Column(String, nullable=False, index=True)  # 'resume' or 'cover_letter'
    
    # Original file metadata
    original_filename = Column(String(255))  # e.g., "John_Doe_Resume_2024.txt"
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # TEXT-ONLY STORAGE (no file_path, no BLOB)
    original_text = Column(Text, nullable=False)  # Complete document content
    
    # Text statistics
    word_count = Column(INTEGER)
    character_count = Column(INTEGER)
    line_count = Column(INTEGER)
    
    # Lifecycle management
    is_active = Column(Boolean, default=True, nullable=False)
    archived_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", backref="sample_documents")


class JobContentRankingModel(Base):
    """Job-specific content rankings for AI generation (v3.0)."""
    __tablename__ = "job_content_rankings"

    # Primary identification
    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Ranked content arrays (stored as JSON of UUID arrays)
    ranked_experience_ids = Column(JSON, nullable=False, default=list)  # ["uuid1", "uuid2", ...]
    ranked_project_ids = Column(JSON, nullable=False, default=list)     # ["uuid3", "uuid4", ...]
    ranked_skill_ids = Column(JSON, nullable=False, default=list)        # ["uuid5", "uuid6", ...]
    
    # AI generation metadata
    ranking_model_used = Column(String)  # e.g., "llama-3.1-8b-instant"
    ranking_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ranking_confidence_score = Column(Float)  # 0.0-1.0
    
    # Ranking rationale (JSON with explanation per item)
    ranking_explanations = Column(JSON, default=dict)  # {"uuid1": "Strong match because...", ...}
    
    # Usage tracking
    times_used_in_generation = Column(INTEGER, default=0)
    last_used_at = Column(DateTime)
    
    # User override capability
    user_modified = Column(Boolean, default=False)
    user_override_timestamp = Column(DateTime)
    
    # Lifecycle
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", backref="job_content_rankings")
    job = relationship("JobModel", backref="content_rankings")


# Removed PromptTemplateModel - prompts are now stored in source code