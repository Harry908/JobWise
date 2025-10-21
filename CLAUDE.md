# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**JobWise** is an AI-powered job application assistant built with Flutter (mobile) and FastAPI (backend). The app helps users generate tailored resumes and cover letters for specific job postings by combining their master profile with AI-driven document generation.

**Current Status**: Sprint 1 completed (backend foundation + Profile/Job APIs). Sprint 2 ready to start (Generation API + Document Export).

## Common Development Commands

### Backend (FastAPI)

**Location**: `backend/` directory

**Environment Setup**:
```powershell
# Windows PowerShell
cd backend
.\venv\Scripts\Activate.ps1

# Windows CMD
cd backend
call venv\Scripts\activate.bat
```

**Start Server**:
```powershell
cd backend
.\start-server.bat
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

Or manually:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Testing**:
```powershell
cd backend

# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing -v

# Run specific test file
pytest tests/test_profile_api.py -v

# Run with fail-fast (stop on first failure)
pytest --maxfail=1 -q

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto
```

**Database**:
```powershell
cd backend

# Initialize/upgrade database
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Downgrade migration
alembic downgrade -1
```

**Code Quality**:
```powershell
cd backend

# Format code with black
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/
```

**Windows-Specific Notes**:
```powershell
# If you get execution policy errors with .bat files
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative activation methods if script fails
python -m venv venv  # Create venv
venv\Scripts\python.exe -m pip install --upgrade pip  # Direct Python invocation
```

### Mobile App (Flutter)

**Location**: `mobile_app/` directory

**Setup**:
```powershell
cd mobile_app
flutter pub get
```

**Run**:
```powershell
cd mobile_app

# Run on default device
flutter run

# Run on specific platform
flutter run -d chrome       # Web
flutter run -d android      # Android
flutter run -d ios          # iOS (macOS only)
```

**Testing**:
```powershell
cd mobile_app

# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Generate coverage report
genhtml coverage/lcov.info -o coverage/html
```

## Architecture Overview

### Backend Clean Architecture with Adapter Pattern

The backend follows **Clean Architecture** with **Ports & Adapters** for external services:

```
backend/app/
├── presentation/api/    # API layer (FastAPI routers)
│   ├── auth.py
│   ├── profiles.py
│   ├── jobs.py
│   ├── job_descriptions.py
│   ├── generation.py
│   └── documents.py
│
├── application/         # Business logic and orchestration
│   ├── services/        # Application services
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── job_service.py
│   │   ├── generation_service.py  # Uses domain ports
│   │   ├── document_service.py
│   │   └── pipeline/               # Generation pipeline stages
│   │       ├── job_analyzer.py
│   │       ├── profile_compiler.py
│   │       ├── content_generator.py
│   │       └── quality_validator.py
│   └── dtos/            # Request/Response DTOs
│
├── domain/              # Core business logic (no external dependencies)
│   ├── entities/        # Business entities (User, Profile, Job, Generation)
│   ├── value_objects/   # Complex types (Experience, Education, Skills)
│   ├── services/        # Domain services (business logic)
│   │   └── stages/      # Generation pipeline stages
│   └── ports/           # Interfaces for external services (adapter pattern)
│       ├── llm_service_port.py     # LLM provider interface
│       ├── pdf_generator_port.py   # PDF export interface
│       └── repository_ports.py     # Repository interfaces
│
├── infrastructure/      # Adapter implementations
│   ├── adapters/        # Concrete adapter implementations
│   │   ├── llm/
│   │   │   └── openai_adapter.py   # Sprint 2 (stub classes only)
│   │   │   # Implementation pending Sprint 2
│   │   ├── pdf/
│   │   │   └── reportlab_adapter.py # Sprint 2 PDF generation
│   │   └── storage/
│   │       └── local_file_adapter.py # Sprint 2 file storage
│   ├── repositories/    # Repository implementations
│   │   ├── profile_repository.py
│   │   ├── job_repository.py
│   │   ├── generation_repository.py
│   │   └── document_repository.py
│   └── database/        # Database layer
│       ├── models.py               # SQLAlchemy models
│       └── connection.py
│
└── core/                # Shared utilities
    ├── config.py
    ├── security.py
    ├── exceptions.py
    └── dependencies.py  # Dependency injection
```

**Key Principles**:
- **Ports & Adapters**: External services (LLM, PDF) use interface-based adapters
- **Dependency Inversion**: Services depend on ports (interfaces), not concrete implementations
- **Single Responsibility**: Each layer has one clear purpose
- **YAGNI**: Only create adapters when you have or will soon have 2+ implementations
- **Dependencies flow**: presentation -> application -> domain <- infrastructure

### Database Architecture

**ORM**: SQLAlchemy 2.0 with async support (`asyncpg` for PostgreSQL, `aiosqlite` for SQLite)

**Key Models**:
- **User**: Authentication and user management
- **Profile**: Master resume with experiences, education, skills, projects
- **JobModel**: Unified job model supporting multiple sources (API, static, user-created, scraped)
- **Generation**: AI resume generation tracking and results
- **Document**: Generated document storage and export metadata

**Important**: Uses **Unified Job Model** - single `JobModel` entity with `source` field distinguishing between:
- `api`: External API jobs
- `static`: Mock/seeded jobs
- `user_created`: User custom job descriptions
- `scraped`: Web-scraped jobs
- `imported`: Imported from JSON/text

### API Service Boundaries

```
Profile API (API-1) ──> Job Description API (API-2) ──> Generation API (API-3) ──> Document API (API-4)
     ✅ Complete              ✅ Complete                   🚧 Sprint 2              🚧 Sprint 2
```

**Data Flow**:
1. User creates/updates master **Profile** (experiences, education, skills)
2. User saves/creates **Job Descriptions** (custom or from external sources)
3. **Generation API** combines Profile + Job to create tailored resume
4. **Document API** exports generated content as PDF/DOCX/TXT

### AI Generation Pipeline (5 Stages)

**Current Implementation**: Mock pipeline with realistic timing (Sprint 2)

**Stages** (total ~5.5 seconds):
1. **Job Analyzer** (1s): Extract requirements, keywords, key skills from job description
2. **Profile Compiler** (1s): Score and match profile sections against job requirements
3. **Content Generator** (2s): Generate tailored resume using selected template
4. **Quality Validator** (1s): ATS compliance check, keyword density validation
5. **Export Preparation** (0.5s): Format content for document export

**Future**: Will integrate real LLM providers (OpenAI GPT-4, Anthropic Claude) with proper prompt engineering.

## Key Technical Decisions

### Authentication
- **JWT tokens** with bcrypt password hashing
- Token stored in Authorization header: `Bearer <token>`
- All `/api/v1/*` endpoints require authentication (except `/auth/register`, `/auth/login`)
- Middleware validates JWT and injects user context into requests

### Database Patterns
- **Repository Pattern**: All database access goes through repositories
- **Async/Await**: All database operations use SQLAlchemy async sessions
- **Value Objects**: Complex types (Email, PhoneNumber, DateRange) use Pydantic models
- **No Raw SQL**: Use SQLAlchemy ORM queries exclusively

### API Design
- **RESTful** conventions with proper HTTP methods and status codes
- **Pydantic v2** for request/response validation
- **OpenAPI 3.0** spec auto-generated at `/docs` (Swagger UI)
- **Consistent Error Format**:
  ```json
  {
    "error": {
      "code": "error_code_snake_case",
      "message": "Human-readable message",
      "details": {} // optional additional context
    }
  }
  ```

### Testing Strategy
- **pytest** with async support (`pytest-asyncio`)
- **Test Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.ai`
- **Coverage Target**: 80%+ (currently 45.78%, 133 tests passing)
- **Test Database**: Separate SQLite database (`test_jobwise.db`) with fixtures in `tests/conftest.py`
- **Factory Pattern**: Use `factory-boy` for test data generation

### Code Style
- **Black** formatter (line length: 88)
- **isort** for import sorting (black-compatible profile)
- **Type hints** required for all functions (enforced by mypy)
- **Async-first**: All I/O operations must be async

## Common Patterns and Conventions

### Adding a New API Endpoint

1. **Define DTOs** in `app/application/dtos/`:
   ```python
   # Request DTO
   class CreateResourceRequest(BaseModel):
       field: str
       model_config = ConfigDict(from_attributes=True)

   # Response DTO
   class ResourceResponse(BaseModel):
       id: str
       field: str
       created_at: datetime
       model_config = ConfigDict(from_attributes=True)
   ```

2. **Create/Update Domain Entity** in `app/domain/entities/`:
   ```python
   from dataclasses import dataclass
   from datetime import datetime

   @dataclass
   class Resource:
       id: str
       user_id: str
       field: str
       created_at: datetime
   ```

3. **Define Repository Interface** in `app/domain/repositories/`:
   ```python
   from abc import ABC, abstractmethod
   from typing import Optional, List

   class ResourceRepository(ABC):
       @abstractmethod
       async def create(self, resource: Resource) -> Resource:
           pass

       @abstractmethod
       async def get_by_id(self, id: str) -> Optional[Resource]:
           pass
   ```

4. **Implement Repository** in `app/infrastructure/repositories/`:
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.domain.repositories.resource_repository import ResourceRepository

   class SQLAlchemyResourceRepository(ResourceRepository):
       def __init__(self, session: AsyncSession):
           self.session = session

       async def create(self, resource: Resource) -> Resource:
           # Implementation using SQLAlchemy
           pass
   ```

5. **Create Application Service** (if needed) in `app/application/services/`:
   ```python
   class ResourceService:
       def __init__(self, repository: ResourceRepository):
           self.repository = repository

       async def create_resource(self, user_id: str, data: CreateResourceRequest) -> Resource:
           # Business logic
           pass
   ```

6. **Add API Router** in `app/presentation/api/v1/`:
   ```python
   from fastapi import APIRouter, Depends, status
   from app.core.security import get_current_user

   router = APIRouter(prefix="/resources", tags=["Resources"])

   @router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
   async def create_resource(
       request: CreateResourceRequest,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       # Implementation
       pass
   ```

7. **Register Router** in `app/presentation/api/__init__.py`:
   ```python
   from app.presentation.api.v1 import resources

   api_router.include_router(resources.router)
   ```

8. **Write Tests** in `tests/`:
   - Unit tests for domain logic
   - Integration tests for repository
   - API tests for endpoints

### Async Database Sessions

Always use dependency injection for database sessions:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_db

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    # Use db session
    async with db.begin():
        # Transaction automatically committed or rolled back
        pass
```

### Error Handling

Use custom exceptions from `app/core/exceptions.py`:

```python
from app.core.exceptions import JobWiseException, NotFoundException, UnauthorizedException

# Raise custom exception
if not resource:
    raise NotFoundException(
        error_code="resource_not_found",
        message="Resource not found",
        details={"resource_id": id}
    )
```

## Important Files and Locations

### Configuration
- `backend/.env` - Environment variables (DATABASE_URL, JWT_SECRET, etc.)
- `backend/.env.example` - Template for environment variables
- `backend/app/core/config.py` - Settings class using pydantic-settings

### Documentation
- `README.md` - Project overview, sprint progress, getting started
- `docs/sprint2/sprint2-plan.md` - Detailed Sprint 2 implementation plan
- `backend/FEATURE_IMPLEMENTATION_PLAN_CLEAN.md` - API implementation roadmap
- `.context/api/openapi-spec.yaml` - OpenAPI specification (if exists)

### Database
- `backend/alembic/` - Database migrations
- `backend/alembic.ini` - Alembic configuration
- `backend/jobwise.db` - Development SQLite database
- `backend/test_jobwise.db` - Test SQLite database

### Testing
- `backend/tests/conftest.py` - Pytest fixtures and test configuration
- `backend/pyproject.toml` - Test configuration (pytest, coverage, markers)

### Current Codebase Stats (October 2025)
- **Total Tests**: 133 tests across 12 test files
- **Test Coverage**: 45.78% (target: 80%)
- **API Endpoints**: Profile API (12 endpoints), Job API (5 endpoints), Auth API (8 endpoints)
- **Backend LOC**: ~3,500 lines (app/ directory)
- **Sprint Progress**: Sprint 1 complete (Auth + Profile + Job APIs), Sprint 2 pending

## Sprint Context

**Current Sprint**: Sprint 2 (Week 11) - Generation & Document Export APIs

**Status**: NOT STARTED - Sprint 1 complete, Sprint 2 planned but not yet implemented

**Evidence**:
- No `test_generation_api.py` or `test_document_api.py` files exist yet
- Generation and Document API endpoints created but not fully implemented
- 133 tests passing (all Sprint 1 tests)
- Adapter files exist in `infrastructure/adapters/` but contain only empty stub classes

**Sprint 2 Goals**:
- Implement Generation API (API-3) with 5-stage mock pipeline
- Implement Document Export API (API-4) with PDF generation
- Add 53+ new tests (target: 67 total tests passing)
- Achieve 65%+ test coverage
- Complete end-to-end flow: Profile → Job → Generation → PDF Export

**Sprint 2 Files to Create** (see `docs/sprint2/sprint2-plan.md` for details):
- Domain models: `app/domain/generation.py`, `app/domain/document.py`
- Repositories: `app/infrastructure/repositories/generation_repository.py`, `document_repository.py`
- Services: `app/application/services/generation_pipeline.py`, `pdf_export_service.py`, etc.
- API endpoints: `app/presentation/api/v1/generation.py`, `documents.py`
- Tests: `tests/test_generation_api.py`, `tests/test_document_api.py`, etc.

## Multi-Agent Coordination

This project uses multiple AI agents with defined roles:

- **Business Analyst Agent** (Claude 3.5 Sonnet): Requirements, user stories
- **Solutions Architect Agent** (ChatGPT-4): Architecture decisions, ADRs
- **Backend Developer Agent** (GitHub Copilot + Claude): Implementation
- **Mobile Developer Agent** (GitHub Copilot): Flutter development
- **QA Engineer Agent** (GitHub Copilot + ChatGPT): Testing strategy

**Coordination Logs**:
- `log/backend-developer-log.md`
- `log/solutions-architect-log.md`
- `log/qa-engineer-log.md`
- `log/general-interaction-log.md`

When making significant changes, update the relevant log file with implementation details, decisions, and learnings.

## Development Tips

### Working with Pydantic v2
- Use `model_config = ConfigDict(from_attributes=True)` instead of deprecated `orm_mode=True`
- Use `model_validate()` instead of `from_orm()`
- Field definitions: `field: str = Field(..., description="...")` not `Field(default=...)`

### Pytest Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Database Testing Pattern
```python
@pytest.mark.asyncio
async def test_repository_operation(db_session):
    # db_session is a fixture from conftest.py
    repository = MyRepository(db_session)
    result = await repository.create(entity)
    assert result.id is not None
```

### API Testing Pattern
```python
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_api_endpoint(async_client, auth_headers):
    # async_client and auth_headers from conftest.py
    response = await async_client.post(
        "/api/v1/resources",
        json={"field": "value"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["field"] == "value"
```

## Performance Targets

- **CRUD Operations**: <200ms response time
- **Job Search**: <2s response time
- **Resume Generation**: <6s total (5-stage pipeline)
- **PDF Export**: <2s per document
- **Database Queries**: Use indexes, avoid N+1 queries, use `selectinload()` for relationships

## Quick Diagnostic Commands

### Check Current Status
```powershell
# See what tests exist
cd backend && python -m pytest --collect-only -q | tail -5

# Check test coverage quickly
cd backend && python -m pytest --cov=app --cov-report=term-missing -q

# List all API endpoints
cd backend && python -c "from app.main import app; print('\n'.join([r.path for r in app.routes]))"

# Check database schema
cd backend && python -c "from app.infrastructure.database.models import Base; print([t.name for t in Base.metadata.sorted_tables])"

# Count lines of code
cd backend && find app -name "*.py" -not -path "*__pycache__*" | xargs wc -l | tail -1

# Check which tests are failing
cd backend && python -m pytest --tb=no -q
```

## Architecture Simplification (Recent Change)

### What We Removed
The architecture was previously over-engineered with many empty adapter stubs. We simplified to focus on what's actually needed for Sprint 2:

**Removed:**
- Empty LLM adapters (Azure, Claude, Gemini, Groq, Local) - keeping only Mock for Sprint 2
- Empty PDF adapters (CloudPDF, WeasyPrint) - keeping only ReportLab
- Empty storage adapters (S3, Azure Blob) - keeping only local storage
- Over-engineered infrastructure (circuit breaker, fallback manager, service factory)
- Empty use_cases layer (redundant with services)
- Duplicate `backend/infrastructure/` directory

**What We Kept:**
- **Adapter pattern structure** (domain/ports + infrastructure/adapters)
- **Domain entities and value objects** (core business logic)
- **Repository pattern** (clean data access)
- **Service layer** (business logic orchestration)

**Current State of Adapters (October 2025)**:
- Adapter files exist in `infrastructure/adapters/` but contain only empty stub classes
- `llm/openai_adapter.py`: Contains empty OpenAI, Claude, Gemini, Groq, Azure, Local adapter classes
- `pdf/reportlab_adapter.py`: Exists but implementation pending Sprint 2
- `storage/local_file_adapter.py`: Exists but implementation pending Sprint 2
- These will be implemented as part of Sprint 2 work

### When to Add Complexity Back

**Add 2nd LLM Adapter (Sprint 3-4):**
```python
# Create infrastructure/adapters/llm/openai.py
class OpenAIAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
        # Real OpenAI implementation
```

**Add Service Factory (when 3+ providers):**
```python
# Create core/service_factory.py
def get_llm_service() -> ILLMService:
    if settings.LLM_PROVIDER == "openai":
        return OpenAIAdapter()
    elif settings.LLM_PROVIDER == "claude":
        return ClaudeAdapter()
    return MockLLMAdapter()
```

**Rule of Thumb**: Don't create an adapter until you have a second implementation or concrete plans to add one soon.

## Known Gotchas

1. **Pydantic v2 Syntax**: This project uses Pydantic v2 - check version-specific syntax
2. **Async Sessions**: Always use `async with` for transaction management
3. **JWT Middleware**: Endpoints outside `/api/v1/auth/*` require authentication
4. **Test Database**: Tests use separate SQLite file, automatically created/torn down
5. **Mock vs Real AI**: Current pipeline is mock - future sprint will integrate real LLMs
6. **Unified Job Model**: Single `JobModel` table with `source` field - don't create separate tables
7. **Windows Paths**: Use forward slashes or raw strings for file paths in tests
8. **Adapter Pattern**: Only used for external services (LLM, PDF, storage) - not for repositories
9. **Domain Ports**: Interface files in domain/ports/, implementations in infrastructure/adapters/
10. **Empty Adapter Stubs**: Files in `infrastructure/adapters/` exist but contain only empty class definitions - implementation pending Sprint 2
11. **Test Count Discrepancy**: CLAUDE.md may reference outdated test counts - always run `pytest --collect-only` to verify current count
12. **Coverage Measurement**: Coverage tool excludes `__pycache__`, `tests/`, and `alembic/` directories by default (see `pyproject.toml`)

## Future Considerations

- **Real LLM Integration**: Replace mock pipeline with OpenAI/Anthropic in Sprint 3-4
- **PDF Generation**: Currently using ReportLab (Sprint 2), may add WeasyPrint for complex layouts
- **Job API Integration**: Connect to real job APIs (Indeed, LinkedIn) in later sprints
- **Flutter Mobile App**: Frontend development starts Sprint 3
- **WebSocket**: Consider adding for real-time generation progress (currently polling)
- **Caching**: Add Redis caching for job search and profile data in production
