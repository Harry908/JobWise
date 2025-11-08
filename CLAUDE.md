# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**JobWise** is an AI-powered job application assistant built with Flutter (mobile) and FastAPI (backend). The app helps users generate tailored resumes and cover letters for specific job postings by combining their master profile with AI-driven document generation.

**Current Status** (Updated November 2025):
- ✅ **Sprint 1 Complete**: Backend foundation with Auth, Profile, and Job APIs
- ✅ **Sprint 2 Complete**: Documentation ready, implementation pending
- ✅ **Sprint 3 Complete**: Mobile job management screens fully implemented
- 🚧 **Sprint 4 Ready**: Generation & Document APIs ready for implementation

**IMPORTANT - Sprint 4 Status**:
- **Implemented**: Auth API, Profile API, Job API (Sprint 1-3)
- **Ready for Implementation**: Generation API, Document API (Sprint 4)
- All Generation & Document API specs have been reviewed and corrected (Nov 7, 2025)
- See `docs/api-services/GENERATION_API_REVIEW.md` for detailed spec review
- 9 critical issues fixed in API specifications before Sprint 4 implementation

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
pytest tests/test_profile_api_live.py -v

# Run with fail-fast (stop on first failure)
pytest --maxfail=1 -q

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto

# Check which tests are failing
pytest --tb=no -q
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

**Code Generation (Freezed models)**:
```powershell
cd mobile_app

# Generate freezed and json_serializable files
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate on changes)
flutter pub run build_runner watch --delete-conflicting-outputs
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

### Backend Clean Architecture

The backend follows **Clean Architecture** with clear separation of concerns:

```
backend/app/
├── presentation/api/        # API layer (FastAPI routers)
│   ├── auth.py             # ✅ EXISTS
│   ├── profile.py          # ✅ EXISTS
│   └── job.py              # ✅ EXISTS
│
├── application/services/    # Business logic orchestration
│   ├── auth_service.py
│   ├── profile_service.py
│   └── job_service.py
│
├── domain/entities/         # Core business entities
│   ├── user.py
│   ├── profile.py
│   └── job.py
│
├── infrastructure/
│   ├── database/            # Database layer
│   │   ├── models.py       # SQLAlchemy models
│   │   └── connection.py
│   └── repositories/        # Data access implementations
│       ├── user_repository.py
│       ├── profile_repository.py
│       └── job_repository.py
│
└── core/                    # Shared utilities
    ├── config.py
    ├── security.py
    ├── exceptions.py
    └── dependencies.py
```

**Key Principles**:
- **Repository Pattern**: All database access through repositories
- **Dependency Injection**: FastAPI Depends() for session management
- **Async/Await**: All I/O operations use async SQLAlchemy
- **Clean Separation**: presentation → application → domain ← infrastructure

### Database Architecture

**ORM**: SQLAlchemy 2.0 with async support (`aiosqlite` for SQLite, `asyncpg` for PostgreSQL)

**Key Models**:
- **User**: Authentication and user management (JWT tokens)
- **Profile**: Master resume with experiences, education, skills, projects
- **JobModel**: Unified job model with `source` field (api, static, user_created, scraped, imported)

**Important**: Uses **Unified Job Model** - single table with source discrimination, not separate tables per source.

### Mobile App Architecture (Flutter + Riverpod)

**State Management**: Riverpod with StateNotifier pattern

**Key Patterns**:
- **Riverpod StateNotifier**: Used for AuthNotifier, ProfileNotifier, JobNotifier
- **Freezed Models**: Job-related models use `@freezed` annotation for immutability
- **Manual Models**: Profile models use manual data classes (inconsistent - consider migrating)
- **API Clients**: Dio-based clients with interceptors for auth and logging
- **Secure Storage**: flutter_secure_storage for JWT tokens

**Screens** (9 total):
- Authentication: Login, Register
- Profile: View, Edit (multi-step form), Settings
- Jobs: Browse, List (saved jobs), Detail, Paste (text input)
- Debug: Debug utilities

**Data Flow**:
1. User authenticates → JWT token stored securely
2. User creates/edits Profile (experiences, education, skills, projects)
3. User browses/saves Jobs → stored in backend with application status
4. *(Future Sprint 2)* User generates resume → AI tailoring → PDF export

## API Service Boundaries

```
Auth API (✅) ──> Profile API (✅) ──> Job API (✅) ──> Generation API (🚧) ──> Document API (🚧)
   Complete           Complete            Complete         SPRINT 4 READY        SPRINT 4 READY
```

**Implemented APIs** (Sprint 1-3):
- **Auth API**: Register, login, token refresh, JWT validation
- **Profile API**: CRUD, bulk operations (experiences, education, projects), skills management, custom fields
- **Job API**: Browse, create, list, get, update (status/keywords), delete

**Sprint 4 Ready** (Specs reviewed Nov 7, 2025):
- **Generation API**: 5-stage AI pipeline fully specified with error handling, progress tracking
- **Document API**: PDF/DOCX export with 3 templates (modern, classic, creative)

## Key Technical Decisions

### Authentication
- **JWT tokens** with bcrypt password hashing
- Token stored in Authorization header: `Bearer <token>`
- All `/api/v1/*` endpoints require authentication (except `/auth/register`, `/auth/login`)
- Middleware validates JWT and injects user context into requests

### Database Patterns
- **Repository Pattern**: All database access goes through repositories
- **Async/Await**: All database operations use SQLAlchemy async sessions
- **Value Objects**: Complex types (Experience, Education, Skills) in domain entities
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
      "details": {}
    }
  }
  ```

### Testing Strategy
- **pytest** with async support (`pytest-asyncio`)
- **Test Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- **Coverage Target**: 80%+ (currently ~50% with many failing tests)
- **Test Database**: Separate SQLite database (`test_jobwise.db`) with fixtures in `tests/conftest.py`

### Code Style
- **Backend**: Black formatter (line length: 88), isort, type hints, mypy
- **Mobile**: Dart analyzer, flutter_lints
- **Async-first**: All I/O operations must be async

## Common Patterns and Conventions

### Adding a New API Endpoint

1. **Define DTOs** in `app/application/dtos/`
2. **Create/Update Domain Entity** in `app/domain/entities/`
3. **Define Repository Interface** (if new entity)
4. **Implement Repository** in `app/infrastructure/repositories/`
5. **Create Application Service** in `app/application/services/`
6. **Add API Router** in `app/presentation/api/v1/`
7. **Register Router** in `app/main.py`
8. **Write Tests** in `tests/`

### Async Database Sessions

Always use dependency injection for database sessions:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import get_db

async def my_endpoint(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        # Transaction automatically committed or rolled back
        pass
```

### Error Handling

Use custom exceptions from `app/core/exceptions.py`:

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
// StateNotifier with no public properties beyond state
class ProfileNotifier extends StateNotifier<ProfileState> {
  ProfileNotifier(this._apiClient) : super(ProfileState.initial());

  final ProfilesApiClient _apiClient;

  // Use methods to update state, never expose mutable properties
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

## Important Files and Locations

### Configuration
- `backend/.env` - Environment variables (DATABASE_URL, JWT_SECRET, etc.)
- `backend/.env.example` - Template for environment variables
- `backend/app/core/config.py` - Settings class using pydantic-settings
- `mobile_app/.env` - Mobile environment (API_BASE_URL)

### Documentation
- `README.md` - Project overview (**Note**: Claims Sprint 2-3 complete but code disagrees)
- `docs/sprint2/sprint2-plan.md` - Sprint 2 planning (not yet implemented)
- `docs/api-services/` - API specifications for each service
- `docs/mobile/` - Mobile feature designs

### Database
- `backend/alembic/` - Database migrations
- `backend/jobwise.db` - Development SQLite database
- `backend/test_jobwise.db` - Test SQLite database

### Testing
- `backend/tests/conftest.py` - Pytest fixtures and test configuration
- `backend/pytest.ini` - Test configuration

### Current Codebase Stats (November 2025)
- **Backend Files**: 19 Python files in `app/`
- **Mobile Files**: 38 Dart files in `lib/`
- **Total Tests**: 150 tests across 10 test files
- **Tests Passing**: 76 (51% pass rate)
- **Tests Failing**: 72 (49% failure rate - mostly profile API "live" tests)
- **API Endpoints**: Auth (complete), Profile (complete), Job (complete)
- **APIs NOT Implemented**: Generation, Document
- **Mobile Screens**: 9 screens (2 auth, 3 profile, 4 job)

**Test Health Warning**: Nearly half of all tests are currently failing, primarily in profile bulk operations and granular operations. These need investigation and fixes before proceeding to Sprint 2.

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

### Working with Freezed (Mobile)
- Job models use `@freezed` annotation for immutability and JSON serialization
- After modifying `*.dart` files with `@freezed`:
  ```powershell
  flutter pub run build_runner build --delete-conflicting-outputs
  ```
- Generates `*.freezed.dart` and `*.g.dart` files
- **Inconsistency**: Profile models use manual data classes - consider migrating to Freezed

### Date Handling (Mobile)
- Mobile supports 3 date formats: US (MM/dd/yyyy), European (dd/MM/yyyy), ISO (yyyy-MM-dd)
- User can configure in Settings screen
- API always expects `yyyy-MM-dd` format
- Use date conversion utilities in validators.dart

## Quick Diagnostic Commands

### Check Current Status
```powershell
# See what tests exist
cd backend && python -m pytest --collect-only -q

# Check test pass/fail counts
cd backend && python -m pytest --tb=no -q

# Check test coverage
cd backend && python -m pytest --cov=app --cov-report=term-missing -q

# List all API endpoints
cd backend && python -c "from app.main import app; print('\n'.join([r.path for r in app.routes]))"

# Verify which API routers are registered
cd backend && python -c "from app.main import app; [print(r.prefix) for r in app.routes if hasattr(r, 'prefix')]"

# Check database tables
cd backend && python -c "from app.infrastructure.database.models import Base; print([t.name for t in Base.metadata.sorted_tables])"
```

## Known Gotchas

1. **Sprint 4 Status**: Generation & Document API specifications reviewed and corrected (Nov 7, 2025). Ready for implementation. See `GENERATION_API_REVIEW.md` for details.

2. **Test Failures**: 48% of tests currently failing (72/150), mostly profile API tests. Run `pytest -v` to see failures before making changes.

3. **Pydantic v2 Syntax**: This project uses Pydantic v2 - check version-specific syntax.

4. **Async Sessions**: Always use `async with` for transaction management.

5. **JWT Middleware**: Endpoints outside `/api/v1/auth/*` require authentication.

6. **Test Database**: Tests use separate SQLite file, automatically created/torn down.

7. **Unified Job Model**: Single `JobModel` table with `source` field - don't create separate tables.

8. **Windows Paths**: Use forward slashes or raw strings for file paths in tests.

9. **Freezed Inconsistency**: Job models use Freezed, Profile models use manual classes. Pick one pattern.

10. **No Adapters Directory**: Documentation references `infrastructure/adapters/` but this directory does not exist and won't be needed until Sprint 4 implements Generation/Document APIs.

11. **Android Emulator**: Use `10.0.2.2` to access localhost backend from Android emulator, not `localhost`.

12. **GoRouter Context**: Use `context.push()` for secondary screens to enable back button, `context.go()` for top-level navigation.

## Multi-Agent Coordination

This project uses multiple AI agents with defined roles:

- **Business Analyst Agent** (Claude 3.5 Sonnet): Requirements, user stories
- **Solutions Architect Agent** (ChatGPT-4): Architecture decisions, ADRs
- **Backend Developer Agent** (GitHub Copilot + Claude): Implementation
- **Mobile Developer Agent** (GitHub Copilot): Flutter development
- **QA Engineer Agent** (GitHub Copilot + ChatGPT): Testing strategy

**Coordination Logs**:
- `session-logs/sprint1-log/backend-developer-log.md`
- `session-logs/sprint1-log/mobile-developer-log.md`
- `session-logs/sprint1-log/solutions-architect-log.md`
- `session-logs/sprint1-log/qa-engineer-log.md`

When making significant changes, update the relevant log file with implementation details, decisions, and learnings.

## Sprint 4 Implementation Guide

**Status**: Ready to begin (Specifications reviewed and corrected Nov 7, 2025)

Implement in this order:

1. **Generation Domain Models**: Create `app/domain/entities/generation.py` and `document.py`
2. **Generation Repository**: Implement `app/infrastructure/repositories/generation_repository.py`
3. **Generation Service**: Create 5-stage pipeline services (job analyzer, profile compiler, content generator, quality validator, export prep)
4. **Generation API**: Add `app/presentation/api/generation.py` router
5. **Document Service**: PDF generation with templates
6. **Document API**: Add `app/presentation/api/document.py` router
7. **Tests**: 50+ tests covering all stages and endpoints
8. **Integration**: Update `app/main.py` to include new routers

**Critical: Follow Corrected Specifications**:
- Use `id` not `generation_id` in API responses
- Implement progress calculation with stage weights [20, 20, 40, 15, 5]
- Use exact stage names from specification
- Follow error response format matching Auth/Profile/Job APIs
- Implement regeneration endpoint
- Add Pagination model to mobile

**Don't prematurely create**:
- Adapter directories and interfaces (wait until 2+ implementations needed)
- Service factories and dependency injection complexity
- Infrastructure for "future" LLM providers

**YAGNI Principle**: Build what Sprint 4 actually needs, not what future sprints might need.

**See**: `docs/api-services/GENERATION_API_REVIEW.md` for complete implementation checklist.
