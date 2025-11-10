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
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="generations")
    profile = relationship("MasterProfileModel", backref="generations")
    job = relationship("JobModel", backref="generations")


# NEW PREFERENCE-BASED GENERATION TABLES

class WritingStyleConfigModel(Base):
    """Writing style configuration extracted from user's cover letter."""
    __tablename__ = "writing_style_configs"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    
    # Core writing characteristics
    vocabulary_level = Column(String, default="professional")  # professional, academic, conversational, technical
    vocabulary_complexity_score = Column(Integer, default=5)  # 1-10
    tone = Column(String, default="semi-formal")  # formal, semi-formal, enthusiastic, authoritative, collaborative
    formality_level = Column(Integer, default=5)  # 1-10
    
    # Sentence structure preferences
    sentence_structure = Column(String, default="varied")  # simple, compound, complex, varied
    avg_sentence_length = Column(String, default="medium")  # short, medium, long
    active_voice_ratio = Column(Float, default=0.7)  # 0.0-1.0
    first_person_frequency = Column(String, default="moderate")  # rare, moderate, frequent
    
    # Style elements
    transition_style = Column(String, default="standard")  # minimal, standard, elaborate
    paragraph_length = Column(String, default="medium")  # short, medium, long
    closing_style = Column(String, default="warm")  # direct, warm, formal, enthusiastic
    
    # Language patterns stored as JSON
    language_patterns = Column(JSON, default=dict)
    content_approach = Column(JSON, default=dict)
    
    # Metadata
    source_document_type = Column(String, default="cover_letter")
    source_document_hash = Column(String)
    extraction_confidence = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="writing_style_configs")


class LayoutConfigModel(Base):
    """Layout and structural configuration extracted from user's example resumes."""
    __tablename__ = "layout_configs"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    
    # Section organization stored as JSON
    section_order = Column(JSON, default=list)
    
    # Header and contact styling
    header_style = Column(String, default="left-aligned")  # centered, left-aligned, two-column, contact-block
    date_format = Column(String, default="MM/YYYY")  # MM/YYYY, MM/DD/YYYY, Month YYYY, YYYY
    location_display = Column(String, default="city-state")  # city-state, full-address, city-only, remote
    bullet_style = Column(String, default="achievement")  # standard, achievement, CAR, STAR, numeric
    
    # Density and formatting stored as JSON
    content_density = Column(JSON, default=dict)
    formatting_patterns = Column(JSON, default=dict)
    section_characteristics = Column(JSON, default=dict)
    professional_polish = Column(JSON, default=dict)
    
    # Source tracking
    source_resume_ids = Column(JSON, default=list)  # List of example resume IDs
    extraction_method = Column(String, default="single_resume")  # single_resume, multi_resume_consensus, user_defined
    consistency_score = Column(Float, default=0.0)  # Across multiple examples
    extraction_confidence = Column(Float, default=0.0)
    user_modifications = Column(JSON, default=list)  # Track user changes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="layout_configs")


class UserGenerationProfileModel(Base):
    """Complete user generation profile combining writing style and layout preferences."""
    __tablename__ = "user_generation_profiles"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True, unique=True)  # One profile per user
    
    # Profile status
    is_active = Column(Boolean, default=True)
    is_complete = Column(Boolean, default=False)
    setup_stage = Column(String, default="not_started")  # not_started, cover_letter_uploaded, examples_uploaded, preferences_extracted, completed
    
    # Associated configurations
    writing_style_config_id = Column(String, ForeignKey("writing_style_configs.id"), nullable=True)
    layout_config_id = Column(String, ForeignKey("layout_configs.id"), nullable=True)
    
    # Quality and generation preferences stored as JSON
    quality_targets = Column(JSON, default=dict)
    job_type_overrides = Column(JSON, default=dict)  # job_type -> config overrides
    
    # Experience and learning metrics
    generations_count = Column(Integer, default=0)
    successful_generations = Column(Integer, default=0)
    user_satisfaction_scores = Column(JSON, default=list)  # List of 1.0-5.0 scores
    
    # Continuous improvement settings
    preference_learning_enabled = Column(Boolean, default=True)
    auto_update_from_feedback = Column(Boolean, default=True)
    last_feedback_learning = Column(DateTime)
    
    # Template and style preferences
    preferred_templates = Column(JSON, default=list)
    industry_focus = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_generation_at = Column(DateTime)

    # Relationships
    user = relationship("UserModel", backref="generation_profile", uselist=False)
    writing_style_config = relationship("WritingStyleConfigModel", backref="generation_profiles")
    layout_config = relationship("LayoutConfigModel", backref="generation_profiles")


class ExampleResumeModel(Base):
    """Example resume uploaded by user for preference extraction."""
    __tablename__ = "example_resumes"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information stored as JSON
    file_metadata = Column(JSON, nullable=False)
    storage_path = Column(String, nullable=False)
    storage_provider = Column(String, default="local")  # local, s3, azure
    
    # Content extraction
    extracted_text = Column(Text)
    text_extraction_status = Column(String, default="pending")  # pending, completed, failed
    text_extraction_error = Column(Text)
    
    # Analysis status
    structural_analysis_completed = Column(Boolean, default=False)
    layout_config_id = Column(String, ForeignKey("layout_configs.id"), nullable=True)
    analysis_confidence = Column(Float, default=0.0)
    
    # Usage tracking
    is_primary_example = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    
    # Quality assessment
    quality_score = Column(Float)  # 0.0-1.0
    ats_compatibility_score = Column(Float)  # 0.0-1.0
    professional_polish_score = Column(Float)  # 0.0-1.0
    
    # User feedback
    user_rating = Column(Integer)  # 1-5
    user_notes = Column(String(500))
    
    # Status and lifecycle
    status = Column(String, default="uploaded")  # uploaded, processing, analyzed, active, archived, failed
    archived_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analyzed_at = Column(DateTime)

    # Relationships
    user = relationship("UserModel", backref="example_resumes")
    layout_config = relationship("LayoutConfigModel", backref="example_resumes")


class ConsistencyScoreModel(Base):
    """Consistency score tracking for generated content validation."""
    __tablename__ = "consistency_scores"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    generation_id = Column(String, ForeignKey("generations.id"), nullable=False, index=True)
    
    # Validation components stored as JSON
    writing_style_consistency = Column(JSON, nullable=False)
    structural_consistency = Column(JSON, nullable=False)
    quality_assessment = Column(JSON, nullable=False)
    ats_optimization = Column(JSON, nullable=False)
    content_accuracy = Column(JSON, nullable=False)
    
    # Overall metrics
    overall_consistency_score = Column(Float, nullable=False)  # 0.0-1.0
    meets_quality_standards = Column(Boolean, default=False)
    validation_confidence = Column(Float, default=0.0)  # 0.0-1.0
    
    # Comparison data stored as JSON
    compared_against = Column(JSON, default=list)  # Example resume IDs used
    user_preferences_applied = Column(JSON, default=dict)
    
    # Improvement tracking stored as JSON
    improvement_areas = Column(JSON, default=list)
    critical_issues = Column(JSON, default=list)
    minor_issues = Column(JSON, default=list)
    
    # User feedback correlation
    user_satisfaction_predicted = Column(Float)  # 1.0-5.0
    user_satisfaction_actual = Column(Float)  # 1.0-5.0
    feedback_accuracy = Column(Float)  # 0.0-1.0
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", backref="consistency_scores")
    generation = relationship("GenerationModel", backref="consistency_score", uselist=False)


class JobTypeOverrideModel(Base):
    """Job-type specific preference overrides learned from user feedback."""
    __tablename__ = "job_type_overrides"

    id = Column(String, primary_key=True)  # UUID as string
    user_id = Column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    user_generation_profile_id = Column(String, ForeignKey("user_generation_profiles.id"), nullable=False)
    
    # Job type identification
    job_type = Column(String, nullable=False, index=True)  # software_engineer, data_scientist, etc.
    industry_sector = Column(String, index=True)  # technology, finance, healthcare, etc.
    seniority_level = Column(String, index=True)  # entry, mid, senior, lead, executive
    
    # Override configurations stored as JSON
    writing_style_overrides = Column(JSON, default=dict)
    layout_overrides = Column(JSON, default=dict)
    quality_target_overrides = Column(JSON, default=dict)
    
    # Learning and confidence metrics
    learning_source = Column(String, default="user_feedback")  # user_feedback, edit_analysis, a_b_testing, manual
    confidence_score = Column(Float, default=0.0)  # 0.0-1.0
    applications_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # 0.0-1.0
    
    # Specific override examples
    keyword_emphasis_boost = Column(Float)  # 1.0-3.0
    section_reordering = Column(JSON)  # Custom section order
    tone_adjustment = Column(Integer)  # -3 to +3
    
    # Activation conditions
    is_active = Column(Boolean, default=True)
    auto_apply = Column(Boolean, default=True)
    requires_user_confirmation = Column(Boolean, default=False)
    
    # Usage tracking
    last_applied_at = Column(DateTime)
    last_updated_from_feedback = Column(DateTime)
    user_approval_status = Column(String, default="pending")  # pending, approved, rejected, needs_review
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", backref="user_job_type_overrides")
    generation_profile = relationship("UserGenerationProfileModel", backref="profile_job_type_overrides")