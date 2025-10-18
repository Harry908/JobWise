# JobWise Services and APIs Specification

## Overview

This document specifies all internal services, external APIs, and infrastructure components required for JobWise implementation. The specification covers both prototype and production configurations with clear upgrade paths.

---

## Internal Services Architecture

### 1. Core Application Services

#### 1.1 Profile Management Service
**Purpose**: Master resume profile lifecycle management
**Boundaries**: CRUD operations, validation, version control
**Dependencies**: Profile Repository, Validation Service

**Interface Contract:**
```
IProfileService:
- create_profile(profile_data: ProfileCreateRequest) -> ProfileResult
- get_profile(profile_id: str) -> ProfileResult
- update_profile(profile_id: str, updates: ProfileUpdateRequest) -> ProfileResult
- delete_profile(profile_id: str) -> void
- validate_profile(profile_data: ProfileData) -> ValidationResult
- get_profile_history(profile_id: str) -> List[ProfileVersion]
```

**Implementation Strategy:**
- **Prototype**: Single-user local storage with SQLite
- **Production**: Multi-tenant with PostgreSQL and user isolation

#### 1.2 Job Discovery Service
**Purpose**: Job listing search, filtering, and management
**Boundaries**: Job search, caching, external API integration
**Dependencies**: Job Repository, External Job APIs, Cache Service

**Interface Contract:**
```
IJobService:
- search_jobs(query: JobSearchQuery) -> JobSearchResult
- get_job_details(job_id: str) -> JobResult
- save_job(job_id: str, user_notes: str) -> SavedJobResult
- get_saved_jobs(user_filters: JobFilters) -> List[SavedJob]
- update_job_status(job_id: str, status: JobStatus) -> void
- refresh_job_data() -> RefreshResult
```

**Data Sources:**
- **Prototype**: Static JSON file with 100+ curated jobs
- **Production**: Indeed API + LinkedIn API with fallback to static data

#### 1.3 AI Generation Service
**Purpose**: Core resume and cover letter generation orchestration
**Boundaries**: AI pipeline management, quality control, progress tracking
**Dependencies**: AI Orchestrator, Profile Service, Job Service, Document Service

**Interface Contract:**
```
IGenerationService:
- generate_resume(request: ResumeGenerationRequest) -> GenerationResult
- generate_cover_letter(request: CoverLetterGenerationRequest) -> GenerationResult
- get_generation_status(generation_id: str) -> GenerationStatusResult
- cancel_generation(generation_id: str) -> void
- retry_failed_generation(generation_id: str) -> GenerationResult
- validate_generation_quality(content: DocumentContent) -> QualityValidationResult
```

**AI Pipeline Stages:**
- Stage 1: Job Analysis (1500 tokens)
- Stage 2: Profile Compilation (2000 tokens)  
- Stage 3: Content Generation (3000 tokens)
- Stage 4: Quality Validation (1500 tokens)
- Stage 5: PDF Export (no tokens)

#### 1.4 Document Management Service
**Purpose**: Generated document storage, retrieval, and version control
**Boundaries**: Document lifecycle, PDF generation, sharing capabilities
**Dependencies**: Document Repository, PDF Service, Storage Service

**Interface Contract:**
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