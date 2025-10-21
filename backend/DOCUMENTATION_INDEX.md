# JobWise Backend - Documentation Index

**Project**: JobWise AI-Powered Job Application Assistant
**Component**: Backend API Service
**Last Updated**: October 20, 2025

---

## Quick Start

**New to the project?** Start here:
1. Read [BACKEND_DESIGN_DOCUMENT.md](./BACKEND_DESIGN_DOCUMENT.md) for system overview
2. Check [README.md](./README.md) for setup instructions
3. Review [SIMPLIFIED_ARCHITECTURE.puml](./SIMPLIFIED_ARCHITECTURE.puml) for architecture diagram

**Developer onboarding?**
1. [Setup Guide](./README.md#setup)
2. [Development Commands](./README.md#common-commands)
3. [Testing Guide](./TESTING_EXAMPLES.md)

---

## Core Documentation

### Design & Architecture

**[BACKEND_DESIGN_DOCUMENT.md](./BACKEND_DESIGN_DOCUMENT.md)** (Primary Reference)
- Complete system design document
- Architecture patterns (Clean Architecture + Adapter Pattern)
- Database design with ERD reference
- API structure and endpoints
- Security model
- Data flow & sequence diagrams
- Design patterns explanation
- Technology stack
- Testing strategy
- Deployment architecture

**[SIMPLIFIED_ARCHITECTURE.puml](./SIMPLIFIED_ARCHITECTURE.puml)**
- Consolidated architecture diagram (PlantUML)
- Replaces 3 previous diagrams
- Shows actual implementation (not theoretical)
- Layer responsibilities clearly defined
- Dependency injection flow
- Current Sprint 2 scope

**[diagrams/sequence-diagrams.puml](./diagrams/sequence-diagrams.puml)**
- User authentication flow
- Resume generation flow (5-stage pipeline)
- PDF export flow
- Complete user journey workflow

---

## Database Documentation

**[.context/diagrams/backend/database-schema-erd.puml](../.context/diagrams/backend/database-schema-erd.puml)**
- Complete entity relationship diagram
- All tables with fields and types
- Relationship cardinality
- Indexes and constraints
- Implementation notes

**Database Models**:
- Source code: `app/infrastructure/database/models.py`
- Repositories: `app/infrastructure/repositories/`

---

## Implementation Guides

### API Implementation

**[FEATURE_IMPLEMENTATION_PLAN_CLEAN.md](./FEATURE_IMPLEMENTATION_PLAN_CLEAN.md)**
- API-by-API implementation roadmap
- Sprint 1 completed features
- Sprint 2 current focus (Generation + Document APIs)
- Future sprints planning
- API service boundaries
- Quality targets

### Testing

**[TESTING_EXAMPLES.md](./TESTING_EXAMPLES.md)**
- Pytest examples
- Test markers and organization
- Async testing patterns
- API testing with fixtures
- Coverage reports

**[pyproject.toml](./pyproject.toml)**
- pytest configuration
- Test markers definition
- Coverage settings
- Code quality tools config

---

## Architecture Simplification (Recent)

**[ARCHITECTURE_ANALYSIS.md](./ARCHITECTURE_ANALYSIS.md)**
- Analysis of over-engineering issues
- What was wrong with old architecture
- Comparison: old vs new structure
- Recommendations for simplification

**[CLEANUP_PLAN.md](./CLEANUP_PLAN.md)**
- Step-by-step cleanup strategy
- What to keep vs remove
- When to add complexity back
- Migration guide

**[CLEANUP_EXECUTION_SUMMARY.md](./CLEANUP_EXECUTION_SUMMARY.md)**
- Results of cleanup execution
- 26 files removed (40% reduction)
- Test results (125 passing)
- Impact analysis

**[cleanup-architecture.ps1](./cleanup-architecture.ps1)**
- Automated cleanup script
- PowerShell automation
- Dry-run support

**[ARCHITECTURE_SIMPLIFICATION_SUMMARY.md](./ARCHITECTURE_SIMPLIFICATION_SUMMARY.md)**
- Executive summary of changes
- Benefits and metrics
- How to execute
- Q&A section

---

## Development Resources

### Setup & Configuration

**[README.md](./README.md)**
- Project overview
- Environment setup
- Running the server
- Common commands
- Testing instructions

**[SERVER_STARTUP_README.md](./SERVER_STARTUP_README.md)**
- Detailed server startup guide
- Troubleshooting
- Environment validation

**[.env.example](./.env.example)**
- Environment variables template
- Configuration options
- Security settings

### Scripts

**[start-server.bat](./start-server.bat)**
- Windows batch script to start server
- Automatic environment activation
- Health check instructions

**[start_server.py](./start_server.py)**
- Python server launcher
- Environment validation
- Database initialization

**[init_database.py](./init_database.py)**
- Database initialization script
- Create tables
- Seed initial data

---

## API Reference

### OpenAPI Documentation

**Live Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc (if enabled)
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

### Endpoint Documentation

All endpoints documented in [BACKEND_DESIGN_DOCUMENT.md](./BACKEND_DESIGN_DOCUMENT.md#42-api-endpoints-by-service):
- Authentication API (`/api/v1/auth/`)
- Profile API (`/api/v1/profiles/`)
- Job API (`/api/v1/jobs/`)
- Generation API (`/api/v1/generations/`) - Sprint 2
- Document API (`/api/v1/documents/`) - Sprint 2

---

## Diagrams

### PlantUML Diagrams

All diagrams are in PlantUML format (`.puml`). To render:

**Online**: https://www.plantuml.com/plantuml/uml/
- Copy diagram source code
- Paste into online editor

**VS Code**:
- Install "PlantUML" extension
- Press `Alt+D` to preview

**CLI**:
```bash
plantuml backend/SIMPLIFIED_ARCHITECTURE.puml
```

### Available Diagrams

1. **System Architecture** (`SIMPLIFIED_ARCHITECTURE.puml`)
   - Clean architecture layers
   - Adapter pattern implementation
   - Dependency flow

2. **Database ERD** (`.context/diagrams/backend/database-schema-erd.puml`)
   - All entities and relationships
   - Field definitions
   - Constraints and indexes

3. **Sequence Diagrams** (`diagrams/sequence-diagrams.puml`)
   - Authentication flow
   - Resume generation pipeline
   - PDF export process
   - Complete user journey

---

## Context Documentation

**[.context/](../.context/)**
- Project context for AI assistants
- API specifications
- Architecture diagrams
- Development summaries

**Root Documentation**:
- [CLAUDE.md](../CLAUDE.md) - AI assistant guidance
- [README.md](../README.md) - Project overview

---

## Code Organization

```
backend/
├── app/                        # Application source code
│   ├── presentation/api/       # API endpoints (routers)
│   ├── application/            # Services & DTOs
│   ├── domain/                 # Entities, value objects, ports
│   ├── infrastructure/         # Adapters, repositories, database
│   └── core/                   # Config, security, exceptions
│
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── alembic/                    # Database migrations (future)
├── data/                       # Seed data & fixtures
├── scripts/                    # Utility scripts
└── docs/                       # Additional documentation
```

---

## Sprint Documentation

### Current Sprint (Sprint 2)

**[docs/sprint2/sprint2-plan.md](../docs/sprint2/sprint2-plan.md)**
- Detailed Sprint 2 plan
- 40-hour breakdown
- Task organization
- Success criteria
- Risk assessment

### Feature Status

**Completed (Sprint 1)**:
- ✅ Authentication System
- ✅ Profile Management API
- ✅ Job Description API

**In Progress (Sprint 2)**:
- 🚧 Generation API (Mock pipeline)
- 🚧 Document Export API (PDF)

**Planned (Sprint 3+)**:
- ⏳ Real LLM integration
- ⏳ Flutter mobile app
- ⏳ Advanced features

---

## How to Use This Documentation

### For New Developers

1. **Week 1**: Read BACKEND_DESIGN_DOCUMENT.md
2. **Week 2**: Set up environment (README.md)
3. **Week 3**: Explore codebase, run tests
4. **Week 4**: Start contributing

### For Architects

- Review SIMPLIFIED_ARCHITECTURE.puml
- Read ARCHITECTURE_ANALYSIS.md
- Check design patterns in BACKEND_DESIGN_DOCUMENT.md

### For API Consumers

- Swagger UI: http://localhost:8000/docs
- API reference in BACKEND_DESIGN_DOCUMENT.md
- Sequence diagrams for workflows

### For QA Engineers

- TESTING_EXAMPLES.md for test patterns
- pyproject.toml for test configuration
- Run: `pytest --cov=app tests/`

---

## Documentation Maintenance

### Update Frequency

- **BACKEND_DESIGN_DOCUMENT.md**: After each sprint
- **Architecture diagrams**: When structure changes
- **API documentation**: When endpoints added/modified
- **Test documentation**: When test strategy changes

### Contributors

This documentation is maintained by the backend development team. Updates should be reviewed during sprint retrospectives.

### Feedback

For documentation improvements, create an issue or submit a PR.

---

## Quick Reference Cards

### Start Development

```powershell
cd backend
.\venv\Scripts\Activate.ps1
.\start-server.bat
```

### Run Tests

```powershell
pytest --cov=app -v
```

### View API Docs

```
http://localhost:8000/docs
```

### Common Patterns

```python
# Service with dependency injection
def get_service(repo: IRepo = Depends(get_repo)) -> Service:
    return Service(repo)

# Protected endpoint
@router.get("/resource")
async def get_resource(user: User = Depends(get_current_user)):
    pass

# Async repository
async def create(self, entity: Entity) -> Entity:
    db_entity = DBModel(**entity.dict())
    self.session.add(db_entity)
    await self.session.commit()
    return entity
```

---

## Version History

- **v1.0** (Oct 20, 2025) - Initial comprehensive documentation
  - Backend design document created
  - Architecture simplified (40% file reduction)
  - Sequence diagrams added
  - Documentation index created

---

**Maintained By**: Backend Development Team
**Contact**: See project README
**License**: Educational Use (CptS 483 Project)
