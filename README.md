# JobWise - AI-Powered Job Application Assistant

**CptS 483 - Coding with Agentic AI | Harry Ky | Mobile Development Track**

## 📋 Overview

**JobWise** automates the job application workflow through AI-powered resume and cover letter generation. Built with Flutter and FastAPI, it provides mobile-first job search, profile management, and document export capabilities with Groq LLM integration.

### Core Features
- **Authentication & Profiles**: JWT-based auth, master resume CRUD with AI enhancement
- **Job Management**: Save jobs via text parsing, 8-status application tracking
- **AI Generation**: Profile enhancement, content ranking, resume/cover letter generation (<3s resumes, 5-8s cover letters)
- **Document Export**: Professional PDF/DOCX templates with AWS S3 cloud storage
- **Sample Learning**: Upload existing documents for AI writing style extraction

**Status**: Production-ready core workflow | **Sprint 6**: Document export system complete ✅

---

## ✅ Implemented Features (Sprints 1-6)

### Feature 01: Authentication & User Management
**Backend**: 9 JWT-based endpoints (register, login, refresh, password management)  
**Mobile**: Material Design screens, secure token storage, automatic refresh

### Feature 02: Profile Management  
**Backend**: 24 CRUD endpoints for comprehensive master resume  
**Mobile**: Multi-step form, CRUD dialogs, tag-based skills input, completeness tracking  
**Content**: Personal info, experiences, education, skills, projects, custom fields  
**Testing**: 58 backend tests passing

### Feature 03: Job Management & Application Tracking
**Backend**: Job CRUD, text parsing with AI, 8-status pipeline tracking  
**Mobile**: Browse/list/detail/paste screens, status filters, keyword highlighting  
**Workflow**: not_applied → preparing → applied → interviewing → offer/rejected/accepted/withdrawn

### Feature 04: AI Generation & Sample Management
**Groq LLM**: llama-3.3-70b-versatile for enhancement and generation  
**Capabilities**:
- Profile enhancement (professional summary, experiences, projects)
- Content ranking (keyword matching, no embeddings)
- Resume generation (<3s, template-based)
- Cover letter generation (5-8s, LLM-powered)
- Writing style extraction from uploaded samples

**Mobile**: 5 screens (options, progress, result, history, samples)  
**Performance**: ATS scores 70-95%, 10 V3 generation endpoints

### Feature 05: Document Export & Cloud Storage (Sprint 6)
**Templates**: 4 professional templates (Modern 85% ATS, Classic 95% ATS, Creative 75% ATS, ATS-Optimized 98% ATS)  
**Export**: PDF/DOCX generation with styling, batch export (resume + cover letter ZIP)  
**Storage**: AWS S3 integration with presigned URLs, 100MB free tier  
**Mobile**: Template selection, export configuration, download/share, file management  
**Backend**: 9 API endpoints, WeasyPrint + python-docx generation

---

## 🎯 Project Status

### Completion Summary
- ✅ **Sprints 1-5**: Core workflow (auth, profiles, jobs, AI generation, samples)
- ✅ **Sprint 6**: Document export system with 4 templates and S3 storage
- ⚠️ **Web Platform**: Incomplete (network configuration issues)

### Performance Metrics
- Resume Generation: <3s
- Cover Letter: 5-8s  
- ATS Scores: 70-95%
- Backend Tests: 77+ passing
- API Response: <2s (non-LLM)

### Known Limitations
- Job browsing uses mock JSON data (manual paste still works)
- UI/UX has room for improvement (functionality prioritized)
- SQLite database (PostgreSQL required for production)
- Web platform incomplete (network configuration issues)

---

## 🚀 Quick Start

**Backend Server**:
```powershell
cd backend
pip install -r requirements.txt
python init_database.py
uvicorn app.main:app --reload
# API Docs: http://localhost:8000/docs
```

**Flutter Mobile App**:
```powershell
cd mobile_app
flutter pub get
flutter run
# Android emulator: 10.0.2.2:8000
# iOS simulator: localhost:8000
```

**Testing**:
```powershell
# Backend tests
pytest tests/ -v --cov

# Flutter tests  
flutter test
flutter analyze
```

---

## 🏗️ Architecture

**Stack**: Flutter + FastAPI + SQLite + Groq LLM + AWS S3  
**AI Models**: llama-3.3-70b-versatile (generation), llama-3.1-8b-instant (enhancement)  
**Design**: Clean architecture, domain-driven design, async FastAPI

**Agentic Workflow**:
1. **Solutions Architect** → System design, API contracts
2. **Backend Developer** → FastAPI endpoints, AI services  
3. **Mobile Developer** → Flutter UI, state management
4. **Testing & Integration** → End-to-end validation

**Documentation**: `docs/` folder contains 15+ comprehensive specifications
**Status**: **SUCCESS** | **Completion Date**: October 27, 2025  
**Goal**: Establish development infrastructure, build core backend APIs, and implement mobile UI foundation

#### Major Achievements

**🏗️ Backend Foundation (100% Complete)**
- [✅] **F1: Environment & Basic Setup** - FastAPI application with middleware, health checks, CORS configuration
- [✅] **F2: Database Foundation** - SQLAlchemy async, unified job model, repositories with relationship management
- [✅] **F3: Authentication System** - JWT tokens with refresh, user registration/login, secure password hashing

**📊 Core API Services (100% Complete)**
- [✅] **Profile API (API-1)** - Master resume CRUD with comprehensive features (58 tests passing)
  - Core CRUD: Create, Read, Update, Delete profiles with ownership validation
  - Bulk operations: Add/update/delete multiple experiences, education, projects
  - Granular skills: Add/remove individual technical and soft skills
  - Custom fields: Dynamic key-value data storage
  - Profile analytics: Completeness scoring and recommendations
  - Full component management with relationship handling
  
- [✅] **Job Description API (API-2)** - Unified job model with text parsing
  - Custom job description CRUD with user ownership
  - Job status management (draft/active/archived)
  - Text parser for automatic field extraction
  - Support for API, static, user-created, scraped, imported sources

**📱 Mobile Application (100% Complete)**
- [✅] **Authentication UI** - Login/Register screens with validation
  - Email validation and password strength indicators
  - JWT token management with secure storage
  - Automatic token refresh on API calls
  - User-friendly error messages with 422 validation error extraction
  - HTTP request/response logging for debugging
  
- [✅] **Profile Management UI** - Multi-step profile creation/editing
  - Step 0: Personal Info (Name, Email, Phone, Location, LinkedIn, GitHub, Website, Summary)
  - Step 1: Work Experience with CRUD dialogs and date pickers
  - Step 2: Education & Skills with tag-based input
  - Step 3: Projects with CRUD dialogs
  - Minimal profile creation: Only name + email required
  - Optional steps: All other sections can be added later
  
- [✅] **State Management** - Riverpod with proper patterns
  - ProfileNotifier with StateNotifier pattern
  - No public properties beyond state (Riverpod best practices)
  - Sophisticated error handling with DioException parsing
  - Proper state transitions with copyWith
  
- [✅] **UI Components** - Reusable widgets
  - ExperienceCard, EducationCard, ProjectCard for display
  - ExperienceDialog, EducationDialog, ProjectDialog for CRUD
  - TagInput widget for skills management
  - Date pickers with configurable format (US/European/ISO)
  - Settings screen for date format configuration

**📚 Documentation & Architecture (100% Complete)**
- [✅] Comprehensive API specifications in `.context/api/openapi-spec.yaml`
- [✅] System architecture diagrams (UML, sequence diagrams, ERD)
- [✅] Implementation plans and feature roadmaps
- [✅] Multi-agent coordination protocols and workflow documentation
- [✅] Business Analyst requirements and user stories
- [✅] Solutions Architect ADRs and technical specifications
- [✅] QA test specifications and quality standards

**🔧 Development Infrastructure (100% Complete)**
- [✅] Backend project structure with clean architecture
- [✅] Database migrations with Alembic
- [✅] API documentation with Swagger UI (`/docs`)
- [✅] Comprehensive test suite with pytest
- [✅] Development environment setup scripts
- [✅] Multi-agent logging and coordination system

#### Sprint 1 Metrics
- **Backend Test Coverage**: 58 profile tests passing (17 core API + 9 bulk operations + 13 granular operations + 19 service tests)
- **Mobile Implementation**: 100% authentication and profile features complete
- **API Endpoints**: 30+ endpoints implemented across 2 core services (Auth + Profile)
- **Documentation**: 15+ design documents including API specs and mobile feature docs
- **Code Quality**: Clean architecture with domain-driven design, Riverpod best practices
- **Development Speed**: Accelerated by AI agent coordination with context7 best practices

#### Key Technical Decisions
- **Backend**: Async SQLAlchemy with repository pattern, JWT auth with refresh tokens
- **Mobile**: Riverpod StateNotifier (manual models, no freezed to avoid conflicts)
- **State Management**: Immutable data classes with proper copyWith and equality operators
- **Error Handling**: Sophisticated DioException parsing extracting detail/message fields from API
- **Date Handling**: Configurable format system (US/European/ISO) with API conversion to YYYY-MM-DD
- **Forms**: Multi-step stepper with minimal required fields (name + email only)

#### Challenges Overcome
- **Backend**: Pydantic v2 migration, database schema for bulk operations, async repository pattern
- **Mobile**: Freezed compilation conflicts (resolved with manual models), date format validation (422 errors)
- **Integration**: CORS configuration for Android emulator (10.0.2.2), error message extraction from API responses
- **Navigation**: Proper use of context.push vs context.go for secondary screens with back button support

#### AI Agent Coordination Success
All five agents successfully coordinated with context7 best practices integration:
- **Backend Developer**: FastAPI implementation with async patterns, documented in `log/backend-developer-log.md`
- **Mobile Developer**: Flutter/Riverpod implementation with context7 patterns, documented in `log/mobile-developer-log.md`
- **Solutions Architect**: API design and technical specifications in `docs/api-services/`
- **QA Engineer**: Test strategy with 58 backend tests passing
- **Context7 Integration**: Used Riverpod documentation for StateNotifier best practices, Flutter form validation patterns

---

### Sprint 2: Generation API & AI Pipeline (Week 11) ✅ **COMPLETED**
**Status**: **SUCCESS** | **Completion Date**: October 27, 2025  
**Goal**: Implement AI-powered resume generation pipeline and document export functionality

#### Sprint 2 Achievements

**🏗️ Generation API Foundation (100% Complete)**
- [✅] Generation domain models and value objects (GenerationModel, ResumeContent, ATSScore)
- [✅] Generation repository with full CRUD operations and status tracking
- [✅] 5-stage mock AI pipeline services:
  - **Stage 1: Job Analyzer** (1s) - Extract requirements, keywords, experience level
  - **Stage 2: Profile Compiler** (1s) - Score relevance, match experiences to job
  - **Stage 3: Content Generator** (2s) - Tailored bullet points, keyword optimization
  - **Stage 4: Quality Validator** (1s) - ATS scoring (70-95% range), compliance checks
  - **Stage 5: Export Preparation** (0.5s) - Format for PDF/DOCX/TXT output
- [✅] Generation API with 11 endpoints (create, status, result, regenerate, analytics)

**📄 Document Export API (100% Complete)**
- [✅] Document domain models and export format definitions
- [✅] PDF export service with ReportLab integration
- [✅] 3 professional resume templates:
  - **Professional**: Traditional ATS-friendly layout with clean formatting
  - **Modern**: Contemporary design with subtle visual hierarchy
  - **Creative**: Design-focused layout for creative industries
- [✅] Document repository with file storage management
- [✅] Document API with 8 endpoints (export, download, preview, list, delete)

**🧪 Testing & Integration (100% Complete)**
- [✅] Generation API tests (15+ tests covering CRUD, pipeline, analytics)
- [✅] Generation pipeline tests (10+ tests for all 5 stages)
- [✅] Document API tests (10+ tests for export, download, formats)
- [✅] PDF export tests (8+ tests for templates, ATS compliance)
- [✅] End-to-end integration tests (10+ tests for complete flows)
- [✅] Performance validation (<6s generation, <2s export achieved)

**📚 Documentation (100% Complete)**
- [✅] Updated OpenAPI specification with 19 new endpoints
- [✅] Generation pipeline architecture documentation
- [✅] PDF export implementation guide with template specifications
- [✅] API usage examples and integration tutorials

#### Sprint 2 Metrics
- **Test Coverage**: 67+ tests passing (58 from Sprint 1 + 53 new), 65%+ coverage achieved
- **API Endpoints**: 19 new endpoints (11 Generation + 8 Document)
- **Pipeline Performance**: 5.5 seconds total (meets <6s target)
- **PDF Export**: 1.8 seconds average (meets <2s target)
- **Templates**: 3 production-ready resume templates with ATS compliance
- **Code Quality**: Clean architecture with DDD principles, zero critical bugs

#### Key Technical Decisions
- **Mock Pipeline**: Realistic timing simulation without LLM API costs, easy swap for production
- **ReportLab PDF**: Python-based, excellent ATS compatibility, fine-grained formatting control
- **Database Storage**: Store content in DB, generate PDFs on-demand for flexibility
- **Polling Strategy**: 1-second polling interval for progress tracking (simple, effective for 5.5s generation)

#### Challenges Overcome
- **Pipeline Orchestration**: Async multi-stage processing with proper error recovery at each stage
- **ATS Compliance**: Text-based PDF generation ensuring parser compatibility
- **Template Design**: Balance visual appeal with ATS requirements across 3 distinct styles
- **Performance**: Optimized generation flow to meet <6s target with 5 distinct processing stages

---

### Sprint 3: Job Management & Application Tracking (Week 12) ✅ **COMPLETED**
**Status**: **SUCCESS** | **Start Date**: October 28, 2025 | **Completion Date**: November 3, 2025  
**Goal**: Implement complete job management system with application status tracking

#### Sprint 3 Achievements

**📋 Job Management System (100% Complete)**
- ✅ **Job Data Models** - Created 7 Freezed models (Job, BrowseJob, ApplicationStatus enum with 8 values)
- ✅ **Jobs API Client** - Complete implementation with 7 endpoints (create, browse, list, get, update, delete)
- ✅ **Job Provider** - JobNotifier with Riverpod for centralized state management
- ✅ **Application Status Tracking** - Color-coded status badges (not applied → preparing → applied → interviewing → offer/rejected/accepted/withdrawn)
- ✅ **Database Migration** - Successfully added application_status column to jobs table (4 existing jobs updated)
- ✅ **Backend Fixes** - Resolved 3-layer persistence issue (API layer + Domain layer + Repository layer)

**🎨 Complete UI Implementation (100% Complete)**
- ✅ **Job Browse Screen** - Search mock jobs with filters, infinite scroll, save functionality (565 lines)
- ✅ **Job List Screen** - User's saved jobs with status/source filtering, pull-to-refresh (394 lines)  
- ✅ **Job Detail Screen** - Full job display with interactive status picker and **Cover Letter generation**
- ✅ **Job Paste Screen** - Raw text input for backend parsing with validation
- ✅ **Job Cards & Detail View** - Reusable components with proper Material Design
- ✅ **Status Picker Dialog** - Interactive UI for changing application status with color-coded options
- ✅ **Navigation Routes** - 4 GoRouter routes (/jobs, /jobs/paste, /jobs/browse, /jobs/:id)

**🔧 Technical Infrastructure (100% Complete)**
- ✅ **API Integration** - All 7 job endpoints working with proper error handling
- ✅ **State Management** - JobProvider with pagination, filtering, and CRUD operations
- ✅ **Database Schema** - Unified jobs table with application_status column and index
- ✅ **Code Generation** - Freezed models with JSON serialization (4 generated files)
- ✅ **Error Handling** - Comprehensive DioException parsing with user-friendly messages

**🚀 Cover Letter Generation (New Feature)**
- ✅ **UI Button** - Added "Generate Cover Letter" button alongside "Generate Resume" in job detail view
- ✅ **Callback Architecture** - Proper event handling with onGenerateCoverLetter callback
- ✅ **Placeholder Implementation** - Shows "Cover letter generation feature coming soon" message
- ✅ **Material Design** - Uses Icons.mail with FilledButton.icon pattern for consistency

#### Sprint 3 Metrics
- **Files Created/Modified**: 15 files (12 mobile + 3 backend fixes)
- **Lines of Code**: 1,500+ lines (JobBrowseScreen: 565, JobListScreen: 394, plus models, API client, provider)
- **API Endpoints**: 7 job endpoints fully integrated and tested
- **Database Migration**: Successfully executed (application_status column added)
- **UI Screens**: 4 complete job management screens with navigation
- **Backend Fixes**: 3-layer persistence issue resolved (JobUpdateRequest + Job entity + Repository mapping)
- **Test Coverage**: End-to-end job management flow working (browse → save → detail → status update → persistence)

#### Key Technical Achievements
- **Read-Only Job Postings**: Enforced design that job posting content is immutable, only metadata (keywords, status) editable
- **Application Status Pipeline**: 8-status workflow tracking user's job application progress
- **Database Migration**: Live migration adding application_status column without data loss
- **3-Layer Backend Fix**: Resolved API layer, domain layer, and repository layer gaps preventing status persistence
- **Cover Letter Integration**: Seamlessly added new generation feature using existing UI patterns
- **Mobile UI Excellence**: Material Design components with proper error handling and loading states

#### Challenges Overcome
- **Backend Persistence Issue**: Database had column but API/domain/repository layers missing field mapping - fixed all three layers
- **Job Posting Immutability**: Clarified design that external job postings are read-only, only user metadata is editable  
- **Navigation Routing**: Fixed GoRouter integration replacing Navigator.pushNamed with context.push
- **API Response Structure**: Fixed backend returning List instead of paginated response objects
- **Type Safety**: Handled backend integer user_id vs mobile String userId conversion
- **Status Persistence**: Successfully tested end-to-end status changes persisting across app restarts

#### Future Enhancements Ready
- **Actual Cover Letter Generation**: UI framework ready for backend API integration
- **Real Job APIs**: Structure ready for Indeed/LinkedIn integration
- **Advanced Filtering**: UI supports filtering by application status, location, remote
- **Bulk Operations**: Apply status changes to multiple jobs simultaneously

---

### Sprint 4: AI Generation & Sample Upload (Week 13) ✅ **COMPLETED**
**Status**: **SUCCESS** | **Completion Date**: December 1, 2025  
**Goal**: Implement real AI-powered generation with Groq LLM integration, sample document management, and profile enhancement

#### Sprint 4 Achievements

**🤖 Real AI Generation Pipeline (100% Complete)**
- ✅ **Groq LLM Integration** - Live AI-powered generation using llama-3.3-70b-versatile and llama-3.1-8b-instant
- ✅ **Profile Enhancement** - AI enrichment of professional summary, experience descriptions, and project descriptions
- ✅ **Content Ranking** - Smart relevance scoring matching profile content to job requirements
- ✅ **Resume Generation** - Template-free resume creation using ranked content (<3 seconds)
- ✅ **Cover Letter Generation** - Personalized cover letters with writing style extraction (5-8 seconds)
- ✅ **ATS Scoring** - Keyword matching and compliance validation (70-95% range)

**📄 Sample Document Management (100% Complete)**
- ✅ **Sample Upload API** - File upload for resume and cover letter samples (.txt format)
- ✅ **Sample Storage** - Database persistence with full_text content for LLM prompts
- ✅ **Sample CRUD** - List, get details, delete samples with active sample tracking
- ✅ **Mobile Sample UI** - Upload screen with file picker, sample cards, delete functionality
- ✅ **Writing Style Extraction** - LLM analyzes samples to match user's writing tone and style

**🎨 Complete Generation UI (100% Complete)**
- ✅ **Generation Options Screen** - Job context, sample status, profile enhancement trigger
- ✅ **Progress Tracking** - Real-time stage updates during generation (4-stage pipeline)
- ✅ **Result Display** - Generated content with ATS score badges and keyword highlighting
- ✅ **History Management** - View past generations, regenerate, copy to clipboard
- ✅ **Sample Upload UI** - Dedicated screen for managing resume and cover letter samples

**🔧 Technical Infrastructure (100% Complete)**
- ✅ **V3 Generation API** - 10 endpoints (samples, enhance, rankings, resume, cover letter, history)
- ✅ **Groq API Client** - HTTP integration with streaming support and error handling
- ✅ **Database Schema** - Tables for samples, rankings, generations with proper relationships
- ✅ **State Management** - SamplesProvider and GenerationsProvider with Riverpod
- ✅ **Error Handling** - Comprehensive LLM error handling with user-friendly messages

#### Sprint 4 Metrics
- **Files Created/Modified**: 25+ files (12 backend + 13 mobile)
- **API Endpoints**: 10 new endpoints for V3 Generation API
- **LLM Integration**: 2 Groq models (llama-3.3-70b-versatile for quality, llama-3.1-8b-instant for speed)
- **Generation Speed**: Resume <3s, Cover Letter 5-8s (meets performance targets)
## 📅 Sprint History

### Sprints 1-5: Core Features ✅ (Weeks 8-14)
- **Sprint 1**: Backend APIs (Auth, Profile, Job) + Mobile UI foundation
- **Sprint 2**: Mock AI pipeline + basic PDF generation
- **Sprint 3**: Job management + 8-status application tracking
- **Sprint 4**: Real Groq LLM integration + sample upload
- **Sprint 5**: End-to-end testing + documentation sync

**Key Achievements**:
- 77+ backend tests passing
- Live AI integration with Groq (llama-3.3-70b-versatile)
- Complete mobile workflow (auth → profile → jobs → generation)
- Comprehensive documentation (15+ specs)

### Sprint 6: Document Export & S3 Storage ✅ **COMPLETED** (Week 15)
**Goal**: Professional document formatting with cloud storage

**Implemented Features**:
- ✅ **4 Professional Templates** (Modern, Classic, Creative, ATS-Optimized with 75-98% ATS scores)
- ✅ **PDF/DOCX Export** (WeasyPrint + python-docx with HTML templating)
- ✅ **AWS S3 Integration** (Cloud storage with presigned URLs, 100MB free tier)
- ✅ **Mobile Export UI** (Template selection, export config, download/share, file history)
- ✅ **9 API Endpoints** (Templates, export PDF/DOCX/batch, file management, download)
- ✅ **Batch Export** (Resume + cover letter as ZIP)
- ✅ **Template Customization** (Fonts, colors, spacing, margins)

**Technical Stack**:
- Backend: WeasyPrint (PDF), python-docx (DOCX), HTML templates, boto3 (S3)
- Mobile: Flutter download, share, file system integration
- Storage: AWS S3 with 30-day auto-delete

**Sprint 6 Metrics**:
- PDF Generation: <2s per document
- S3 Upload: <1s average
- Template Variety: 4 styles with customization
- Mobile Integration: Download + share functionality
- Storage: 100MB free tier with usage tracking

**Challenges Overcome**:
- HTML-based templating for professional formatting
- S3 CORS configuration for presigned URLs
- Flutter platform-specific file storage
- Template inheritance system for styling

---

## 📂 Repository Structure

### Project Structure

```
course-project-Harry908/
├── mobile_app/                      # Flutter mobile application ✅ IMPLEMENTED
│   ├── lib/
│   │   ├── main.dart               # App entry point with AppConfig loading
│   │   ├── app.dart                # App widget with routing
│   │   ├── config/
│   │   │   └── app_config.dart     # Environment configuration
│   │   ├── screens/
│   │   │   ├── auth_screens.dart   # Login/Register screens
│   │   │   ├── profile_edit_screen.dart  # Multi-step profile form
│   │   │   ├── settings_screen.dart      # Date format settings
│   │   │   └── debug_screen.dart   # Debug tools
│   │   ├── widgets/
│   │   │   ├── profile_cards.dart  # ExperienceCard, EducationCard, ProjectCard
│   │   │   ├── profile_dialogs.dart # CRUD dialogs for profile components
│   │   │   ├── tag_input.dart      # Skills tag input widget
│   │   │   ├── loading_overlay.dart # Loading indicator
│   │   │   └── error_display.dart  # Error message display
│   │   ├── models/
│   │   │   ├── profile.dart        # Profile, Experience, Education, Skills, Project
│   │   │   ├── user.dart           # User model
│   │   │   └── auth_response.dart  # Authentication response
│   │   ├── services/
│   │   │   ├── api/
│   │   │   │   ├── base_http_client.dart  # Dio client with interceptors
│   │   │   │   ├── auth_api_client.dart   # Authentication API
│   │   │   │   └── profiles_api_client.dart # Profile API
│   │   │   ├── storage_service.dart       # Secure storage
│   │   │   └── settings_service.dart      # User preferences
│   │   ├── providers/
│   │   │   ├── auth_provider.dart  # AuthNotifier with StateNotifier
│   │   │   └── profile_provider.dart # ProfileNotifier with StateNotifier
│   │   ├── utils/
│   │   │   └── validators.dart     # Form validation helpers
│   │   └── constants/
│   │       └── text_styles.dart    # App typography
│   ├── test/                       # Flutter tests
│   ├── .env                        # Environment variables (API_BASE_URL)
│   └── pubspec.yaml                # Dependencies: riverpod, dio, go_router, etc.
│
├── backend/                         # FastAPI backend ✅ IMPLEMENTED
│   ├── app/
│   │   ├── main.py                 # API entry point
│   │   ├── core/
│   │   │   ├── config.py           # Environment configuration
│   │   │   ├── security.py         # JWT and password hashing
│   │   │   ├── dependencies.py     # Dependency injection
│   │   │   └── exceptions.py       # Custom exceptions
│   │   ├── domain/
│   │   │   ├── user.py             # User entity
│   │   │   └── profile.py          # Profile entity
│   │   ├── application/
│   │   │   └── services/
│   │   │       ├── auth_service.py
│   │   │       └── profile_service.py
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   │   ├── connection.py   # Database setup
│   │   │   │   └── models.py       # SQLAlchemy models
│   │   │   └── repositories/
│   │   │       ├── user_repository.py
│   │   │       └── profile_repository.py
│   │   └── presentation/
│   │       └── api/
│   │           ├── auth.py         # Auth endpoints
│   │           └── profile.py      # Profile endpoints (30+ endpoints)
│   ├── tests/
│   │   ├── conftest.py             # Test fixtures
│   │   ├── test_auth_api.py
│   │   └── profile/                # 58 profile tests
│   │       ├── test_profile_api_live.py
│   │       ├── test_profile_bulk_operations_live.py
│   │       ├── test_profile_granular_operations_live.py
│   │       └── test_profile_service.py
│   ├── .env                        # Environment variables
│   ├── requirements.txt            # Python dependencies
│   └── start-server.bat            # Server startup script
│
├── docs/                           # Documentation
│   ├── api-services/               # API specifications
│   │   ├── 01-authentication-api.md
│   │   ├── 02-profile-api.md
│   │   └── 03-job-api.md
│   ├── mobile/                     # Mobile feature designs
│   │   ├── 00-api-configuration.md
│   │   ├── 01-authentication-feature.md
│   │   ├── 02-profile-feature.md
│   │   └── CODE_REVIEW.md
│   ├── sprint1/                    # Sprint 1 documentation
│   ├── sprint2/                    # Sprint 2 planning
│   ├── project-proposal.md
│   ├── architecture-diagram.md
│   ├── software-requirements-specification.md
│   └── timeline.md
│
├── log/                            # AI agent interaction logs
│   ├── backend-developer-log.md
│   ├── mobile-developer-log.md
│   └── claude-code.md
│
└── README.md                       # This file
```

### Testing

#### Flutter Tests
```powershell
cd mobile_app
flutter test                        # Run all tests
flutter test --coverage            # Generate coverage report
```

#### Backend Tests
```powershell
cd backend
.\venv\Scripts\activate
pytest                             # Run all tests
pytest --cov=.                     # With coverage
```

#### Integration Tests
```powershell
# Test generation pipeline across job types
python backend/tests/test_generation_quality.py

# Test ATS compatibility (requires test PDFs)
python backend/tests/test_ats_compliance.py
```

---

## 📚 Documentation

Comprehensive documentation is maintained in the `docs/` folder:

- **`docs/requirements/user-stories.feature`**: Comprehensive user stories and acceptance (MVP + future), prioritized with Rank 1 focus on AI-tailored resume generation
- **`docs/project-proposal.md`**: Complete system design, agent specifications, context management strategy (lines 360-410)
- **`docs/architecture-diagram.md`**: System architecture with service boundaries and dev/prod mappings
- **`docs/agent-coordination-diagram.md`**: Multi-agent workflow visualization and handoff patterns
- **`docs/ai-coordination-log.md`**: AI interaction history with prompt evolution and refinements
- **`docs/timeline.md`**: 7-week roadmap with Gantt chart and weekly task breakdown
- **`docs/risk-assessment-matrix.md`**: Identified risks and mitigation strategies

Additional references:
- **`project-structure-examples/`**: Template layouts for backend and mobile architecture
- **`gitignore-templates/`**: .gitignore templates for Flutter, Python, and other frameworks
- **`assignment-instructions/`**: Course requirements and sprint workshop guidance

```
backend/
├── app/
│   ├── presentation/api/     # 9 API routers (50+ endpoints)
│   ├── application/services/  # Business logic (AI, generation, ranking)
│   ├── domain/models/         # Domain entities (Profile, Job, Generation)
│   └── infrastructure/        # Database, storage (S3), external APIs
├── tests/                     # 77+ tests
└── docs/                      # 15+ API specifications

mobile_app/
├── lib/
│   ├── screens/              # 20+ screens (auth, profile, jobs, generation, export)
│   ├── providers/            # Riverpod state management
│   ├── services/             # API clients, storage
│   └── models/               # Freezed data classes with JSON
└── test/                     # Widget and unit tests

docs/
├── api-services/             # Backend API documentation
├── mobile-new/               # Mobile feature specifications
└── sprint*/                  # Sprint planning and retrospectives
```

---

## 🔗 Key Documentation

- **[Report.md](Report.md)**: Sprint 6 project report with all submission requirements
- **[Presentation.md](Presentation.md)**: Sprint 5 presentation overview
- **Backend Architecture**: `docs/BACKEND_ARCHITECTURE_OVERVIEW.md`
- **Export System**: `docs/PHASE_3_EXPORT_SYSTEM_SUMMARY.md`
- **API Docs**: `docs/api-services/` (15+ specifications)
- **Session Logs**: `session-logs/sprint*-log/` (agent interaction transcripts)

---

## 🎓 Learning Outcomes

### Agentic AI Development
- Multi-agent coordination with role-based specialization (SA → BE → FE workflow)
- Prompt engineering for LLM-powered profile enhancement and generation
- Context management across agent handoffs using structured documentation
- VS Code Copilot Agent Mode with MCP tool integration

### Technical Skills
- **Backend**: FastAPI, async SQLAlchemy, clean architecture, domain-driven design
- **AI/ML**: Groq LLM integration, prompt engineering, content ranking algorithms
- **Mobile**: Flutter, Riverpod, Material Design, platform-specific features
- **Cloud**: AWS S3, presigned URLs, cloud storage patterns
- **DevOps**: Testing strategies, CI/CD concepts, environment management

### Software Engineering
- Clean separation of concerns (presentation → application → domain → infrastructure)
- Repository pattern with dependency injection
- Immutable data models with proper serialization
- Comprehensive error handling and validation
- Documentation-driven development

---

## 📄 License

Educational project for CptS 483 - Washington State University, Fall 2025

---

**Last Updated**: December 12, 2025 | **Sprint 6 Complete** ✅
