# GitHub Copilot Instructions - JobWise

## Project Overview
JobWise is an AI-powered job application assistant: Flutter mobile app + FastAPI backend with 5-stage resume generation pipeline. **Sprint Status**: Sprint 1-2 complete (Auth, Profile, Job APIs + mobile UI). Sprint 3 in progress (job browsing mobile UI).

## Critical Architecture Patterns

### Backend: Clean Architecture with Ports & Adapters
```
Presentation (API routes) → Application (services) → Domain (entities + ports) ← Infrastructure (adapters + repos)
```

**Key Rule**: Dependencies flow INWARD. Domain has zero external dependencies.

**Adapter Pattern Usage**: ONLY for external services (LLM, PDF, storage). Current state: stub classes in `infrastructure/adapters/` pending Sprint 2 implementation. Repository pattern uses direct SQLAlchemy implementations—NOT adapters.

**Example Pattern**:
```python
# Domain port (interface)
class ILLMService(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str: pass

# Infrastructure adapter
class MockLLMAdapter(ILLMService):
    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(2)
        return "Mock content"

# Service uses port
class GenerationService:
    def __init__(self, llm: ILLMService):
        self.llm = llm  # Depends on interface, not concrete class
```

### Mobile: Simplified 3-Layer (Flutter + Riverpod)
```
UI (Screens/Widgets) ← State (Notifiers with business logic) → Services (API clients)
```

**NO repository layer**—notifiers call API clients directly. **NO adapter pattern** unless swapping implementations. Manual data models (no Freezed to avoid conflicts).

**Riverpod StateNotifier Best Practices**:
- No public properties beyond `state`
- All state changes via `state = state.copyWith(...)`
- Comprehensive error handling with DioException parsing
- Pattern: `ProfileNotifier extends StateNotifier<ProfileState>`

## Development Workflow Commands

### Backend (FastAPI)
```powershell
# Start server (Windows)
cd backend
.\start-server.bat  # http://localhost:8000 | Docs: /docs

# Testing
pytest tests/ -v --cov=app  # 133 tests, 45% coverage target: 80%
pytest tests/profile/ -v    # Specific test suite

# Database
alembic upgrade head        # Apply migrations
```

### Mobile (Flutter)
```powershell
# Run app
cd mobile_app
flutter pub get
flutter run  # Android emulator: API at 10.0.2.2:8000

# Code generation (Freezed + JSON)
flutter pub run build_runner build --delete-conflicting-outputs

# Testing
flutter test
flutter analyze
```

## Project-Specific Conventions

### Database Patterns
- **Async SQLAlchemy**: All DB ops use `AsyncSession` with `async def`
- **Repository Pattern**: `infrastructure/repositories/` with interface in `domain/ports/`
- **Unified Job Model**: Single `JobModel` table with `source` field (api/static/user_created/scraped)—DON'T create separate tables
- **Test Database**: `test_jobwise.db` auto-created in fixtures

### API Conventions
- **JWT Auth**: All `/api/v1/*` except `/auth/register` and `/auth/login` require `Authorization: Bearer <token>`
- **Pydantic v2**: Use `model_config = ConfigDict(from_attributes=True)` not deprecated `orm_mode`
- **Error Format**: `{"error": {"code": "snake_case", "message": "...", "details": {}}}`
- **Async Endpoints**: FastAPI endpoints MUST be `async def` for I/O operations

### Mobile Conventions
- **State Pattern**: `ProfileState.copyWith(...)` for immutability
- **Error Extraction**: Parse `DioException` → extract `response.data['detail']` or `response.data['message']`
- **Date Format**: Configurable US/European/ISO in settings, convert to `YYYY-MM-DD` for API
- **Navigation**: Use `context.push('/path')` for secondary screens (shows back button) vs `context.go()` for top-level
- **Job Editing**: Job postings are READ-ONLY (external content). Users can only edit metadata (keywords, status, notes)

### Critical Gotchas
1. **Adapter Stubs**: Files in `backend/infrastructure/adapters/` exist but contain ONLY empty class definitions—implementation pending
2. **No Freezed**: Mobile uses manual models with `copyWith` to avoid compilation conflicts
3. **Windows Paths**: Use forward slashes or raw strings in tests
4. **Test Count**: Always verify with `pytest --collect-only`, don't trust cached counts
5. **Unified Job Model**: Don't create `job_descriptions` table—use `jobs.source` field

## Key Integration Points

### Backend → Mobile Communication
- **Base URL**: `http://10.0.2.2:8000` (Android emulator maps to host's localhost)
- **iOS Simulator**: `http://localhost:8000` directly
- **Token Refresh**: `BaseHttpClient` intercepts 401 → auto-refresh → retry
- **HTTP Logging**: All requests/responses logged for debugging

### AI Generation Pipeline (5 stages, ~5.5s total)
```
Job Analyzer (1s) → Profile Compiler (1s) → Content Generator (2s) → Quality Validator (1s) → Export Prep (0.5s)
```
**Current**: Mock pipeline with realistic timing. **Future**: Real LLM integration Sprint 3-4.

### API Service Boundaries
```
Auth API (complete) → Profile API (complete) → Job API (complete) → Generation API (Sprint 2) → Document API (Sprint 2)
```

## Testing Patterns

### Backend Testing
```python
# Async test with DB session
@pytest.mark.asyncio
async def test_create_profile(db_session, auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/profiles", json=data, headers=auth_headers)
        assert response.status_code == 201

# Test markers
@pytest.mark.unit       # Domain logic tests
@pytest.mark.integration # Repository tests
@pytest.mark.slow       # Long-running tests
@pytest.mark.ai         # LLM integration tests
```

### Mobile Testing
- **Current**: 46 backend unit tests passing, 0 mobile tests
- **Priority**: Add `ProfileNotifier` state transition tests
- **Pattern**: Mock API clients, test state changes

## File Locations Reference

### Key Documentation
- `README.md` - Sprint progress, architecture overview
- `CLAUDE.md` - Detailed development commands, architecture deep-dive
- `docs/BACKEND_DESIGN_DOCUMENT.md` - Complete backend specification
- `.context/mobile-developer-summary.md` - Mobile implementation status
- `docs/mobile/*.md` - Feature design documents (auth, profile, jobs, etc.)

### Backend Structure
- `app/domain/` - Entities, value objects, port interfaces (NO external deps)
- `app/application/services/` - Business logic orchestration
- `app/infrastructure/repositories/` - SQLAlchemy implementations
- `app/infrastructure/adapters/` - LLM/PDF/storage adapters (STUB CLASSES ONLY)
- `app/presentation/api/` - FastAPI routers
- `tests/conftest.py` - Test fixtures (db_session, auth_headers, async_client)

### Mobile Structure
- `lib/providers/` - Riverpod StateNotifiers (auth, profile, job)
- `lib/services/api/` - API clients (auth_api_client, profiles_api_client, jobs_api_client)
- `lib/models/` - Data classes with copyWith (user, profile, job)
- `lib/screens/` - UI screens (flat structure, no feature folders)
- `lib/widgets/` - Reusable components (cards, dialogs)

## When Adding New Features

### Backend Endpoint
1. Define Pydantic DTOs in `application/dtos/`
2. Create/update domain entity in `domain/entities/`
3. Update repository in `infrastructure/repositories/`
4. Create service in `application/services/` if complex logic
5. Add API route in `presentation/api/`
6. Write tests in `tests/` with appropriate markers

### Mobile Screen
1. Create data models in `models/` with copyWith
2. Add API client methods in `services/api/`
3. Create StateNotifier in `providers/`
4. Build screen in `screens/` using ConsumerWidget
5. Add route in `app.dart` GoRouter
6. Create reusable widgets in `widgets/` if needed

## Performance Targets
- CRUD operations: <200ms
- Resume generation: <6s (5-stage pipeline)
- PDF export: <2s
- Job search: <2s

## Current Sprint Context
**Sprint 3 (Nov 2025)**: Job browsing mobile UI implementation complete. 9 files created (models, API client, provider, widgets, screens). Navigation routes added. **Next**: Integration testing with backend, implement job edit screen.

**Test Coverage**: 133 backend tests passing (45.78%), 0 mobile tests. Target: 80%+ coverage.

**Known Technical Debt**: Add mobile unit tests, implement offline caching, complete Generation/Document API implementations.
