# JobWise - Unified Backend Architecture

**Version**: 1.0  
**Architecture**: Single FastAPI Application  
**Database**: SQLite  
**LLM Provider**: Groq (Llama models)  
**File Storage**: Local filesystem  

## System Overview

Single FastAPI server handling all operations:
- User authentication (JWT)
- Profile management with AI enhancement
- Job description parsing
- Sample document processing
- Content ranking and generation
- Document storage

## Technology Stack

```yaml
Backend Framework: FastAPI 0.104+
Database: SQLite 3.x
ORM: SQLAlchemy 2.x
Authentication: JWT (python-jose)
LLM Client: Groq SDK
File Processing:
  - PyPDF2 (PDF extraction)
  - python-docx (DOCX extraction)
Background Tasks: FastAPI BackgroundTasks
Caching: functools.lru_cache (in-memory)
Validation: Pydantic v2
```

## Project Structure

```
jobwise/
├── main.py                          # FastAPI app entry point
├── config.py                        # Environment configuration
├── database.py                      # SQLAlchemy setup
│
├── models/                          # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   ├── profile.py
│   ├── experience.py
│   ├── project.py
│   ├── education.py
│   ├── job.py
│   ├── sample_document.py
│   ├── enhancement_job.py
│   ├── job_content_ranking.py
│   ├── generation.py
│   └── document.py
│
├── schemas/                         # Pydantic schemas
│   ├── __init__.py
│   ├── auth.py
│   ├── profile.py
│   ├── job.py
│   ├── sample.py
│   ├── enhancement.py
│   ├── ranking.py
│   ├── generation.py
│   └── document.py
│
├── routers/                         # API route handlers
│   ├── __init__.py
│   ├── auth.py                      # POST /auth/register, /auth/login
│   ├── profiles.py                  # /api/v1/profiles/*
│   ├── jobs.py                      # /api/v1/jobs/*
│   ├── samples.py                   # /api/v1/samples/*
│   ├── enhancement.py               # /api/v1/enhancement/*
│   ├── rankings.py                  # /api/v1/rankings/*
│   ├── generations.py               # /api/v1/generations/*
│   └── documents.py                 # /api/v1/documents/*
│
├── services/                        # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py
│   ├── profile_service.py
│   ├── job_service.py
│   ├── sample_service.py
│   ├── enhancement_service.py
│   ├── ranking_service.py
│   ├── generation_service.py
│   └── document_service.py
│
├── ai/                              # LLM integration
│   ├── __init__.py
│   ├── groq_client.py               # Groq API wrapper
│   ├── prompt_loader.py             # Load prompts from JSON
│   ├── style_extractor.py           # Extract writing styles
│   ├── content_enhancer.py          # Enhance profile content
│   ├── content_ranker.py            # Rank content by relevance
│   └── cover_letter_generator.py   # Generate cover letters
│
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── text_extraction.py           # PDF/DOCX parsing
│   ├── file_storage.py              # File upload/download
│   ├── text_processing.py           # Text parsing/formatting
│   ├── validators.py                # Custom validators
│   └── security.py                  # JWT, hashing
│
├── prompts/                         # AI prompts (JSON)
│   ├── enhancement_prompts.json
│   ├── ranking_prompts.json
│   └── generation_prompts.json
│
├── migrations/                      # Database migrations
│   └── versions/
│
├── tests/                           # Test suite
│   ├── test_auth.py
│   ├── test_profiles.py
│   ├── test_enhancement.py
│   └── ...
│
├── uploads/                         # Local file storage
│   └── {user_id}/
│       ├── samples/
│       └── exports/
│
├── .env                             # Environment variables
├── requirements.txt
└── README.md
```

## Database Schema (SQLite)

### Complete Schema Definition

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Master profiles table
CREATE TABLE master_profiles (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    personal_info TEXT NOT NULL,  -- JSON
    professional_summary TEXT,
    enhanced_summary TEXT,
    previous_enhanced_summary TEXT,
    skills TEXT,  -- JSON
    custom_fields TEXT,  -- JSON
    enhancement_version INTEGER DEFAULT 0,
    last_enhanced_at DATETIME,
    enhancement_status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Experiences table
CREATE TABLE experiences (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current INTEGER DEFAULT 0,
    description TEXT,  -- Newline-separated bullets
    enhanced_description TEXT,
    previous_enhanced_description TEXT,
    use_enhanced INTEGER DEFAULT 0,
    technologies TEXT,  -- JSON array
    display_order INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,  -- Newline-separated bullets
    enhanced_description TEXT,
    previous_enhanced_description TEXT,
    use_enhanced INTEGER DEFAULT 0,
    technologies TEXT,  -- JSON array
    url TEXT,
    github_url TEXT,
    start_date DATE,
    end_date DATE,
    display_order INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

-- Education table
CREATE TABLE education (
    id TEXT PRIMARY KEY,
    profile_id TEXT NOT NULL,
    institution TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    location TEXT,
    start_date DATE,
    end_date DATE,
    gpa REAL,
    honors TEXT,
    relevant_coursework TEXT,  -- JSON array
    display_order INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

-- Jobs table
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    raw_text TEXT,
    parsed_keywords TEXT,  -- JSON array
    requirements TEXT,  -- JSON array
    benefits TEXT,  -- JSON array
    salary_range TEXT,
    remote INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    application_status TEXT DEFAULT 'not_applied',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Sample documents table
CREATE TABLE sample_documents (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    document_type TEXT NOT NULL,  -- 'resume_sample' or 'cover_letter_sample'
    file_name TEXT NOT NULL,
    file_path TEXT,
    full_text TEXT NOT NULL,
    extracted_style TEXT,  -- JSON
    version INTEGER DEFAULT 1,
    file_size_bytes INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, document_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Enhancement jobs table
CREATE TABLE enhancement_jobs (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    profile_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'processing', 'completed', 'failed'
    progress INTEGER DEFAULT 0,
    current_step TEXT,
    sample_version_used INTEGER,
    error_message TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

-- Job content rankings table
CREATE TABLE job_content_rankings (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    ranking_data TEXT NOT NULL,  -- JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

-- Generations table
CREATE TABLE generations (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    ranking_id TEXT,
    document_type TEXT NOT NULL,  -- 'resume' or 'cover_letter'
    content_text TEXT NOT NULL,
    content_format TEXT DEFAULT 'plain',
    metadata TEXT NOT NULL,  -- JSON
    generation_params TEXT,  -- JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (ranking_id) REFERENCES job_content_rankings(id)
);

-- Documents table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    generation_id TEXT NOT NULL,
    profile_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content_text TEXT NOT NULL,
    content_format TEXT DEFAULT 'plain',
    metadata TEXT NOT NULL,  -- JSON
    file_path TEXT,
    notes TEXT,
    version INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_experiences_profile ON experiences(profile_id);
CREATE INDEX idx_projects_profile ON projects(profile_id);
CREATE INDEX idx_education_profile ON education(profile_id);
CREATE INDEX idx_jobs_user ON jobs(user_id);
CREATE INDEX idx_samples_user_type ON sample_documents(user_id, document_type);
CREATE INDEX idx_rankings_user_job ON job_content_rankings(user_id, job_id);
CREATE INDEX idx_generations_user ON generations(user_id);
CREATE INDEX idx_documents_user ON documents(user_id);
```

## Application Bootstrap (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base
from routers import (
    auth, profiles, jobs, samples, 
    enhancement, rankings, generations, documents
)
from ai.prompt_loader import PromptLoader
from config import settings

# Load AI prompts at startup
prompt_loader = PromptLoader()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting JobWise Backend...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
    
    # Load AI prompts
    prompt_loader.load_all_prompts()
    print("✅ AI prompts loaded")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="JobWise API",
    version="1.0.0",
    description="AI-powered job application document generator",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(samples.router, prefix="/api/v1/samples", tags=["Samples"])
app.include_router(enhancement.router, prefix="/api/v1/enhancement", tags=["Enhancement"])
app.include_router(rankings.router, prefix="/api/v1/rankings", tags=["Rankings"])
app.include_router(generations.router, prefix="/api/v1/generations", tags=["Generations"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
def root():
    return {"message": "JobWise API v1.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
```

## Configuration (config.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "JobWise"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./jobwise.db"
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Groq LLM
    GROQ_API_KEY: str
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"
    GROQ_MODEL_QUALITY: str = "llama-3.1-70b-versatile"
    GROQ_TIMEOUT: int = 30
    GROQ_MAX_RETRIES: int = 3
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: list = ["txt", "pdf", "docx"]
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Prompts
    PROMPTS_DIR: str = "./prompts"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

## Database Connection (database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## AI Prompt Loader (ai/prompt_loader.py)

```python
import json
from pathlib import Path
from typing import Dict, Any
from config import settings

class PromptLoader:
    def __init__(self):
        self.prompts: Dict[str, Dict[str, Any]] = {}
    
    def load_all_prompts(self):
        """Load all prompt files at startup"""
        prompts_dir = Path(settings.PROMPTS_DIR)
        
        # Load enhancement prompts
        with open(prompts_dir / "enhancement_prompts.json") as f:
            self.prompts["enhancement"] = json.load(f)
        
        # Load ranking prompts
        with open(prompts_dir / "ranking_prompts.json") as f:
            self.prompts["ranking"] = json.load(f)
        
        # Load generation prompts
        with open(prompts_dir / "generation_prompts.json") as f:
            self.prompts["generation"] = json.load(f)
        
        print(f"✅ Loaded {len(self.prompts)} prompt collections")
    
    def get_prompt(self, category: str, name: str) -> Dict[str, Any]:
        """Get a specific prompt by category and name"""
        return self.prompts.get(category, {}).get(name)
    
    def format_prompt(self, category: str, name: str, **kwargs) -> str:
        """Format a prompt with provided variables"""
        prompt_config = self.get_prompt(category, name)
        if not prompt_config:
            raise ValueError(f"Prompt not found: {category}.{name}")
        
        prompt_template = prompt_config["prompt"]
        return prompt_template.format(**kwargs)

# Global instance
prompt_loader = PromptLoader()
```

## Groq Client (ai/groq_client.py)

```python
from groq import Groq
from typing import Optional, Dict, Any
from config import settings
import time

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def complete(
        self,
        prompt: str,
        model: str = settings.GROQ_MODEL_QUALITY,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        max_retries: int = settings.GROQ_MAX_RETRIES
    ) -> str:
        """Send completion request to Groq with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=settings.GROQ_TIMEOUT
                )
                
                return response.choices[0].message.content
            
            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    print(f"⚠️ Groq API error, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Groq API failed after {max_retries} attempts: {e}")
    
    def complete_json(
        self,
        prompt: str,
        model: str = settings.GROQ_MODEL_FAST,
        **kwargs
    ) -> Dict[str, Any]:
        """Complete and parse JSON response"""
        import json
        
        response_text = self.complete(prompt, model=model, **kwargs)
        
        # Clean markdown code blocks if present
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(response_text)

# Global instance
groq_client = GroqClient()
```

## Background Task Processing

### Enhancement Service (services/enhancement_service.py)

```python
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from models.enhancement_job import EnhancementJob
from models.master_profile import MasterProfile
from models.sample_document import SampleDocument
from ai.groq_client import groq_client
from ai.prompt_loader import prompt_loader
import json

def run_enhancement_job(
    job_id: str,
    user_id: int,
    profile_id: str,
    db: Session
):
    """Background task to enhance profile content"""
    
    try:
        # Update job status
        job = db.query(EnhancementJob).filter(EnhancementJob.id == job_id).first()
        job.status = "processing"
        job.current_step = "loading_data"
        job.progress = 10
        db.commit()
        
        # Load profile and samples
        profile = db.query(MasterProfile).filter(MasterProfile.id == profile_id).first()
        resume_sample = db.query(SampleDocument).filter(
            SampleDocument.user_id == user_id,
            SampleDocument.document_type == "resume_sample"
        ).first()
        cover_sample = db.query(SampleDocument).filter(
            SampleDocument.user_id == user_id,
            SampleDocument.document_type == "cover_letter_sample"
        ).first()
        
        # Extract combined style guide
        job.current_step = "extracting_style"
        job.progress = 20
        db.commit()
        
        style_guide = {
            "resume_structure": json.loads(resume_sample.extracted_style) if resume_sample.extracted_style else {},
            "cover_letter_style": json.loads(cover_sample.extracted_style) if cover_sample.extracted_style else {}
        }
        
        # Enhance professional summary
        job.current_step = "enhancing_summary"
        job.progress = 40
        db.commit()
        
        if profile.professional_summary:
            prompt = prompt_loader.format_prompt(
                "enhancement",
                "enhance_summary",
                original_summary=profile.professional_summary,
                style_guide=json.dumps(style_guide, indent=2)
            )
            
            enhanced_summary = groq_client.complete(
                prompt,
                model=settings.GROQ_MODEL_QUALITY,
                temperature=0.7
            )
            
            # Apply rotation logic
            if profile.enhancement_version >= 1:
                profile.previous_enhanced_summary = profile.enhanced_summary
            profile.enhanced_summary = enhanced_summary
        
        # Enhance experiences (similar pattern)
        job.current_step = "enhancing_experiences"
        job.progress = 60
        db.commit()
        
        # ... enhance experiences logic ...
        
        # Enhance projects
        job.current_step = "enhancing_projects"
        job.progress = 80
        db.commit()
        
        # ... enhance projects logic ...
        
        # Update profile metadata
        profile.enhancement_version += 1
        profile.last_enhanced_at = datetime.utcnow()
        profile.enhancement_status = "completed"
        
        # Mark job as completed
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        # Handle failure
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        raise

def trigger_enhancement(
    user_id: int,
    profile_id: str,
    background_tasks: BackgroundTasks,
    db: Session
) -> str:
    """Trigger enhancement as background task"""
    
    # Create enhancement job
    job = EnhancementJob(
        user_id=user_id,
        profile_id=profile_id,
        status="queued"
    )
    db.add(job)
    db.commit()
    
    # Add to background tasks
    background_tasks.add_task(
        run_enhancement_job,
        job_id=job.id,
        user_id=user_id,
        profile_id=profile_id,
        db=db
    )
    
    return job.id
```

## API Router Example (routers/enhancement.py)

```python
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.security import get_current_user
from services.enhancement_service import trigger_enhancement
from models.enhancement_job import EnhancementJob

router = APIRouter()

@router.post("/trigger")
def start_enhancement(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger profile enhancement"""
    
    # Check prerequisites (profile exists, samples uploaded, etc.)
    # ... validation logic ...
    
    # Trigger background job
    job_id = trigger_enhancement(
        user_id=current_user["user_id"],
        profile_id=current_user["profile_id"],
        background_tasks=background_tasks,
        db=db
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Enhancement started"
    }

@router.get("/status")
def get_enhancement_status(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest enhancement job status"""
    
    job = db.query(EnhancementJob).filter(
        EnhancementJob.user_id == current_user["user_id"]
    ).order_by(EnhancementJob.started_at.desc()).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="No enhancement jobs found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "error": job.error_message
    }
```

## Environment Variables (.env)

```env
# App
DEBUG=true

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# Groq
GROQ_API_KEY=your-groq-api-key

# Database (SQLite - no config needed beyond default)
DATABASE_URL=sqlite:///./jobwise.db

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=5

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
**Days 1-2: Project Setup**
- Initialize FastAPI project structure
- Set up SQLAlchemy models
- Create database with all tables
- Configure environment variables

**Days 3-4: Authentication & Profile**
- Implement auth endpoints (register, login)
- Implement profile CRUD endpoints
- Test JWT flow

**Day 5: Jobs & File Upload**
- Implement job endpoints
- Implement sample upload with text extraction
- Test file processing

### Phase 2: AI Integration (Week 2)
**Days 1-2: Prompt System**
- Load prompts at startup
- Integrate Groq client
- Test basic completions

**Days 3-4: Enhancement Service**
- Implement style extraction
- Implement enhancement background tasks
- Test enhancement flow

**Day 5: Testing & Polish**
- End-to-end enhancement test
- Error handling
- Background task monitoring

### Phase 3: Generation (Week 3)
**Days 1-2: Rankings**
- Implement ranking service
- Test relevance scoring
- Bullet reordering logic

**Days 3-4: Generation**
- Resume compilation (pure logic)
- Cover letter generation (AI)
- Document storage

**Day 5: Integration Testing**
- Complete user journey test
- Performance optimization
- Bug fixes

## Running the Application

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your keys
cp .env.example .env

# Run migrations (create tables)
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn main:app --reload --port 8000
```

### Production
```bash
# Use gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Key Advantages of Single Backend

1. **Simplicity**: One codebase, one deployment
2. **Performance**: No network overhead between services
3. **Transactions**: Easy database transactions across tables
4. **Development**: Faster iteration, easier debugging
5. **Deployment**: Single server, simpler infrastructure
6. **Cost**: Lower hosting costs
7. **Scaling**: Vertical scaling first, horizontal later if needed

## Future Enhancements (Post-MVP)

- **Redis Integration**: For better caching and task queue
- **PostgreSQL Migration**: If concurrent users increase
- **WebSocket**: Real-time enhancement progress
- **PDF Export**: Convert text to formatted PDFs
- **Email Integration**: Send generated documents
- **Analytics**: Track generation success rates

---

**Ready for Implementation**: Single FastAPI backend with all features consolidated, using SQLite and in-memory operations for maximum simplicity.
