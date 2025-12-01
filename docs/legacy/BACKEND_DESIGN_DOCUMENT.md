# JobWise Backend - Comprehensive Design Document

**Project**: JobWise - AI-Powered Job Application Assistant
**Version**: 1.0
**Last Updated**: October 20, 2025
 

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Database Design](#database-design)
4. [API Architecture](#api-architecture)
5. [Security Model](#security-model)
6. [Data Flow & Sequences](#data-flow--sequences)
7. [Design Patterns](#design-patterns)
8. [Technology Stack](#technology-stack)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Architecture](#deployment-architecture)

---

## 1. Executive Summary

### 1.1 Project Overview

JobWise is a backend API service that powers an AI-driven job application assistant. The system helps users:
- Manage master resume profiles with comprehensive career data
- Search and save job opportunities from multiple sources
- Generate tailored resumes and cover letters using AI
- Export professional documents in multiple formats

### 1.2 Scope

This document is a specification for the JobWise backend system. It describes the architecture, API surface, data models, and integration patterns for generation and document export capabilities, along with repository, adapter, and deployment guidance. The content is intended to be implementation-agnostic where possible and to guide development, review, and integration efforts.

Key areas covered:
- Profile management and profile-driven generation
- Job description ingestion, parsing, and source attribution
- AI-powered generation pipeline and document export
- Adapter patterns for LLMs and storage
- Operational guidance (rate limits, quotas, and monitoring)

### 1.3 Key Metrics

- **API Endpoints**: 25+ implemented
- **Test Coverage**: 64%
- **Response Time**: <200ms (CRUD), <6s (generation)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Architecture**: Clean Architecture with Ports & Adapters

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
graph TB
    subgraph Client["Client Applications"]
        Mobile["Flutter Mobile App"]
        Web["Web Interface"]
        CLI["CLI Tools"]
    end
    
    subgraph FastAPI["FastAPI Application (Port 8000)"]
        subgraph Presentation["Presentation Layer (API)"]
            AuthAPI["Authentication endpoints"]
            ProfileAPI["Profile management"]
            JobAPI["Job search & management"]
            GenAPI["Generation & document APIs"]
        end
        
        subgraph Application["Application Layer (Services)"]
            AuthSvc["Auth Service"]
            ProfileSvc["Profile Service"]
            JobSvc["Job Service"]
            GenSvc["Generation Service"]
        end
        
        subgraph Domain["Domain Layer (Entities)"]
            Entities["Core business entities<br/>User, Profile, Job, Generation"]
            ValueObjects["Value objects<br/>Experience, Education, Skills"]
            Ports["Service ports<br/>ILLMService, IPDFGenerator"]
        end
        
        subgraph Infrastructure["Infrastructure Layer (Adapters)"]
            Repos["Database repositories"]
            Adapters["External service adapters"]
            Storage["File storage"]
        end
    end
    
    Database[(PostgreSQL Database)]
    ExtAPI[External APIs<br/>LLM, PDF Export]
    
    Client -->|HTTPS/JSON| FastAPI
    Presentation --> Application
    Application --> Domain
    Domain --> Infrastructure
    Infrastructure --> Database
    Infrastructure --> ExtAPI
    
    style Client fill:#e1f5ff
    style Presentation fill:#fff3cd
    style Application fill:#d4edda
    style Domain fill:#f8d7da
    style Infrastructure fill:#d1ecf1
    style Database fill:#6c757d,color:#fff
    style ExtAPI fill:#6c757d,color:#fff
```

### 2.2 Clean Architecture with Adapter Pattern

**See**: `backend/SIMPLIFIED_ARCHITECTURE.puml` for detailed diagram

#### Layer Responsibilities

**Presentation Layer** (`app/presentation/api/`)
- HTTP request/response handling
- Request validation (Pydantic DTOs)
- JWT authentication middleware
- OpenAPI documentation generation
- Error response formatting

**Application Layer** (`app/application/`)
- Business logic orchestration
- Service coordination
- Transaction boundaries
- Business rule validation
- Cross-entity operations

**Domain Layer** (`app/domain/`)
- Core business entities (User, Profile, Job, Generation)
- Value objects (Experience, Education, Skills)
- Port interfaces (ILLMService, IPDFGenerator)
- Domain invariants and rules
- No external dependencies

**Infrastructure Layer** (`app/infrastructure/`)
- Adapter implementations (LLM, PDF, Storage)
- Repository implementations
- Database models (SQLAlchemy)
- External service integration
- File system operations

#### Dependency Flow

```mermaid
graph LR
    Presentation["Presentation<br/>REST API Routers"] --> Application["Application<br/>Services & DTOs"]
    Application --> Domain["Domain<br/>Entities & Ports"]
    Infrastructure["Infrastructure<br/>Adapters & Repositories"] --> Domain
    
    style Presentation fill:#fff3cd
    style Application fill:#d4edda
    style Domain fill:#f8d7da
    style Infrastructure fill:#d1ecf1
```

**Key Principle**: Dependencies point inward. Domain layer has no external dependencies.

### 2.3 Adapter Pattern Implementation

```python
# Domain Port (Interface)
# File: app/domain/ports/llm_service_port.py
class ILLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Infrastructure Adapter (Implementation)
# File: app/infrastructure/adapters/llm/mock_llm.py
class MockLLMAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
    # Mock implementation for development
        await asyncio.sleep(2)
        return "Generated resume content..."

# Future (planned):
# File: app/infrastructure/adapters/llm/openai.py
class OpenAIAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
        # Real OpenAI implementation
        return await openai.ChatCompletion.create(...)
```

**Active Adapters (development)**:
- `mock_llm.py` - Mock LLM for development
- `reportlab.py` - PDF generation
- `local_storage.py` - File storage

**Planned Adapters**:
- `openai.py` - OpenAI GPT-4
- `claude.py` - Anthropic Claude
- `s3_storage.py` - AWS S3 (production)

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

**See**: `.context/diagrams/backend/database-schema-erd.puml` for complete ERD

```mermaid
erDiagram
    UserModel ||--o{ UserSessionModel : "has sessions"
    UserModel ||--o{ MasterProfileModel : "owns profiles"
    UserModel ||--o{ JobModel : "creates (when user_id set)"
    UserModel ||--o{ GenerationModel : "requests generations"
    UserModel ||--o{ SavedJobModel : "tracks applications"
    UserModel ||--o{ AuditLogModel : "generates logs"

    MasterProfileModel ||--o{ ExperienceModel : contains
    MasterProfileModel ||--o{ EducationModel : contains
    MasterProfileModel ||--o{ SkillModel : contains
    MasterProfileModel ||--o{ LanguageModel : contains
    MasterProfileModel ||--o{ CertificationModel : contains
    MasterProfileModel ||--o{ ProjectModel : contains
    MasterProfileModel ||--o{ GenerationModel : "used in"

    JobModel ||--o{ GenerationModel : "generates for"
    JobModel ||--o{ SavedJobModel : "applied to"

    GenerationModel ||--o{ DocumentModel : produces
    GenerationModel ||--o{ SavedJobModel : "used in applications"

    UserModel {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        bool is_active
        bool is_verified
        enum subscription_tier
        int generations_used
        int generations_limit
        timestamp created_at
        timestamp updated_at
    }

    MasterProfileModel {
        uuid id PK
        uuid user_id FK
        json personal_info "JSON: full_name, email, phone, location, linkedin, github, website"
        text professional_summary
        json skills "JSON: technical[], soft[], languages[], certifications[]"
        json custom_fields "JSON: flexible key-value pairs for achievements, hobbies, interests, etc."
        int version
        bool is_active
        timestamp created_at
        timestamp updated_at
    }

    ExperienceModel {
        uuid id PK
        uuid profile_id FK
        string title
        string company
        string location
        date start_date
        date end_date "nullable for current positions"
        bool is_current
        text description
        json achievements "array of achievement strings"
        timestamp created_at
        timestamp updated_at
    }

    EducationModel {
        uuid id PK
        uuid profile_id FK
        string institution
        string degree
        string field_of_study
        date start_date
        date end_date
        string gpa "optional"
        json honors "array of honor strings"
        timestamp created_at
        timestamp updated_at
    }

    ProjectModel {
        uuid id PK
        uuid profile_id FK
        string name
        text description
        json technologies "array of technology strings"
        string url "optional GitHub/project URL"
        date start_date
        date end_date "nullable for ongoing projects"
        timestamp created_at
        timestamp updated_at
    }

    SkillModel {
        uuid id PK
        uuid profile_id FK
        string category "technical, soft, language, certification"
        string name
        string proficiency "optional: native, fluent, conversational, basic"
        string issuer "optional: for certifications"
        date date_obtained "optional: for certifications"
        string credential_id "optional: for certifications"
        timestamp created_at
        timestamp updated_at
    }

    JobModel {
        uuid id PK
        uuid user_id FK "nullable"
        string source
        string title
        string company
        string location
        text description
        text raw_text
        json parsed_keywords
        json requirements
        text benefits
        string salary_range
        bool remote
        date date_posted
        date application_deadline
        enum status
        timestamp created_at
        timestamp updated_at
    }

    GenerationModel {
        uuid id PK
        uuid user_id FK
        uuid profile_id FK
        uuid job_id FK
        enum document_type
        enum status
        float match_score
        int keywords_required_count
        int keywords_matched_count
        json recommendations
        json stage_progress
        text error_message
        int token_usage
        float generation_time_seconds
        timestamp created_at
        timestamp completed_at
        timestamp updated_at
    }

    DocumentModel {
        uuid id PK
        uuid generation_id FK
        uuid user_id FK
        uuid job_id FK
        uuid profile_id FK
        enum document_type
        int version_number
        string template
        json parameters
        text content_text
        text content_html
        text content_markdown
        string pdf_file_path
        int pdf_size_bytes
        int pdf_page_count
        float ats_score
        json ats_score_details
        timestamp created_at
        timestamp updated_at
    }

    SavedJobModel {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
        enum status
        text notes
        timestamp saved_at
        timestamp applied_at
        timestamp updated_at
    }
```

#### Core Entities

**UserModel**
- `id`: UUID (Primary Key)
- `email`: String (unique, indexed)
- `hashed_password`: String
- `full_name`: String
- `is_active`: Boolean (default: true)
- `is_verified`: Boolean (default: false)
- `subscription_tier`: Enum (free, premium, enterprise)
- `generations_used`: Integer (monthly counter)
- `generations_limit`: Integer (based on tier)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**MasterProfileModel** (JSON-based Storage)
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → UserModel)
- `personal_info`: JSON (structured object containing: full_name, email, phone, location, linkedin, github, website)
- `professional_summary`: Text (optional)
- `skills`: JSON (structured object containing: technical[], soft[], languages[], certifications[])
- `custom_fields`: JSON (flexible key-value pairs for achievements, hobbies, interests, volunteer_work, publications, awards, etc.)
- `version`: Integer (for versioning support, incremented on updates)
- `is_active`: Boolean (default: true)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- **Note**: Uses JSON fields for flexible schema evolution and bulk operations support

**ExperienceModel**
- `id`: UUID (Primary Key)
- `profile_id`: UUID (Foreign Key → MasterProfileModel)
- `title`: String (job title, max 200 chars)
- `company`: String (company name, max 200 chars)
- `location`: String (optional, max 200 chars)
- `start_date`: Date (required)
- `end_date`: Date (nullable for current positions)
- `is_current`: Boolean (derived from end_date being null)
- `description`: Text (job description and responsibilities)
- `achievements`: JSON (array of achievement strings)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**EducationModel**
- `id`: UUID (Primary Key)
- `profile_id`: UUID (Foreign Key → MasterProfileModel)
- `institution`: String (school/university name, max 200 chars)
- `degree`: String (degree title, max 200 chars)
- `field_of_study`: String (major/field, max 200 chars)
- `start_date`: Date (required)
- `end_date`: Date (required)
- `gpa`: String (optional, e.g., "3.8/4.0")
- `honors`: JSON (array of honor/award strings)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**ProjectModel**
- `id`: UUID (Primary Key)
- `profile_id`: UUID (Foreign Key → MasterProfileModel)
- `name`: String (project name, max 200 chars)
- `description`: Text (project description and impact)
- `technologies`: JSON (array of technology strings)
- `url`: String (optional GitHub/project URL)
- `start_date`: Date (required)
- `end_date`: Date (nullable for ongoing projects)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**SkillModel** (Unified Skills & Certifications)
- `id`: UUID (Primary Key)
- `profile_id`: UUID (Foreign Key → MasterProfileModel)
- `category`: String (technical, soft, language, certification)
- `name`: String (skill/certification name, max 200 chars)
- `proficiency`: String (optional: native, fluent, conversational, basic for languages; level for skills)
- `issuer`: String (optional: issuing organization for certifications)
- `date_obtained`: Date (optional: for certifications)
- `credential_id`: String (optional: credential ID for certifications)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**JobModel (Unified)**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → UserModel, nullable for external jobs)
- `source`: String (e.g., `user_created`, `indeed`, `linkedin`, `glassdoor`, `monster`, `static`, `scraped`, `imported`)
- `title`: String (job title, indexed)
- `company`: String (company name, indexed)
- `location`: String (optional)
- `description`: Text (full job description)
- `raw_text`: Text (original unparsed text)
- `parsed_keywords`: JSON (extracted keywords and requirements)
- `requirements`: JSON (structured requirements list)
- `benefits`: Text (optional)
- `salary_range`: String (optional)
- `remote`: Boolean (default: false)
- `date_posted`: Date (optional)
- `application_deadline`: Date (optional)
- `status`: Enum (active, draft, archived, expired)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- Relationships: One-to-many (Generations, SavedJobs)

**GenerationModel**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → UserModel)
- `profile_id`: UUID (Foreign Key → MasterProfileModel)
- `job_id`: UUID (Foreign Key → JobModel)
- `document_type`: Enum (resume, cover_letter)
- `status`: Enum (pending, generating, completed, needs_review, failed, cancelled)
- `match_score`: Float (0-100, job-profile match percentage)
- `keywords_required_count`: Integer (total keywords from job)
- `keywords_matched_count`: Integer (keywords found in profile)
- `recommendations`: JSON (array of improvement suggestions)
- `stage_progress`: JSON (tracks 5-stage pipeline progress)
- `error_message`: Text (optional, for failed generations)
- `token_usage`: Integer (LLM tokens consumed)
- `generation_time_seconds`: Float (time to complete)
- `created_at`: Timestamp (generation start time)
- `completed_at`: Timestamp (nullable, generation completion time)
- `updated_at`: Timestamp
- Relationships: Many-to-one (User, Profile, Job), One-to-many (Documents)

**DocumentModel**
- `id`: UUID (Primary Key)
- `generation_id`: UUID (Foreign Key → GenerationModel)
- `user_id`: UUID (Foreign Key → UserModel)
- `job_id`: UUID (Foreign Key → JobModel, denormalized for queries)
- `profile_id`: UUID (Foreign Key → MasterProfileModel, denormalized)
- `document_type`: Enum (resume, cover_letter)
- `version_number`: Integer (document version)
- `template`: String (template name used)
- `parameters`: JSON (generation parameters and options)
- `content_text`: Text (plain text content)
- `content_html`: Text (HTML formatted content)
- `content_markdown`: Text (Markdown content)
- `pdf_file_path`: String (path to PDF file)
- `pdf_size_bytes`: Integer
- `pdf_page_count`: Integer
- `ats_score`: Float (0-100, overall ATS compatibility score)
- `ats_score_details`: JSON (breakdown by category)
- `created_at`: Timestamp
- `updated_at`: Timestamp
- Relationships: Many-to-one (Generation, User, Job, Profile)

**SavedJobModel**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key → UserModel)
- `job_id`: UUID (Foreign Key → JobModel)
- `status`: Enum (interested, applied, interviewing, offer, rejected, closed)
- `notes`: Text (user notes about the job)
- `saved_at`: Timestamp (when job was saved)
- `applied_at`: Timestamp (nullable, when user applied)
- `updated_at`: Timestamp
- Relationships: Many-to-one (User, Job)

#### Relationship Summary

```
User (1) ──< (N) Profile
User (1) ──< (N) Job (user_created only)
User (1) ──< (N) Generation
User (1) ──< (N) SavedJob

Profile (1) ──< (N) Experience
Profile (1) ──< (N) Education
Profile (1) ──< (N) Skill (unified: technical, soft, languages, certifications)
Profile (1) ──< (N) Project
Profile (1) ──< (N) Generation

Job (1) ──< (N) Generation (all sources)
Job (1) ──< (N) SavedJob (all sources)

Generation (1) ──< (N) Document
```

### 3.4 Bulk Operations Schema Design

**JSON-Based Storage Strategy**:
The MasterProfileModel uses JSON fields for `personal_info`, `skills`, and `custom_fields` to enable:
- Flexible schema evolution without migrations
- Efficient bulk operations on related data
- Complex nested structures (languages with proficiency, certifications with credentials)
- Custom fields support for user-defined profile sections

**Component Model Strategy**:
Separate tables for Experiences, Education, Projects, and Skills enable:
- Granular CRUD operations with individual record tracking
- Efficient bulk operations (add/update multiple items simultaneously)
- Relationship integrity and cascading deletes
- Optimized queries for specific component types

**Bulk Operation Patterns**:
- **Create Multiple**: INSERT multiple records in single transaction
- **Update Multiple**: UPDATE with WHERE IN clauses for batch updates
- **Delete Multiple**: DELETE with WHERE IN for bulk removal
- **Query Multiple**: SELECT with JOIN for efficient bulk retrieval

**Versioning Strategy**:
- MasterProfileModel.version incremented on any profile update
- Component models track individual created_at/updated_at timestamps
- Enables conflict resolution and audit trails for bulk operations

### 3.2 Database Technology

**Development**: SQLite with async support (`aiosqlite`)
**Production**: PostgreSQL with async support (`asyncpg`)

**Migrations**: Alembic (currently on hold, using direct schema.py)

**Connection Pooling**:
- Pool size: 20 connections
- Max overflow: 10
- Pool timeout: 30 seconds

### 3.3 Indexing Strategy

```sql
-- User and authentication indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active_verified ON users(is_active, is_verified);

-- Profile indexes for bulk operations
CREATE INDEX idx_master_profiles_user_id ON master_profiles(user_id);
CREATE INDEX idx_master_profiles_user_active ON master_profiles(user_id, is_active);
CREATE INDEX idx_master_profiles_version ON master_profiles(version);

-- Component relationship indexes (critical for bulk operations)
CREATE INDEX idx_experiences_profile_id ON experiences(profile_id);
CREATE INDEX idx_experiences_profile_date ON experiences(profile_id, start_date DESC);
CREATE INDEX idx_education_profile_id ON education(profile_id);
CREATE INDEX idx_education_profile_date ON education(profile_id, start_date DESC);
CREATE INDEX idx_projects_profile_id ON projects(profile_id);
CREATE INDEX idx_projects_profile_date ON projects(profile_id, start_date DESC);
CREATE INDEX idx_skills_profile_id ON skills(profile_id);
CREATE INDEX idx_skills_profile_category ON skills(profile_id, category);

-- Job search and filtering indexes
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_user_source ON jobs(user_id, source);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_source_status ON jobs(source, status);

-- Generation pipeline indexes
CREATE INDEX idx_generations_user_status ON generations(user_id, status);
CREATE INDEX idx_generations_profile_job ON generations(profile_id, job_id);
CREATE INDEX idx_generations_created_status ON generations(created_at, status);

-- Document and export indexes
CREATE INDEX idx_documents_generation ON documents(generation_id);
CREATE INDEX idx_documents_job_id ON documents(job_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_profile_id ON documents(profile_id);

-- Saved jobs and application tracking
CREATE INDEX idx_saved_jobs_user_status ON saved_jobs(user_id, status, updated_at);
CREATE INDEX idx_saved_jobs_job_id ON saved_jobs(job_id);

-- JSON field indexes for complex queries (PostgreSQL GIN indexes)
-- CREATE INDEX idx_master_profiles_personal_info_gin ON master_profiles USING gin(personal_info);
-- CREATE INDEX idx_master_profiles_skills_gin ON master_profiles USING gin(skills);
-- CREATE INDEX idx_master_profiles_custom_fields_gin ON master_profiles USING gin(custom_fields);
-- CREATE INDEX idx_jobs_parsed_keywords_gin ON jobs USING gin(parsed_keywords);
-- CREATE INDEX idx_jobs_requirements_gin ON jobs USING gin(requirements);

-- Composite indexes for bulk operations
CREATE INDEX idx_experiences_bulk_ops ON experiences(profile_id, updated_at DESC);
CREATE INDEX idx_education_bulk_ops ON education(profile_id, updated_at DESC);
CREATE INDEX idx_projects_bulk_ops ON projects(profile_id, updated_at DESC);
CREATE INDEX idx_skills_bulk_ops ON skills(profile_id, category, updated_at DESC);
```

**Bulk Operations Performance Notes**:
- Profile component indexes prioritize `profile_id` for efficient bulk queries
- Date-based sorting indexes support chronological ordering in bulk responses
- Category-based indexes on skills enable filtered bulk operations
- Composite indexes on `(profile_id, updated_at DESC)` optimize bulk updates with versioning

---

## 4. API Architecture

### 4.1 API Structure

**Base URL**: `http://localhost:8000/api/v1`

**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

### 4.2 API Endpoints by Service

#### Authentication API (`/api/v1/auth/`)

```
POST   /register           # Create new user account
POST   /login              # Authenticate user, receive JWT
POST   /refresh            # Refresh access token
GET    /me                 # Get current user profile
POST   /logout             # Invalidate session
```

#### Profile API (`/api/v1/profiles/`)

```
POST   /                   # Create master profile
GET    /me                 # Get current user's profile
GET    /{id}               # Get profile by ID
PUT    /{id}               # Update profile
DELETE /{id}               # Delete profile

# Component Management
POST   /{id}/experiences   # Add experience
PUT    /{id}/experiences/{exp_id}
DELETE /{id}/experiences/{exp_id}
POST   /{id}/education     # Add education
PUT    /{id}/education/{edu_id}
DELETE /{id}/education/{edu_id}
POST   /{id}/projects      # Add project
PUT    /{id}/projects/{proj_id}
DELETE /{id}/projects/{proj_id}

# Analytics
GET    /{id}/analytics     # Profile completeness & insights
GET    /{id}/summary       # Profile summary for generation
```


#### Job API (`/api/v1/jobs/`)

Unified CRUD API for managing jobs and job descriptions. Accepts raw text (auto-parsed) or structured data.

```
# Core CRUD endpoints
POST   /                   # Create job (raw text or structured) - request must include `source` field identifying the origin of the job
GET    /                   # List user's jobs (with filters)
GET    /{id}               # Get job details
PUT    /{id}               # Update job
DELETE /{id}               # Delete job (hard delete)

# Query parameters for GET /
?status=active|archived         # Filter by status
?source=user_created|<provider_name>  # Filter by source (e.g., user_created, indeed, linkedin)
?limit=20                       # Items per page (1-100)
?offset=0                       # Pagination offset
```

**Key Features:**
 - Accepts `raw_text` (auto-parsed) OR structured fields
 - Sources: `user_created` (copy-paste) or third-party provider names (e.g., `indeed`, `linkedin`, `glassdoor`, `monster`) for imported job data
    - API Contract Note: The OpenAPI contract requires a `source` field in the POST `/jobs` payload. This is a free-form string that identifies the job origin (for example: `user_created`, `indeed`, or `linkedin`).
 - Text parser extracts title, company, requirements, benefits
 - Text parsing via LLM: The job description text parser may use the LLM service adapter (domain port: `ILLMService`) to improve extraction accuracy for unstructured text. The parser will prefer deterministic parsing rules and fall back to LLM-powered parsing for ambiguous or complex descriptions. LLM usage is opt-in and rate-limited per account to control cost.
 - Ownership verification on all operations
 - Hard delete: Job deletions are performed as hard deletes and immediately remove the job row from the database. If auditing or undelete functionality is required later, a `deleted_at` timestamp and/or archive table will be added.

#### Generation API (`/api/v1/generations/`)

```
POST   /resume             # Start resume generation (requires `profile_id` + `job_id`) -> returns generation resource
POST   /cover-letter       # Start cover letter generation (requires `profile_id` + `job_id`) -> returns generation resource

GET    /{id}               # Get generation status (where {id} == generation_id)
GET    /{id}/result        # Get generated content and document links (document_id, pdf_url)
POST   /{id}/regenerate    # Regenerate using an existing generation_id with optional changed options
DELETE /{id}               # Cancel/delete generation

GET    /                   # List user generations (supports filters, see below)
GET    /?job_id={job_id}   # List generations associated with a specific job description
POST   /{id}/feedback      # Provide feedback
GET    /templates          # List resume templates

GET    /{id}/analytics     # Quality metrics & ATS score
POST   /{id}/validate      # Re-run validation
```

Generation responsibilities
-------------------------
Each generation request is responsible for producing one tailored resume (and optionally a cover letter) for a single target job. The generation pipeline requires a single master profile (`profile_id`) and a single job description (`job_id`) as inputs. The pipeline executes the following responsibilities:

- 1) Fetch & Analyze Inputs: Retrieve the profile and the specified job description from the database. Optionally send the job description to the LLM adapter (via `ILLMService`) with a structured prompt to extract or clarify requirements, skills, and role expectations.
- 2) Profile Compilation: Score and rank profile items (experiences, skills, education) for relevance to the target job; prioritize or redact sections to optimize match and ATS compatibility.
- 3) Document Generation: Generate the tailored resume content and, if requested, a cover letter using the LLM. The prompt includes the job analysis report and the compiled profile as structured context.
- 4) Quality Validation: Run ATS checks, grammar/consistency checks, and policy validations. If issues are found, either auto-correct or flag the generation for review based on configuration.
- 5) Persist & Export: Save the generation record and produced documents with references to `profile_id` and `job_id`. Optionally export a PDF and store the file metadata.

Each produced resume and cover letter is linked to its source job description. This enables users to track which resume was tailored to which job, and to regenerate based on feedback or updated job descriptions.

Notes on `{id}` and client integration
-------------------------------------
- `{id}` in routes such as `GET /{id}` and `GET /{id}/result` is the `generation_id` (UUID) that identifies a single asynchronous generation run.
- The typical client flow is:
    1. Client has `profile_id` (user's selected profile) and `job_id` (the target job the user is viewing).
    2. Client POSTs to `/api/v1/generations/resume` or `/api/v1/generations/cover-letter` with `{profile_id, job_id, options}`.
    3. Server responds 201 Created with:
         - Location header: `/api/v1/generations/{generation_id}`
         - Response body containing `generation_id`, `status` (pending), `profile_id`, `job_id`, and optional `estimated_completion` and `progress` snapshot.
    4. Client stores the `generation_id` and polls `GET /api/v1/generations/{generation_id}` until completion or subscribes to realtime updates (SSE/WebSocket) if available.
    5. On completion, client either calls `GET /api/v1/generations/{generation_id}/result` or reads the `result` section in the completed status response to obtain `document_id`/`pdf_url`.

Operational notes & recommended API improvements
------------------------------------------------
- POST behavior: POST `/resume` and POST `/cover-letter` MUST require `profile_id` and `job_id` in the request body. The server MUST validate ownership and existence of both resources and return 400/403/404 appropriately.
- Response contract: POST requests should return 201 with Location and a minimal `GenerationResponse` body that contains `generation_id` to make it easy for the frontend to continue.
- Idempotency: Add optional support for an `Idempotency-Key` header (or `client_request_id` body field) so clients can safely retry POST without creating duplicate generation runs.
- Query by job: Add `GET /generations?job_id={job_id}` to let clients discover all generations for a job (useful after navigation or when state was lost).
- Real-time updates: Consider providing server-sent events (SSE) or WebSocket notifications for progress updates to avoid aggressive polling.
- Regenerate semantics: `POST /{id}/regenerate` should accept optional updated options or instructions and create a new generation run linked to the same `job_id` and `profile_id` (or optionally update in-place depending on policy). Document whether regenerate creates a new generation resource or reuses the same `generation_id`.
- Result linking: The generation final result should include `document_id` (the DocumentModel id) and `pdf_url` so the client can immediately link to the exported PDF and store the mapping locally.
- Rate limiting & quotas: Document 429 behavior and recommended client backoff strategy for generation endpoints.

Frontend integration checklist (concrete)
---------------------------------------
- Ensure the UI has both `job_id` and `profile_id` available when the user clicks Generate (job list/detail or saved job context).
- POST to `/api/v1/generations/resume` with required fields; read `generation_id` from response body and `Location` header.
- Save `generation_id` (in-memory, store, or local DB) so the user can revisit the job and see in-progress work.
- Poll `GET /api/v1/generations/{generation_id}` or subscribe to realtime updates. On `completed`, fetch `GET /api/v1/generations/{generation_id}/result` or read the `result` field.
- If the client must retry the POST (network blip), include `Idempotency-Key` to prevent duplicates.

Operational notes
-----------------
- The generation API is asynchronous: POST returns a 201 with a Location header to poll generation status. Long-running LLM calls are executed in the background.
- LLM usage for both job analysis and document generation is opt-in and rate-limited per account to control cost.
- Token budgets and performance targets are enforced per-request to limit resource consumption and ensure SLA behavior.

#### Document API (`/api/v1/documents/`) - Sprint 2

```
GET    /                   # List user documents (supports ?job_id= and ?profile_id= filters)
GET    /{id}               # Get document details
DELETE /{id}               # Delete document
PUT    /{id}               # Update metadata

POST   /{id}/export        # Export to format (PDF/TXT)
GET    /{id}/download      # Download exported file
GET    /export-formats     # List available formats
POST   /preview            # Generate preview
GET    /?job_id={job_id}   # List documents related to a specific job description
POST   /generate           # Start generation using `profile_id` + `job_id` (handled by Generation API: /api/v1/generations/)
```

#### Document API (`/api/v1/documents/`)

```
GET    /                   # List user documents (supports ?job_id= and ?profile_id= filters)
GET    /{id}               # Get document details
```

### 4.3 Request/Response Format

**Request Example** (Create Profile):
```json
POST /api/v1/profiles/
Authorization: Bearer <jwt_token>

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "location": "San Francisco, CA",
  "professional_summary": "Senior software engineer...",
  "linkedin": "https://linkedin.com/in/johndoe"
}
```

**Response Example**:
```json
{
  "id": "uuid-here",
  "user_id": "user-uuid",
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "location": "San Francisco, CA",
  "professional_summary": "Senior software engineer...",
  "linkedin": "https://linkedin.com/in/johndoe",
  "version": 1,
  "is_active": true,
  "created_at": "2025-10-20T12:00:00Z",
  "updated_at": "2025-10-20T12:00:00Z"
}
```

**Error Response**:
```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Profile not found",
    "details": {
      "profile_id": "uuid-here"
    }
  }
}
```

### 4.4 HTTP Status Codes

- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (duplicate)
- `422 Unprocessable Entity` - Semantic validation error
- `500 Internal Server Error` - Unexpected error

---

## 5. Security Model

### 5.1 Authentication & Authorization

**JWT Token Authentication**:
```python
# Token structure
{
  "sub": "user_id",
  "email": "user@example.com",
  "exp": 1698624000,  # Expiration timestamp
  "iat": 1698537600   # Issued at timestamp
}
```

**Token Lifecycle**:
- Access token: 1 hour expiration
- Refresh token: 7 days expiration
- Stored in HTTP-only cookies (production)
- Authorization header: `Bearer <token>`

**Password Security**:
- bcrypt hashing (cost factor: 12)
- Minimum 8 characters
- Complexity requirements (uppercase, lowercase, number)
- Salted and hashed before storage

### 5.2 Authorization Model

**Endpoint Protection**:
```python
# Protected endpoint example
@router.get("/profiles/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    # current_user injected by JWT middleware
    # Only authenticated users can access
```

**Resource Ownership**:
```python
# Verify user owns resource
async def verify_profile_ownership(
    profile_id: str,
    current_user: User
):
    profile = await profile_repo.get_by_id(profile_id)
    if profile.user_id != current_user.id:
        raise ForbiddenException("Not authorized")
```

### 5.3 Data Protection

**Sensitive Data**:
- Passwords: Never stored in plain text, bcrypt hashed
- JWT secrets: Stored in environment variables
- API keys: Environment variables only
- Database credentials: Environment variables

**CORS Configuration**:
```python
CORS_ORIGINS = [
    "http://localhost:3000",  # Flutter web dev
    "https://jobwise.app",    # Production
]
```

**Input Validation**:
- All inputs validated with Pydantic models
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (proper escaping)

### 5.4 Rate Limiting

**Planned** (not yet implemented):
- 100 requests/minute per user (general endpoints)
- 10 generations/hour per user (AI endpoints)
- 1000 requests/day per IP (public endpoints)

---

## 6. Data Flow & Sequences

### 6.1 User Registration Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthAPI as Auth API
    participant AuthSvc as Auth Service
    participant Database
    
    Client->>AuthAPI: POST /register
    AuthAPI->>AuthSvc: validate_email()
    AuthSvc->>AuthSvc: hash_password()
    AuthSvc->>Database: create_user()
    Database-->>AuthSvc: User created
    AuthSvc->>AuthSvc: create JWT
    AuthSvc-->>AuthAPI: User + Token
    AuthAPI-->>Client: {user, token}
```

### 6.2 Resume Generation Flow

```mermaid
sequenceDiagram
    participant Client
    participant GenAPI as Generation API
    participant GenSvc as Generation Service
    participant LLM as LLM Service
    participant DB as Database
    participant Profile as Profile Repo
    
    Client->>GenAPI: POST /generations/resume
    GenAPI->>GenSvc: create_generation()
    GenSvc->>DB: save (pending)
    DB-->>GenSvc: Generation ID
    GenSvc-->>GenAPI: {id, status: pending}
    GenAPI-->>Client: 201 Created + Location header
    
    Note over GenSvc,LLM: Async Pipeline Start
    
    GenSvc->>DB: 1. analyze_job()
    GenSvc->>Profile: 2. get_profile()
    Profile-->>GenSvc: Profile data
    GenSvc->>LLM: 3. generate_content()
    Note over LLM: Mock 2s processing
    LLM-->>GenSvc: Generated content
    GenSvc->>GenSvc: 4. validate_quality()
    GenSvc->>GenSvc: 5. prepare_export()
    GenSvc->>DB: save (completed)
    
    Client->>GenAPI: GET /generations/{id}/result
    GenAPI->>GenSvc: get_result()
    GenSvc->>DB: fetch document
    DB-->>GenSvc: Document data
    GenSvc-->>GenAPI: Result
    GenAPI-->>Client: {content, pdf_url}
```

### 6.3 PDF Export Flow

```mermaid
sequenceDiagram
    participant Client
    participant DocAPI as Document API
    participant DocSvc as Document Service
    participant PDFGen as PDF Generator
    participant Storage
    
    Client->>DocAPI: POST /documents/{id}/export
    DocAPI->>DocSvc: export()
    DocSvc->>PDFGen: generate_pdf()
    Note over PDFGen: ReportLab processing
    PDFGen-->>DocSvc: PDF bytes
    DocSvc->>Storage: save_file()
    Storage-->>DocSvc: File path
    DocSvc-->>DocAPI: {download_url}
    DocAPI-->>Client: Export result
    
    Client->>DocAPI: GET /download
    DocAPI->>DocSvc: get_file()
    DocSvc->>Storage: read_file()
    Storage-->>DocSvc: PDF bytes
    DocSvc-->>DocAPI: File data
    DocAPI-->>Client: PDF download
```

---

## 7. Design Patterns

### 7.1 Repository Pattern

**Purpose**: Abstract data access logic from business logic

```python
# Domain Repository Interface
class IProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Profile]:
        pass

# Infrastructure Implementation
class SQLAlchemyProfileRepository(IProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: Profile) -> Profile:
        db_profile = ProfileModel(**profile.dict())
        self.session.add(db_profile)
        await self.session.commit()
        return profile
```

### 7.2 Adapter Pattern (Ports & Adapters)

**Purpose**: Decouple external services from business logic

```python
# Port (Interface in Domain)
class ILLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

# Adapter (Implementation in Infrastructure)
class MockLLMAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(2)
        return "Mock generated content"

# Service uses port, not concrete implementation
class GenerationService:
    def __init__(self, llm_service: ILLMService):
        self.llm = llm_service  # Depends on interface

    async def generate_resume(self, profile, job):
        content = await self.llm.generate(prompt)
        return content
```

### 7.3 Dependency Injection

**Purpose**: Provide loose coupling and testability

```python
# Dependencies module
def get_llm_service() -> ILLMService:
    # Mock implementation for development
    return MockLLMAdapter()
    # Production: Real implementation
    # return OpenAIAdapter(settings.OPENAI_API_KEY)

def get_profile_repo(
    session: AsyncSession = Depends(get_db)
) -> IProfileRepository:
    return SQLAlchemyProfileRepository(session)

# API endpoint
@router.post("/generations/resume")
async def create_generation(
    llm: ILLMService = Depends(get_llm_service),
    repo: IProfileRepository = Depends(get_profile_repo)
):
    service = GenerationService(llm, repo)
    return await service.generate_resume(...)
```

### 7.4 DTO Pattern

**Purpose**: Separate API contracts from domain models

```python
# Request DTO (API Layer)
class CreateProfileRequest(BaseModel):
    full_name: str = Field(..., max_length=200)
    email: EmailStr
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Domain Entity (Domain Layer)
@dataclass
class Profile:
    id: str
    user_id: str
    full_name: str
    email: str
    phone: Optional[str]
    created_at: datetime

# Response DTO (API Layer)
class ProfileResponse(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 7.5 Value Object Pattern

**Purpose**: Encapsulate complex domain concepts

```python
# Value Object
class Experience(BaseModel):
    title: str
    company: str
    start_date: date
    end_date: Optional[date]
    description: str
    achievements: List[str]

    def duration_months(self) -> int:
        end = self.end_date or date.today()
        return (end.year - self.start_date.year) * 12 + \
               (end.month - self.start_date.month)

    def is_current(self) -> bool:
        return self.end_date is None
```

---

## 8. Technology Stack

### 8.1 Core Framework

**FastAPI 0.104.1**
- Async/await support
- Automatic OpenAPI documentation
- Pydantic validation
- High performance (Starlette + Uvicorn)

### 8.2 Database

**SQLAlchemy 2.0.23** (ORM)
- Async support (`asyncpg`, `aiosqlite`)
- Type hints
- Declarative models

**Alembic** (Migrations)
- Currently on hold (using schema.py directly)
- Planned for production

### 8.3 Authentication

**python-jose 3.3.0** (JWT)
**passlib 1.7.4** (Password hashing)
- bcrypt algorithm
- Salted hashing

### 8.4 Validation

**Pydantic 2.5.0**
- Request/response validation
- Data serialization
- Settings management

### 8.5 Testing

**pytest 7.4.3**
- Async support (`pytest-asyncio`)
- Coverage reporting (`pytest-cov`)
- Mocking (`pytest-mock`)
- Factory pattern (`factory-boy`)

### 8.6 External Services

**LLM Providers**:
- Mock implementation: for local development and tests
- OpenAI GPT-4 (`openai 1.6.1`): planned integration
- Anthropic Claude (`anthropic 0.7.7`): planned integration

**PDF Generation**:
- ReportLab 4.0.7 (development)

### 8.7 Development Tools

- **Black** (code formatting)
- **isort** (import sorting)
- **mypy** (type checking)
- **flake8** (linting)

---

## 9. Testing Strategy

### 9.1 Test Pyramid

```
        ┌─────────────┐
        │     E2E     │  10% (Integration)
        │   Tests     │
      ┌─┴─────────────┴─┐
      │  Integration     │  30% (API + DB)
      │     Tests        │
    ┌─┴──────────────────┴─┐
    │    Unit Tests         │  60% (Services + Domain)
    │                       │
    └───────────────────────┘
```

### 9.2 Test Organization

```
tests/
├── unit/
│   ├── test_auth_service.py
│   ├── test_profile_service.py
│   └── test_generation_service.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_profile_api.py
│   ├── test_generation_pipeline.py
│   └── test_document_export.py
├── e2e/
│   └── test_complete_workflow.py
└── conftest.py  # Shared fixtures
```

### 9.3 Test Markers

```python
@pytest.mark.unit        # Unit tests (fast, no I/O)
@pytest.mark.integration # Integration tests (DB, API)
@pytest.mark.slow        # Slow-running tests
@pytest.mark.ai          # Tests requiring AI services
```

### 9.4 Coverage Targets

- **Overall**: 80%
- **Domain Layer**: 90%+
- **Service Layer**: 85%+
- **API Layer**: 75%+
- **Current**: 64%

### 9.5 Test Database

- Separate SQLite database (`test_jobwise.db`)
- Automatic creation/teardown per test session
- Fixtures in `conftest.py`

```python
@pytest.fixture
async def db_session():
    """Provide async database session for tests"""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()
```

---

## 10. Deployment Architecture

### 10.1 Development Environment

```
┌─────────────────────────────────┐
│   Developer Machine (Windows)    │
│                                  │
│  ┌────────────────────────────┐ │
│  │  FastAPI (Port 8000)       │ │
│  │  - uvicorn --reload        │ │
│  │  - SQLite database         │ │
│  │  - Mock external services  │ │
│  └────────────────────────────┘ │
│                                  │
│  ┌────────────────────────────┐ │
│  │  Testing                   │ │
│  │  - pytest with coverage    │ │
│  │  - Test database           │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

### 10.2 Production Architecture (Planned)

```
                    ┌─────────────┐
                    │   Clients   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  CloudFlare │
                    │   (CDN/SSL) │
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │    Load Balancer        │
              │      (nginx)            │
              └────────┬───────┬────────┘
                       │       │
            ┌──────────▼─┐   ┌▼──────────┐
            │  FastAPI    │   │  FastAPI  │
            │  Instance 1 │   │ Instance 2│
            └──────┬──────┘   └───┬───────┘
                   │              │
            ┌──────┴──────────────┴──────┐
            │                             │
     ┌──────▼──────┐            ┌────────▼──────┐
     │ PostgreSQL  │            │  Redis Cache  │
     │   (Primary) │            │               │
     └─────────────┘            └───────────────┘
            │
     ┌──────▼──────┐
     │ PostgreSQL  │
     │  (Replica)  │
     └─────────────┘
```

### 10.3 Environment Configuration

**Development** (`.env`):
```bash
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./jobwise.db
JWT_SECRET_KEY=dev-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

**Production** (`.env`):
```bash
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET_KEY=<secure-random-key>
CORS_ORIGINS=["https://jobwise.app"]
REDIS_URL=redis://cache-host:6379
```

### 10.4 Deployment Steps

1. **Build**: Package application
2. **Test**: Run full test suite
3. **Migrate**: Run database migrations
4. **Deploy**: Deploy to containers
5. **Verify**: Health checks and smoke tests

---

## Appendix

### A. Glossary

- **ATS**: Applicant Tracking System
- **DTO**: Data Transfer Object
- **JWT**: JSON Web Token
- **ORM**: Object-Relational Mapping
- **CRUD**: Create, Read, Update, Delete

### B. References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Clean Architecture: https://blog.cleancoder.com/

### C. Document Diagrams

All PlantUML diagrams can be found in:
- `backend/SIMPLIFIED_ARCHITECTURE.puml` - System architecture
- `.context/diagrams/backend/database-schema-erd.puml` - Database ERD

To render diagrams:
```bash
# Using PlantUML CLI
plantuml backend/SIMPLIFIED_ARCHITECTURE.puml

# Or use online renderer
# https://www.plantuml.com/plantuml/uml/
```

---

**Document Version**: 1.0
**Last Updated**: October 20, 2025
**Maintained By**: Backend Development Team
**Review Frequency**: Periodic (after major milestones or releases)
