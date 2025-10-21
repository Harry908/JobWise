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
1. **Job Discovery:** Search for positions using keywords and filters, browse through swipeable job cards
2. **Job Saving:** Save interesting positions to application pipeline
3. **AI Tailoring:** Automatically generate tailored resume and cover letter drafts for each saved job
4. **Document Review:** Review, edit, and refine AI-generated drafts within the mobile interface
5. **PDF Export:** Export professional, ATS-compatible PDFs ready for submission

---

## 🎯 Project Goals & Success Criteria

### Core Features (Must Complete)
- [✅] User profile and master resume management (Profile API complete)
- [✅] Authentication and user management (JWT auth complete)
- [ ] Job search and browsing interface with swipeable cards
- [ ] AI-powered resume generation tailored to job descriptions
- [ ] AI-powered cover letter generation with personalization
- [ ] Document editing interface with real-time preview
- [ ] ATS-compatible PDF export functionality
- [ ] Saved jobs dashboard and application tracking

### Stretch Goals (If Time Permits)
- [ ] Batch generation for multiple saved jobs
- [ ] Integration with real job APIs (Indeed, LinkedIn)
- [ ] Advanced ATS optimization scoring
- [ ] Application history and analytics
- [ ] Cloud sync and cross-device support

### Success Metrics
- **Functional Completeness**: Seamless workflow from job search to PDF export with AI generation quality validated across diverse job types
- **Multi-Agent Coordination**: Effective collaboration between Architecture, Frontend, Backend, and Integration agents with documented handoffs in ADRs and logs
- **Professional Quality**: ATS-compatible PDFs, <30s generation time, responsive UI with offline support, comprehensive error handling
- **Portfolio Readiness**: Production-quality mobile app demonstrating AI integration, prompt engineering, and full-stack development skills

---

## Recent updates (Oct 20, 2025)

**Sprint 1 Complete + Job API Redesigned**

### Sprint 1 Achievements
- **Backend Foundation Complete**: Authentication (JWT), Profile API, Database layer
- **Profile API**: 12/12 tests passing - Master resume CRUD with components
- **Job API Redesign**: Simplified CRUD with text parsing
  - Single unified job_descriptions table
  - Accepts raw text (auto-parsed) or structured data
  - Text parser extracts title, company, requirements, benefits
  - 5 simple endpoints: POST, GET, GET/:id, PUT/:id, DELETE/:id
- **Architecture Simplification**: Removed 40% redundant files, clean adapter pattern
- **Test Coverage**: 133 tests, 47% coverage

### Sprint 2 In Progress (Oct 21-27, 2025)
- **Job API**: Complete (redesigned CRUD with parsing)
- **Generation API**: Pending (5-stage mock AI pipeline)
- **Document Export API**: Pending (PDF export)
- **Target**: 65%+ coverage, full end-to-end flow

### Quick Start (Backend)

```powershell
cd backend
.\venv\Scripts\Activate.ps1  # or call venv\Scripts\activate.bat in CMD
.\start-server.bat

# API Documentation available at: http://localhost:8000/docs

# Run profile-only tests
pytest tests/test_profile_api.py -q --maxfail=1

# Run full test suite with coverage
pytest --cov=. --maxfail=1 -q
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

### Sprint 1: Foundation & Backend Core APIs ✅ **COMPLETED** (Weeks 8-10)
**Status**: **SUCCESS** | **Completion Date**: October 20, 2025  
**Goal**: Establish development infrastructure and build core backend API services

#### Major Achievements

**🏗️ Backend Foundation (100% Complete)**
- [✅] **F1: Environment & Basic Setup** - FastAPI application with middleware, health checks (16/17 tests passing)
- [✅] **F2: Database Foundation** - SQLAlchemy async, unified job model, repositories (13/13 tests passing)
- [✅] **F3: Authentication System** - JWT tokens, user registration/login, middleware (13/13 tests passing)

**📊 Core API Services (100% Complete)**
- [✅] **Profile API (API-1)** - Master resume CRUD, component management, analytics (12/12 tests passing)
  - Personal info, experience, education, skills, projects management
  - Profile analytics and completeness scoring
  - Async repository pattern with full database integration
  
- [✅] **Job Description API (API-2)** - Unified job model with multi-source support (IMPLEMENTED)
  - Custom job description CRUD with user ownership
  - Job status management (draft/active/archived)
  - Keyword extraction and job analysis pipeline
  - Support for API, static, user-created, scraped, imported sources

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
- **Test Coverage**: ~55% overall (42 tests passing)
- **API Endpoints**: 25+ endpoints implemented across 2 core services
- **Documentation**: 10+ architectural artifacts created
- **Code Quality**: Clean architecture with domain-driven design
- **Development Speed**: Accelerated by AI agent coordination

#### Key Technical Decisions
- Unified job model supporting multiple input sources
- Async SQLAlchemy for scalability
- JWT-based authentication with bcrypt password hashing
- Repository pattern for clean separation of concerns
- Comprehensive value objects for domain modeling

#### Challenges Overcome
- Pydantic v2 migration and syntax updates
- Database schema design for extensible job model
- Authentication middleware integration
- Test environment configuration and isolation

#### AI Agent Coordination Success
All five agents (Business Analyst, Solutions Architect, Backend Developer, Mobile Developer, QA Engineer) successfully coordinated through structured handoffs documented in logs:
- `log/backend-developer-log.md` - Implementation details
- `log/business-analyst-log.md` - Requirements analysis
- `log/solutions-architect-log.md` - Architecture decisions
- `log/qa-engineer-log.md` - Testing strategies
- `log/general-interaction-log.md` - Cross-agent coordination

---

### Sprint 2: Generation API & AI Pipeline (Week 11) 🚀 **READY TO START**
**Status**: Planned | **Start Date**: October 21, 2025 | **Target Completion**: October 27, 2025  
**Goal**: Implement AI-powered resume generation pipeline and document export functionality

#### Sprint 2 Plan Overview

**Time Budget**: 40 hours across 5 days  
**Detailed Plan**: See `docs/sprint2/sprint2-plan.md`

**Phase 1: Generation API Foundation (12 hours)**
- [ ] Generation domain models and value objects
- [ ] Generation repository with full CRUD operations
- [ ] 5-stage mock AI pipeline services:
  - Stage 1: Job Analyzer (1s) - Extract requirements and keywords
  - Stage 2: Profile Compiler (1s) - Score and match profile sections
  - Stage 3: Content Generator (2s) - Tailored resume with templates
  - Stage 4: Quality Validator (1s) - ATS scoring and compliance
  - Stage 5: Export Preparation (0.5s) - Format for document output
- [ ] Generation API with 11 endpoints (create, status, result, regenerate, etc.)

**Phase 2: Document Export API (10 hours)**
- [ ] Document domain models and export format definitions
- [ ] PDF export service with 3 professional templates (Professional, Modern, Creative)
- [ ] Document repository with file storage
- [ ] Document API with 8 endpoints (export, download, preview, etc.)

**Phase 3: Integration & Testing (12 hours)**
- [ ] Generation API tests (15+ tests)
- [ ] Generation pipeline tests (10+ tests)
- [ ] Document API tests (10+ tests)
- [ ] PDF export tests (8+ tests)
- [ ] End-to-end integration tests (10+ tests)
- [ ] Performance validation (<6s generation, <2s export)

**Phase 4: Documentation & Refinement (6 hours)**
- [ ] OpenAPI specification updates
- [ ] Pipeline architecture documentation
- [ ] PDF export implementation guide
- [ ] Testing and bug fixes

#### Success Criteria
- ✅ 53+ new tests passing (67 total)
- ✅ Test coverage increase to 65%+
- ✅ 19 new API endpoints operational
- ✅ Complete generation flow: Profile → Job → Generation → PDF
- ✅ 3 professional resume templates working
- ✅ ATS-compatible PDF export
- ✅ Performance targets met (<6s total generation time)

---

### Sprint 3: Document API & Flutter Mobile Foundation (Week 12)
**Goal**: Document management, PDF export, and Flutter project setup

**Status**: Planned

**Planned Tasks**:
- [ ] **API-4: Document API** - Document CRUD, export formats, download endpoints
- [ ] **PDF Export Service** - Professional PDF generation with templates
- [ ] **Flutter Project Setup** - Mobile app structure and state management
- [ ] **API Client Integration** - HTTP service layer for backend communication
- [ ] **Basic UI Scaffolding** - Navigation, routing, core screens

---

### Sprint 4: Mobile UI Implementation (Week 13)
**Goal**: Job search interface, profile management, document viewing

**Status**: Planned

**Planned Tasks**:
- [ ] Job search and browsing UI with swipeable cards
- [ ] Profile creation and editing screens
- [ ] Saved jobs dashboard
- [ ] Document preview and editing interface
- [ ] State management implementation

---

### Sprint 5: Integration & Polish (Week 14)
**Goal**: End-to-end integration, testing, performance optimization

**Status**: Planned

**Planned Tasks**:
- [ ] Frontend-backend integration testing
- [ ] Generation pipeline E2E testing
- [ ] Performance optimization (<30s generation)
- [ ] Error handling and user feedback
- [ ] UI/UX polish and accessibility

---

### Sprint 6: Final Testing & Presentation (Week 15)
**Goal**: Comprehensive testing, documentation, presentation preparation

**Status**: Planned

**Planned Tasks**:
- [ ] Full system testing and bug fixes
- [ ] Test coverage improvements (>80% target)
- [ ] Documentation finalization
- [ ] Demo video and presentation preparation
- [ ] Portfolio-ready deployment

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

### Project Structure (To Be Created)

```
course-project-Harry908/
├── mobile_app/                      # Flutter mobile application
│   ├── lib/
│   │   ├── main.dart               # App entry point
│   │   ├── screens/                # UI screens
│   │   ├── widgets/                # Reusable widgets
│   │   ├── models/                 # Data models
│   │   ├── services/               # API services
│   │   ├── providers/              # State management
│   │   └── utils/                  # Helper functions
│   ├── test/                       # Flutter tests
│   └── pubspec.yaml                # Flutter dependencies
│
├── backend/                         # FastAPI backend
│   ├── main.py                     # API entry point
│   ├── routers/                    # API route handlers
│   ├── services/                   # Business logic
│   │   ├── job_analyzer.py
│   │   ├── profile_compiler.py
│   │   ├── document_generator.py
│   │   ├── quality_validator.py
│   │   └── pdf_exporter.py
│   ├── models/                     # Data models
│   ├── prompts/                    # LLM prompt templates
│   ├── data/                       # Mock data
│   │   ├── mock_jobs.json
│   │   └── test_cases/
│   ├── tests/                      # Backend tests
│   └── requirements.txt            # Python dependencies
│
├── docs/                           # Documentation
│   ├── project-proposal.md
│   ├── architecture-diagram.md
│   ├── agent-coordination-diagram.md
│   ├── as-instructions.md
│   ├── ai-coordination-log.md
│   ├── timeline.md
│   └── risk-assessment-matrix.md
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

### AI Generation Pipeline
- **5-stage pipeline**: Job parsing → Profile analysis → Document generation → Quality validation → PDF export
- **Smart content selection**: Prioritizes relevant experiences from master resume rather than generating from scratch
- **ATS optimization**: Keyword analysis, format validation, compatibility scoring
- **Factual consistency**: Validates generated content against master resume to prevent fabrication

### Mobile-First Design
- **Swipeable job cards**: Tinder-style interface for job discovery
- **Offline support**: Local caching for saved jobs and generated documents
- **Real-time editing**: Section-level document editing with live preview
- **Cross-platform**: Single codebase for iOS and Android via Flutter

### Context Management
- **Sliding window approach**: 8000 token windows with 500 token overlap
- **Dynamic token allocation**: Adjusts based on generation stage and content complexity
- **Semantic compression**: Intelligently prunes less-relevant context to fit budget

### Error Handling & Resilience
- **Circuit breakers**: Prevents cascading failures with external APIs
- **Exponential backoff**: Automatic retry with increasing delays
- **Graceful degradation**: Fallback to mock data or cached responses
- **User-friendly errors**: Actionable error messages with recovery suggestions

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

## 🚧 Known Issues & Limitations

- **Development Phase**: Project currently in Sprint 1 (Week 8) - implementation just beginning
- **Mock Data**: Currently using mock job listings; real API integration deferred to Weeks 13-14
- **LLM Costs**: Monitoring token usage to stay within budget constraints
- **Platform Testing**: iOS testing limited by macOS availability (Android primary focus)

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

**Last Updated**: October 20, 2025 (Sprint 1 Complete - Sprint 2 Starting)
