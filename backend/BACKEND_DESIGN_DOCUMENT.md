# JobWise Backend - Comprehensive Design Document

**Project**: JobWise - AI-Powered Job Application Assistant
**Version**: 1.0
**Last Updated**: October 20, 2025
**Status**: Sprint 2 - Generation & Document Export APIs

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

### 1.2 Current Implementation Status

**Sprint 1 Complete** (Weeks 8-10):
- Authentication & Authorization (JWT)
- Profile Management API
- Job Description API
- 42 tests passing, 55% coverage

**Sprint 2 In Progress** (Week 11):
- Generation API (Mock AI Pipeline)
- Document Export API (PDF/Text)
- Target: 67 tests, 65%+ coverage

### 1.3 Key Metrics

- **API Endpoints**: 25+ implemented
- **Test Coverage**: 64%
- **Response Time**: <200ms (CRUD), <6s (generation)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Architecture**: Clean Architecture with Ports & Adapters

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Client Applications                    │
│              (Flutter Mobile, Web, CLI)                  │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS/JSON
                   ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Application (Port 8000)             │
│  ┌─────────────────────────────────────────────────┐   │
│  │          Presentation Layer (API)               │   │
│  │  - Authentication endpoints                     │   │
│  │  - Profile management                           │   │
│  │  - Job search & management                      │   │
│  │  - Generation & document APIs                   │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │        Application Layer (Services)             │   │
│  │  - Business logic orchestration                 │   │
│  │  - Transaction management                       │   │
│  │  - Validation & error handling                  │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │           Domain Layer (Entities)               │   │
│  │  - Core business entities                       │   │
│  │  - Value objects                                │   │
│  │  - Domain rules & ports                         │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                    │
│  ┌──────────────────▼──────────────────────────────┐   │
│  │      Infrastructure Layer (Adapters)            │   │
│  │  - Database repositories                        │   │
│  │  - External service adapters                    │   │
│  │  - File storage                                 │   │
│  └──────────────────┬──────────────────────────────┘   │
└────────────────────┬┼──────────────────────────────────┘
                     ││
        ┌────────────┘└────────────┐
        ▼                           ▼
┌───────────────┐          ┌────────────────┐
│   PostgreSQL  │          │  External APIs │
│   Database    │          │  - LLM (Mock)  │
│               │          │  - PDF Export  │
└───────────────┘          └────────────────┘
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

```
Presentation ──> Application ──> Domain <── Infrastructure
     │               │               │            │
  REST API      Services      Entities &    Adapters &
  Routers       & DTOs          Ports      Repositories
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
        # Mock implementation for Sprint 2
        await asyncio.sleep(2)
        return "Generated resume content..."

# Future Sprint 3:
# File: app/infrastructure/adapters/llm/openai.py
class OpenAIAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
        # Real OpenAI implementation
        return await openai.ChatCompletion.create(...)
```

**Active Adapters** (Sprint 2):
- `mock_llm.py` - Mock LLM for development
- `reportlab.py` - PDF generation
- `local_storage.py` - File storage

**Future Adapters** (Sprint 3+):
- `openai.py` - OpenAI GPT-4
- `claude.py` - Anthropic Claude
- `s3_storage.py` - AWS S3 (production)

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

**See**: `.context/diagrams/backend/database-schema-erd.puml` for complete ERD

#### Core Entities

**UserModel**
- Authentication and user management
- Subscription tracking
- Usage limits (generations per month)

**MasterProfileModel**
- Master resume data
- One-to-many: Experiences, Education, Skills, Projects
- Versioning support

**JobModel (Unified)**
- Single table for all job sources
- Fields:
  - `source`: enum(api, static, user_created, scraped, imported)
  - `user_id`: NULL for external jobs, set for user-created
  - `status`: enum(active, draft, archived, expired)
- Keyword extraction and analysis

**GenerationModel**
- AI generation tracking
- Pipeline progress monitoring
- Token usage and cost tracking
- Relationships: User, Profile, Job

**DocumentModel**
- Generated document storage
- Multiple content formats (text, HTML, markdown)
- PDF metadata (file path, size, page count)
- ATS scoring

#### Relationship Summary

```
User (1) ──< (N) Profile
User (1) ──< (N) Job (user_created only)
User (1) ──< (N) Generation
User (1) ──< (N) SavedJob

Profile (1) ──< (N) Experience
Profile (1) ──< (N) Education
Profile (1) ──< (N) Skill
Profile (1) ──< (N) Project
Profile (1) ──< (N) Generation

Job (1) ──< (N) Generation (all sources)
Job (1) ──< (N) SavedJob (all sources)

Generation (1) ──< (N) Document
```

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
-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);
CREATE INDEX idx_jobs_user_source ON jobs(user_id, source);
CREATE INDEX idx_generations_user_status ON generations(user_id, status);
CREATE INDEX idx_documents_generation ON documents(generation_id);

-- Composite indexes for common queries
CREATE INDEX idx_saved_jobs_user_status ON saved_jobs(user_id, status, created_at);
```

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

```
GET    /                   # Search all jobs (all sources)
GET    /{id}               # Get job details
POST   /                   # Create user custom job
PUT    /{id}               # Update user job
DELETE /{id}               # Delete user job

GET    /my-jobs             # List user's custom jobs
PUT    /{id}/status        # Update job status
POST   /{id}/analyze       # Extract keywords

GET    /template           # Get JSON template
POST   /convert-text       # Convert text to structured job
```

#### Generation API (`/api/v1/generations/`) - Sprint 2

```
POST   /resume             # Start resume generation
GET    /{id}               # Get generation status
GET    /{id}/result        # Get generated content
POST   /{id}/regenerate    # Regenerate with changes
DELETE /{id}               # Cancel/delete generation

GET    /                   # List user generations
POST   /{id}/feedback      # Provide feedback
GET    /templates          # List resume templates

GET    /{id}/analytics     # Quality metrics & ATS score
POST   /{id}/validate      # Re-run validation
```

#### Document API (`/api/v1/documents/`) - Sprint 2

```
GET    /                   # List user documents
GET    /{id}               # Get document details
DELETE /{id}               # Delete document
PUT    /{id}               # Update metadata

POST   /{id}/export        # Export to format (PDF/TXT)
GET    /{id}/download      # Download exported file
GET    /export-formats     # List available formats
POST   /preview            # Generate preview
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

```
┌──────┐       ┌──────────┐      ┌─────────┐      ┌──────────┐
│Client│       │Auth API  │      │Auth Svc │      │Database  │
└──┬───┘       └────┬─────┘      └────┬────┘      └────┬─────┘
   │                │                  │                │
   │ POST /register │                  │                │
   ├───────────────>│                  │                │
   │                │ validate_email() │                │
   │                ├─────────────────>│                │
   │                │                  │ hash_password()│
   │                │<─────────────────│                │
   │                │                  │ create_user()  │
   │                │                  ├───────────────>│
   │                │                  │<───────────────│
   │                │ create JWT       │                │
   │                ├────────┐         │                │
   │                │        │         │                │
   │                │<───────┘         │                │
   │<───────────────│                  │                │
   │ {user, token}  │                  │                │
```

### 6.2 Resume Generation Flow (Sprint 2)

```
┌──────┐    ┌─────────┐   ┌─────────┐   ┌──────┐   ┌─────┐   ┌────────┐
│Client│    │Gen API  │   │Gen Svc  │   │LLM   │   │DB   │   │Profile │
└──┬───┘    └────┬────┘   └────┬────┘   └──┬───┘   └──┬──┘   └───┬────┘
   │             │              │           │          │          │
   │ POST        │              │           │          │          │
   │ /generations│              │           │          │          │
   │ /resume     │              │           │          │          │
   ├────────────>│              │           │          │          │
   │             │ create_      │           │          │          │
   │             │ generation() │           │          │          │
   │             ├─────────────>│           │          │          │
   │             │              │ save (pending)       │          │
   │             │              ├──────────────────────>          │
   │             │              │           │          │          │
   │             │<─────────────┤           │          │          │
   │<────────────┤              │           │          │          │
   │ {id, status}│              │           │          │          │
   │             │              │           │          │          │
   │             │        [Async Pipeline Start]      │          │
   │             │              │           │          │          │
   │             │              │ 1. analyze_job()     │          │
   │             │              ├──────────────────────>          │
   │             │              │ 2. get_profile()               │
   │             │              ├────────────────────────────────>│
   │             │              │ 3. generate_content()           │
   │             │              ├──────────>│          │          │
   │             │              │ (mock 2s) │          │          │
   │             │              │<──────────┤          │          │
   │             │              │ 4. validate_quality()           │
   │             │              ├──────────┐│          │          │
   │             │              │<─────────┘│          │          │
   │             │              │ 5. prepare_export()             │
   │             │              ├──────────┐│          │          │
   │             │              │<─────────┘│          │          │
   │             │              │ save (completed)     │          │
   │             │              ├──────────────────────>          │
   │             │              │           │          │          │
   │ GET         │              │           │          │          │
   │ /generations│              │           │          │          │
   │ /{id}/result│              │           │          │          │
   ├────────────>│              │           │          │          │
   │             │ get_result() │           │          │          │
   │             ├─────────────>│           │          │          │
   │             │              │ fetch document       │          │
   │             │              ├──────────────────────>          │
   │             │              │<──────────────────────          │
   │<────────────┤<─────────────┤           │          │          │
   │ {content}   │              │           │          │          │
```

### 6.3 PDF Export Flow (Sprint 2)

```
┌──────┐    ┌────────┐   ┌────────┐   ┌──────────┐   ┌────────┐
│Client│    │Doc API │   │Doc Svc │   │PDF Gen   │   │Storage │
└──┬───┘    └───┬────┘   └───┬────┘   └────┬─────┘   └───┬────┘
   │            │            │             │             │
   │ POST       │            │             │             │
   │ /documents │            │             │             │
   │ /{id}/export           │             │             │
   ├───────────>│            │             │             │
   │            │ export()   │             │             │
   │            ├───────────>│             │             │
   │            │            │ generate_pdf()            │
   │            │            ├────────────>│             │
   │            │            │ (ReportLab) │             │
   │            │            │<────────────┤             │
   │            │            │ save_file() │             │
   │            │            ├─────────────────────────>│
   │            │            │             │             │
   │            │<───────────┤             │             │
   │<───────────┤            │             │             │
   │ {download  │            │             │             │
   │  _url}     │            │             │             │
   │            │            │             │             │
   │ GET        │            │             │             │
   │ /download  │            │             │             │
   ├───────────>│            │             │             │
   │            │ get_file() │             │             │
   │            ├───────────>│             │             │
   │            │            │ read_file() │             │
   │            │            ├─────────────────────────>│
   │            │            │<─────────────────────────┤
   │            │<───────────┤             │             │
   │<───────────┤            │             │             │
   │ PDF bytes  │            │             │             │
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
    # Sprint 2: Mock
    return MockLLMAdapter()
    # Sprint 3: Real
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

### 8.6 External Services (Sprint 2+)

**LLM Providers**:
- Sprint 2: Mock implementation
- Sprint 3: OpenAI GPT-4 (`openai 1.6.1`)
- Sprint 4: Anthropic Claude (`anthropic 0.7.7`)

**PDF Generation**:
- ReportLab 4.0.7 (Sprint 2)

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
**Review Frequency**: After each sprint
