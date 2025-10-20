# JobWise API Services Specification

## Overview

This document specifies the API-focused architecture for JobWise implementation, prioritizing core user-facing API services for resume generation workflow. The specification covers API contracts, service boundaries, and integration patterns with clear implementation priorities.

**Architecture Philosophy**: API-First Design with Service-Oriented Implementation
**Priority Focus**: Generation API, Profile API, Job Description API
**Implementation Approach**: Prototype-first with production upgrade paths

---

## Priority API Services Architecture

### 🎯 High Priority APIs (Current Implementation Focus)

#### API-1: Profile Management API
**Status**: ✅ **IMPLEMENTED** | **Priority**: HIGH | **Foundation Complete**
**Purpose**: Master resume profile lifecycle management with comprehensive CRUD operations
**Boundaries**: Profile data, experiences, education, projects, skills, analytics
**Dependencies**: Profile Repository, User Authentication, Validation Service

**REST API Contract** (`/api/v1/profiles`):
```yaml
# Core Profile Operations
POST   /api/v1/profiles                    # Create new master profile
GET    /api/v1/profiles/me                 # Get current user's profile 
GET    /api/v1/profiles/{id}               # Get profile by ID
PUT    /api/v1/profiles/{id}               # Update profile
DELETE /api/v1/profiles/{id}               # Delete profile

# Profile Components Management
POST   /api/v1/profiles/{id}/experiences   # Add work experience
PUT    /api/v1/profiles/{id}/experiences/{exp_id}  # Update experience
DELETE /api/v1/profiles/{id}/experiences/{exp_id}  # Remove experience
POST   /api/v1/profiles/{id}/education     # Add education entry
PUT    /api/v1/profiles/{id}/education/{edu_id}    # Update education
DELETE /api/v1/profiles/{id}/education/{edu_id}    # Remove education
POST   /api/v1/profiles/{id}/projects      # Add project
PUT    /api/v1/profiles/{id}/projects/{proj_id}    # Update project
DELETE /api/v1/profiles/{id}/projects/{proj_id}    # Remove project

# Profile Analytics & Insights
GET    /api/v1/profiles/{id}/analytics     # Profile completeness and analytics
GET    /api/v1/profiles/{id}/summary       # Profile summary for AI generation
```

**Service Interface:**
```typescript
interface IProfileService {
  // Core CRUD Operations
  create_profile(user_id: string, profile_data: ProfileCreateRequest): Promise<ProfileResult>
  get_profile(profile_id: string): Promise<ProfileResult>
  update_profile(profile_id: string, updates: ProfileUpdateRequest): Promise<ProfileResult>
  delete_profile(profile_id: string): Promise<void>
  
  // Profile Analytics
  get_profile_analytics(profile_id: string): Promise<ProfileAnalytics>
  get_profile_completeness(profile_id: string): Promise<CompletenessScore>
  validate_profile_for_generation(profile_id: string): Promise<ValidationResult>
}
```

**Implementation Status:**
- ✅ **Complete**: Full CRUD operations with comprehensive value objects
- ✅ **Complete**: Experience/Education/Project management with async repositories  
- ✅ **Complete**: Profile analytics endpoints providing completeness scores
- ✅ **Complete**: User ownership validation and JWT-based authentication
- ✅ **Ready**: Profile data structured for AI generation pipeline integration

#### API-2: Job Description API  
**Status**: 🚧 **HIGH PRIORITY** | **Implementation Target**: Next Sprint
**Purpose**: Unified job management supporting all input methods with user-owned custom jobs
**Boundaries**: Job CRUD, keyword extraction, status management, job templates
**Dependencies**: Unified Job Repository, User Authentication, Keyword Extraction Service

**REST API Contract** (`/api/v1/jobs`):
```yaml
# Unified Job Management (All Sources)
GET    /api/v1/jobs                        # Search all jobs (static + user-created + API)
GET    /api/v1/jobs/{id}                   # Get job details (any source)
POST   /api/v1/jobs                        # Create user custom job description
PUT    /api/v1/jobs/{id}                   # Update user job (ownership required)
DELETE /api/v1/jobs/{id}                   # Delete user job (ownership required)

# User Job Management
GET    /api/v1/jobs/my-jobs                # List user's custom job descriptions
PUT    /api/v1/jobs/{id}/status            # Change job status (draft/active/archived)
POST   /api/v1/jobs/{id}/analyze           # Extract keywords and analyze job requirements

# Job Templates & Conversion Tools
GET    /api/v1/jobs/template               # Get JSON template for copy-paste conversion
POST   /api/v1/jobs/convert-text           # Convert raw job text to structured JSON
POST   /api/v1/jobs/validate               # Validate job description format
```

**Service Interface:**
```typescript
interface IJobService {
  // Unified Job Operations (All Sources)
  search_jobs(query: JobSearchQuery, user_id?: string): Promise<JobSearchResult>
  get_job_details(job_id: string): Promise<JobResult>
  
  // User Job Management
  create_user_job(user_id: string, job_data: JobCreateRequest): Promise<JobResult>
  update_user_job(user_id: string, job_id: string, updates: JobUpdateRequest): Promise<JobResult>
  delete_user_job(user_id: string, job_id: string): Promise<void>
  get_user_jobs(user_id: string, filters: JobFilters): Promise<JobResult[]>
  
  // Job Analysis & Conversion
  extract_job_keywords(job_id: string): Promise<KeywordAnalysis>
  convert_text_to_job(raw_text: string): Promise<ConversionResult>
  get_job_template(): Promise<JobTemplate>
}
```

**Unified Job Model Architecture:**
```typescript
interface UnifiedJobModel {
  id: string                              // UUID for user jobs, external_id for API jobs
  user_id?: string                        // NULL for external jobs, set for user-created
  source: 'api' | 'static' | 'user_created' | 'scraped' | 'imported'
  external_job_id?: string               // For API-sourced jobs
  
  // Core Job Data (All Sources)
  title: string
  company: string
  location?: string
  description: string
  requirements: string[]
  responsibilities?: string[]
  benefits?: string[]
  
  // Job Metadata
  status: 'active' | 'draft' | 'archived' | 'expired'
  keywords_extracted?: string[]
  ats_keywords?: string[]
  priority_keywords?: string[]
  
  // Timestamps
  posted_date?: Date
  expires_date?: Date
  created_at: Date
  updated_at: Date
}
```

**Key Features:**
- **Single Entity**: Unified JobModel eliminates JobModel/JobDescriptionModel duplication
- **Multi-Source Support**: API jobs, static data, user-created, scraped, imported
- **User Ownership**: Optional user_id enables user-specific job management
- **Source Tracking**: Source field enables different processing logic per input method
- **Template System**: JSON templates for easy copy-paste job description conversion

#### API-3: Generation API
**Status**: 🚧 **HIGH PRIORITY** | **Implementation Target**: Next Sprint
**Purpose**: AI-powered resume generation with 5-stage mock pipeline and quality validation
**Boundaries**: Generation orchestration, progress tracking, template management, quality scoring
**Dependencies**: Profile API, Job Description API, Mock AI Service, Document Storage

**REST API Contract** (`/api/v1/generations`):
```yaml
# Generation Operations
POST   /api/v1/generations/resume          # Start resume generation
GET    /api/v1/generations/{id}            # Get generation status and progress
GET    /api/v1/generations/{id}/result     # Get generated resume content
POST   /api/v1/generations/{id}/regenerate # Regenerate with feedback/changes
DELETE /api/v1/generations/{id}            # Cancel/delete generation

# Generation Management
GET    /api/v1/generations                 # List user's generations with filters
POST   /api/v1/generations/{id}/feedback   # Provide feedback for improvement
GET    /api/v1/generations/templates       # Get available resume templates

# Generation Analytics
GET    /api/v1/generations/{id}/analytics  # Generation quality metrics and ATS score
POST   /api/v1/generations/{id}/validate   # Re-run quality validation
```

**Service Interface:**
```typescript
interface IGenerationService {
  // Core Generation Operations
  generate_resume(request: ResumeGenerationRequest): Promise<GenerationResult>
  get_generation_status(generation_id: string): Promise<GenerationStatus>
  get_generation_result(generation_id: string): Promise<GeneratedContent>
  cancel_generation(generation_id: string): Promise<void>
  
  // Generation Management
  list_user_generations(user_id: string, filters: GenerationFilters): Promise<GenerationSummary[]>
  regenerate_with_feedback(generation_id: string, feedback: string): Promise<GenerationResult>
  
  // Quality & Analytics
  validate_generation_quality(generation_id: string): Promise<QualityValidationResult>
  get_generation_analytics(generation_id: string): Promise<GenerationAnalytics>
}
```

**Mock AI Pipeline Architecture:**
```yaml
# 5-Stage Generation Pipeline (Total: ~5 seconds)
stage_1_job_analysis:
  duration: 1.0s
  purpose: Parse job requirements, extract key skills and keywords
  mock_processing: Keyword extraction, requirement prioritization
  output: JobAnalysisResult with keyword weights and skill priorities

stage_2_profile_compilation:  
  duration: 1.0s
  purpose: Score profile sections against job requirements
  mock_processing: Profile-job matching, skill gap analysis
  output: ProfileCompilationResult with match scores and recommendations

stage_3_content_generation:
  duration: 2.0s  
  purpose: Generate tailored resume using professional templates
  mock_processing: Template selection, content adaptation, formatting
  output: GeneratedContent with tailored resume text

stage_4_quality_validation:
  duration: 1.0s
  purpose: ATS compliance check, keyword density validation
  mock_processing: ATS scoring simulation, readability analysis
  output: QualityValidationResult with ATS score (0.7-0.95 range)

stage_5_export_preparation:
  duration: 0.5s
  purpose: Prepare content for document export and storage
  mock_processing: Final formatting, metadata preparation
  output: ExportReadyDocument with multiple format options
```

**Generation Request Contract:**
```typescript
interface ResumeGenerationRequest {
  profile_id: string                      // From Profile API
  job_id: string                         // From Job Description API  
  template_preference?: string           // professional, technical, creative
  generation_options?: {
    focus_areas?: string[]               // Areas to emphasize
    max_length?: number                  // Word count target
    include_cover_letter?: boolean       // Generate cover letter too
  }
}
```

**Quality Metrics:**
- **ATS Compatibility Score**: 0.7-0.95 (mock scoring based on keyword density)
- **Keyword Match Rate**: % of job keywords covered in generated resume
- **Section Completeness**: Professional summary, skills, experience coverage
- **Format Compliance**: Standard resume formatting and structure validation

### 📋 Lower Priority APIs (Future Implementation)

#### API-4: Document Management API
**Status**: 🚧 **STRUCTURE READY** | **Priority**: MEDIUM | **Implementation Target**: Phase 2
**Purpose**: Generated document storage, versioning, export, and sharing capabilities
**Boundaries**: Document lifecycle, export formats, file management, sharing
**Dependencies**: Generation API, Storage Service, Export Service

**REST API Contract** (`/api/v1/documents`):
```yaml
# Document Management
GET    /api/v1/documents                   # List user documents with filters
GET    /api/v1/documents/{id}              # Get document details and metadata
DELETE /api/v1/documents/{id}              # Delete document and associated files
PUT    /api/v1/documents/{id}              # Update document metadata

# Export Operations  
POST   /api/v1/documents/{id}/export       # Export document to specified format
GET    /api/v1/documents/{id}/download     # Download exported file
GET    /api/v1/documents/export-formats    # Get available export formats
POST   /api/v1/documents/{id}/share        # Create sharing link with permissions

# Document Analytics
GET    /api/v1/documents/{id}/analytics    # Document performance metrics
GET    /api/v1/documents/usage-stats       # User document usage statistics
```

**Service Interface:**
```typescript
interface IDocumentService {
  // Document Lifecycle Management
  create_document(generation_id: string, content: GeneratedContent): Promise<DocumentResult>
  get_document(document_id: string): Promise<DocumentResult>
  list_user_documents(user_id: string, filters: DocumentFilters): Promise<DocumentSummary[]>
  delete_document(document_id: string): Promise<void>
  
  // Export Operations
  export_document(document_id: string, format: ExportFormat): Promise<ExportResult>
  get_download_url(document_id: string, format: ExportFormat): Promise<string>
  
  // Sharing & Collaboration
  create_share_link(document_id: string, permissions: SharePermissions): Promise<ShareLink>
  revoke_share_link(share_id: string): Promise<void>
}
```

**Export Formats:**
- **Text (.txt)**: Clean, formatted plain text resume (Phase 1 implementation)
- **PDF (.pdf)**: Professional PDF with formatting (Phase 2 implementation)  
- **Word (.docx)**: Microsoft Word format (Future enhancement)
- **HTML**: Web-ready format with styling (Future enhancement)

#### API-5: Job Search API (Enhancement)
**Status**: ✅ **BASIC IMPLEMENTED** | **Priority**: LOW | **Implementation Target**: Phase 3
**Purpose**: Enhanced job discovery with external API integration and recommendations
**Boundaries**: Job search, external API integration, recommendations, job alerts
**Dependencies**: External Job APIs, Recommendation Engine, Notification Service

**Current Implementation**: Basic static job search (6/6 tests passing)
**Future Enhancements**: External API integration, ML recommendations, advanced filtering

**REST API Contract** (`/api/v1/job-search`):
```yaml
# Enhanced Job Search (Future)
GET    /api/v1/job-search                  # Advanced job search with ML recommendations
POST   /api/v1/job-search/save-criteria    # Save job search criteria for alerts
GET    /api/v1/job-search/recommendations  # Personalized job recommendations
POST   /api/v1/job-search/alerts           # Set up job alert notifications
GET    /api/v1/job-search/trending         # Trending jobs and skills

# Job Application Tracking (Future)
POST   /api/v1/job-search/applications     # Track job applications
GET    /api/v1/job-search/applications     # List applications with status
PUT    /api/v1/job-search/applications/{id} # Update application status
```

**Enhanced Service Interface:**
```
IDocumentService:
- save_document(document: GeneratedDocument) -> DocumentResult
- get_document(document_id: str) -> DocumentResult
- list_user_documents(filters: DocumentFilters) -> List[DocumentSummary]
- generate_pdf(document_id: str, template: PDFTemplate) -> PDFResult
- share_document(document_id: str, share_options: ShareOptions) -> ShareResult
- delete_document(document_id: str) -> void
- get_document_history(document_id: str) -> List[DocumentVersion]
```

**Storage Strategy:**
- **Prototype**: Local file system with SQLite metadata
- **Production**: S3/Cloud Storage with PostgreSQL metadata

#### 1.5 Authentication Service
**Purpose**: User authentication and authorization
**Boundaries**: User management, token handling, access control
**Dependencies**: User Repository, Token Service, External Auth Providers

**Interface Contract:**
```
IAuthService:
- authenticate_user(credentials: AuthCredentials) -> AuthResult
- refresh_token(refresh_token: str) -> TokenResult
- validate_token(token: str) -> ValidationResult
- revoke_token(token: str) -> void
- register_user(user_data: UserRegistration) -> UserResult
- get_user_permissions(user_id: str) -> List[Permission]
```

**Implementation Strategy:**
- **Prototype**: Simple API key validation, no user accounts
- **Production**: OAuth 2.0 + JWT tokens with user management

### 2. Domain Services

#### 2.1 AI Orchestrator Service
**Purpose**: Multi-stage AI processing pipeline for resume generation
**Boundaries**: LLM coordination, token management, error handling
**Dependencies**: LLM Service, Token Budget Manager, Quality Validator

**Interface Contract:**
```
IAIOrchestrator:
- execute_pipeline(profile: MasterProfile, job: Job, options: GenerationOptions) -> PipelineResult
- get_pipeline_status(execution_id: str) -> PipelineStatus
- estimate_token_usage(profile: MasterProfile, job: Job) -> TokenEstimate
- validate_pipeline_inputs(profile: MasterProfile, job: Job) -> ValidationResult
```

**Pipeline Configuration:**
- **Development**: GPT-3.5-turbo, 30s timeout, 2 retries
- **Production**: GPT-4 with GPT-3.5-turbo fallback, 60s timeout, 3 retries

#### 2.2 Cache Management Service
**Purpose**: Multi-level caching for performance optimization
**Boundaries**: Cache operations, TTL management, cache invalidation
**Dependencies**: Cache Providers (Redis, SQLite, In-memory)

**Interface Contract:**
```
ICacheService:
- get<T>(key: str, type: Type[T]) -> Optional[T]
- set<T>(key: str, value: T, ttl: int) -> void
- delete(key: str) -> void
- invalidate_pattern(pattern: str) -> void
- get_cache_stats() -> CacheStats
```

**Caching Strategy:**
- Profile data: 1 hour TTL
- Job analysis results: 24 hours TTL  
- Generated content: 1 hour TTL
- Static job data: 7 days TTL

#### 2.3 Notification Service
**Purpose**: User notifications for generation status and updates
**Boundaries**: Notification delivery, template management, user preferences
**Dependencies**: Notification Providers, Template Service

**Interface Contract:**
```
INotificationService:
- send_generation_complete(user_id: str, document_id: str) -> NotificationResult
- send_generation_failed(user_id: str, generation_id: str, error: str) -> NotificationResult
- send_bulk_notification(user_ids: List[str], message: NotificationMessage) -> BatchResult
- get_user_preferences(user_id: str) -> NotificationPreferences
- update_user_preferences(user_id: str, preferences: NotificationPreferences) -> void
```

**Delivery Channels:**
- **Prototype**: In-app notifications only
- **Production**: Push notifications, email, SMS (future)

---

## External APIs and Integrations

### 1. LLM Provider APIs

#### 1.1 OpenAI API Integration
**Purpose**: Primary LLM service for content generation
**Endpoint**: `https://api.openai.com/v1/chat/completions`
**Authentication**: API Key in Authorization header

**Configuration:**
```yaml
openai_config:
  prototype:
    model: "gpt-3.5-turbo"
    max_tokens: 4000
    temperature: 0.3
    timeout: 30s
    retry_attempts: 2
  production:
    model: "gpt-4"
    fallback_model: "gpt-3.5-turbo"
    max_tokens: 8000
    temperature: 0.3
    timeout: 60s
    retry_attempts: 3
```

**Rate Limiting:**
- **Development**: 3 requests/minute, 100 requests/day
- **Production**: 60 requests/minute, 10,000 requests/day

**Error Handling:**
- 429 (Rate Limited): Exponential backoff with jitter
- 503 (Unavailable): Fallback to alternative model
- 500 (Server Error): Retry with exponential backoff

#### 1.2 Claude API Integration (Future)
**Purpose**: Alternative LLM service for diversification
**Endpoint**: `https://api.anthropic.com/v1/messages`
**Authentication**: X-API-Key header

**Configuration:**
```yaml
claude_config:
  model: "claude-3-sonnet-20240229"
  max_tokens: 4000
  timeout: 60s
  retry_attempts: 2
```

### 2. Job Listing APIs

#### 2.1 Indeed API Integration (Production)
**Purpose**: Primary job listing source
**Endpoint**: `https://api.indeed.com/ads/apisearch`
**Authentication**: Publisher ID + API Key

**Configuration:**
```yaml
indeed_config:
  publisher_id: "${INDEED_PUBLISHER_ID}"
  api_key: "${INDEED_API_KEY}"
  rate_limit: 1000_requests_per_day
  cache_ttl: 6_hours
  timeout: 10s
```

**Request Parameters:**
- `q`: Job search query
- `l`: Location (city, state, or zip)
- `sort`: Relevance, date
- `radius`: Search radius in miles
- `limit`: Results per page (max 25)

#### 2.2 LinkedIn Jobs API Integration (Future)
**Purpose**: Secondary job listing source
**Endpoint**: `https://api.linkedin.com/rest/jobs`
**Authentication**: OAuth 2.0

**Configuration:**
```yaml
linkedin_config:
  client_id: "${LINKEDIN_CLIENT_ID}"
  client_secret: "${LINKEDIN_CLIENT_SECRET}"
  rate_limit: 500_requests_per_day
  cache_ttl: 6_hours
  timeout: 10s
```

#### 2.3 Static Job Data (Prototype & Fallback)
**Purpose**: Offline job data for development and fallback
**Format**: JSON files with structured job descriptions

**Data Structure:**
```json
{
  "jobs": [
    {
      "id": "job_001",
      "title": "Senior Software Engineer",
      "company": "TechCorp",
      "location": "Seattle, WA",
      "description": "Full job description...",
      "requirements": ["Python", "React", "5+ years"],
      "experience_level": "senior",
      "industry": "technology",
      "posted_date": "2024-01-15T00:00:00Z"
    }
  ]
}
```

### 3. PDF Generation APIs

#### 3.1 WeasyPrint Service (Prototype)
**Purpose**: HTML to PDF conversion
**Type**: Python library (local processing)
**Dependencies**: `weasyprint`, `cairo`, `pango`

**Configuration:**
```yaml
weasyprint_config:
  base_font_size: 12pt
  font_family: "Arial, sans-serif"
  page_size: "letter"
  margins: "0.75in"
  quality: "high"
```

#### 3.2 Puppeteer PDF Service (Production)
**Purpose**: High-quality PDF generation with Chrome engine
**Type**: Node.js service via REST API
**Endpoint**: `http://pdf-service:3000/generate`

**Configuration:**
```yaml
puppeteer_config:
  format: "A4"
  margin: "0.75in"
  print_background: true
  timeout: 30s
  quality: 100
```

### 4. File Storage APIs

#### 4.1 Local File Storage (Prototype)
**Purpose**: Development file storage
**Location**: `./storage/documents/`
**Structure**: `{user_id}/{document_type}/{document_id}.pdf`

#### 4.2 AWS S3 Integration (Production)
**Purpose**: Scalable file storage
**Endpoint**: `https://s3.amazonaws.com/{bucket}`
**Authentication**: IAM roles or access keys

**Configuration:**
```yaml
s3_config:
  bucket_name: "jobwise-documents-prod"
  region: "us-west-2"
  encryption: "AES256"
  lifecycle_rules:
    - expire_after: "90_days"
    - transition_to_ia: "30_days"
```

---

## Infrastructure Services

### 1. Database Services

#### 1.1 SQLite (Prototype)
**Purpose**: Development database
**Configuration:**
```yaml
sqlite_config:
  database_url: "sqlite:///./jobwise.db"
  pool_size: 1
  echo: true
  foreign_keys: true
```

**Schema Management:**
- Migration tool: Alembic
- Backup strategy: File-based daily backups
- Connection handling: SQLAlchemy ORM

#### 1.2 PostgreSQL (Production)
**Purpose**: Production database with high availability
**Configuration:**
```yaml
postgresql_config:
  host: "${DB_HOST}"
  port: 5432
  database: "jobwise_prod"
  username: "${DB_USER}"
  password: "${DB_PASSWORD}"
  pool_size: 20
  max_overflow: 0
  pool_timeout: 30
  ssl_mode: "require"
```

**High Availability:**
- Primary-replica setup
- Automated backups (daily + WAL)
- Connection pooling with PgBouncer
- Read replica for analytics queries

### 2. Caching Services

#### 2.1 In-Memory Cache (Prototype)
**Purpose**: Simple application-level caching
**Implementation**: Python dictionaries with TTL
**Limitations**: Single process, no persistence

#### 2.2 Redis (Production)
**Purpose**: Distributed caching and session storage
**Configuration:**
```yaml
redis_config:
  host: "${REDIS_HOST}"
  port: 6379
  password: "${REDIS_PASSWORD}"
  ssl: true
  max_connections: 50
  socket_keepalive: true
  health_check_interval: 30
```

**Usage Patterns:**
- Session storage: 1 hour TTL
- API response caching: Variable TTL
- Rate limiting counters: Sliding window
- Background job queue: Bull/RQ integration

### 3. Message Queue Services

#### 3.1 Celery (Production)
**Purpose**: Background task processing for AI generation
**Broker**: Redis
**Backend**: PostgreSQL

**Configuration:**
```yaml
celery_config:
  broker_url: "${REDIS_URL}"
  result_backend: "${DATABASE_URL}"
  task_serializer: "json"
  accept_content: ["json"]
  timezone: "UTC"
  worker_concurrency: 4
```

**Task Types:**
- Resume generation pipeline
- Cover letter generation
- PDF export processing
- Batch document processing

### 4. Monitoring and Observability

#### 4.1 Application Metrics
**Tool**: Prometheus + Grafana
**Metrics Collected:**
- API request rates and latencies
- Generation pipeline performance
- Token usage and costs
- Error rates by endpoint
- Cache hit/miss ratios

#### 4.2 Logging Service
**Tool**: Structured logging with JSON format
**Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
**Privacy**: PII anonymization for all logs

**Configuration:**
```yaml
logging_config:
  level: "INFO"
  format: "json"
  anonymize_pii: true
  retention_days: 30
  destinations:
    - console
    - file: "/var/log/jobwise/app.log"
    - elasticsearch: "${ES_URL}"  # Production only
```

#### 4.3 Health Check Service
**Endpoints:**
- `/health`: Basic application health
- `/health/detailed`: Component-specific health status
- `/metrics`: Prometheus metrics endpoint

**Health Checks:**
- Database connectivity
- External API availability
- Cache service status
- Disk space and memory usage

---

## Service Dependencies and Integration

### 1. Service Dependency Graph

```
┌─────────────────┐    ┌─────────────────┐
│  Profile Mgmt   │◄──►│   Job Discovery │
│    Service      │    │     Service     │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          ▼                      ▼
┌─────────────────────────────────────────┐
│          AI Generation Service          │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│        Document Management Service      │
└─────────────────────────────────────────┘
```

### 2. External Service Integration Patterns

#### 2.1 Circuit Breaker Pattern
**Implementation**: For all external API calls
**Configuration:**
- Failure threshold: 5 consecutive failures
- Recovery timeout: 60 seconds
- Half-open state: Allow 1 request to test recovery

#### 2.2 Retry Pattern
**Implementation**: Exponential backoff with jitter
**Configuration:**
- Initial delay: 1 second
- Max delay: 30 seconds
- Max attempts: 3
- Jitter: ±25% of calculated delay

#### 2.3 Bulkhead Pattern
**Implementation**: Resource isolation for critical services
**Configuration:**
- Separate connection pools for different services
- Dedicated thread pools for AI processing
- Rate limiting per service type

### 3. Configuration Management

#### 3.1 Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/jobwise
SQLITE_URL=sqlite:///./jobwise.db

# External API Keys
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
INDEED_PUBLISHER_ID=...

# Infrastructure
REDIS_URL=redis://localhost:6379
S3_BUCKET_NAME=jobwise-documents
AWS_REGION=us-west-2

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
```

#### 3.2 Service Discovery
**Prototype**: Hard-coded endpoints
**Production**: Service registry (Consul/etcd) or Kubernetes services

---

## API Rate Limits and Quotas

### 1. Internal API Rate Limits

```yaml
rate_limits:
  profiles:
    create: "5/minute"
    update: "10/minute"
    read: "100/minute"
  
  jobs:
    search: "30/minute"
    details: "100/minute"
  
  generation:
    resume: "5/hour"
    cover_letter: "10/hour"
    status_check: "60/minute"
  
  documents:
    download: "50/minute"
    list: "30/minute"
```

### 2. External API Quotas

#### OpenAI API Quotas:
- **Development**: $50/month token budget
- **Production**: $200/month token budget with alerts at 80%

#### Job API Quotas:
- **Indeed**: 1000 requests/day (free tier)
- **LinkedIn**: 500 requests/day (partner tier)

### 3. Cost Management

#### Token Budget Tracking:
```yaml
token_budgets:
  daily_limit: 50000
  per_user_daily: 5000
  per_generation_max: 8000
  alert_thresholds:
    - 70%: warning
    - 85%: throttle
    - 95%: suspend
```

---

## Security Configuration

### 1. API Security

#### Authentication Headers:
```yaml
prototype:
  api_key_header: "X-API-Key"
  validation: "simple_key_check"

production:
  authorization_header: "Authorization: Bearer {jwt_token}"
  token_validation: "jwt_decode_verify"
  refresh_mechanism: "refresh_token_rotation"
```

#### Input Validation:
- Request size limits: 10MB max
- Rate limiting per IP and user
- SQL injection prevention
- XSS protection for all inputs
- File upload validation

### 2. Data Security

#### Encryption:
- **At Rest**: Database encryption, file storage encryption
- **In Transit**: TLS 1.2+ for all communications
- **In Memory**: Sensitive data cleared after use

#### Privacy:
- PII anonymization in logs
- Data retention policies (90 days for documents)
- Right to deletion compliance
- Audit trail for data access

---

## Development and Testing Services

### 1. Mock Services

#### Mock LLM Service:
```python
class MockLLMService:
    """Deterministic responses for testing"""
    def analyze_job(description: str) -> JobAnalysisResult:
        return predefined_analysis_by_hash(hash(description))
```

#### Mock Job API Service:
```python
class MockJobService:
    """Static responses for development"""
    def search_jobs(query: str) -> List[Job]:
        return filter_static_jobs_by_query(query)
```

### 2. Test Data Services

#### Test Data Factory:
- Generate realistic master profiles
- Create diverse job descriptions
- Produce expected AI generation outputs
- Generate performance test scenarios

### 3. Integration Testing

#### Contract Testing:
- API contract validation
- External service mock validation  
- Database schema compatibility testing
- Message format validation

This comprehensive services specification provides the foundation for implementing JobWise with clear boundaries, dependencies, and upgrade paths from prototype to production configurations.