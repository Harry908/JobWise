# JobWise Data Models

## Core Data Schemas

### User Profile (Master Resume)

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PersonalInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None

class Experience(BaseModel):
    id: str
    company: str
    position: str
    start_date: str  # YYYY-MM format
    end_date: Optional[str] = None  # YYYY-MM or "present"
    location: Optional[str] = None
    description: str
    achievements: List[str] = []
    skills_used: List[str] = []
    is_current: bool = False

class Education(BaseModel):
    id: str
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: str  # YYYY-MM format
    end_date: Optional[str] = None
    gpa: Optional[float] = None
    honors: List[str] = []
    coursework: List[str] = []

class Project(BaseModel):
    id: str
    name: str
    description: str
    start_date: str
    end_date: Optional[str] = None
    technologies: List[str] = []
    url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    achievements: List[str] = []

class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"

class Skill(BaseModel):
    name: str
    category: SkillCategory
    proficiency: Optional[str] = None  # "beginner", "intermediate", "advanced", "expert"
    years_experience: Optional[int] = None

class MasterProfile(BaseModel):
    id: str
    personal_info: PersonalInfo
    summary: str
    experiences: List[Experience]
    education: List[Education]
    skills: List[Skill]
    projects: List[Project] = []
    certifications: List[str] = []
    languages: List[str] = []
    created_at: datetime
    updated_at: datetime
    version: int = 1
```

### Job Listing

```python
class JobSource(str, Enum):
    STATIC = "static"  # Prototype: mock data
    INDEED = "indeed"  # Production
    LINKEDIN = "linkedin"  # Production

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class JobRequirement(BaseModel):
    type: str  # "required", "preferred", "nice_to_have"
    description: str
    category: str  # "skill", "experience", "education", "certification"

class JobAnalysis(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: ExperienceLevel
    industry: str
    role_type: str
    keywords: List[str]
    company_culture: Optional[str] = None
    responsibilities: List[str]

class Job(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[JobRequirement] = []
    salary_range: Optional[str] = None
    employment_type: str = "full_time"  # "full_time", "part_time", "contract"
    posted_date: datetime
    source: JobSource
    source_url: Optional[HttpUrl] = None
    analysis: Optional[JobAnalysis] = None
    created_at: datetime
    updated_at: datetime
```

### Resume Generation

```python
class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TemplateType(str, Enum):
    ATS = "ats"          # Plain text, ATS-optimized
    VISUAL = "visual"    # Enhanced design

class ResumeLength(str, Enum):
    ONE_PAGE = "one_page"
    TWO_PAGE = "two_page"

class GenerationOptions(BaseModel):
    template: TemplateType = TemplateType.ATS
    length: ResumeLength = ResumeLength.ONE_PAGE
    focus_areas: List[str] = []  # "technical_skills", "leadership", "achievements"

class ResumeGenerateRequest(BaseModel):
    profile_id: str
    job_id: str
    options: GenerationOptions = GenerationOptions()

class CoverLetterTone(str, Enum):
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    FORMAL = "formal"

class CoverLetterLength(str, Enum):
    SHORT = "short"    # ~200 words
    MEDIUM = "medium"  # ~300 words
    LONG = "long"      # ~400 words

class CoverLetterOptions(BaseModel):
    tone: CoverLetterTone = CoverLetterTone.PROFESSIONAL
    length: CoverLetterLength = CoverLetterLength.MEDIUM

class CoverLetterGenerateRequest(BaseModel):
    profile_id: str
    job_id: str
    options: CoverLetterOptions = CoverLetterOptions()

class GenerationMetadata(BaseModel):
    ats_score: Optional[float] = None  # 0-100
    generation_time_ms: int
    token_usage: int
    model_used: str
    pipeline_version: str = "1.0"
    quality_checks_passed: int
    quality_checks_total: int

class GenerationResult(BaseModel):
    generation_id: str
    profile_id: str
    job_id: str
    status: GenerationStatus
    progress: int = 0  # 0-100
    document_id: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[GenerationMetadata] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
```

### Generated Documents

```python
class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"

class DocumentSection(BaseModel):
    type: str  # "summary", "experience", "skills", "education", "projects"
    content: str
    order: int

class ResumeContent(BaseModel):
    sections: Dict[str, Any]  # Flexible structure for different templates
    raw_text: str  # Plain text version for ATS
    formatted_html: Optional[str] = None  # For visual templates

class GeneratedDocument(BaseModel):
    id: str
    type: DocumentType
    profile_id: str
    job_id: str
    template: TemplateType
    content: ResumeContent
    metadata: GenerationMetadata
    file_path: Optional[str] = None  # Path to generated PDF
    created_at: datetime
```

## Database Schemas

### SQLite Schema (Prototype)

```sql
-- Profiles table
CREATE TABLE profiles (
    id TEXT PRIMARY KEY,
    personal_info TEXT NOT NULL,  -- JSON
    summary TEXT NOT NULL,
    experiences TEXT NOT NULL,    -- JSON array
    education TEXT NOT NULL,      -- JSON array
    skills TEXT NOT NULL,         -- JSON array
    projects TEXT,                -- JSON array
    certifications TEXT,          -- JSON array
    languages TEXT,               -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Jobs table
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,            -- JSON array
    salary_range TEXT,
    employment_type TEXT DEFAULT 'full_time',
    posted_date TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    analysis TEXT,                -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generation requests table
CREATE TABLE generation_requests (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    type TEXT NOT NULL,           -- 'resume' or 'cover_letter'
    status TEXT NOT NULL DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    options TEXT,                 -- JSON
    document_id TEXT,
    error_message TEXT,
    metadata TEXT,                -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Generated documents table  
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    template TEXT NOT NULL,
    content TEXT NOT NULL,        -- JSON
    metadata TEXT NOT NULL,       -- JSON
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

-- Indexes for performance
CREATE INDEX idx_profiles_updated_at ON profiles(updated_at);
CREATE INDEX idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX idx_generation_requests_profile_id ON generation_requests(profile_id);
CREATE INDEX idx_generation_requests_status ON generation_requests(status);
CREATE INDEX idx_documents_profile_id ON documents(profile_id);
```

### PostgreSQL Schema (Production)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Profiles table with better JSON support
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personal_info JSONB NOT NULL,
    summary TEXT NOT NULL,
    experiences JSONB NOT NULL,
    education JSONB NOT NULL,
    skills JSONB NOT NULL,
    projects JSONB DEFAULT '[]',
    certifications JSONB DEFAULT '[]',
    languages JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- Add GIN indexes for JSON fields
CREATE INDEX idx_profiles_skills_gin ON profiles USING GIN (skills);
CREATE INDEX idx_profiles_experiences_gin ON profiles USING GIN (experiences);

-- Jobs table with full-text search
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements JSONB DEFAULT '[]',
    salary_range TEXT,
    employment_type TEXT DEFAULT 'full_time',
    posted_date TIMESTAMP WITH TIME ZONE NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    analysis JSONB,
    search_vector tsvector,  -- For full-text search
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create full-text search index
CREATE INDEX idx_jobs_search_vector ON jobs USING GIN (search_vector);

-- Auto-update search vector
CREATE OR REPLACE FUNCTION update_job_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', NEW.title), 'A') ||
        setweight(to_tsvector('english', NEW.company), 'B') ||
        setweight(to_tsvector('english', NEW.description), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvector_update_trigger
    BEFORE INSERT OR UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_job_search_vector();
```

## Cache Models (Redis)

```python
# Cache key patterns
CACHE_KEYS = {
    "job_analysis": "job_analysis:{job_id}",
    "profile_compilation": "profile_comp:{profile_id}:{job_id}",
    "generated_content": "gen_content:{profile_id}:{job_id}:{template}",
    "user_rate_limit": "rate_limit:{user_id}:{endpoint}",
    "llm_response": "llm_resp:{prompt_hash}",
}

# Cache TTL (seconds)
CACHE_TTL = {
    "job_analysis": 86400,      # 24 hours
    "profile_compilation": 3600, # 1 hour
    "generated_content": 7200,   # 2 hours
    "user_rate_limit": 3600,     # 1 hour
    "llm_response": 86400,       # 24 hours
}
```

## Migration Strategy

### Prototype to Production Migration

```python
class DataMigrator:
    def migrate_sqlite_to_postgres(self):
        """
        Migrate data from SQLite to PostgreSQL
        1. Export profiles to JSON
        2. Transform job data with full-text indexing
        3. Migrate generation history
        4. Validate data integrity
        """
        pass
    
    def upgrade_schema_v1_to_v2(self):
        """
        Handle schema version upgrades
        1. Add new fields with defaults
        2. Transform existing data
        3. Update version numbers
        4. Rebuild indexes
        """
        pass
```

This data model provides a solid foundation for both prototype and production environments, with clear upgrade paths and performance optimizations.