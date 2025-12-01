# JobWise System Design - Clean Architecture

## Executive Summary

JobWise remains aligned with **Clean Architecture** and **Hexagonal** patterns while tracking the complete API surface defined in `docs/api-services/01-06`. Although only subsets may be feature-flagged on in a given environment, the system design documents how authentication, profiles, jobs, sample upload, AI generation, document export, and database schema interact end-to-end so teams can toggle capabilities without architectural drift.

### API Coverage Snapshot
| Spec | Domain | Runtime Status |
|------|--------|----------------|
| 01 | Authentication | Active across all environments |
| 02 | Profile Management | Active |
| 03 | Job Management | Active |
| 04a | Sample Upload & Writing Style | Design-complete, enabled per env via feature flag |
| 04b | AI Generation & Ranking | Design-complete, requires LLM credentials to enable |
| 05 | Document Export | Design-complete, requires S3 credentials to enable |
| 06 | Database Schema | Canonical for every deployment |

## Core Design Principles

### 1. Clean Architecture Layers
```
┌─────────────────────────────────────┐
│         Presentation Layer          │ ← Flutter UI, FastAPI routers
├─────────────────────────────────────┤
│         Application Layer           │ ← Use cases, services, DTOs
├─────────────────────────────────────┤
│            Domain Layer             │ ← Entities, aggregates, rules
├─────────────────────────────────────┤
│        Infrastructure Layer         │ ← SQLAlchemy, adapters
└─────────────────────────────────────┘
```

### 2. Dependency Direction
- Controllers depend on application services, which in turn depend on domain interfaces.
- Domain entities have no knowledge of FastAPI, SQLAlchemy, or external APIs.
- Repositories and gateways implement interfaces defined in the domain/application layers (Ports & Adapters).
- Dependency injection (FastAPI + custom factories) binds concrete implementations at runtime.

### 3. Configuration Strategy
- Environment-driven settings distinguish local (SQLite) vs. deployed (PostgreSQL) stacks.
- JWT, database URL, and observability toggles live in `.env` and are surfaced through Pydantic settings objects.
- No model-provider or object-storage secrets remain, simplifying deployment.

## System Context (C4 Model Level 1)

```
                ┌─────────────────┐
                │   Job Seeker    │
                │ (Mobile Client) │
                └────────┬────────┘
                         │ HTTPS/JSON
                ┌────────▼────────┐
                │   JobWise API   │
                │ (FastAPI App)   │
                └────────┬────────┘
                         │ SQL/HTTP
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐               ┌────────▼────────┐
│  SQL Database  │               │ Optional Job    │
│ (SQLite/PG)    │               │ Feed Adapters   │
└────────────────┘               └─────────────────┘
```

## Container Architecture (C4 Model Level 2)

```
┌───────────────────────────────────────────────────────────┐
│                     JobWise Platform                      │
│                                                           │
│  ┌───────────────┐    HTTPS    ┌──────────────────────┐   │
│  │ Flutter App   │◄───────────►│  FastAPI Backend     │   │
│  │ (Android/iOS) │             │  (Uvicorn workers)   │   │
│  └───────────────┘             └────────┬─────────────┘   │
│                                         │                 │
│                                 ┌───────▼─────────┐       │
│                                 │ Relational DB   │       │
│                                 │ (SQLAlchemy ORM)│       │
│                                 └─────────────────┘       │
└───────────────────────────────────────────────────────────┘
```

## Component Architecture (C4 Model Level 3)

### Flutter Client
- **Auth Module** - login, register, token refresh flows.
- **Profile Module** - CRUD forms, analytics visualization, bulk edit workflows.
- **Jobs Module** - saved jobs list, mock browse feed, application status controls.
- **Shared Services** - HTTP client, secure storage, offline cache for pending mutations.

### FastAPI Backend
```
┌────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ Auth Router  │ │ ProfileRouter│ │ Job Router   │          │
│ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘          │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ AuthSvc   │    │ ProfileSvc│    │ JobSvc    │            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │UserRepo   │    │ProfileRepo│    │ JobRepo   │            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ TokenSvc  │    │ SampleSvc │    │ RankingSvc│            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ LLMAdapter│    │ ExportSvc │◄───┤ Generation │            │
│  └───────────┘    └─────┬─────┘    └─────┬─────┘            │
│                          │                │                  │
│                     ┌────▼────┐      ┌────▼────┐             │
│                     │ S3Adapter│      │ History │            │
│                     └─────────┘      └─────────┘            │
└────────────────────────────────────────────────────────────┘
```
Routers for Sample Upload, Generation, and Export remain available behind feature flags; their services plug into shared repositories and adapters.

## Domain Model

### MasterProfile (Aggregate Root)
```
Attributes: id, user_id, personal_info, professional_summary,
skills, custom_fields, created_at, updated_at
Child Collections: experiences, education, projects

Rules:
- personal_info must contain contact methods.
- at least one of experiences or education is required for a publishable profile.
- timestamps are managed centrally to avoid client drift.
```

### Job (Entity)
```
Attributes: id, user_id, source, title, company, location,
description, parsed_keywords, requirements, benefits,
salary_range, employment_type, status, application_status,
created_at, updated_at

Rules:
- title/company are mandatory.
- application_status transitions must follow the allowed state machine defined in services.
- mock jobs have `user_id` null and are read-only.
```

### ProfileAnalytics (Value Object)

### SampleDocument (Entity)
```
Attributes: id, user_id, document_type, original_filename,
word_count, character_count, line_count, is_active,
text_blob, created_at, updated_at

Rules:
- only `.txt` samples accepted in prototype.
- uploading a new active sample of the same type deactivates the previous one.
```

### WritingStyle (Value Object)
```
Attributes: user_id, tone, structure, vocabulary, cadence,
model_metadata, source_sample_id, extracted_at

Rules:
- computed from the latest active cover-letter sample.
- cached for reuse across multiple generations.
```

### JobContentRanking (Entity)
```
Attributes: id, user_id, job_id, ranked_experience_ids,
ranked_project_ids, ranked_skill_clusters, model_name,
confidence_scores, created_at

Rules:
- generated per job/context pair.
- reused until job description changes or user invalidates it.
```

### Generation (Aggregate Root)
```
Attributes: id, user_id, job_id, profile_id, ranking_id,
document_type, status, ats_score, ats_feedback,
content_text, options, llm_metadata, created_at

Rules:
- resume generation is deterministic; cover letter generation leverages LLM adapter and writing style.
- history must remain immutable; retries create new records.
```

### Export (Entity)
```
Attributes: id, user_id, generation_id, document_type,
format, template, filename, file_path, file_size_bytes,
page_count, options, metadata, expires_at, download_count

Rules:
- exports require completed generations.
- `expires_at` enforced by scheduled cleanup jobs.
```
```
Attributes: completeness_score, missing_sections, warning_flags,
last_evaluated_at

Rules:
- Derived entirely from persisted profile data.
- Contains no external-model metadata.
```

## Application Layer Architecture

### Auth Use Cases
- **RegisterUserCommand** → creates user, hashes password, returns auth tokens.
- **LoginCommand** → validates credentials, issues JWT + refresh pair.
- **ResetPasswordCommand** → validates token, replaces password hash.

### Profile Use Cases
- **CreateOrUpdateProfileCommand** → upserts master profile and nested records within a transaction.
- **BulkExperienceCommand / BulkEducationCommand** → batch operations that enforce ownership and ordering.
- **GetProfileAnalyticsQuery** → materializes `ProfileAnalytics` for UI consumption.

### Job Use Cases
- **CreateJobCommand** → saves user-created or parsed jobs.
- **BrowseJobsQuery** → returns mock feed with pagination and total counts.
- **UpdateJobStatusCommand** → sets `status` or `application_status` with validation.

### Sample Upload & Style Use Cases (04a)
- **UploadSampleCommand** → validates `.txt` payloads, calculates stats, stores text, toggles `is_active`.
- **ListSamplesQuery** / **DeleteSampleCommand** → manage stored samples per user.
- **ExtractWritingStyleJob** → asynchronous process that updates `writing_styles` from the latest cover-letter sample.

### Ranking & Generation Use Cases (04b)
- **EnhanceProfileCommand** → applies LLM prompts to enrich summaries/descriptions, writes to `enhanced_*` columns.
- **CreateRankingCommand** → runs LLM analysis on job postings and persists `job_content_rankings`.
- **GenerateResumeCommand** → compiles ranked content without LLM usage, stores `generations` row.
- **GenerateCoverLetterCommand** → calls Groq LLM, injects writing style, and records metadata plus ATS feedback.
- **ListGenerationHistoryQuery** → filters generations for dashboards and export hand-offs.

### Export Use Cases (05)
- **CreateExportCommand** → renders PDF/DOCX/ZIP files, streams to S3/local storage, and logs metadata.
- **ListExportsQuery** → surfaces stored files with pagination and storage usage metrics.
- **DownloadExportCommand** → validates ownership/expiry and either streams bytes or returns pre-signed URLs.
- **DeleteExportCommand** → removes files and metadata, freeing quota.
- **CreateJobCommand** → saves user-created or parsed jobs.
- **BrowseJobsQuery** → returns mock feed with pagination and total counts.
- **UpdateJobStatusCommand** → sets `status` or `application_status` with validation.

DTOs mirror the payloads documented in `docs/api-services/01-03`. No DTO references generation options anymore.

## Infrastructure Layer Design

### Repositories
- **UserRepository** - CRUD for `users`, unique email enforcement.
- **ProfileRepository** - manages `master_profiles` plus child tables using SQLAlchemy relationships.
- **JobRepository** - user job CRUD, mock feed querying, aggregation helpers.
- **SampleRepository** - stores `sample_documents`, enforces active-sample toggles, streams text blobs.
- **WritingStyleRepository** - persists extracted style metadata per user.
- **RankingRepository** - manages `job_content_rankings` with invalidation helpers.
- **GenerationRepository** - handles `generations` lifecycle and history filters.
- **ExportRepository** - stores export metadata, retention states, and download counters.

### Gateways / Adapters
- **PasswordHasher** - wraps Bcrypt and centralizes cost factors.
- **TokenService** - encapsulates JWT signing, verification, and rotation policies.
- **MockJobSourceAdapter** - optional adapter that reads from `data/mock_jobs.json` to seed demo data.
- **LLMAdapter** - handles Groq/OpenAI calls with retry/backoff and telemetry hooks.
- **StyleExtractionWorker** - background worker bridging samples to writing styles.
- **ExportRenderer** - orchestrates WeasyPrint/python-docx templating and packaging.
- **ObjectStorageAdapter** - encapsulates S3 (or local filesystem) interactions, including pre-signed URLs and lifecycle policies.

### Configuration Management
- `Settings` class (Pydantic) loads from environment with sensible defaults and exposes feature flags (`ENABLE_SAMPLES`, `ENABLE_GENERATION`, `ENABLE_EXPORTS`).
- Factory helpers select SQLite vs. PostgreSQL engines based on `APP_ENV` while ensuring optional tables remain migrated.
- Observability toggles enable structured logging levels and request timing metrics, plus opt-in tracing for LLM calls and S3 uploads.

## Data Flow Architecture

### Authentication Flow
```
Client → /auth/register → UserService (validates + hashes password) → UserRepo
Client → /auth/login → TokenService issues JWT/refresh → response headers/body
Client refreshes token before expiry via /auth/refresh
```

### Profile Lifecycle Flow
```
Client → /profiles (POST/PUT) with profile DTO
ProfileService validates ownership + schema
ProfileRepository persists master profile + nested tables in one transaction
ProfileAnalyticsService recomputes summary used by /profiles/{id}/analytics
```

### Job Lifecycle Flow
### Sample → Style Flow
```
Client → /samples/upload with `.txt` payload
SampleService validates + stores text
StyleExtractionWorker triggers (async) and updates writing_styles
Analytics endpoints reuse cached style metadata
```

### Generation Flow
```
Client → /rankings/create (job_id)
RankingService calls LLM, stores job_content_rankings
Client → /generations/resume or /generations/cover-letter
GenerationService composes resume (logic) or invokes LLM for cover letter
Results persisted in generations; history endpoints surface them
```

### Export Flow
```
Client → /exports/{format}
ExportService fetches generation, renders via ExportRenderer
ObjectStorageAdapter uploads file, repository stores metadata
Client retrieves list/download using exports API; cleanup jobs enforce expires_at
```
```
Client → /jobs (POST) to save a job or /jobs/browse to view mock feed
JobService normalizes payload (keywords, requirements lists)
JobRepository writes/reads with pagination + filtering
Application status updates reuse JobService validation to guard transitions
```

## Security Architecture

- **Authentication**: Short-lived JWT access tokens, refresh tokens stored securely on client. Tokens embed `user_id`, `email`, and roles (currently `user` only).
- **Authorization**: Route-level dependencies ensure resources are filtered by `user_id`. Mock browse endpoints remain public but capped via throttling; generation/export APIs require ownership of upstream artifacts.
- **Data Protection**: Passwords hashed with Bcrypt, TLS enforced by the hosting layer, and logs scrub sensitive fields before emission. Export binaries live in private buckets with per-user keys and presigned URL expirations.
- **LLM Governance**: Prompt/response payloads are filtered for PII, and telemetry captures token usage for audit and billing.

## Performance & Scalability

- SQL indexes on `users.email`, `jobs.user_id`, `jobs.status`, `jobs.application_status`, `sample_documents.user_id`, `generations.job_id`, and `exports.user_id` keep lookups bounded.
- Repository queries cap page size (default 20, max 100) to thwart accidental full-table scans.
- Mock job data can be cached in memory for read-heavy demos without affecting user-owned rows; ranking/generation/export queues scale horizontally if high throughput is needed.
- Async FastAPI stack plus background workers keep the service responsive even while LLM or rendering tasks run.
- Feature flags allow horizontal scaling of costly APIs independently from core CRUD traffic.

## Deployment Architecture

- **Prototype / Dev**: Single FastAPI process, SQLite DB, local storage for exports, mocked LLM adapter. Feature flags for APIs 04-05 default to off.
- **Staging**: FastAPI + worker queue + PostgreSQL + MinIO/S3. Sample/generation/export routes toggled on for verification.
- **Production-ready**: Containerized FastAPI app behind an API gateway, PostgreSQL managed service, Redis/Queue for async work, and S3 for exports. Observability includes tracing for LLM and storage calls.
- **CI/CD hooks**: Pytest, coverage, static checks, schema diffing, and contract tests per API spec; feature-flag matrix ensures dormant routes continue to compile.

## Architecture Decision Records (ADRs)

- **ADR-005 - Clean Architecture**: Still in effect; retiring generation features reduced complexity but boundaries remain for future expansion.
- **ADR-006 - Configuration Strategy**: Simplified inputs (JWT + DB) but still uses environment-based instantiation.
- **ADR-007 - Domain-Driven Design**: DDD continues to drive profile/job models so reintroducing AI or exports later will only require new adapters, not rewrites.

## Quality Attributes

- **Testability**: Unit tests cover services/repositories; integration tests spin up in-memory FastAPI clients instead of remote HTTP calls; LLM and S3 adapters are mocked behind interfaces; coverage tracked in `htmlcov/`.
- **Maintainability**: Modules map 1:1 to APIs (auth, profiles, jobs, samples, generation, exports) with shared utilities kept in `app/core`; feature flags prevent dead code while retaining design artifacts.
- **Reliability**: Validation + transactional writes guarantee data integrity; health/readiness endpoints monitor DB, LLM, and S3 dependencies; logging includes correlation IDs and request metadata.
- **Security**: JWT best practices, dependency overrides for tests, strict ownership checks, encrypted storage of sample text, and limited lifetimes for export downloads keep data safe even when advanced APIs are enabled.

This streamlined system design documents the post-cleanup baseline so future contributors understand the active architecture and the deliberate omission of AI generation components.