"""Database migration script for initial JobWise schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial database schema."""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('phone', sa.String(20)),
        sa.Column('timezone', sa.String(50)),
        sa.Column('subscription_tier', sa.String(20), nullable=False, default='free'),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True)),
        sa.Column('generations_this_month', sa.Integer(), nullable=False, default=0),
        sa.Column('last_active_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("subscription_tier IN ('free', 'basic', 'premium', 'enterprise')"),
        sa.CheckConstraint("generations_this_month >= 0"),
    )
    
    # Create indexes for users table
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_subscription', 'users', ['subscription_tier', 'subscription_expires_at'])
    
    # Master profiles table
    op.create_table(
        'master_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('location', sa.String(200)),
        sa.Column('linkedin', sa.String(500)),
        sa.Column('github', sa.String(500)),
        sa.Column('website', sa.String(500)),
        sa.Column('professional_summary', sa.Text()),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("version > 0"),
        sa.UniqueConstraint('user_id', 'email', name='unique_user_profile_email'),
    )
    
    # Create indexes for master_profiles table
    op.create_index('idx_profile_user', 'master_profiles', ['user_id'])
    op.create_index('idx_profile_active', 'master_profiles', ['is_active', 'user_id'])
    op.create_index('idx_profile_user_active', 'master_profiles', ['user_id', 'is_active'])
    
    # Experiences table
    op.create_table(
        'experiences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('company', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200)),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('is_current', sa.Boolean(), nullable=False, default=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('achievements', sa.JSON(), default=list),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_date <= COALESCE(end_date, CURRENT_DATE)"),
        sa.CheckConstraint("NOT (is_current AND end_date IS NOT NULL)"),
    )
    
    # Create indexes for experiences table
    op.create_index('idx_experience_profile', 'experiences', ['profile_id'])
    op.create_index('idx_experience_dates', 'experiences', ['start_date', 'end_date'])
    
    # Education table
    op.create_table(
        'education',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('institution', sa.String(200), nullable=False),
        sa.Column('degree', sa.String(100), nullable=False),
        sa.Column('field_of_study', sa.String(200), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('gpa', sa.Float()),
        sa.Column('honors', sa.JSON(), default=list),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_date <= COALESCE(end_date, CURRENT_DATE)"),
        sa.CheckConstraint("gpa IS NULL OR (gpa >= 0.0 AND gpa <= 4.0)"),
    )
    
    # Create indexes for education table
    op.create_index('idx_education_profile', 'education', ['profile_id'])
    op.create_index('idx_education_dates', 'education', ['start_date', 'end_date'])
    
    # Skills table
    op.create_table(
        'skills',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('category', sa.Enum('technical', 'soft', 'language', 'certification', name='skillcategory'), nullable=False),
        sa.Column('proficiency_level', sa.Enum('basic', 'conversational', 'fluent', 'native', 'beginner', 'intermediate', 'advanced', 'expert', name='proficiencylevel')),
        sa.Column('years_experience', sa.Float()),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("years_experience IS NULL OR years_experience >= 0"),
        sa.UniqueConstraint('profile_id', 'name', 'category', name='unique_profile_skill'),
    )
    
    # Create indexes for skills table
    op.create_index('idx_skill_profile', 'skills', ['profile_id'])
    op.create_index('idx_skill_category', 'skills', ['category', 'proficiency_level'])
    
    # Languages table
    op.create_table(
        'languages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('proficiency', sa.Enum('basic', 'conversational', 'fluent', 'native', 'beginner', 'intermediate', 'advanced', 'expert', name='proficiencylevel'), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('profile_id', 'name', name='unique_profile_language'),
    )
    
    # Create indexes for languages table
    op.create_index('idx_language_profile', 'languages', ['profile_id'])
    
    # Certifications table
    op.create_table(
        'certifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('issuer', sa.String(200), nullable=False),
        sa.Column('date_obtained', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('credential_id', sa.String(100)),
        sa.Column('verification_url', sa.String(500)),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("date_obtained <= COALESCE(expiry_date, CURRENT_DATE)"),
    )
    
    # Create indexes for certifications table
    op.create_index('idx_certification_profile', 'certifications', ['profile_id'])
    op.create_index('idx_certification_dates', 'certifications', ['date_obtained', 'expiry_date'])
    
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('technologies', sa.JSON(), default=list),
        sa.Column('url', sa.String(500)),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("start_date IS NULL OR end_date IS NULL OR start_date <= end_date"),
    )
    
    # Create indexes for projects table
    op.create_index('idx_project_profile', 'projects', ['profile_id'])
    op.create_index('idx_project_dates', 'projects', ['start_date', 'end_date'])
    
    # Job postings table
    op.create_table(
        'job_postings',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('company', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', sa.JSON(), nullable=False),
        sa.Column('salary_min', sa.Integer()),
        sa.Column('salary_max', sa.Integer()),
        sa.Column('salary_currency', sa.String(3), default='USD'),
        sa.Column('remote', sa.Boolean(), nullable=False, default=False),
        sa.Column('job_type', sa.Enum('full_time', 'part_time', 'contract', 'freelance', 'internship', name='jobtype'), nullable=False),
        sa.Column('experience_level', sa.Enum('entry', 'mid', 'senior', 'lead', 'executive', name='experiencelevel'), nullable=False),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_date', sa.DateTime(timezone=True)),
        sa.Column('application_url', sa.String(500)),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('keywords_extracted', sa.JSON(), default=list),
        sa.Column('ats_keywords', sa.JSON(), default=list),
        sa.Column('match_difficulty', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("salary_min IS NULL OR salary_min > 0"),
        sa.CheckConstraint("salary_max IS NULL OR salary_max > 0"),
        sa.CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max"),
        sa.CheckConstraint("match_difficulty IS NULL OR (match_difficulty >= 0 AND match_difficulty <= 1)"),
    )
    
    # Create indexes for job_postings table
    op.create_index('idx_job_title', 'job_postings', ['title'])
    op.create_index('idx_job_company', 'job_postings', ['company'])
    op.create_index('idx_job_source', 'job_postings', ['source'])
    op.create_index('idx_job_location', 'job_postings', ['location', 'remote'])
    op.create_index('idx_job_type_level', 'job_postings', ['job_type', 'experience_level'])
    op.create_index('idx_job_posted_date', 'job_postings', ['posted_date'])
    op.create_index('idx_job_expires', 'job_postings', ['expires_date'])
    op.create_index('idx_job_title_company', 'job_postings', ['title', 'company'])
    op.create_index('idx_job_location_remote_type', 'job_postings', ['location', 'remote', 'job_type'])
    op.create_index('idx_job_posted_expires', 'job_postings', ['posted_date', 'expires_date'])
    
    # Generations table
    op.create_table(
        'generations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('profile_id', sa.String(36), sa.ForeignKey('master_profiles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', sa.String(100), sa.ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'analyzing_job', 'compiling_profile', 'generating_documents', 'validating_quality', 'exporting_pdf', 'completed', 'failed', name='generationstatus'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('processing_time_seconds', sa.Float()),
        sa.Column('error_message', sa.Text()),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('pipeline_metadata', sa.JSON(), default=dict),
        sa.Column('llm_provider_used', sa.String(50)),
        sa.Column('total_tokens_used', sa.Integer()),
        sa.Column('estimated_cost', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("processing_time_seconds IS NULL OR processing_time_seconds >= 0"),
        sa.CheckConstraint("retry_count >= 0"),
        sa.CheckConstraint("total_tokens_used IS NULL OR total_tokens_used > 0"),
        sa.CheckConstraint("estimated_cost IS NULL OR estimated_cost >= 0"),
    )
    
    # Create indexes for generations table
    op.create_index('idx_generation_user', 'generations', ['user_id', 'status'])
    op.create_index('idx_generation_profile', 'generations', ['profile_id'])
    op.create_index('idx_generation_job', 'generations', ['job_id'])
    op.create_index('idx_generation_status', 'generations', ['status'])
    op.create_index('idx_generation_completed', 'generations', ['completed_at'])
    op.create_index('idx_generation_user_status_date', 'generations', ['user_id', 'status', 'created_at'])
    
    # Generation results table
    op.create_table(
        'generation_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('generation_id', sa.String(36), sa.ForeignKey('generations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.Enum('resume', 'cover_letter', 'linkedin_profile', 'portfolio_summary', name='documenttype'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('ats_score', sa.Float()),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('pdf_file_path', sa.String(500)),
        sa.Column('docx_file_path', sa.String(500)),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metadata', sa.JSON(), default=dict),
        sa.Column('readability_score', sa.Float()),
        sa.Column('keyword_density', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("ats_score IS NULL OR (ats_score >= 0 AND ats_score <= 1)"),
        sa.CheckConstraint("word_count > 0"),
        sa.CheckConstraint("readability_score IS NULL OR (readability_score >= 0 AND readability_score <= 100)"),
        sa.CheckConstraint("keyword_density IS NULL OR (keyword_density >= 0 AND keyword_density <= 1)"),
        sa.UniqueConstraint('generation_id', 'document_type', name='unique_generation_document_type'),
    )
    
    # Create indexes for generation_results table
    op.create_index('idx_result_generation', 'generation_results', ['generation_id'])
    op.create_index('idx_result_type', 'generation_results', ['document_type'])
    
    # Job applications table
    op.create_table(
        'job_applications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', sa.String(100), sa.ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('generation_id', sa.String(36), sa.ForeignKey('generations.id', ondelete='SET NULL')),
        sa.Column('status', sa.String(50), nullable=False, default='applied'),
        sa.Column('applied_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('follow_up_date', sa.DateTime(timezone=True)),
        sa.Column('interview_date', sa.DateTime(timezone=True)),
        sa.Column('response_date', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.Text()),
        sa.Column('feedback', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('applied', 'under_review', 'interview_scheduled', 'interviewed', 'rejected', 'withdrawn', 'offer_received', 'accepted')"),
        sa.UniqueConstraint('user_id', 'job_id', name='unique_user_job_application'),
    )
    
    # Create indexes for job_applications table
    op.create_index('idx_application_user', 'job_applications', ['user_id', 'status'])
    op.create_index('idx_application_status', 'job_applications', ['status'])
    op.create_index('idx_application_dates', 'job_applications', ['applied_date', 'follow_up_date'])
    
    # User sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_token', sa.String(255), nullable=False, unique=True),
        sa.Column('refresh_token', sa.String(255), unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('device_type', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # Create indexes for user_sessions table
    op.create_index('idx_session_token', 'user_sessions', ['session_token'])
    op.create_index('idx_refresh_token', 'user_sessions', ['refresh_token'])
    op.create_index('idx_session_user', 'user_sessions', ['user_id', 'is_active'])
    op.create_index('idx_session_expires', 'user_sessions', ['expires_at'])
    
    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('event_description', sa.String(500), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(36)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('metadata', sa.JSON(), default=dict),
        sa.Column('severity', sa.String(20), nullable=False, default='info'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('debug', 'info', 'warning', 'error', 'critical')"),
    )
    
    # Create indexes for audit_logs table
    op.create_index('idx_audit_event_type', 'audit_logs', ['event_type'])
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('idx_audit_event', 'audit_logs', ['event_type', 'created_at'])
    op.create_index('idx_audit_user_date', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade():
    """Drop all tables (use with caution!)."""
    
    # Drop tables in reverse order of dependencies
    op.drop_table('audit_logs')
    op.drop_table('user_sessions') 
    op.drop_table('job_applications')
    op.drop_table('generation_results')
    op.drop_table('generations')
    op.drop_table('job_postings')
    op.drop_table('projects')
    op.drop_table('certifications')
    op.drop_table('languages')
    op.drop_table('skills')
    op.drop_table('education')
    op.drop_table('experiences')
    op.drop_table('master_profiles')
    op.drop_table('users')
    
    # Drop custom enums (PostgreSQL specific)
    try:
        op.execute('DROP TYPE IF EXISTS skillcategory CASCADE')
        op.execute('DROP TYPE IF EXISTS proficiencylevel CASCADE')
        op.execute('DROP TYPE IF EXISTS jobtype CASCADE')
        op.execute('DROP TYPE IF EXISTS experiencelevel CASCADE')
        op.execute('DROP TYPE IF EXISTS generationstatus CASCADE')
        op.execute('DROP TYPE IF EXISTS documenttype CASCADE')
    except Exception:
        pass  # SQLite doesn't support DROP TYPE