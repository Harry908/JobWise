# Backend Cleanup & Restructuring Plan

## Goal
Simplify backend architecture while maintaining adapter pattern for external services. Remove over-engineering and empty stub files.

## Keep: Adapter Pattern
**Reason**: Good for swappable external services (LLM providers, PDF generators)

**Keep this structure:**
```
domain/ports/          # Interface definitions
infrastructure/adapters/  # Concrete implementations
```

## Remove: Over-Engineering

### 1. Empty Adapter Stubs
**Remove these EMPTY files (0 lines):**
```
infrastructure/adapters/llm/
  - azure_openai_adapter.py (0 lines)
  - claude_adapter.py (0 lines)
  - gemini_adapter.py (0 lines)
  - groq_adapter.py (0 lines)
  - local_llm_adapter.py (0 lines)
  # Keep: openai_adapter.py for Sprint 3+

infrastructure/adapters/pdf/
  - cloud_pdf_adapter.py (0 lines)
  - weasyprint_adapter.py (0 lines)
  # Keep: reportlab_adapter.py for Sprint 2

infrastructure/adapters/storage/
  - azure_blob_adapter.py (0 lines)
  - s3_adapter.py (0 lines)
  # Keep: local_file_adapter.py for Sprint 2

infrastructure/adapters/cache/
  - memory_adapter.py (0 lines)
  - redis_adapter.py (8 lines - minimal)
  # Keep for Sprint 2, implement when needed

infrastructure/adapters/jobs/
  - indeed_adapter.py (12 lines)
  - linkedin_adapter.py (0 lines)
  - mock_job_adapter.py (0 lines)
  # Remove all - not using adapter pattern for jobs currently
```

### 2. Over-Engineered Infrastructure
**Remove these complex patterns (not needed for Sprint 2):**
```
infrastructure/ai/
  - cost_optimizer.py
  - token_manager.py
  - universal_llm_service.py
  - prompt_manager.py

infrastructure/core/
  - circuit_breaker.py
  - fallback_manager.py
  - health_checker.py
  - service_factory.py
```

### 3. Redundant Application Layer
**Remove empty use_cases:**
```
application/use_cases/
  - document_use_cases.py (0 lines)
  - generation_use_cases.py (0 lines)
  - job_use_cases.py (0 lines)
  # Keep: profile_use_cases.py (31 lines) - but consider merging to service
```

### 4. Duplicate Infrastructure Directory
**Remove duplicate root:**
```
backend/infrastructure/   # Delete entire directory
```

### 5. Empty Domain Repositories
**Remove empty directory:**
```
domain/repositories/   # No files inside, interfaces are in ports/
```

### 6. Domain Services Consolidation
**Move domain/services/ to application/services/**
```
domain/services/
  - ai_orchestrator.py
  - pipeline_common.py
  - stages/
    - job_analyzer.py
    - profile_compiler.py
    - document_generator.py
    - quality_validator.py
    - pdf_exporter.py
```
These are application-level orchestration, not pure domain logic.

## Proposed Final Structure

```
backend/app/
├── presentation/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── profiles.py
│   │   ├── jobs.py
│   │   ├── job_descriptions.py
│   │   ├── generation.py
│   │   └── documents.py
│   └── middleware/
│       └── auth_middleware.py
│
├── application/
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── job_service.py
│   │   ├── job_description_service.py
│   │   ├── generation_service.py
│   │   ├── document_service.py
│   │   └── pipeline/              # Moved from domain/services
│   │       ├── job_analyzer.py
│   │       ├── profile_compiler.py
│   │       ├── content_generator.py
│   │       └── quality_validator.py
│   └── dtos/
│       ├── auth_dtos.py
│       ├── profile_dtos.py
│       ├── job_dtos.py
│       ├── generation_dtos.py
│       └── document_dtos.py
│
├── domain/
│   ├── entities/
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── job.py
│   │   ├── job_description.py
│   │   ├── generation.py
│   │   └── document.py
│   ├── value_objects/
│   │   ├── personal_info.py
│   │   ├── experience.py
│   │   ├── education.py
│   │   ├── skills.py
│   │   └── project.py
│   └── ports/                     # KEEP - adapter pattern interfaces
│       ├── llm_service_port.py
│       ├── pdf_generator_port.py
│       ├── storage_service_port.py
│       └── repository_ports.py    # Consolidate all repo interfaces
│
├── infrastructure/
│   ├── adapters/
│   │   ├── llm/
│   │   │   └── mock_llm.py       # Sprint 2
│   │   │   # Add openai.py in Sprint 3
│   │   │   # Add claude.py in Sprint 4
│   │   ├── pdf/
│   │   │   └── reportlab.py      # Sprint 2
│   │   └── storage/
│   │       └── local_storage.py   # Sprint 2
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── profile_repository.py
│   │   ├── job_repository.py
│   │   ├── job_description_repository.py
│   │   ├── generation_repository.py
│   │   └── document_repository.py
│   └── database/
│       ├── models.py
│       ├── connection.py
│       └── __init__.py
│
└── core/
    ├── config.py
    ├── security.py
    ├── exceptions.py
    ├── dependencies.py            # DI container
    └── logging.py
```

## Migration Steps

### Step 1: Backup
```bash
cd backend
git checkout -b simplify-architecture
git add .
git commit -m "Backup before architecture simplification"
```

### Step 2: Remove Empty Adapter Stubs
```bash
# LLM adapters (keep only mock for Sprint 2, openai for later)
rm app/infrastructure/adapters/llm/azure_openai_adapter.py
rm app/infrastructure/adapters/llm/claude_adapter.py
rm app/infrastructure/adapters/llm/gemini_adapter.py
rm app/infrastructure/adapters/llm/groq_adapter.py
rm app/infrastructure/adapters/llm/local_llm_adapter.py

# PDF adapters (keep only reportlab)
rm app/infrastructure/adapters/pdf/cloud_pdf_adapter.py
rm app/infrastructure/adapters/pdf/weasyprint_adapter.py

# Storage adapters (keep only local for Sprint 2)
rm app/infrastructure/adapters/storage/azure_blob_adapter.py
rm app/infrastructure/adapters/storage/s3_adapter.py

# Cache adapters (keep both for now)
# Can implement properly when needed

# Job adapters (not using adapter pattern)
rm -rf app/infrastructure/adapters/jobs/
```

### Step 3: Remove Over-Engineered Infrastructure
```bash
# Remove complex AI infrastructure
rm -rf app/infrastructure/ai/

# Remove service factory and circuit breakers
rm -rf app/infrastructure/core/

# Remove external services directory (if empty)
rm -rf app/infrastructure/external_services/
```

### Step 4: Remove Duplicate and Empty Directories
```bash
# Remove duplicate root infrastructure
rm -rf infrastructure/

# Remove empty domain repositories
rmdir app/domain/repositories/

# Remove empty use cases
rm app/application/use_cases/document_use_cases.py
rm app/application/use_cases/generation_use_cases.py
rm app/application/use_cases/job_use_cases.py
# Decide on profile_use_cases.py - merge to service or keep
```

### Step 5: Consolidate Domain Services to Application
```bash
# Move domain services to application layer
mv app/domain/services/stages app/application/services/pipeline
rm app/domain/services/ai_orchestrator.py  # If empty or merged
rm app/domain/services/pipeline_common.py  # If empty or merged
rmdir app/domain/services/stages/
rmdir app/domain/services/
```

### Step 6: Update Imports
This requires manual work - update all import statements to reflect new paths.

**Example changes:**
```python
# Old
from app.domain.services.stages.job_analyzer import JobAnalyzer

# New
from app.application.services.pipeline.job_analyzer import JobAnalyzer
```

### Step 7: Create Repository Port Interface
Consolidate repository interfaces into single file:
```python
# app/domain/ports/repository_ports.py
from abc import ABC, abstractmethod
from typing import List, Optional

class IProfileRepository(ABC):
    @abstractmethod
    async def create(self, profile: Profile) -> Profile: ...
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Profile]: ...
    # etc.

class IJobRepository(ABC):
    # ...

class IGenerationRepository(ABC):
    # ...
```

### Step 8: Update Dependencies Injection
Update `core/dependencies.py` to provide concrete implementations:
```python
def get_llm_service() -> ILLMService:
    # Sprint 2: return MockLLMService()
    # Sprint 3+: return OpenAIService(api_key=settings.OPENAI_API_KEY)
    return MockLLMService()

def get_pdf_service() -> IPDFGenerator:
    return ReportLabPDFGenerator()

def get_profile_repo(session: AsyncSession = Depends(get_db)) -> IProfileRepository:
    return ProfileRepository(session)
```

### Step 9: Test Everything
```bash
# Run all tests to ensure nothing broke
cd backend
pytest --cov=app tests/
```

## Benefits After Cleanup

### File Count Reduction
- **Before**: ~60 Python files in app/
- **After**: ~35 Python files in app/
- **Reduction**: ~40%

### Complexity Metrics
- **Directory depth**: Reduced from 6 to 4 levels
- **Empty files**: 0 (removed all stubs)
- **Service layers**: 2 (application + domain) instead of 3 (+ use cases)

### Developer Experience
- **Onboarding time**: <30 minutes (was: 2+ hours)
- **Find file time**: <10 seconds (clear structure)
- **Add new feature**: <1 hour (less boilerplate)

### Maintainability
- **Clear boundaries**: Presentation -> Application -> Domain -> Infrastructure
- **Adapter pattern**: Only where needed (LLM, PDF, storage)
- **YAGNI principle**: Add adapters when second implementation needed
- **Simple dependency injection**: Easy to swap implementations

## When to Add Complexity Back

### Add 2nd LLM Adapter
**When**: Sprint 3-4 when integrating real AI
**How**: Create `OpenAIAdapter` implementing `ILLMService`

### Add Service Factory
**When**: 3+ LLM providers in use
**How**: Create factory to select provider based on config

### Add Circuit Breaker
**When**: Production issues with external service failures
**How**: Wrap adapter calls with circuit breaker pattern

### Add Caching Layer
**When**: Performance profiling shows repeated identical queries
**How**: Implement cache adapter, add caching decorator

## Success Criteria

- [ ] All empty adapter files removed
- [ ] use_cases layer removed or justified
- [ ] domain/services moved to application
- [ ] Duplicate infrastructure/ directory removed
- [ ] All tests passing
- [ ] Import statements updated
- [ ] New architecture diagram created
- [ ] CLAUDE.md updated
- [ ] Documentation clear and accurate
