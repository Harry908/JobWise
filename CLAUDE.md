# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**JobWise** is an AI-powered job application assistant built with Flutter (mobile) and FastAPI (backend). The app helps users generate tailored resumes and cover letters for specific job postings using their master profile and AI-driven content generation with real Groq LLM integration.

**Current Status** (Updated November 2025):
- ✅ **Sprints 1-3 Complete**: Backend foundation (Auth, Profile, Job APIs) + Mobile UI
- ✅ **V3 Generation API**: 10 endpoints fully implemented with real Groq LLM
- ✅ **Mobile App**: 13 screens across 5 feature areas
- 🔄 **Architecture Redesign**: Sprint 5 design docs complete, implementation in progress

**IMPORTANT - Implementation Status**:
- **Fully Implemented**: Auth API, Profile API, Job API, V3 Generation API (10 endpoints with real LLM)
- **Backend Services**: WritingStyleService, ProfileEnhancementService, ContentRankingService, DocumentGenerationService
- **Real AI Integration**: Groq API (llama-3.3-70b-versatile, llama-3.1-8b-instant) confirmed working

---

## Common Development Commands

### Windows Environment

**CRITICAL**: This project runs on Windows with PowerShell. All commands use PowerShell syntax.

```powershell
# PowerShell command chaining (use semicolon, not &&)
cd backend ; python -m pytest

# Virtual environment activation
cd backend ; .\venv\Scripts\Activate.ps1

# NOT bash syntax (will fail)
cd backend && python -m pytest  # ❌ WRONG
```

### Backend (FastAPI)

**Location**: `backend/` directory

**Environment Setup**:
```powershell
cd backend
.\venv\Scripts\Activate.ps1   # PowerShell
# OR
venv\Scripts\activate          # CMD
```

**Start Server**:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Testing**:
```powershell
cd backend

# Run all tests with coverage
python -m pytest --cov=app --cov-report=html --cov-report=term-missing -v

# Run specific test file
python -m pytest tests/test_profile_api.py -v

# Run with fail-fast
python -m pytest --maxfail=1 -q

# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration
```

**Database**:
```powershell
cd backend

# Initialize/upgrade database
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

**Code Quality**:
```powershell
cd backend

# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Type checking
mypy app/

# Linting
flake8 app/ tests/
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

# Default device
flutter run

# Specific platform
flutter run -d chrome
flutter run -d android
flutter run -d ios  # macOS only
```

**Code Generation (Freezed models)**:
```powershell
cd mobile_app

# Generate freezed files
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode
flutter pub run build_runner watch --delete-conflicting-outputs
```

**Testing**:
```powershell
cd mobile_app

# Run all tests
flutter test

# With coverage
flutter test --coverage
```

---

## Architecture Overview

### Backend Clean Architecture

The backend follows **Clean Architecture** with Ports & Adapters pattern:

```
backend/app/
├── presentation/
│   ├── api/                    # FastAPI routers
│   │   ├── auth.py            # ✅ Authentication
│   │   ├── profile.py         # ✅ Profile management
│   │   └── job.py             # ✅ Job CRUD
│   └── v3_api.py              # ✅ V3 Generation System (10 endpoints)
│
├── application/services/       # Business logic orchestration
│   ├── auth_service.py
│   ├── profile_service.py
│   ├── job_service.py
│   ├── writing_style_service.py         # ✅ NEW (Sprint 5)
│   ├── profile_enhancement_service.py   # ✅ NEW (Sprint 5)
│   ├── content_ranking_service.py       # ✅ NEW (Sprint 5)
│   ├── document_generation_service.py   # ✅ NEW (Sprint 5)
│   ├── generation_service.py            # ✅ NEW (Sprint 5)
│   └── prompt_service.py                # ✅ NEW (Sprint 5)
│
├── domain/
│   ├── entities/               # Core business entities
│   │   ├── user.py
│   │   ├── profile.py
│   │   └── job.py
│   └── ports/                  # Service interfaces
│       ├── llm_service.py      # ILLMService interface
│       └── pdf_generator.py    # IPDFGenerator interface
│
└── infrastructure/
    ├── adapters/               # External service implementations
    │   └── llm_factory.py      # LLM service factory
    ├── database/
    │   ├── models.py           # SQLAlchemy ORM models
    │   └── connection.py       # Database session management
    └── repositories/           # Data access implementations
        ├── user_repository.py
        ├── profile_repository.py
        └── job_repository.py
```

**Key Principles**:
- **Repository Pattern**: All database access through repositories
- **Dependency Injection**: FastAPI Depends() for session management
- **Async/Await**: All I/O operations use async SQLAlchemy
- **Clean Separation**: presentation → application → domain ← infrastructure
- **Ports & Adapters**: Domain defines interfaces, infrastructure implements

---

## Database Architecture

**ORM**: SQLAlchemy 2.0 with async support (`aiosqlite` for SQLite)

**Key Models**:
- **UserModel**: Authentication and user management (JWT tokens)
- **MasterProfileModel**: Master resume with JSON fields (personal_info, skills, custom_fields)
- **ExperienceModel**: Work experiences with enhanced_description support
- **ProjectModel**: Projects with enhanced_description support
- **JobModel**: Unified job model with `source` field (api, user_created, scraped, etc.)
- **SampleDocumentModel**: Uploaded resume/cover letter samples (full text stored)
- **WritingStyleModel**: Normalized writing style configs (separate table)
- **JobContentRankingModel**: Job-specific content rankings
- **GenerationModel**: Generation requests and results

**Important Design Decisions**:
- **Unified Job Model**: Single `jobs` table with `source` discrimination (not separate tables)
- **JSON Fields**: Profile uses JSON for flexible schema (personal_info, skills, custom_fields)
- **Enhanced Content**: Experiences/projects have both `description` and `enhanced_description`
- **Sample Storage**: Full text stored in database for re-analysis capability

---

## Mobile App Architecture (Flutter + Riverpod)

**State Management**: Riverpod with StateNotifier pattern

**Key Patterns**:
- **Riverpod StateNotifier**: AuthNotifier, ProfileNotifier, JobNotifier
- **Freezed Models**: Job-related models use `@freezed` annotation
- **Manual Models**: Profile models use manual data classes
- **API Clients**: Dio-based clients with interceptors (auth, logging)
- **Secure Storage**: flutter_secure_storage for JWT tokens

**Mobile Screens** (13 total):
- **Authentication** (2): Login, Register
- **Profile** (3): View, Edit (multi-step), Settings
- **Jobs** (4): Browse, List (saved), Detail, Paste (text input)
- **Generation** (4): Options, Progress, Result, History
- **Debug** (1): Debug utilities

**Data Flow**:
1. User authenticates → JWT stored securely
2. User creates/edits Profile (manual entry)
3. User uploads sample documents (resume/cover letter .txt files)
4. User browses/saves Jobs → stored with application status
5. User generates tailored resume/cover letter → AI pipeline
6. User downloads PDF exports

---

## API Service Boundaries

```
Auth API     Profile API     Job API     V3 Generation API
   (✅)    →      (✅)    →    (✅)    →       (✅)
Complete        Complete      Complete    10 Endpoints Live
```

### Implemented APIs

**Auth API** (`/api/v1/auth/`):
- POST /register - Create user account
- POST /login - Authenticate (JWT)
- POST /refresh - Refresh token
- GET /me - Get current user

**Profile API** (`/api/v1/profiles/`):
- Full CRUD operations
- Bulk operations (experiences, education, projects)
- Skills management (technical, soft)
- Custom fields support
- Profile analytics

**Job API** (`/api/v1/jobs/`):
- POST / - Create job (text parsing supported)
- GET / - List user's jobs (with filters)
- GET /{id} - Get job details
- PUT /{id} - Update job
- DELETE /{id} - Delete job

**V3 Generation API** (`/api/v1/`):
1. POST /samples/upload - Upload sample documents
2. POST /profile/enhance - AI-enhance profile
3. POST /rankings/create - Rank content for job
4. POST /generations/resume - Generate resume (pure logic)
5. POST /generations/cover-letter - Generate cover letter (LLM)
6. GET /samples - List uploaded samples
7. GET /samples/{id} - Get sample details
8. DELETE /samples/{id} - Delete sample
9. GET /rankings/job/{id} - Get job rankings
10. GET /generations/history - Generation history

---

## Key Technical Decisions

### Authentication
- **JWT tokens** with bcrypt password hashing
- Token in Authorization header: `Bearer <token>`
- All `/api/v1/*` endpoints require auth (except /auth/register, /auth/login)

### AI Integration (Groq LLM)
- **Provider**: Groq.com (ultra-fast inference)
- **Models**:
  - llama-3.3-70b-versatile (quality, resume/cover letter generation)
  - llama-3.1-8b-instant (speed, analysis/ranking)
- **Status**: ✅ Real API integration confirmed working
- **Token Usage**: Tracked per request, logged in GenerationModel
- **Rate Limiting**: Planned (10 generations/hour per user)

### Database Patterns
- **Repository Pattern**: All DB access through repositories
- **Async/Await**: SQLAlchemy async sessions everywhere
- **Value Objects**: Complex types (Experience, Education) in domain
- **No Raw SQL**: SQLAlchemy ORM queries only

### API Design
- **RESTful**: Proper HTTP methods and status codes
- **Pydantic v2**: Request/response validation
- **OpenAPI 3.0**: Auto-generated at `/docs`
- **Consistent Errors**:
  ```json
  {
    "error": {
      "code": "error_code_snake_case",
      "message": "Human-readable message",
      "details": {}
    }
  }
  ```

### Testing Strategy
- **pytest** with async support (`pytest-asyncio`)
- **Test Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`
- **Coverage Target**: 80%+
- **Test Database**: Separate SQLite (`test_jobwise.db`)

### Code Style
- **Backend**: Black (line length: 88), isort, type hints, mypy
- **Mobile**: Dart analyzer, flutter_lints
- **Async-first**: All I/O must be async

---

## Common Patterns and Conventions

### Adding a New API Endpoint

1. **Define Request/Response DTOs** in router file
2. **Create/Update Domain Entity** in `app/domain/entities/`
3. **Define Repository Interface** (if new entity)
4. **Implement Repository** in `app/infrastructure/repositories/`
5. **Create Application Service** in `app/application/services/`
6. **Add API Router** endpoint
7. **Register Router** in `app/main.py` (if new router file)
8. **Write Tests** in `tests/`

### Async Database Sessions

Always use dependency injection:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db_session

async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
    async with db.begin():
        # Transaction auto-committed or rolled back
        pass
```

### Error Handling

Use custom exceptions:

```python
from app.core.exceptions import NotFoundException

if not resource:
    raise NotFoundException(
        error_code="resource_not_found",
        message="Resource not found",
        details={"resource_id": id}
    )
```

### Mobile State Management (Riverpod)

```dart
// StateNotifier - no public properties beyond state
class ProfileNotifier extends StateNotifier<ProfileState> {
  ProfileNotifier(this._apiClient) : super(ProfileState.initial());

  final ProfilesApiClient _apiClient;

  Future<void> fetchProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final profile = await _apiClient.getProfile();
      state = state.copyWith(profile: profile, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
}
```

---

## Important Files and Locations

### Configuration
- `backend/.env` - Environment variables (GROQ_API_KEY, JWT_SECRET, DATABASE_URL)
- `backend/.env.example` - Template
- `backend/app/core/config.py` - Settings class
- `mobile_app/.env` - Mobile config (API_BASE_URL)

### Design Documentation
**IMPORTANT**: All design documents are in `docs/` folder:

**Sprint 5 (Current Architecture)**:
- `docs/sprint5/00-OVERVIEW.md` - System redesign overview
- `docs/sprint5/01-DATABASE-SCHEMA.md` - Complete schema
- `docs/sprint5/02-AI-PIPELINE.md` - LLM workflows
- `docs/sprint5/03-API-ENDPOINTS.md` - API specifications
- `docs/sprint5/04-PROMPT-MANAGEMENT.md` - Prompt system
- `docs/sprint5/05-LLM-ADAPTER.md` - LLM integration

**Comprehensive Guides**:
- `docs/UNIFIED-BACKEND-ARCHITECTURE.md` - Single backend design
- `docs/JOBWISE_AI_GENERATION_SYSTEM.md` - Complete AI system reference
- `docs/BACKEND_DESIGN_DOCUMENT.md` - Backend architecture
- `docs/COVER_LETTER_TEXT_STORAGE_IMPLEMENTATION.md` - Text storage design

**Mobile Documentation**:
- `docs/mobile/README.md` - Mobile feature overview
- `docs/mobile/00-api-configuration.md` - API integration
- `docs/mobile/01-authentication-feature.md` - Auth screens
- `docs/mobile/02-profile-feature.md` - Profile management
- `docs/mobile/03-job-browsing-feature.md` - Job screens
- `docs/mobile/04-generation-feature.md` - Generation UI
- `docs/mobile/05-document-feature.md` - Document export

**Legacy/Archive**:
- `docs/legacy/` - Older API specs (reference only)
- `docs/sprint1/` - Sprint 1 planning
- `docs/sprint2/` - Sprint 2 planning
- `docs/sprint3/` - Sprint 3 planning

### Database
- `backend/alembic/` - Database migrations
- `backend/jobwise.db` - Development SQLite database
- `backend/test_jobwise.db` - Test database

### Testing
- `backend/tests/conftest.py` - Pytest fixtures
- `backend/pytest.ini` - Test configuration

### Agent Configuration
**IMPORTANT**: This project uses GitHub Copilot custom agents:

- `.github/agents/backend-developer.agent.md` - Backend development agent
- `.github/agents/mobile-developer.agent.md` - Flutter/Dart agent
- `.github/agents/solutions-architect.agent.md` - Architecture decisions
- `.github/agents/qa-engineer.agent.md` - Testing and QA
- `.github/agents/business-analyst.agent.md` - Requirements analysis

**Agent Summaries**:
- `.context/backend-developer-summary.md` - Backend implementation status
- `.context/mobile-developer-summary.md` - Mobile implementation status

**Agent Logs**:
- `log/backend-developer-log.md` - Backend interaction log
- `log/mobile-developer-log.md` - Mobile interaction log

---

## Current Codebase Stats (November 2025)

- **Backend Files**: 35+ Python files in `app/`
- **Mobile Files**: 60+ Dart files in `lib/`
- **Mobile Screens**: 13 screens (2 auth, 3 profile, 4 job, 4 generation, 1 debug)
- **API Endpoints**: 40+ endpoints across 4 routers
  - Auth API (4 endpoints)
  - Profile API (15+ endpoints)
  - Job API (5 endpoints)
  - V3 Generation API (10 endpoints)
- **Backend Services**: 11 service files
- **Repositories**: 8+ repository implementations
- **Tests**: 100+ tests (unit + integration)
- **Test Coverage**: 64% (target: 80%+)

**V3 API Implementation**:
- ✅ Sample upload endpoint with text extraction
- ✅ Profile enhancement with real LLM
- ✅ Content ranking with llama-3.1-8b-instant
- ✅ Resume generation (pure logic, <1s)
- ✅ Cover letter generation (LLM, ~3-5s)
- ✅ Sample management (list, get, delete)
- ✅ Ranking retrieval
- ✅ Generation history

---

## Development Tips

### Working with Pydantic v2
- Use `model_config = ConfigDict(from_attributes=True)` not `orm_mode=True`
- Use `model_validate()` instead of `from_orm()`
- Field definitions: `field: str = Field(..., description="...")`

### Pytest Async Tests
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Working with Freezed (Mobile)
- Job models use `@freezed` for immutability
- After modifying freezed files:
  ```powershell
  flutter pub run build_runner build --delete-conflicting-outputs
  ```
- Generates `*.freezed.dart` and `*.g.dart`

### Date Handling (Mobile)
- Mobile supports 3 formats: US (MM/dd/yyyy), European (dd/MM/yyyy), ISO (yyyy-MM-dd)
- User configurable in Settings
- API always expects `yyyy-MM-dd`

---

## Quick Diagnostic Commands

```powershell
# Check backend test status
cd backend ; python -m pytest --collect-only -q

# Check test pass/fail counts
cd backend ; python -m pytest --tb=no -q

# Check coverage
cd backend ; python -m pytest --cov=app --cov-report=term-missing -q

# List all API endpoints
cd backend ; python -c "from app.main import app; print('\n'.join([r.path for r in app.routes]))"

# Check database tables
cd backend ; python -c "from app.infrastructure.database.models import Base; print([t.name for t in Base.metadata.sorted_tables])"
```

---

## Known Gotchas

1. **PowerShell Syntax**: Use `;` not `&&` for command chaining
2. **Virtual Environment**: Use `.\venv\Scripts\Activate.ps1` on Windows
3. **Pydantic v2**: This project uses Pydantic v2 syntax
4. **Async Sessions**: Always use `async with` for transactions
5. **JWT Required**: All API endpoints require auth except /auth/register, /auth/login
6. **Test Database**: Tests use separate SQLite file
7. **Unified Job Model**: Single `jobs` table with `source` field
8. **Freezed**: Job models use Freezed, Profile models use manual classes
9. **Android Emulator**: Use `10.0.2.2` to access localhost, not `localhost`
10. **GoRouter**: Use `context.push()` for secondary screens, `context.go()` for top-level

---

## V3 Generation System (Implemented)

**Status**: ✅ Complete with real Groq LLM integration

### User Flow

1. **Upload Sample Documents** → User provides .txt files
2. **Extract Writing Style** → WritingStyleService analyzes cover letter
3. **Enhance Profile** → ProfileEnhancementService improves content
4. **Create Ranking** → ContentRankingService ranks by job relevance
5. **Generate Documents**:
   - Resume: Pure logic compilation (fast, <1s)
   - Cover Letter: LLM generation (llama-3.3-70b-versatile, ~3-5s)

### LLM Integration

**Provider**: Groq.com
**Models**:
- `llama-3.3-70b-versatile` - High quality (cover letters, enhancements)
- `llama-3.1-8b-instant` - Fast speed (ranking, analysis)

**Confirmed Working**:
- Real API calls successfully tested
- Token usage tracked and logged
- Generation metadata stored in database

### Key Files

**Services**:
- `app/application/services/writing_style_service.py`
- `app/application/services/profile_enhancement_service.py`
- `app/application/services/content_ranking_service.py`
- `app/application/services/document_generation_service.py`

**API Router**:
- `app/presentation/v3_api.py` - All 10 V3 endpoints

**Domain Ports**:
- `app/domain/ports/llm_service.py` - ILLMService interface

**Infrastructure**:
- `app/infrastructure/adapters/llm_factory.py` - LLM adapter factory

---

## Multi-Agent Coordination

This project uses multiple AI agents with defined roles:

- **Backend Developer Agent**: FastAPI, SQLAlchemy, AI integration
- **Mobile Developer Agent**: Flutter, Riverpod, Material Design
- **Solutions Architect Agent**: Architecture decisions, ADRs
- **QA Engineer Agent**: Testing strategy, quality assurance
- **Business Analyst Agent**: Requirements, user stories

**Coordination**:
- Agents update `.context/*-summary.md` files
- Agents log interactions in `log/*-log.md`
- Use PowerShell syntax
- No emoji usage

**When making significant changes**, update relevant log file and agent summary.

---

## Sprint 5 Implementation Guide

**Status**: Design documents complete, implementation in progress

**Key Changes from Previous Sprints**:
- Simplified sample document storage (single table)
- Job-specific tailoring only (no generic preferences)
- Enhanced descriptions stored alongside originals
- Database-stored prompts with versioning
- Clear LLM vs pure logic separation

**Implementation Order**:
1. Database schema updates (sample_documents, enhanced fields)
2. Sample upload endpoints
3. Writing style extraction service
4. Profile enhancement service
5. Content ranking service
6. Resume compilation (pure logic)
7. Cover letter generation (LLM)
8. Mobile UI integration

**See**: `docs/sprint5/00-OVERVIEW.md` for complete implementation plan

---

## References

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/
- **Pydantic v2**: https://docs.pydantic.dev/
- **Flutter**: https://docs.flutter.dev/
- **Riverpod**: https://riverpod.dev/
- **Groq API**: https://console.groq.com/docs/

---

**Last Updated**: November 2025
**Project Phase**: Sprint 5 (Backend redesign + Mobile integration)
**Backend Status**: V3 API fully implemented with real LLM
**Mobile Status**: 13 screens complete, generation UI in progress
