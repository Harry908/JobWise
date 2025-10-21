"""SQLAlchemy database models for JobWise application."""

import uuid
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, String, Integer, Float, DateTime, Date, Text, 
    ForeignKey, JSON, CheckConstraint, Index, UniqueConstraint,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from ...domain.entities.job import JobType, ExperienceLevel
from ...domain.entities.generation import GenerationStatus, DocumentType
from ...domain.entities.job_description import JobDescriptionStatus, JobDescriptionSource
from ...domain.value_objects import ProficiencyLevel, SkillCategory, LanguageProficiency

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin for common timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UserModel(Base, TimestampMixin):
    """User account model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Authentication fields
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Profile fields
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Subscription fields
    subscription_tier: Mapped[str] = mapped_column(String(20), default="free", nullable=False)
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Usage tracking
    generations_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    master_profiles: Mapped[List["MasterProfileModel"]] = relationship(
        "MasterProfileModel", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    generations: Mapped[List["GenerationModel"]] = relationship(
        "GenerationModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    saved_jobs: Mapped[List["JobApplicationModel"]] = relationship(
        "JobApplicationModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    user_sessions: Mapped[List["UserSessionModel"]] = relationship(
        "UserSessionModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    job_descriptions: Mapped[List["JobDescriptionModel"]] = relationship(
        "JobDescriptionModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("subscription_tier IN ('free', 'basic', 'premium', 'enterprise')"),
        CheckConstraint("generations_this_month >= 0"),
        Index("idx_user_email", "email"),
        Index("idx_user_subscription", "subscription_tier", "subscription_expires_at"),
    )


class MasterProfileModel(Base, TimestampMixin):
    """Master resume profile model."""
    
    __tablename__ = "master_profiles"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Profile fields
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    linkedin: Mapped[Optional[str]] = mapped_column(String(500))
    github: Mapped[Optional[str]] = mapped_column(String(500))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Content fields
    professional_summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="master_profiles")
    experiences: Mapped[List["ExperienceModel"]] = relationship(
        "ExperienceModel",
        back_populates="profile", 
        cascade="all, delete-orphan",
        order_by="ExperienceModel.start_date.desc()"
    )
    education: Mapped[List["EducationModel"]] = relationship(
        "EducationModel",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="EducationModel.start_date.desc()"
    )
    skills: Mapped[List["SkillModel"]] = relationship(
        "SkillModel",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    languages: Mapped[List["LanguageModel"]] = relationship(
        "LanguageModel",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    certifications: Mapped[List["CertificationModel"]] = relationship(
        "CertificationModel", 
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="CertificationModel.date_obtained.desc()"
    )
    projects: Mapped[List["ProjectModel"]] = relationship(
        "ProjectModel",
        back_populates="profile",
        cascade="all, delete-orphan", 
        order_by="ProjectModel.start_date.desc()"
    )
    generations: Mapped[List["GenerationModel"]] = relationship(
        "GenerationModel",
        back_populates="profile"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("version > 0"),
        UniqueConstraint("user_id", "email", name="unique_user_profile_email"),
        Index("idx_profile_user", "user_id"),
        Index("idx_profile_active", "is_active", "user_id"),
    )


class ExperienceModel(Base, TimestampMixin):
    """Work experience model."""
    
    __tablename__ = "experiences"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Experience fields
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    achievements: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Display order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="experiences")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("start_date <= COALESCE(end_date, CURRENT_DATE)"),
        CheckConstraint("NOT (is_current AND end_date IS NOT NULL)"),
        Index("idx_experience_profile", "profile_id"),
        Index("idx_experience_dates", "start_date", "end_date"),
    )


class EducationModel(Base, TimestampMixin):
    """Education model."""
    
    __tablename__ = "education"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys  
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Education fields
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str] = mapped_column(String(100), nullable=False) 
    field_of_study: Mapped[str] = mapped_column(String(200), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    gpa: Mapped[Optional[float]] = mapped_column(Float)
    honors: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Display order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="education")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("start_date <= COALESCE(end_date, CURRENT_DATE)"),
        CheckConstraint("gpa IS NULL OR (gpa >= 0.0 AND gpa <= 4.0)"),
        Index("idx_education_profile", "profile_id"),
        Index("idx_education_dates", "start_date", "end_date"),
    )


class SkillModel(Base, TimestampMixin):
    """Skills model."""
    
    __tablename__ = "skills"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Skill fields
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[SkillCategory] = mapped_column(SQLEnum(SkillCategory), nullable=False)
    proficiency_level: Mapped[Optional[ProficiencyLevel]] = mapped_column(SQLEnum(ProficiencyLevel))
    years_experience: Mapped[Optional[float]] = mapped_column(Float)
    
    # Display fields
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="skills")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("years_experience IS NULL OR years_experience >= 0"),
        UniqueConstraint("profile_id", "name", "category", name="unique_profile_skill"),
        Index("idx_skill_profile", "profile_id"),
        Index("idx_skill_category", "category", "proficiency_level"),
    )


class LanguageModel(Base, TimestampMixin):
    """Language proficiency model."""
    
    __tablename__ = "languages"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Language fields
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Display order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="languages")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("profile_id", "name", name="unique_profile_language"),
        Index("idx_language_profile", "profile_id"),
    )


class CertificationModel(Base, TimestampMixin):
    """Certification model."""
    
    __tablename__ = "certifications"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Certification fields
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[str] = mapped_column(String(200), nullable=False)
    date_obtained: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    credential_id: Mapped[Optional[str]] = mapped_column(String(100))
    verification_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Display order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="certifications")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("date_obtained <= COALESCE(expiry_date, CURRENT_DATE)"),
        Index("idx_certification_profile", "profile_id"),
        Index("idx_certification_dates", "date_obtained", "expiry_date"),
    )


class ProjectModel(Base, TimestampMixin):
    """Project model."""
    
    __tablename__ = "projects"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Project fields
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[List[str]] = mapped_column(JSON, default=list)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Display fields
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="projects")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("start_date IS NULL OR end_date IS NULL OR start_date <= end_date"),
        Index("idx_project_profile", "profile_id"),
        Index("idx_project_dates", "start_date", "end_date"),
    )


class JobPostingModel(Base, TimestampMixin):
    """Job posting model - renamed from job_postings to jobs for API consistency."""
    
    __tablename__ = "jobs"
    
    # Primary key (external job ID)
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    
    # Job fields
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Salary and type
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer) 
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    job_type: Mapped[JobType] = mapped_column(SQLEnum(JobType), nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(SQLEnum(ExperienceLevel), nullable=False)
    
    # Dates and source
    posted_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    application_url: Mapped[Optional[str]] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Optional ownership for user-created jobs
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    # Status for user-created jobs (draft/active/archived)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    
    # Processing metadata
    keywords_extracted: Mapped[List[str]] = mapped_column(JSON, default=list)
    ats_keywords: Mapped[List[str]] = mapped_column(JSON, default=list)
    match_difficulty: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships  
    generations: Mapped[List["GenerationModel"]] = relationship(
        "GenerationModel",
        back_populates="job_posting"
    )
    saved_jobs: Mapped[List["JobApplicationModel"]] = relationship(
        "JobApplicationModel",
        back_populates="job_posting"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("salary_min IS NULL OR salary_min > 0"),
        CheckConstraint("salary_max IS NULL OR salary_max > 0"),
        CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max"),
        CheckConstraint("match_difficulty IS NULL OR (match_difficulty >= 0 AND match_difficulty <= 1)"),
        CheckConstraint("status IN ('draft','active','archived')"),
        Index("idx_job_location", "location", "remote"),
        Index("idx_job_type_level", "job_type", "experience_level"),
        Index("idx_job_posted_date", "posted_date"),
        Index("idx_job_expires", "expires_date"),
    )


class JobDescriptionModel(Base, TimestampMixin):
    """Simplified job description model for all user job data."""

    __tablename__ = "job_descriptions"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Core job fields
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    benefits: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Optional metadata
    job_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    remote_work: Mapped[Optional[str]] = mapped_column(String(20))

    # Source tracking
    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user_created",
        index=True
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(100))
    external_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Original text (for reference)
    raw_text: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        index=True
    )

    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="job_descriptions")
    generations: Mapped[List["GenerationModel"]] = relationship(
        "GenerationModel",
        back_populates="job_description"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("source IN ('user_created', 'saved_external')"),
        CheckConstraint("status IN ('active', 'archived', 'deleted')"),
        CheckConstraint("salary_min IS NULL OR salary_min > 0"),
        CheckConstraint("salary_max IS NULL OR salary_max > 0"),
        CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max"),
        Index("idx_job_desc_user_status", "user_id", "status", "created_at"),
        Index("idx_job_desc_title_company", "title", "company"),
    )


class GenerationModel(Base, TimestampMixin):
    """AI generation process model."""
    
    __tablename__ = "generations"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        ForeignKey("jobs.id", ondelete="CASCADE")
    )
    job_description_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("job_descriptions.id", ondelete="CASCADE")
    )
    
    # Generation status and timing
    status: Mapped[GenerationStatus] = mapped_column(SQLEnum(GenerationStatus), nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    processing_time_seconds: Mapped[Optional[float]] = mapped_column(Float)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Pipeline metadata
    pipeline_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    llm_provider_used: Mapped[Optional[str]] = mapped_column(String(50))
    total_tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="generations")
    profile: Mapped["MasterProfileModel"] = relationship("MasterProfileModel", back_populates="generations")
    job_posting: Mapped[Optional["JobPostingModel"]] = relationship("JobPostingModel", back_populates="generations")
    job_description: Mapped[Optional["JobDescriptionModel"]] = relationship("JobDescriptionModel", back_populates="generations")
    results: Mapped[List["GenerationResultModel"]] = relationship(
        "GenerationResultModel",
        back_populates="generation",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("processing_time_seconds IS NULL OR processing_time_seconds >= 0"),
        CheckConstraint("retry_count >= 0"),
        CheckConstraint("total_tokens_used IS NULL OR total_tokens_used > 0"),
        CheckConstraint("estimated_cost IS NULL OR estimated_cost >= 0"),
        CheckConstraint("(job_id IS NOT NULL AND job_description_id IS NULL) OR (job_id IS NULL AND job_description_id IS NOT NULL)"),
        Index("idx_generation_user", "user_id", "status"),
        Index("idx_generation_profile", "profile_id"),
        Index("idx_generation_job", "job_id"),
        Index("idx_generation_job_desc", "job_description_id"),
        Index("idx_generation_completed", "completed_at"),
    )


class GenerationResultModel(Base, TimestampMixin):
    """Generated document result model - renamed from generation_results to documents for API consistency."""
    
    __tablename__ = "documents"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    generation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Result fields
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ats_score: Mapped[Optional[float]] = mapped_column(Float)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # File storage
    pdf_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    docx_file_path: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Generation metadata
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generation_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Quality metrics
    readability_score: Mapped[Optional[float]] = mapped_column(Float)
    keyword_density: Mapped[Optional[float]] = mapped_column(Float)
    
    # Relationships
    generation: Mapped["GenerationModel"] = relationship("GenerationModel", back_populates="results")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("ats_score IS NULL OR (ats_score >= 0 AND ats_score <= 1)"),
        CheckConstraint("word_count > 0"),
        CheckConstraint("readability_score IS NULL OR (readability_score >= 0 AND readability_score <= 100)"),
        CheckConstraint("keyword_density IS NULL OR (keyword_density >= 0 AND keyword_density <= 1)"),
        UniqueConstraint("generation_id", "document_type", name="unique_generation_document_type"),
        Index("idx_result_generation", "generation_id"),
        Index("idx_result_type", "document_type"),
    )


class JobApplicationModel(Base, TimestampMixin):
    """Job application tracking model - renamed from job_applications to saved_jobs for API consistency."""
    
    __tablename__ = "saved_jobs"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    generation_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("generations.id", ondelete="SET NULL")
    )
    
    # Application status
    status: Mapped[str] = mapped_column(
        String(50),
        default="applied",
        nullable=False,
        index=True
    )
    applied_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Follow-up dates
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    response_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Notes and feedback
    notes: Mapped[Optional[str]] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="saved_jobs")
    job_posting: Mapped["JobPostingModel"] = relationship("JobPostingModel", back_populates="saved_jobs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('applied', 'under_review', 'interview_scheduled', 'interviewed', 'rejected', 'withdrawn', 'offer_received', 'accepted')"),
        UniqueConstraint("user_id", "job_id", name="unique_user_job_application"),
        Index("idx_application_user", "user_id", "status"),
        Index("idx_application_dates", "applied_date", "follow_up_date"),
    )


class UserSessionModel(Base, TimestampMixin):
    """User session tracking model."""
    
    __tablename__ = "user_sessions"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Session fields
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Device and location info
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 support
    device_type: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="user_sessions")
    
    # Constraints
    __table_args__ = (
        Index("idx_session_user", "user_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )


class AuditLogModel(Base, TimestampMixin):
    """Audit log for tracking important system events."""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    
    # Foreign keys
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True
    )
    
    # Event fields
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_description: Mapped[str] = mapped_column(String(500), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    # Context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    audit_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Severity
    severity: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("severity IN ('debug', 'info', 'warning', 'error', 'critical')"),
        Index("idx_audit_event", "event_type", "created_at"),
        Index("idx_audit_user", "user_id", "created_at"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
    )


# Create indexes for performance optimization
def create_performance_indexes():
    """Create additional performance indexes."""
    from sqlalchemy import text
    
    # Composite indexes for common query patterns
    indexes = [
        # User and profile queries
        "CREATE INDEX IF NOT EXISTS idx_profile_user_active ON master_profiles (user_id, is_active);",
        "CREATE INDEX IF NOT EXISTS idx_generation_user_status_date ON generations (user_id, status, created_at);",
        
        # Job search queries  
        "CREATE INDEX IF NOT EXISTS idx_job_title_company ON jobs (title, company);",
        "CREATE INDEX IF NOT EXISTS idx_job_location_remote_type ON jobs (location, remote, job_type);",
        
        # Time-based queries
        "CREATE INDEX IF NOT EXISTS idx_generation_completed_time ON generations (completed_at) WHERE completed_at IS NOT NULL;",
        "CREATE INDEX IF NOT EXISTS idx_job_posted_expires ON jobs (posted_date, expires_date);",
        
        # Full-text search preparation (for PostgreSQL)
        "CREATE INDEX IF NOT EXISTS idx_job_description_gin ON jobs USING gin(to_tsvector('english', description));",
        "CREATE INDEX IF NOT EXISTS idx_job_requirements_gin ON jobs USING gin(to_tsvector('english', array_to_string(requirements, ' ')));",
    ]
    
    return indexes