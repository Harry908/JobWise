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
- [ ] Job search and browsing interface with swipeable cards
- [ ] AI-powered resume generation tailored to job descriptions
- [ ] AI-powered cover letter generation with personalization
- [ ] Document editing interface with real-time preview
- [ ] ATS-compatible PDF export functionality
- [ ] User profile and master resume management
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

#### Agent 1: Innovation & Architecture Agent
- **Primary Responsibility**: Generate technical specifications, create feature epics, propose architectural improvements, maintain project vision
- **Input**: Current system state, performance metrics, test results, integration feedback
- **Output**: ADRs (Architecture Decision Records), feature epics with acceptance criteria, technical specifications, architecture refinements
- **AI Tool**: ChatGPT
- **Coordination**: Initiates development cycles, receives feedback from Integration Agent

#### Agent 2: Frontend Development Agent
- **Primary Responsibility**: Implement Flutter mobile UI components, navigation flows, state management, local caching
- **Input**: Feature epics, UI/UX requirements, API contracts from Architecture Agent
- **Output**: Flutter widgets, screens, navigation logic, API integration code, implementation summaries
- **AI Tool**: GitHub Copilot, Claude (via Cursor)
- **Coordination**: Receives specs from Architecture Agent, passes implementation to Integration Agent

#### Agent 3: Backend Development Agent
- **Primary Responsibility**: Build FastAPI endpoints, AI generation pipeline (5 stages), data persistence, external service integration
- **Input**: Feature epics, API specifications, data models, prompt templates from Architecture Agent
- **Output**: REST APIs, generation logic, database schemas, service integrations, API documentation
- **AI Tool**: GitHub Copilot, Claude (via Cursor)
- **Coordination**: Receives specs from Architecture Agent, passes services to Integration Agent

#### Agent 4: Integration & Testing Agent
- **Primary Responsibility**: Merge frontend/backend work, conduct testing, validate requirements, ensure system coherence
- **Input**: Flutter app, backend services, test criteria from development agents
- **Output**: Integrated features, test reports, bug findings, performance metrics, feedback for next iteration
- **AI Tool**: GitHub Copilot, ChatGPT (test strategy)
- **Coordination**: Receives implementations, sends feedback to Architecture Agent

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

### Sprint 1: Foundation & Core Setup (Weeks 8-9)
**Goal**: Build AI generation pipeline foundation and establish development infrastructure

**Completed**:
- [✓] Project proposal and architecture documentation
- [✓] Multi-agent coordination strategy defined
- [✓] Risk assessment and mitigation planning
- [✓] 7-week timeline with sprint breakdown

**In Progress**:
- [ ] Flutter project initialization and structure setup
- [ ] FastAPI backend scaffolding
- [ ] Mock job data creation (100+ listings)
- [ ] Job Analyzer implementation (Stage 1)
- [ ] Profile Compiler implementation (Stage 2)
- [ ] Basic LLM integration with prompt templates

**Challenges**: None yet (Sprint 1 just beginning)

**AI Coordination**: Architecture Agent (ChatGPT) produced initial specifications. Frontend Agent (Copilot) and Backend Agent (Copilot/Claude) beginning implementation. See `docs/ai-coordination-log.md` for detailed interaction logs.

---

### Sprint 2: Resume Generation Quality & Validation (Week 9)
**Goal**: Refine AI generation quality with validation and context management

**Status**: Not started

**Planned Tasks**:
- [ ] Document Generator implementation (Stage 3)
- [ ] Quality Validator with ATS scoring (Stage 4)
- [ ] Context management for sliding window LLM calls
- [ ] Factual consistency checker
- [ ] Resume editing interface in Flutter
- [ ] Generation quality testing across job types

---

### Sprint 3: Cover Letter & PDF Export (Week 10)
**Goal**: Add cover letter generation and professional PDF export

**Status**: Not started

---

### Sprint 4: Document Management & UX (Week 11)
**Goal**: Build job search UI, saved jobs dashboard, document preview

**Status**: Not started

---

### Sprint 5: Integration & Performance (Week 12)
**Goal**: Connect frontend to backend, optimize generation speed, error handling

**Status**: Not started

---

### Sprint 6: Final Polish & Presentation (Weeks 13-14)
**Goal**: Comprehensive testing, UI polish, documentation, presentation preparation

**Status**: Not started

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

**Last Updated**: October 13, 2025 (Sprint 1 - Week 8)
