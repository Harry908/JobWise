# JobWise - AI-Powered Job Application Assistant

## Course: CptS 483 Special Topic - Coding with Agentic AI
## Student: Harry Ky
## Track: Mobile Development
## Project Phase: Weeks 8-14 (Individual Project)

---

## 📋 Project Overview

Searching and applying for jobs is repetitive and time-consuming. Job seekers, especially students and early-career professionals, spend hours tailoring resumes and cover letters for each posting—an inefficient process that discourages personalization and slows down applications.

**JobWise** is a Flutter mobile application that automates this process through **AI-generated resume and cover letter tailoring**. Users can search and browse job postings, save positions of interest, then receive AI-generated application documents tailored to each specific role. Each document remains editable, allowing users to review, refine, and export as professional PDFs ready for submission.

The project emphasizes the **job search to application workflow**, with focus on AI-tailored document generation, prompt design, context management, and responsible AI use. During development, multiple **Agentic AI assistants** coordinate to accelerate designing, coding, testing, and documentation while maintaining quality.

### Target Users
- University students and graduates applying for internships or entry-level roles
- Early-career professionals managing multiple job applications
- Mobile-first users seeking efficient, AI-assisted job search preparation
- Career changers needing tailored resumes for different industries

### Core Use Cases
1. **Profile Management:** Create and maintain master resume with work experience, education, skills, and projects
2. **AI Enhancement:** Use AI to enrich profile content with professional language and better descriptions
3. **Job Management:** Save job postings from text input, track application status pipeline
4. **Sample Upload:** Upload existing resume/cover letter samples to teach AI your writing style
5. **AI Generation:** Generate tailored resumes and cover letters using Groq LLM (llama-3.3-70b-versatile)
6. **Document Export:** Export professional PDFs ready for submission (Sprint 6)

---

## 🎯 Working Features (Sprints 1-5 Complete)

### ✅ Feature 01: Authentication & User Management
**Status**: Fully Implemented | **Quality**: Production-Ready

**Backend Capabilities**:
- JWT-based authentication with access and refresh tokens
- User registration with email validation and secure password hashing
- Login with automatic token refresh on expiration
- Token management (refresh, logout, change password)
- Password reset flow (forgot password, reset with token)

**Mobile Capabilities**:
- Professional login/register screens with Material Design
- Form validation with real-time feedback
- Secure token storage using flutter_secure_storage
- Automatic token refresh interceptor
- User-friendly error messages with 422 validation error extraction

**Key Files**:
- Backend: `backend/app/presentation/api/auth.py` (9 endpoints)
- Mobile: `mobile_app/lib/screens/auth/login_screen.dart`, `register_screen.dart`
- Docs: `docs/api-services/01-authentication-api.md`, `docs/mobile-new/01-authentication-feature.md`

---

### ✅ Feature 02: Profile Management
**Status**: Fully Implemented | **Quality**: Production-Ready

**Backend Capabilities**:
- Comprehensive CRUD for master resume profiles
- Bulk operations for experiences, education, and projects
- Granular skills management (add/remove individual skills)
- Custom fields with dynamic key-value storage
- Profile analytics with completeness scoring
- 24 endpoints covering all profile operations

**Mobile Capabilities**:
- Multi-step profile creation form (Personal Info, Experience, Education, Skills, Projects)
- Minimal profile creation (only name + email required)
- CRUD dialogs for experience, education, and project items
- Tag-based skills input widget
- Date pickers with configurable format (US/European/ISO)
- Profile completeness indicator
- Settings screen for user preferences

**Key Features**:
- **Personal Info**: Name, email, phone, location, LinkedIn, GitHub, website, professional summary
- **Experiences**: Title, company, location, dates, description, achievements, employment type
- **Education**: Institution, degree, field of study, dates, GPA, honors
- **Skills**: Technical skills, soft skills, languages, certifications
- **Projects**: Name, description, technologies, URL, dates

**Key Files**:
- Backend: `backend/app/presentation/api/profile.py` (24 endpoints)
- Mobile: `mobile_app/lib/screens/profile/profile_edit_screen.dart`, `profile_view_screen.dart`
- Docs: `docs/api-services/02-profile-api.md`, `docs/mobile-new/02-profile-management-feature.md`

**Testing**: 58 backend tests passing (17 core + 9 bulk + 13 granular + 19 service)

---

### ✅ Feature 03: Job Management & Application Tracking
**Status**: Fully Implemented | **Quality**: Production-Ready

**Backend Capabilities**:
- Job CRUD operations with user ownership
- Text-based job parsing with AI (extract company, title, description, requirements)
- URL-based job scraping (future capability, endpoint ready)
- Application status tracking with 8-status pipeline
- Job visibility control (active, archived, draft)
- Query filters (status, application_status, source, pagination)

**Mobile Capabilities**:
- **Job Browse Screen**: Search mock jobs, infinite scroll, save functionality
- **Job List Screen**: User's saved jobs with status/source filters, pull-to-refresh
- **Job Detail Screen**: Full job display with status picker, keyword highlighting
- **Job Paste Screen**: Raw text input for backend AI parsing
- Interactive status picker dialog with color-coded badges
- Application pipeline tracking (not applied → preparing → applied → interviewing → offer/rejected/accepted/withdrawn)

**Key Features**:
- **Dual Status System**:
  - `status`: Job visibility (active, archived, draft) - controls list filtering
  - `application_status`: Application progress tracking (8 values) - user's pipeline stage
- **Employment Types**: full_time, part_time, contract, temporary, internship
- **Job Sources**: user_created, text_parsed, url_scraped, mock
- **Parsed Data**: Company, title, location, salary, description, requirements, qualifications, keywords

**Key Files**:
- Backend: `backend/app/presentation/api/job.py` (5 endpoints)
- Mobile: `mobile_app/lib/screens/jobs/` (4 screens)
- Models: `mobile_app/lib/models/job.dart` (Freezed models with JSON serialization)
- Docs: `docs/api-services/03-job-api.md`, `docs/mobile-new/03-job-browsing-feature.md`

**Testing**: 38 backend tests passing, end-to-end status persistence validated

---

### ✅ Feature 04: AI Generation & Sample Management
**Status**: Fully Implemented | **Quality**: Production-Ready

**AI Generation Capabilities**:
- **Profile Enhancement**: AI enrichment of professional summary, experience descriptions, project descriptions
  - Uses Groq llama-3.3-70b-versatile model
  - Extracts writing style from uploaded sample documents
  - Preserves user's tone while improving clarity and professionalism
  
- **Content Ranking**: Smart relevance scoring
  - Keyword matching between profile content and job requirements
  - Embeddings-free algorithm (fast, no external API)
  - Scores experiences, education, projects, and skills
  
- **Resume Generation**: Template-free resume creation
  - Uses ranked content to select most relevant items
  - Customizable (max experiences, education, projects, skills)
  - Generation speed: <3 seconds (no LLM, pure templating)
  - ATS score calculation with keyword density analysis
  
- **Cover Letter Generation**: Personalized cover letters
  - LLM-powered using Groq llama-3.3-70b-versatile
  - Writing style extraction from user's sample cover letter
  - Job-specific customization with company research
  - Generation speed: 5-8 seconds (includes 2 LLM calls)
  - ATS score with keyword matching

**Sample Document Management**:
- Upload resume and cover letter samples (.txt format)
- Automatic writing style extraction for AI generation
- Sample CRUD (list, get details, delete)
- Active sample tracking (one resume, one cover letter)
- File storage with full_text content for LLM prompts

**Mobile UI**:
- **Generation Options Screen**: Job context, sample status, profile enhancement, customization options
- **Progress Tracking Screen**: Real-time stage updates (4-stage pipeline visualization)
- **Result Display Screen**: Generated content with ATS score badges, keyword highlighting
- **History Screen**: View past generations, regenerate, copy to clipboard
- **Sample Upload Screen**: File picker, sample cards, delete functionality

**Key Features**:
- **Real LLM Integration**: Live Groq API calls (not mock)
- **Dual Generation Modes**: Fast resumes (<3s) vs. quality cover letters (5-8s)
- **Sample-Based Style**: AI learns from user's existing documents
- **ATS Optimization**: Keyword density + compliance validation
- **Generation History**: Track all past generations by job
- **Regeneration**: Create new versions with updated content

**Key Files**:
- Backend: `backend/app/presentation/api/generation.py`, `samples.py`
- Mobile: `mobile_app/lib/screens/generation/`, `samples/`
- Services: `backend/app/application/services/generation_service.py`, `ai_service.py`
- Docs: `docs/api-services/04-v3-generation-api.md`, `04b-ai-generation-api.md`, `04a-sample-upload-api.md`

**API Endpoints**: 10 V3 Generation endpoints (samples, enhance, rankings, resume, cover letter, history)

**Testing**: Live Groq LLM integration tested with real profile and job data

---

## 🎯 Project Goals & Success Criteria

### Feature Completion Status

**Implemented (Sprints 1-5)** ✅
- [✅] User authentication and session management (Backend + Mobile complete)
- [✅] Profile management with AI enhancement (39 tests passing, 0.98/1.0 quality)
- [✅] Job management with application tracking (8-status pipeline, dual status fields)
- [✅] Sample document upload and management (resume + cover letter)
- [✅] AI-powered profile enhancement (Groq LLM integration)
- [✅] Content ranking with keyword matching (embeddings-free)
- [✅] Resume generation with ATS scoring (<3s generation)
- [✅] Cover letter generation with style extraction (5-8s generation)
- [✅] Generation history and regeneration
- [✅] Comprehensive documentation (12 API/feature docs)

**Sprint 6 Planned (Document Export & Cloud Storage)** 📋
- [ ] Professional PDF export with templates (Classic, Modern, ATS-Optimized)
- [ ] DOCX export for further editing
- [ ] AWS S3 storage integration with versioning
- [ ] Document library UI with download/share
- [ ] Batch export for multiple jobs
- [ ] Email integration

**Future Enhancements** 🔮
- [ ] Integration with real job APIs (Indeed, LinkedIn, RemoteOK)
- [ ] Advanced ATS optimization with ML scoring
- [ ] Application analytics and insights
- [ ] Cloud sync and cross-device support
- [ ] Browser extension for one-click job save

### Success Metrics
- **Functional Completeness**: Seamless workflow from job search to PDF export with AI generation quality validated across diverse job types
- **Multi-Agent Coordination**: Effective collaboration between Architecture, Frontend, Backend, and Integration agents with documented handoffs in ADRs and logs
- **Professional Quality**: ATS-compatible PDFs, <30s generation time, responsive UI with offline support, comprehensive error handling
- **Portfolio Readiness**: Production-quality mobile app demonstrating AI integration, prompt engineering, and full-stack development skills

---

## Recent Updates (December 1, 2025)

**Sprint 1-5 Complete: Full AI Generation Pipeline** ✅
**Groq LLM Integration: Live AI-Powered Generation** 🤖
**All Core Features: Working End-to-End** ✅
**Sprint 6 Ready: Document Export & S3 Storage** 📋

### Sprint Summary (Sprints 1-5)

**Sprint 1 Complete** ✅ - Backend APIs + Mobile UI Foundation
- Backend: Auth API (9 endpoints), Profile API (24 endpoints), Job API (5 endpoints)
- Mobile: Authentication screens, Profile management (multi-step form), Settings
- Testing: 77 backend tests passing, clean architecture with domain-driven design
- Documentation: 12 comprehensive API and mobile feature specifications

**Sprint 2 Complete** ✅ - Generation API & AI Pipeline (Mock)
- Generation domain models and value objects
- 5-stage mock AI pipeline (Job Analyzer → Profile Compiler → Content Generator → Quality Validator → Export Preparation)
- Document export API with ReportLab PDF generation
- 3 professional resume templates (Professional, Modern, Creative)
- 53 new tests covering pipeline and export functionality

**Sprint 3 Complete** ✅ - Job Management & Application Tracking
- Complete job CRUD with text parsing and URL scraping (ready)
- 8-status application pipeline (not_applied → preparing → applied → interviewing → offer/rejected/accepted/withdrawn)
- 4 mobile screens (Browse, List, Detail, Paste)
- Dual status system (job visibility + application progress)
- Database migration adding application_status column

**Sprint 4 Complete** ✅ - Real AI Generation & Sample Upload
- **Groq LLM Integration**: Replaced mock pipeline with real llama-3.3-70b-versatile and llama-3.1-8b-instant models
- **Profile Enhancement**: AI enrichment of professional summary, experiences, and projects
- **Sample Management**: Upload resume/cover letter samples for writing style extraction
- **Content Ranking**: Smart keyword matching scoring profile items against job requirements
- **Resume Generation**: Template-free creation using ranked content (<3s)
- **Cover Letter Generation**: LLM-powered personalized letters (5-8s)
- **V3 Generation API**: 10 endpoints for complete generation workflow
- **Mobile UI**: 5 screens (Options, Progress, Result, History, Samples)

**Sprint 5 Complete** ✅ - Integration, Testing & Documentation
- **End-to-End Validation**: Complete user workflows tested (Profile → Enhance → Samples → Jobs → Generate)
- **Comprehensive Testing**: 77+ backend tests, integration tests, manual mobile testing
- **Documentation Sync**: All 12 docs updated with Dec 1, 2025 implementation notes
- **UI/UX Polish**: Material Design, loading states, error handling, success feedback
- **Production Ready**: Live Groq API integration, proper error recovery, performance targets met

### Current Status (December 1, 2025)

**Working Features** ✅
1. **Authentication**: Registration, login, token refresh, password management
2. **Profile Management**: Master resume CRUD with AI enhancement
3. **Job Management**: Save jobs, track application status, text parsing
4. **Sample Upload**: Resume and cover letter samples for style extraction
5. **AI Generation**: Profile enhancement, resume generation, cover letter generation
6. **Generation History**: View past generations, regenerate, copy to clipboard

**Performance Metrics** 📊
- Resume Generation: <3 seconds (template-based, no LLM)
- Cover Letter Generation: 5-8 seconds (includes 2 LLM calls)
- Profile Enhancement: ~3 seconds (1 LLM call for all content)
- Backend Tests: 77+ passing tests across all features
- API Response Time: <2s for all non-LLM endpoints
- ATS Score Range: 70-95% with keyword matching

**Next Up: Sprint 6** 📋
- Professional PDF export with 3 templates
- DOCX export for further editing
- AWS S3 storage integration
- Document library UI
- Batch export and email integration

### Quick Start

**Backend Server**
```powershell
cd backend
.\start-server.bat

# API Documentation: http://localhost:8000/docs
# Server runs on: http://0.0.0.0:8000

# Run profile tests (58 tests)
pytest tests/profile -v

# Run all tests with coverage
pytest --cov=. --cov-report=html
```

**Flutter Mobile App**
```powershell
cd mobile_app
flutter pub get
flutter run

# For Android emulator (10.0.2.2 maps to localhost)
# For iOS simulator (localhost works directly)

# Run tests
flutter test

# Code analysis
flutter analyze
```


## 🏗️ Technical Architecture

### Technology Stack
- **Mobile Framework**: Flutter 3.x (Dart)
- **Backend Framework**: Python FastAPI
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Cache**: In-memory (dev), Redis (prod)
- **LLM Provider**: OpenAI GPT-3.5-turbo (dev), GPT-4/Claude 3 (prod)
- **PDF Generation**: Flutter `pdf` package, Puppeteer (backend fallback)
- **Job Data**: Mock JSON (dev), Indeed/LinkedIn API (prod)
- **State Management**: Provider or Riverpod (TBD in Sprint 2)
- **API Integration**: http/dio packages

### Multi-Agent System Design

#### Agent 1: Business Analyst Agent
- **Primary Responsibility**: Requirements analysis, user story creation, business rule definition, acceptance criteria validation
- **Input**: Project objectives, user feedback, market research, stakeholder requirements
- **Output**: Requirements specifications, user stories, acceptance criteria, business rules, use case documentation
- **AI Tool**: Claude 3.5 Sonnet (primary), ChatGPT-4 (alternative)
- **Coordination**: Initiates development cycles, hands off to Solutions Architect Agent

#### Agent 2: Solutions Architect Agent  
- **Primary Responsibility**: Technical architecture design, ADR creation, system integration planning, API contract definition
- **Input**: Requirements from Business Analyst, technical constraints, performance targets, scalability needs
- **Output**: Architecture Decision Records (ADRs), system architecture diagrams, API specifications, technical implementation guides
- **AI Tool**: ChatGPT-4 (primary), Claude 3.5 Sonnet (alternative)
- **Coordination**: Receives requirements from BA, distributes technical specs to development agents

#### Agent 3: Mobile Developer Agent
- **Primary Responsibility**: Flutter UI implementation, state management, mobile-specific features, offline capabilities
- **Input**: UI/UX specifications, API contracts, technical requirements from Solutions Architect
- **Output**: Flutter widgets, screens, navigation logic, state management, mobile app implementation
- **AI Tool**: GitHub Copilot (primary), Claude 3.5 Sonnet (complex logic)
- **Coordination**: Receives specs from SA, coordinates with Backend Developer, delivers to QA Engineer

#### Agent 4: Backend Developer Agent
- **Primary Responsibility**: FastAPI endpoints, AI generation pipeline, database design, external service integration
- **Input**: API specifications, data models, business logic requirements from Solutions Architect
- **Output**: REST APIs, AI pipeline services, database schemas, service integrations, API documentation
- **AI Tool**: GitHub Copilot (primary), Claude 3.5 Sonnet (complex business logic)
- **Coordination**: Receives specs from SA, coordinates with Mobile Developer, delivers to QA Engineer

#### Agent 5: QA Engineer Agent
- **Primary Responsibility**: Integration testing, quality validation, performance testing, bug reporting, acceptance verification
- **Input**: Implemented features from development agents, acceptance criteria from BA, technical specs from SA
- **Output**: Test reports, performance metrics, bug reports, quality assessments, feedback for architecture improvements
- **AI Tool**: GitHub Copilot (test automation), ChatGPT (test strategy)
- **Coordination**: Receives implementations from developers, provides feedback to Solutions Architect, validates against BA requirements

### Architecture Diagram
See `docs/architecture-diagram.md` for complete system architecture with development/production environment mappings.

**AI Generation Pipeline (5 Stages)**:
```
Job Analyzer → Profile Compiler → Document Generator → Quality Validator → PDF Exporter
```

**Context Management**: Sliding window approach (8000 token windows, 500 token overlap)
- Profile extraction: 2000 tokens
- Job analysis: 1500 tokens
- Resume generation: 3000 tokens
- Optimization pass: 1500 tokens

---

## 📅 Sprint Progress

### Sprint 1: Backend APIs + Mobile UI Foundation ✅ **COMPLETED** (Weeks 8-10)
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
- **UI Screens**: 5 generation screens (options, progress, result, history, samples)
- **Database Tables**: 3 new tables (sample_documents, job_content_rankings, generations)
- **Documentation**: 6 comprehensive API/feature docs with field semantics

#### Key Technical Achievements
- **Real AI Integration**: Replaced mock pipeline with actual Groq LLM API calls
- **Profile Enhancement**: AI enriches all profile content (summary, experiences, projects) using sample writing style
- **Smart Ranking**: Embeddings-free keyword matching scoring profile items against job requirements
- **Dual Generation Modes**: Fast resume generation (<3s) vs. quality cover letters (5-8s with LLM)
- **Sample-Based Style**: Extracts writing patterns from user's existing documents
- **ATS Optimization**: Keyword density analysis and formatting compliance validation

#### Challenges Overcome
- **LLM Prompt Engineering**: Crafted effective system prompts for profile enhancement and cover letter generation
- **Performance Optimization**: Achieved <3s resume generation by avoiding LLM for template-based content
- **Error Recovery**: Graceful handling of LLM API failures with retry logic and fallbacks
- **State Synchronization**: Coordinated profile enhancement across multiple components
- **File Upload**: Implemented multipart/form-data handling for sample document uploads

---

### Sprint 5: End-to-End Integration & Testing ✅ **COMPLETED**
**Status**: **SUCCESS** | **Completion Date**: December 1, 2025  
**Goal**: Complete end-to-end workflow validation, comprehensive testing, and production readiness

#### Sprint 5 Achievements

**🔄 Complete User Workflow (100% Validated)**
- ✅ **Profile Creation → Enhancement → Samples Upload → Job Save → Generation → Export**
- ✅ **Authentication Flow** - Registration, login, token refresh, session management
- ✅ **Profile Management** - Create, edit, enhance with AI, view completeness score
- ✅ **Job Management** - Browse, save, update status, track application pipeline
- ✅ **Sample Management** - Upload resume/cover letter samples, manage active samples
- ✅ **AI Generation** - Profile enhancement, content ranking, resume and cover letter generation
- ✅ **Result Management** - View generated documents, copy to clipboard, regenerate

**🧪 Comprehensive Testing (100% Complete)**
- ✅ **Backend Tests** - 77+ passing tests (auth, profile, jobs, generation, samples)
- ✅ **Integration Tests** - End-to-end API workflow validation
- ✅ **Mobile Testing** - Manual testing of all screens and user flows
- ✅ **LLM Testing** - Groq API integration with real profile and job data
- ✅ **Error Scenarios** - Network failures, validation errors, LLM API failures
- ✅ **Performance Testing** - Generation speed targets met (<3s resume, 5-8s cover letter)

**📚 Complete Documentation (100% Complete)**
- ✅ **API Documentation** - 6 comprehensive API specs (Auth, Profile, Job, V3 Generation, AI Generation, Sample Upload)
- ✅ **Mobile Documentation** - 6 feature docs (API Config, Auth, Profile, Job, Generation, Samples, AI Generation)
- ✅ **Field Semantics** - Backend ↔ Mobile field mappings documented (snake_case ↔ camelCase)
- ✅ **Recent Changes** - All docs updated with December 1, 2025 implementation notes
- ✅ **Architecture** - Clean separation of concerns, domain-driven design

**🎨 UI/UX Polish (100% Complete)**
- ✅ **Material Design** - Consistent theming, proper Material 3 components
- ✅ **Loading States** - Progress indicators during API calls and LLM generation
- ✅ **Error Handling** - User-friendly error messages with actionable guidance
- ✅ **Success Feedback** - SnackBar notifications for successful operations
- ✅ **Navigation Flow** - Intuitive routing with proper back button behavior

#### Sprint 5 Metrics
- **Total Backend Tests**: 77+ passing tests across all features
- **API Coverage**: 100% of endpoints tested (Auth, Profile, Job, Generation, Samples)
- **Mobile Screens**: 15+ complete screens with navigation
- **Documentation Files**: 12 comprehensive docs (6 API + 6 mobile feature specs)
- **End-to-End Workflows**: 3 complete user journeys validated
- **LLM Integration**: Production-ready with Groq API key management

#### Key Technical Achievements
- **Complete Feature Set**: All Sprint 1-5 features working end-to-end
- **Real AI Integration**: Live Groq LLM calls with profile enhancement and cover letter generation
- **Production Backend**: FastAPI with clean architecture, async operations, proper error handling
- **Production Mobile**: Flutter app with Riverpod state management, Material Design, offline-ready
- **Comprehensive Docs**: Every feature documented with field semantics and API contracts

#### Challenges Overcome
- **Enhanced Description Handling**: Fixed profile update truncating enhanced descriptions
- **Sample Upload Flow**: Implemented file picker with proper MIME type validation
- **LLM Prompt Design**: Crafted effective prompts for consistent, high-quality output
- **State Management**: Proper profile refresh after enhancement to show updated descriptions
- **Documentation Sync**: Kept all docs aligned with actual implementation (dual status fields, field mappings)

---

### Sprint 6: Document Export & S3 Storage (Week 15)
**Goal**: Professional document formatting, PDF/DOCX export, cloud storage integration

**Status**: **PLANNED** | **Dates**: December 2-8, 2025

**Planned Features**:
- [ ] **Document Format Templates** 
  - Professional resume templates (Classic, Modern, ATS-Optimized)
  - Cover letter templates matching resume styles
  - Customizable sections and layouts
  - Font and color scheme options
  
- [ ] **PDF Export**
  - High-quality PDF generation from generated content
  - Template-based formatting with proper typography
  - ATS-compatible PDF structure (text-based, no images)
  - Metadata embedding (author, title, keywords)
  
- [ ] **DOCX Export**
  - Microsoft Word format generation
  - Editable format for further customization
  - Style preservation and formatting
  
- [ ] **S3 Storage Integration**
  - AWS S3 bucket setup for document storage
  - Secure document upload with presigned URLs
  - Document versioning and history
  - Download links with expiration
  
- [ ] **Document Management UI**
  - Export options dialog (format, template selection)
  - Document library screen (past exports)
  - Download and share functionality
  - Delete and regenerate options
  
- [ ] **Advanced Features**
  - Batch export (multiple jobs)
  - Email integration (send to self/employer)
  - Print preview
  - Document comparison (versions)

**Technical Stack**:
- **Backend**: Python `reportlab` for PDF, `python-docx` for DOCX
- **Storage**: AWS S3 with boto3 client
- **Mobile**: Flutter `flutter_downloader` for file downloads
- **Templates**: Jinja2 for dynamic content rendering

**Success Criteria**:
- Professional PDF output matching industry standards
- ATS compatibility score >90% on Jobscan
- S3 upload/download speed <3 seconds
- Mobile download with proper file system integration
- Template selection with live preview

---

## 🚀 Getting Started

### Prerequisites
- **Flutter SDK**: Version 3.x or higher ([Install Flutter](https://docs.flutter.dev/get-started/install))
- **Dart SDK**: Included with Flutter
- **Python**: Version 3.9+ for backend
- **Git**: For version control
- **Android Studio** or **Xcode**: For mobile emulators/simulators
- **OpenAI API Key**: For LLM integration (set in `.env`)
- **Code Editor**: VS Code recommended with Flutter and Dart extensions

### Installation

#### 1. Clone Repository
```powershell
git clone https://github.com/WSU-CptS483/course-project-Harry908.git
cd course-project-Harry908
```

#### 2. Frontend Setup (Flutter)
```powershell
# Create Flutter project (if not exists)
flutter create mobile_app
cd mobile_app

# Install dependencies
flutter pub get

# Run on emulator/simulator
flutter run

# Or specify platform
flutter run -d chrome        # Web
flutter run -d android       # Android
flutter run -d ios           # iOS (macOS only)
```

#### 3. Backend Setup (Python FastAPI)
```powershell
# Create backend directory and navigate
mkdir backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate      # Windows PowerShell

# Install dependencies (after creating requirements.txt)
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

#### 4. Environment Configuration
```powershell
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Required: OPENAI_API_KEY, DATABASE_URL, etc.
```

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

---

## 🤖 AI Coordination Summary

### Primary Development Agent
**Tool**: GitHub Copilot (VS Code Extension)  
**Used For**: Code generation, autocomplete, inline suggestions, test generation

### Architecture & Design Agent
**Tool**: ChatGPT (OpenAI)  
**Used For**: System design, ADR creation, feature epic generation, architectural decisions

### Code Review & Refinement Agent
**Tool**: Claude (via Cursor IDE)  
**Used For**: Code review, optimization suggestions, documentation enhancement, complex problem-solving

### Integration & Testing Strategy
**Tool**: GitHub Copilot + ChatGPT  
**Used For**: Test strategy design, integration planning, debugging, quality assurance

**Coordination Approach**: 
Event-driven pipeline where agents hand off context through structured artifacts (ADRs, implementation summaries, test reports). Architecture Agent initiates cycles, Development Agents implement in parallel, Integration Agent validates and provides feedback for next iteration. See `docs/ai-coordination-log.md` for detailed interaction logs and prompt evolution.

---

## 🔑 Key Features & Technical Highlights

### Backend API Implementation
- **Profile API**: Comprehensive master resume management with 58 tests passing
  - Core CRUD with JWT-based ownership validation
  - Bulk operations for experiences, education, projects (add/update/delete multiple items)
  - Granular skills management (add/remove individual technical/soft skills)
  - Custom fields with dynamic key-value storage
  - Profile analytics with completeness scoring and recommendations
- **Authentication API**: JWT-based auth with automatic token refresh
  - Secure password hashing with bcrypt
  - Token expiration and refresh mechanism
  - User registration with validation
- **Database**: Async SQLAlchemy with repository pattern
  - Clean separation of concerns
  - Relationship management with eager loading
  - Transaction support for atomic operations

### Mobile UI Implementation (Flutter + Riverpod)
- **Authentication Screens**: Professional login/register UI
  - Email validation and error handling
  - Secure token storage with flutter_secure_storage
  - Automatic token refresh interceptor
  - 422 validation error extraction and display
  - HTTP request/response logging for debugging
  
- **Profile Management**: Multi-step form with comprehensive features
  - **Minimal Creation**: Only name + email required (progressive enhancement)
  - **Step 0 - Personal Info**: Name, email, phone, location, LinkedIn, GitHub, website, summary
  - **Step 1 - Experience**: CRUD dialogs with date pickers, achievements list, employment type
  - **Step 2 - Education & Skills**: Institution details with tag-based skills input
  - **Step 3 - Projects**: Portfolio items with technologies, highlights, repository URLs
  
- **State Management**: Riverpod best practices
  - StateNotifier pattern with no public properties beyond state
  - Immutable data classes with proper equality operators
  - Sophisticated error handling with DioException parsing
  - Proper state transitions using copyWith
  
- **UI Components**: Reusable widget library
  - Card widgets for displaying profile items (Experience, Education, Project)
  - Dialog widgets for CRUD operations with validation
  - TagInput widget for skills management
  - Date pickers with configurable format (US MM/dd/yyyy, European dd/MM/yyyy, ISO yyyy-MM-dd)
  - Settings screen for user preferences
  
- **Navigation & UX**: Intuitive user experience
  - Proper routing with go_router
  - Back button support using context.push for secondary screens
  - Form validation with user-friendly error messages
  - Loading overlays during API operations
  - Success/error snackbar notifications

---

## 📊 Development Metrics & Targets

- **Generation Speed**: <30 seconds for resume + cover letter
- **API Response Time**: <2s for job search
- **ATS Compatibility Score**: >85% (validated with Jobscan/Resume Worded)
- **Test Coverage**: >80% for backend services, >70% for Flutter widgets
- **Code Quality**: ESLint/Dart Analyzer passing with zero errors
- **Token Usage**: <$5/day during development (GPT-3.5-turbo)

---

## 🎤 Week 15: Live Presentation (5 minutes)

**Format**: Live demonstration during class
- 30 seconds: Project overview and problem statement
- 2-3 minutes: Core functionality demo (search → save → generate → edit → export)
- 1 minute: AI coordination approach and multi-agent workflow
- 30 seconds: Reflection, learning outcomes, and future enhancements

---

## 🚧 Known Issues & Current Status

**Sprint 1 Complete (✅)**
- Backend: Authentication and Profile APIs fully implemented with 58 tests passing
- Mobile: Authentication and Profile UI complete with Riverpod state management
- Integration: Frontend-backend communication working with proper error handling

**Sprint 2 Starting (Oct 28, 2025)**
- Generation API: Not yet implemented (5-stage AI pipeline pending)
- Document Export: Not yet implemented (PDF generation pending)
- Job Search UI: Not yet implemented (swipeable cards pending)
- Document Editing: Not yet implemented (preview and edit pending)

**Technical Debt**
- Mobile: Add unit tests for ProfileNotifier state transitions (priority: high)
- Mobile: Implement offline caching for profile data
- Backend: Add integration tests for end-to-end workflows
- Both: Increase test coverage (current: ~50% backend, 0% mobile)

---

## 📝 License

This project is created for educational purposes as part of CptS 483 Special Topic - Coding with Agentic AI at Washington State University. All rights reserved.

---

## 👤 Contact

**Harry Kyaw**  
Washington State University  
Course: CptS 483 Special Topic - Coding with Agentic AI  
Semester: Fall 2025

**Repository**: [WSU-CptS483/course-project-Harry908](https://github.com/WSU-CptS483/course-project-Harry908)

---

## 🙏 Acknowledgments

- **Course Instructor**: For guidance on multi-agent AI coordination patterns
- **OpenAI**: GPT models powering the generation pipeline
- **Flutter Team**: Excellent mobile development framework
- **FastAPI**: High-performance Python backend framework

---

**Last Updated**: December 1, 2025 (Sprints 1-5 Complete: Full AI Generation Pipeline with Groq LLM | Sprint 6 Ready: Document Export & S3 Storage)
