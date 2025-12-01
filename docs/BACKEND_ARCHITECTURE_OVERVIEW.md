# JobWise Backend Architecture Overview

**Version**: 1.2  
**Scope**: API Specs 01-06 (Auth, Profile, Job, Sample Upload, Generation, Export/Schema)  
**Status**: Code cleanup complete; design kept authoritative for all APIs

---

## 1. Clean Architecture Layers

The backend follows **Clean Architecture** principles, separating concerns into concentric layers where dependencies point inward.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  FastAPI Routers: auth.py, profile.py, job.py                               │
│  HTTP request/response handling, DTOs, OpenAPI schemas                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                           APPLICATION LAYER                                 │
│  Services: auth_service.py, profile_service.py, job_service.py              │
│  Use cases, orchestration, business workflows, DTOs                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                             DOMAIN LAYER                                    │
│  Entities: user.py, profile.py, job.py                                      │
│  Core business objects, validation rules, domain logic                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                          INFRASTRUCTURE LAYER                               │
│  Repositories: user_repository.py, profile_repository.py, job_repository.py │
│  Database: models.py, connection.py (SQLAlchemy ORM)                        │
│  External adapters (LLM, S3) when enabled                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
   Presentation ─────► Application ─────► Domain
        │                   │                │
        │                   │                │
        ▼                   ▼                ▼
   Infrastructure ◄──── Interfaces ◄──── Contracts
```

- **Presentation** depends on Application services (never directly on Infrastructure).
- **Application** orchestrates Domain entities and calls repository interfaces.
- **Domain** contains pure business logic with no external dependencies.
- **Infrastructure** implements repository interfaces and handles I/O (database, APIs).

---

## 2. Backend Folder Structure (Target Design)

This folder structure is derived from `docs/api-services/01-06` and represents the complete architecture for all documented APIs.

```
backend/
├── app/
│   ├── main.py                        # FastAPI application entry, lifespan, router registration
│   ├── __init__.py
│   │
│   ├── core/                          # Cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── config.py                  # Pydantic settings (.env: DB, JWT, S3, LLM keys, feature flags)
│   │   ├── dependencies.py            # FastAPI Depends() factories (get_db, get_current_user, get_*_service)
│   │   ├── exceptions.py              # Domain exceptions (NotFound, Unauthorized, Conflict, RateLimitExceeded)
│   │   ├── security.py                # Bcrypt hashing, JWT encode/decode, token validation
│   │   └── rate_limiter.py            # Per-IP and per-user rate limiting middleware
│   │
│   ├── presentation/                  # PRESENTATION LAYER - FastAPI Routers
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   │   # API 01 - Authentication (01-authentication-api.md)
│   │   │   ├── auth.py                # /api/v1/auth/* (register, login, refresh, logout, password reset)
│   │   │   │
│   │   │   │   # API 02 - Profile Management (02-profile-api.md)
│   │   │   ├── profile.py             # /api/v1/profiles/* (CRUD, analytics, 24 endpoints)
│   │   │   ├── experience.py          # /api/v1/profiles/{id}/experiences/* (bulk CRUD)
│   │   │   ├── education.py           # /api/v1/profiles/{id}/education/* (bulk CRUD)
│   │   │   ├── project.py             # /api/v1/profiles/{id}/projects/* (bulk CRUD)
│   │   │   ├── skill.py               # /api/v1/profiles/{id}/skills/* (technical, soft, languages, certs)
│   │   │   │
│   │   │   │   # API 03 - Job Management (03-job-api.md)
│   │   │   ├── job.py                 # /api/v1/jobs/* (CRUD, browse, text parsing, 5 endpoints)
│   │   │   │
│   │   │   │   # API 04a - Sample Upload (04a-sample-upload-api.md)
│   │   │   ├── sample.py              # /api/v1/samples/* (upload, list, get, delete, 4 endpoints)
│   │   │   │
│   │   │   │   # API 04b - AI Generation (04b-ai-generation-api.md)
│   │   │   ├── generation.py          # /api/v1/generations/* (resume, cover-letter, history)
│   │   │   ├── ranking.py             # /api/v1/rankings/* (create, get by job)
│   │   │   ├── enhancement.py         # /api/v1/profile/enhance (profile enhancement)
│   │   │   │
│   │   │   │   # API 05 - Document Export (05-document-export-api.md)
│   │   │   ├── export.py              # /api/v1/exports/* (pdf, docx, batch, templates, files, 9 endpoints)
│   │   │   │
│   │   │   └── health.py              # /health, /ready (liveness, readiness probes)
│   │   │
│   │   └── schemas/                   # Pydantic request/response models per API
│   │       ├── __init__.py
│   │       ├── auth.py                # RegisterRequest, LoginRequest, TokenResponse, UserResponse
│   │       ├── profile.py             # ProfileCreate, ProfileUpdate, ProfileResponse, AnalyticsResponse
│   │       ├── experience.py          # ExperienceCreate, ExperienceBulkCreate, ExperienceResponse
│   │       ├── education.py           # EducationCreate, EducationBulkCreate, EducationResponse
│   │       ├── project.py             # ProjectCreate, ProjectBulkCreate, ProjectResponse
│   │       ├── skill.py               # SkillsUpdate, TechnicalSkillsAdd, SkillsResponse
│   │       ├── job.py                 # JobCreate, JobUpdate, JobResponse, JobListResponse
│   │       ├── sample.py              # SampleUploadResponse, SampleDetailResponse, SampleListResponse
│   │       ├── generation.py          # ResumeRequest, CoverLetterRequest, GenerationResponse
│   │       ├── ranking.py             # RankingCreate, RankingResponse
│   │       ├── enhancement.py         # EnhanceRequest, EnhanceResponse
│   │       └── export.py              # PdfExportRequest, DocxExportRequest, ExportResponse, TemplateResponse
│   │
│   ├── application/                   # APPLICATION LAYER - Use Cases & Services
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   │   # API 01 - Authentication
│   │   │   ├── auth_service.py        # register_user, login_user, refresh_token, change_password
│   │   │   │
│   │   │   │   # API 02 - Profile Management
│   │   │   ├── profile_service.py     # create_profile, update_profile, get_analytics, bulk operations
│   │   │   │
│   │   │   │   # API 03 - Job Management
│   │   │   ├── job_service.py         # create_job, parse_job_text, update_status, browse_jobs
│   │   │   │
│   │   │   │   # API 04a - Sample Upload
│   │   │   ├── sample_service.py      # upload_sample, list_samples, get_sample, delete_sample
│   │   │   │
│   │   │   │   # API 04b - AI Generation
│   │   │   ├── generation_service.py  # generate_resume, generate_cover_letter, get_history
│   │   │   ├── ranking_service.py     # create_ranking, get_ranking_for_job
│   │   │   ├── enhancement_service.py # enhance_profile (LLM orchestration)
│   │   │   ├── style_extraction_service.py  # extract_writing_style from samples
│   │   │   │
│   │   │   │   # API 05 - Document Export
│   │   │   └── export_service.py      # export_pdf, export_docx, batch_export, manage_files
│   │   │
│   │   └── dtos/                      # Data Transfer Objects for inter-layer communication
│   │       ├── __init__.py
│   │       ├── auth_dto.py
│   │       ├── profile_dto.py
│   │       ├── job_dto.py
│   │       ├── sample_dto.py
│   │       ├── generation_dto.py
│   │       └── export_dto.py
│   │
│   ├── domain/                        # DOMAIN LAYER - Entities & Business Logic
│   │   ├── __init__.py
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   │   # Core entities (APIs 01-03)
│   │   │   ├── user.py                # User entity, email validation, role definitions
│   │   │   ├── profile.py             # MasterProfile entity, personal_info, skills JSON
│   │   │   ├── experience.py          # Experience entity, date validation, is_current logic
│   │   │   ├── education.py           # Education entity, degree/GPA validation
│   │   │   ├── project.py             # Project entity, technologies list
│   │   │   ├── job.py                 # Job entity, source enum, application_status state machine
│   │   │   │
│   │   │   │   # Pipeline entities (APIs 04-05)
│   │   │   ├── sample_document.py     # SampleDocument entity, document_type, is_active
│   │   │   ├── writing_style.py       # WritingStyle entity, extracted_style JSON
│   │   │   ├── job_content_ranking.py # JobContentRanking entity, ranked IDs, relevance scores
│   │   │   ├── generation.py          # Generation entity, document_type, status, ats_score
│   │   │   └── export.py              # Export entity, format, template, S3 file_path
│   │   │
│   │   ├── enums/
│   │   │   ├── __init__.py
│   │   │   ├── job_source.py          # JobSource: user_created, text_parsed, url_scraped, api, mock (mock only for job browse)
│   │   │   ├── job_status.py          # JobStatus: active, archived, draft
│   │   │   ├── application_status.py  # ApplicationStatus: not_applied, preparing, applied, interviewing, etc.
│   │   │   ├── employment_type.py     # EmploymentType: full_time, part_time, contract, internship, temporary
│   │   │   ├── document_type.py       # DocumentType: resume, cover_letter
│   │   │   ├── generation_status.py   # GenerationStatus: pending, generating, completed, failed
│   │   │   └── export_format.py       # ExportFormat: pdf, docx, zip
│   │   │
│   │   └── interfaces/                # Repository interfaces (ports)
│   │       ├── __init__.py
│   │       ├── user_repository_interface.py
│   │       ├── profile_repository_interface.py
│   │       ├── job_repository_interface.py
│   │       ├── sample_repository_interface.py
│   │       ├── generation_repository_interface.py
│   │       ├── ranking_repository_interface.py
│   │       └── export_repository_interface.py
│   │
│   └── infrastructure/                # INFRASTRUCTURE LAYER - Adapters & I/O
│       ├── __init__.py
│       │
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py          # Async SQLAlchemy engine, session factory, lifespan
│       │   ├── models/                # ORM models matching 06-database-schema.md
│       │   │   ├── __init__.py
│       │   │   ├── user_model.py      # users table
│       │   │   ├── profile_model.py   # master_profiles table
│       │   │   ├── experience_model.py # experiences table
│       │   │   ├── education_model.py # education table
│       │   │   ├── project_model.py   # projects table
│       │   │   ├── job_model.py       # jobs table
│       │   │   ├── sample_model.py    # sample_documents table
│       │   │   ├── writing_style_model.py  # writing_styles table
│       │   │   ├── ranking_model.py   # job_content_rankings table
│       │   │   ├── generation_model.py # generations table
│       │   │   └── export_model.py    # exports table
│       │   └── migrations/            # Alembic migration scripts
│       │       ├── env.py
│       │       ├── script.py.mako
│       │       └── versions/
│       │
│       ├── repositories/              # Repository implementations (adapters)
│       │   ├── __init__.py
│       │   ├── user_repository.py     # UserRepository (users CRUD)
│       │   ├── profile_repository.py  # ProfileRepository (profiles + nested entities)
│       │   ├── job_repository.py      # JobRepository (jobs CRUD, filtering, pagination)
│       │   ├── sample_repository.py   # SampleRepository (sample_documents CRUD)
│       │   ├── writing_style_repository.py  # WritingStyleRepository (1:1 with user)
│       │   ├── ranking_repository.py  # RankingRepository (job_content_rankings CRUD)
│       │   ├── generation_repository.py # GenerationRepository (generations CRUD, history)
│       │   └── export_repository.py   # ExportRepository (exports CRUD)
│       │
│       ├── adapters/                  # External service adapters
│       │   ├── __init__.py
│       │   │
│       │   │   # LLM Adapters (API 04b)
│       │   ├── llm/
│       │   │   ├── __init__.py
│       │   │   ├── llm_interface.py   # Abstract LLM adapter interface
│       │   │   └── groq_adapter.py    # Groq API: llama-3.3-70b, llama-3.1-8b
│       │   │
│       │   │   # Storage Adapters (API 05)
│       │   └── storage/
│       │       ├── __init__.py
│       │       ├── storage_interface.py # Abstract storage interface
│       │       └── s3_adapter.py      # S3: upload, download, delete, presigned URLs
│       │
│       └── renderers/                 # Document rendering (API 05)
│           ├── __init__.py
│           ├── pdf_renderer.py        # WeasyPrint HTML->PDF rendering
│           ├── docx_renderer.py       # python-docx DOCX rendering
│           └── templates/             # Export templates
│               ├── modern/
│               │   ├── resume.html
│               │   ├── cover_letter.html
│               │   └── styles.css
│               ├── classic/
│               ├── creative/
│               └── ats_optimized/
│
├── alembic/                           # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── data/                              # Static data files
│   ├── mock_jobs.json                 # Mock job feed for browse endpoint (ONLY mock data in system)
│   └── templates/                     # Template metadata
│       └── template_registry.json     # Template definitions for export API
│
├── tests/                             # Test suites
│   ├── __init__.py
│   ├── conftest.py                    # Shared fixtures, test client, DB setup
│   │
│   ├── unit/                          # Unit tests (no I/O)
│   │   ├── domain/
│   │   │   ├── test_user_entity.py
│   │   │   ├── test_profile_entity.py
│   │   │   ├── test_job_entity.py
│   │   │   └── test_enums.py
│   │   └── application/
│   │       ├── test_auth_service.py
│   │       ├── test_profile_service.py
│   │       └── test_job_service.py
│   │
│   ├── integration/                   # Integration tests (with DB)
│   │   ├── api/
│   │   │   ├── test_auth_api.py
│   │   │   ├── test_profile_api.py
│   │   │   ├── test_job_api.py
│   │   │   ├── test_sample_api.py
│   │   │   ├── test_generation_api.py
│   │   │   └── test_export_api.py
│   │   └── repositories/
│   │       ├── test_user_repository.py
│   │       ├── test_profile_repository.py
│   │       └── test_job_repository.py
│   │
│   └── e2e/                           # End-to-end tests
│       ├── test_auth_flow.py
│       ├── test_profile_flow.py
│       └── test_generation_flow.py
│
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Dev dependencies (pytest, coverage, etc.)
├── .env.example                       # Environment variable template
├── init_database.py                   # DB initialization script
├── start-server.bat                   # Windows launch helper
└── start-server.sh                    # Linux/Mac launch helper
```

---

## 3. Layer Responsibilities

### 3.1 Core (`app/core/`)

| File | Purpose |
|------|---------|
| `config.py` | Pydantic settings loaded from `.env` (DB URL, JWT secrets, feature flags) |
| `dependencies.py` | FastAPI `Depends()` factories for sessions, current user, services |
| `exceptions.py` | Domain-specific exceptions (NotFound, Unauthorized, Conflict) |
| `security.py` | Password hashing (Bcrypt), JWT encode/decode, token validation |

### 3.2 Presentation (`app/presentation/api/`)

| Router | Base Path | Responsibilities |
|--------|-----------|------------------|
| `auth.py` | `/api/v1/auth` | Register, login, refresh, logout, password reset |
| `profile.py` | `/api/v1/profiles` | Profile CRUD, bulk ops, analytics |
| `job.py` | `/api/v1/jobs` | Job CRUD, browse, status transitions |

### 3.3 Application (`app/application/services/`)

| Service | Orchestrates |
|---------|--------------|
| `auth_service.py` | User creation, credential validation, token issuance |
| `profile_service.py` | Profile + nested entity management, analytics computation |
| `job_service.py` | Job persistence, mock feed loading, status workflows |

### 3.4 Domain (`app/domain/entities/`)

| Entity | Core Logic |
|--------|------------|
| `user.py` | Email/password validation, role definitions |
| `profile.py` | Personal info, experiences, education, projects, skills |
| `job.py` | Title/company rules, status enums, application state machine |

### 3.5 Infrastructure (`app/infrastructure/`)

| Component | Responsibility |
|-----------|----------------|
| `database/connection.py` | Async SQLAlchemy engine, session factory, lifespan management |
| `database/models.py` | ORM table classes mirroring `06-database-schema.md` |
| `repositories/*` | CRUD operations, query builders, transaction handling |

---

## 4. Backend Responsibilities

The design intentionally tracks every API specification (`docs/api-services/01-06`) even though some services are paused in code. The responsibilities are split into:

- **01 - Authentication**: Secure signup/login, password resets, refresh rotation, and session validation.
- **02 - Profiles**: Master profile CRUD, nested experiences/education/projects, analytics, and bulk mutations.
- **03 - Jobs**: Saved job intake, mock browsing, application status lifecycle, and analytics hooks.
- **04a - Sample Upload**: Text-only resume/cover-letter ingestion, stats collection, and active-sample management.
- **04b - AI Generation**: Profile enhancement, ranking, resume compilation, cover-letter LLM orchestration, and history retrieval.
- **05 - Document Export**: PDF/DOCX/ZIP export, S3 metadata management, download/cleanup flows.
- **06 - Database Schema**: Canonical mapping of tables/entities that back every API.

While the active deployment currently exposes only APIs 01-03, this overview preserves the end-to-end architecture so future re-enablement of 04-05 requires minimal rediscovery.

---

## 5. Core Entities and Tables

`docs/api-services/06-database-schema.md` remains the single source of truth for entities. The schema spans two bands:

1. **Core Tables (Active Runtime)**
   - `users`, `master_profiles`, `experiences`, `education`, `projects`, `jobs`, plus helper enums and audit tables. These power APIs 01-03 today.

2. **Pipeline Tables (Design-Ready)**
   - `sample_documents`, `writing_styles`, `job_content_rankings`, `generations`, `exports`, and related status/history tables. These exist in the canonical schema to service APIs 04-05 when re-enabled. Even if the live ORM omits them temporarily, migrations keep their definitions so data can be rehydrated later.

All tables include `user_id` or explicit ownership columns to enforce row-level security. Soft deletes and archival flags are documented per table for auditability.

---

## 6. Authentication and Authorization

- The **Auth API** (`docs/api-services/01-authentication-api.md`) exposes register, login, refresh, logout, and password reset flows using JWT access tokens.
- Each downstream API (`profiles`, `jobs`) requires the `Authorization: Bearer <token>` header. The current user context is resolved via FastAPI dependencies so repository queries always include a `user_id` filter.
- Authorization decisions are binary (resource owner vs. non-owner). Attempts to access another user's resource return `404` to avoid resource enumeration.
- Live test suites now default to in-process FastAPI clients; integration tests that previously targeted a remote server are being refactored to avoid unnecessary `httpx` network calls.

---

## 7. High-Level Data Flows

### 7.1 User Onboarding - Secure Session (API 01)

1. Mobile or CLI client calls `POST /api/v1/auth/register`.
2. On success, the client authenticates with `POST /api/v1/auth/login` and stores the JWT.
3. Health checks (`/health`) and configuration endpoints confirm environment readiness before further actions.

### 7.2 Profile Authoring and Analytics (API 02)

1. Authenticated users create or update a master profile plus nested experiences/education/projects via `PUT /api/v1/profiles/{profile_id}` and the bulk mutation helpers described in `02-profile-api.md`.
2. Profile analytics endpoints read only from the persisted profile tables to compute completion scores, section coverage, and warning flags (missing dates, conflicting statuses, etc.).
3. Any optional `enhanced_*` field writes are treated as user-provided improvements; no background jobs or AI pipelines are triggered.

### 7.3 Job Intake and Tracking (API 03)

1. Users capture job postings through manual entry or the mock browse feed (`03-job-api.md`).
2. Saved jobs maintain `status` (`active`, `archived`, `draft`) and `application_status` (`not_applied`, `applied`, `interview`, etc.).
3. Filtering, pagination, and aggregation logic lives inside repository queries so both the API and tests rely on the same semantics.
4. Jobs are loosely linked to profiles only at the client level today; no generation/export step follows.

### 7.4 Sample Upload - Writing Style Extraction (API 04a)

1. Users upload `.txt` resume or cover-letter samples via `/api/v1/samples/upload`.
2. The system stores raw text, word/character counts, and toggles `is_active` flags per document type.
3. Style extraction services (LLM-backed) compute tone/voice fingerprints persisted in `writing_styles` for reuse.

### 7.5 Ranking and Generation Pipeline (API 04b)

1. **Profile Enhancement**: `/profile/enhance` leverages stored samples and profiles to create `enhanced_*` fields.
2. **Job Content Ranking**: `/rankings/create` processes a job posting, producing ordered lists of experience/project IDs stored in `job_content_rankings`.
3. **Resume Generation**: `/generations/resume` deterministically assembles content based on rankings—no LLM call required.
4. **Cover Letter Generation**: `/generations/cover-letter` calls Groq LLM models, incorporating writing style metadata, and records responses in `generations` with ATS scores.
5. **History & Retrieval**: `/generations/history` and `/rankings/job/{job_id}` surface cached artifacts to avoid redundant computation.

### 7.6 Export Lifecycle (API 05)

1. Users request exports (`/exports/pdf|/docx|/batch`) referencing completed generations.
2. The service renders content via templating engines (WeasyPrint/python-docx) and streams directly to S3 buckets defined per environment.
3. Metadata lands in `exports` with retention and download counters. `/exports/files` and `/exports/files/{id}/download` provide listing/download endpoints.
4. Scheduled cleanup removes expired exports and deletes associated S3 objects, keeping storage costs bounded.

---

## 8. Technical Architecture Snapshot

- **Framework**: FastAPI + Pydantic for all routers 01-05; background tasks orchestrate ranking/generation/export steps when those routes are enabled.
- **Persistence**: SQLite (dev) and PostgreSQL (prod) schemas contain both core and pipeline tables. Alembic tracks migrations even while certain tables are dormant in code.
- **Async stack**: `httpx`/`httpcore` handle outbound Groq calls and S3 operations. When APIs 04-05 are disabled, these adapters become no-ops but remain documented.
- **Deployment**: Single container with optional worker queue (e.g., Celery/RQ) to offload long-running generation/export tasks. Health/readiness probes report dependency status.
- **Configuration**: `.env` includes DB/JWT plus feature flags for enabling LLM provider keys, S3 buckets, and rate-limit quotas so environments can toggle APIs 04-05 safely.

---

## 9. Cross-Cutting Concerns

- **Validation & Errors**: Consistent 422 responses for schema issues, 400 for semantic conflicts (duplicate emails, invalid job status transitions), and 404 for missing resources.
- **Rate Limiting**: Per-IP throttles guard auth and job endpoints; sample upload, generation, and export APIs add per-user quotas (e.g., 10 uploads/day, 25 cover letters/day, 50 exports/hour) to control LLM/S3 spend.
- **Security & Privacy**: Password hashes use Bcrypt, tokens are short-lived, and PII never leaves the database. Export files live in private S3 buckets accessed only through pre-signed URLs.
- **Observability**: Structured logs capture `request_id`, `user_id`, and latency. Coverage reports (`htmlcov/`) help ensure regression safety as we retire legacy code.

---

## 10. Implementation Notes and Order

The recommended order for maintaining and extending the current system is:

1. **Authentication foundation** - keep JWT config, password reset, and email uniqueness tests green.
2. **Profiles domain** - ensure profile CRUD, analytics, and bulk operations stay consistent with `docs/api-services/02-profile-api.md`.
3. **Jobs domain** - maintain repository integrity, mock browse feed, and application status workflows per `03-job-api.md`.
4. **Sample + Generation domain** - keep schema, prompts, and adapters healthy even if routes are feature-flagged off; required for future release trains.
5. **Export services** - validate S3 credentials, retention jobs, and batching flows when re-enabled.
6. **Operational polish** - migrations, test refactors (in-memory clients), and observability improvements spanning all APIs.

Documenting the full API surface ensures architecture/design artifacts stay in sync with the official specifications regardless of which subsets are deployed at any given time.
