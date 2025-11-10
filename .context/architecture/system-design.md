# JobWise System Design - Clean Architecture

## Executive Summary

JobWise is designed using **Clean Architecture** principles with **Hexagonal Architecture** patterns to ensure clear separation of concerns, testability, and seamless switching between prototype and production configurations. The system prioritizes AI-powered resume and cover letter generation while maintaining simplicity and upgrade paths.

## Core Design Principles

### 1. Clean Architecture Layers
```
┌─────────────────────────────────────┐
│           Presentation Layer         │ ← Flutter UI, FastAPI Controllers
├─────────────────────────────────────┤
│           Application Layer          │ ← Use Cases, Services, DTOs
├─────────────────────────────────────┤
│              Domain Layer            │ ← Business Logic, Entities, Rules
├─────────────────────────────────────┤
│          Infrastructure Layer        │ ← Database, External APIs, Files
└─────────────────────────────────────┘
```

### 2. Dependency Direction
- **Inward Dependencies**: Each layer only depends on inner layers
- **Domain Independence**: Core business logic has no external dependencies
- **Interface Segregation**: Ports (interfaces) define contracts
- **Adapter Pattern**: Infrastructure implements interfaces

### 3. Configuration Strategy
- **Environment-Based**: Prototype vs Production configurations
- **Strategy Pattern**: Swappable implementations based on environment
- **Factory Pattern**: Create services based on configuration
- **Dependency Injection**: Runtime binding of implementations

## System Context (C4 Model Level 1)

```
                    ┌─────────────────┐
                    │   Job Seeker    │
                    │    (Person)     │
                    └────────┬────────┘
                            │
                    ┌───────▼────────┐
                    │    JobWise     │
                    │   AI Resume    │
                    │   Assistant    │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
│   OpenAI API   │ │   Job Listing   │ │  PDF Generation│
│   (External)   │ │     APIs        │ │   Libraries    │
│                │ │   (External)    │ │   (External)   │
└────────────────┘ └─────────────────┘ └────────────────┘
```

## Container Architecture (C4 Model Level 2)

```
┌─────────────────────────────────────────────────────────────────┐
│                        JobWise System                           │
│                                                                 │
│  ┌───────────────┐    ┌─────────────────┐    ┌──────────────┐  │
│  │ Flutter App   │◄──►│  FastAPI        │◄──►│      AI      │  │
│  │ (Mobile UI)   │    │   Backend       │    │ Orchestrator │  │
│  │               │    │                 │    │              │  │
│  └───────────────┘    └─────────────────┘    └──────────────┘  │
│                              │                                  │
│                       ┌──────▼──────┐                          │
│                       │ Data Layer  │                          │
│                       │ (SQLite/    │                          │
│                       │ PostgreSQL) │                          │
│                       └─────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture (C4 Model Level 3)

### Flutter Mobile App Components
```
┌─────────────────────────────────────────────────────┐
│                Flutter Application                  │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │   Profile   │ │    Jobs     │ │  Generate   │    │
│ │ Management  │ │ Discovery   │ │   Resume    │    │
│ │             │ │             │ │             │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │ Document    │ │  Offline    │ │    HTTP     │    │
│ │ Viewer      │ │   Cache     │ │   Client    │    │
│ │             │ │             │ │             │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
```

### FastAPI Backend Components
```
┌─────────────────────────────────────────────────────┐
│                FastAPI Backend                      │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │   Profile   │ │    Job      │ │ Generation  │    │
│ │ Controller  │ │ Controller  │ │ Controller  │    │
│ │             │ │             │ │             │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
│                                                     │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│ │ Document    │ │   Auth      │ │   Config    │    │
│ │ Controller  │ │ Middleware  │ │  Manager    │    │
│ │             │ │             │ │             │    │
│ └─────────────┘ └─────────────┘ └─────────────┘    │
└─────────────────────────────────────────────────────┘
```

## Domain Model

### Core Entities

#### 1. MasterProfile (Aggregate Root)
```
MasterProfile:
- id: ProfileId
- personal_info: PersonalInfo
- summary: Summary
- experiences: List<Experience>
- skills: List<Skill>
- education: List<Education>
- projects: List<Project>
- version: Version
- created_at: DateTime
- updated_at: DateTime

Domain Rules:
- Must have at least one experience OR education
- Skills must be categorized (technical, soft, language, certification)
- All dates must be valid and logical
- Contact information must be valid format
```

#### 2. Job (Entity)
```
Job:
- id: JobId
- title: JobTitle
- company: Company
- location: Location
- description: JobDescription
- requirements: JobRequirements
- analysis: JobAnalysis (value object)
- posted_date: DateTime
- source: JobSource

Domain Rules:
- Job description cannot be empty
- Analysis must be complete before resume generation
- Requirements must be structured format
```

#### 3. GeneratedDocument (Aggregate Root)
```
GeneratedDocument:
- id: DocumentId
- profile_id: ProfileId
- job_id: JobId
- type: DocumentType (resume, cover_letter)
- content: DocumentContent
- metadata: GenerationMetadata
- status: DocumentStatus
- created_at: DateTime

Domain Rules:
- Must be linked to valid profile and job
- Content must pass ATS validation
- Metadata must include generation metrics
```

### Value Objects

#### PersonalInfo
```
PersonalInfo:
- full_name: Name
- email: Email
- phone: PhoneNumber
- location: Location

Invariants:
- Email must be valid format
- Phone must be valid format
- Name cannot be empty
```

#### GenerationMetadata
```
GenerationMetadata:
- ats_score: ATSScore (0-100)
- generation_time_ms: Duration
- token_usage: TokenCount
- stage_timings: Map<Stage, Duration>
- quality_metrics: QualityMetrics

Invariants:
- ATS score must be 0-100
- Generation time must be positive
- Token usage must not exceed limits
```

## Application Layer Architecture

### Use Cases (Application Services)

#### 1. Profile Management Use Cases
```
CreateMasterProfileUseCase:
- Input: CreateMasterProfileCommand
- Output: MasterProfileResult
- Rules: Validate profile data, ensure uniqueness

UpdateMasterProfileUseCase:
- Input: UpdateMasterProfileCommand
- Output: MasterProfileResult
- Rules: Maintain version history, validate changes

GetMasterProfileUseCase:
- Input: GetMasterProfileQuery
- Output: MasterProfileResult
- Rules: Check access permissions
```

#### 2. Resume Generation Use Cases
```
GenerateResumeUseCase:
- Input: GenerateResumeCommand
- Output: GenerationResult
- Dependencies: AIOrchestrator, ProfileRepository, JobRepository
- Rules: Validate inputs, check token budget, ensure quality

GetGenerationStatusUseCase:
- Input: GetGenerationStatusQuery
- Output: GenerationStatusResult
- Rules: Return current pipeline stage and progress
```

#### 3. Job Management Use Cases
```
SearchJobsUseCase:
- Input: SearchJobsQuery
- Output: JobSearchResult
- Dependencies: JobRepository, JobSearchService
- Rules: Apply filters, sort by relevance

GetJobDetailsUseCase:
- Input: GetJobDetailsQuery  
- Output: JobDetailsResult
- Rules: Include analysis if available
```

### DTOs and Commands

#### Commands (Write Operations)
```
CreateMasterProfileCommand:
- personal_info: PersonalInfoDTO
- summary: string
- experiences: List<ExperienceDTO>
- skills: List<SkillDTO>
- education: List<EducationDTO>
- projects: List<ProjectDTO>

GenerateResumeCommand:
- profile_id: string
- job_id: string
- options: GenerationOptions
```

#### Queries (Read Operations)
```
GetMasterProfileQuery:
- profile_id: string

SearchJobsQuery:
- search_term: string
- location: string
- filters: SearchFilters
- pagination: PaginationOptions
```

## Infrastructure Layer Design

### Repository Pattern Implementation

#### 1. Profile Repository
```
Interface: IProfileRepository
Methods:
- create(profile: MasterProfile) -> ProfileId
- get_by_id(id: ProfileId) -> MasterProfile
- update(profile: MasterProfile) -> void
- delete(id: ProfileId) -> void

Implementations:
- SQLiteProfileRepository (prototype)
- PostgreSQLProfileRepository (production)
```

#### 2. Job Repository  
```
Interface: IJobRepository
Methods:
- search(query: JobSearchQuery) -> List<Job>
- get_by_id(id: JobId) -> Job
- save(job: Job) -> JobId

Implementations:
- StaticJobRepository (prototype)
- APIJobRepository (production)
```

#### 3. Document Repository
```
Interface: IDocumentRepository
Methods:
- save(document: GeneratedDocument) -> DocumentId
- get_by_id(id: DocumentId) -> GeneratedDocument
- get_by_profile(profile_id: ProfileId) -> List<GeneratedDocument>
- delete(id: DocumentId) -> void

Implementations:
- SQLiteDocumentRepository (prototype)
- PostgreSQLDocumentRepository (production)
```

### External Service Adapters

#### 1. LLM Service Adapter
```
Interface: ILLMService
Methods:
- analyze_job(description: string) -> JobAnalysisResult
- compile_profile(profile: MasterProfile, analysis: JobAnalysis) -> ProfileCompilerResult
- generate_content(compilation: ProfileCompilerResult, job: Job) -> DocumentContent
- validate_quality(content: DocumentContent) -> QualityValidationResult

Implementations:
- OpenAILLMService
- ClaudeLLMService (future)
- MockLLMService (testing)
```

#### 2. PDF Service Adapter
```
Interface: IPDFService  
Methods:
- generate_pdf(content: DocumentContent, template: Template) -> PDF
- get_templates() -> List<Template>

Implementations:
- WeasyPrintPDFService
- ReportLabPDFService
```

### Configuration Management

#### Environment-Based Configuration
```
Configuration Strategy:
- EnvironmentConfig (base class)
- PrototypeConfig (SQLite, static data, GPT-3.5)
- ProductionConfig (PostgreSQL, live APIs, GPT-4)

Factory Pattern:
- ServiceFactory creates implementations based on config
- Dependency injection binds interfaces to implementations
- Runtime switching possible through configuration
```

## AI Orchestrator Domain Service

### 2-Stage Pipeline Architecture
```
AIOrchestrator (Domain Service):
- Stage1: Analysis & Matching
- Stage2: Generation & Validation

Each Stage:
- Input/Output interfaces
- Error handling  
- Progress reporting
- Token budget tracking (2500 tokens per stage)
```

### Pipeline Execution Flow
```
1. Validate inputs (profile + job)
2. Check token budget availability (5000 total)
3. Execute 2 stages sequentially:
   - Stage 1 (40%): Analysis & Matching
   - Stage 2 (60%): Generation & Validation
4. Handle errors with retry logic
5. Update progress status
6. Return result or error
```

### Error Handling Strategy
```
Pipeline Error Types:
- ValidationError: Invalid input data
- TokenLimitError: Exceeded budget
- LLMTimeoutError: External service timeout
- QualityError: Generated content fails validation

Recovery Strategies:
- Retry with exponential backoff
- Fallback to simpler model
- Use cached results
- Return partial results with warnings
```

## Data Flow Architecture

### Generation Request Flow
```
1. Flutter App → FastAPI /generate endpoint
2. GenerateResumeUseCase validates command
3. AIOrchestrator executes 2-stage pipeline
4. Results persisted via DocumentRepository
5. Status updates sent to client
6. PDF generated and cached
7. Client notified of completion
```

### Offline Synchronization Flow
```
1. Flutter caches operations locally
2. Connection restored triggers sync queue
3. Backend processes queued operations
4. Conflicts resolved with last-write-wins
5. Client receives confirmation
6. Local cache updated
```

## Security Architecture

### Authentication Strategy
```
Prototype:
- Simple API key validation
- No user management
- Local data only

Production:
- OAuth 2.0 + JWT tokens
- User account management
- Role-based access control
- Refresh token rotation
```

### Data Protection
```
At Rest:
- Local: SQLite encryption
- Production: Database encryption + TLS

In Transit:
- HTTPS for all API calls
- TLS 1.2+ encryption
- Certificate pinning (mobile)

In Processing:
- Input sanitization
- Output validation
- PII anonymization in logs
```

## Performance Architecture

### Caching Strategy
```
Multi-Level Caching:
- L1: In-memory application cache
- L2: Local SQLite cache (mobile)
- L3: Redis distributed cache (production)
- L4: CDN for static content

Cache Keys:
- Profile: profile_id + version
- Job Analysis: sha256(job_description)
- Generated Content: profile_id + job_id + options_hash
```

### Scalability Design
```
Horizontal Scaling:
- Stateless API services
- Load balancer distribution
- Database read replicas
- Background job queues

Vertical Scaling:
- Connection pooling
- Async processing
- Memory optimization
- CPU-bound task scheduling
```

## Deployment Architecture

### Prototype Deployment
```
Single Machine:
- FastAPI application
- SQLite database
- Local file storage
- Direct LLM API calls
- Simple monitoring
```

### Production Deployment
```
Microservices:
- API Gateway (nginx/traefik)
- FastAPI services (containerized)
- PostgreSQL cluster
- Redis cluster
- Background workers
- Monitoring stack (Prometheus/Grafana)
- Log aggregation (ELK stack)
```

## Architecture Decision Records (ADRs)

### ADR-005: Clean Architecture Implementation
**Status**: Accepted

**Decision**: Implement Clean Architecture with Hexagonal patterns
**Rationale**: Provides clear separation of concerns, testability, and flexibility for prototype-to-production evolution

**Consequences**:
- **Positive**: Clear boundaries, testable code, flexible implementations
- **Negative**: Additional abstraction layers, learning curve
- **Implementation**: Use dependency injection, repository pattern, adapter pattern

### ADR-006: Configuration Strategy
**Status**: Accepted

**Decision**: Environment-based configuration with strategy pattern
**Rationale**: Enables seamless switching between prototype and production without code changes

**Consequences**:
- **Positive**: Single codebase, easy deployment, clear environments
- **Negative**: Configuration complexity, testing overhead
- **Implementation**: Factory pattern for service creation, environment variables for config

### ADR-007: Domain-Driven Design
**Status**: Accepted

**Decision**: Use DDD patterns for core business logic
**Rationale**: Resume generation has complex business rules that benefit from domain modeling

**Consequences**:
- **Positive**: Clear business logic, better communication, maintainable code
- **Negative**: Additional complexity for simple CRUD operations
- **Implementation**: Aggregate roots, value objects, domain services, repositories

## Quality Attributes

### Testability
```
Testing Strategy:
- Unit tests for domain logic (>90% coverage)
- Integration tests for repositories
- Contract tests for external APIs
- End-to-end tests for critical flows
- Performance tests for generation pipeline
```

### Maintainability
```
Code Quality:
- SOLID principles enforcement
- Clean code practices
- Comprehensive documentation
- Automated code quality checks
- Regular refactoring cycles
```

### Reliability
```
Error Handling:
- Graceful degradation
- Circuit breaker pattern
- Retry mechanisms
- Fallback strategies
- Monitoring and alerting
```

This clean architecture design ensures JobWise can start simple with a prototype configuration and evolve seamlessly into a production-ready system while maintaining code quality, testability, and clear separation of concerns.