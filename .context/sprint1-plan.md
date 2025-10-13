# Sprint 1 Detailed Plan - Week 9 Implementation

**Project:** JobWise - AI-Powered Job Application Assistant  
**Sprint Duration:** Week 8 (Planning) → Week 9 (Implementation)  
**Sprint Goal:** Establish project foundation, AI coordination infrastructure, and core generation pipeline  
**Deliverable Date:** Monday, October 13, 2025 (Peer Review)

---

## Sprint 1 Overview

### Primary Objectives
1. **AI Agent Infrastructure**: Create chatmode files defining roles, personas, and coordination patterns for all four agents
2. **Project Structure Setup**: Initialize Flutter mobile app and FastAPI backend with professional folder organization
3. **Development Documentation**: Establish ADR templates, prompt libraries, and coordination logs
4. **Core Pipeline Foundation**: Implement Job Analyzer and Profile Compiler (Stages 1-2 of generation pipeline)
5. **Mock Data Creation**: Build comprehensive mock job listings dataset (100+ entries)
6. **LLM Integration**: Configure OpenAI API integration with prompt templates

### Success Criteria
- All agents have defined chatmode files with clear roles and responsibilities
- Flutter and FastAPI projects initialized with working development environments
- At least 2 AI coordination log entries documenting agent interactions
- Job Analyzer successfully parses mock job descriptions into structured data
- Profile Compiler extracts and structures user profile information
- Basic LLM integration functional with test prompt responses
- Monday peer review demonstrates foundation for Sprint 2 implementation

---

## Part 1: AI Agent Infrastructure Setup

### Task 1.1: Create Chatmode Files for All Agents

**Deliverables**: Four chatmode configuration files in `.context/agents/`

#### 1.1.1: Innovation & Architecture Agent Chatmode
**File**: `.context/agents/innovation-architecture-agent.md`

**Content Structure**:
```markdown
# Innovation & Architecture Agent - Chatmode Configuration

## Agent Persona
Expert system architect and technical strategist specializing in AI-powered application design, 
with deep knowledge of mobile development patterns, backend service orchestration, and LLM integration strategies.

## Primary Responsibilities
- Generate Architecture Decision Records (ADRs) for major technical choices
- Create feature epics with clear acceptance criteria and implementation guidance
- Propose architectural improvements based on performance metrics and test results
- Maintain project vision and ensure technical coherence across development cycles
- Analyze integration feedback to inform next iteration planning

## Input Sources
- Current system state and codebase structure
- Performance metrics from Integration Agent
- Test results and quality reports
- User feedback and requirements changes
- Technology landscape and best practices research

## Output Artifacts
1. **ADRs**: Structured documents in `docs/adrs/` following format:
   - Context and Problem Statement
   - Decision and Rationale
   - Alternatives Considered
   - Consequences and Trade-offs
   - Implementation Guidance

2. **Feature Epics**: Specifications in `docs/epics/` including:
   - User stories and use cases
   - Acceptance criteria (measurable)
   - Technical approach and architecture
   - API contracts and data models
   - Testing strategy

3. **Technical Specifications**: Detailed docs for complex features
4. **Architecture Refinements**: Updates to system diagrams and component interactions

## Coordination Patterns
- **Initiates**: Development cycles by publishing ADRs and epics
- **Receives From**: Integration Agent (test reports, performance metrics, bug findings)
- **Provides To**: Frontend and Backend Development Agents (specifications and guidance)
- **Escalation**: Consult when architectural decisions impact multiple systems

## Context Handoff Protocol
When passing specifications to development agents:
1. Reference ADR number and epic ID
2. Provide clear acceptance criteria checklist
3. Include API contracts with request/response examples
4. Link to relevant documentation and diagrams
5. Note dependencies on other features or services

## Failure Handling
- Non-blocking: Development continues with existing specifications if agent unavailable
- Specifications versioned in Git; use latest approved ADR if new guidance unavailable
- Critical decisions escalate to manual review if agent cannot reach consensus

## Prompt Engineering Guidelines
- Frame architectural questions with full system context
- Request alternatives analysis for major decisions
- Ask for specific examples and edge case considerations
- Request validation against project constraints (budget, timeline, tech stack)

## AI Tool Recommendation
**Primary**: ChatGPT (GPT-4) for strategic thinking and architectural analysis
**Alternative**: Claude (Anthropic) for complex multi-system reasoning

## Example Interaction
**Input**: "Current integration tests show 45-second generation time. Analyze performance and propose optimization."
**Expected Output**: ADR documenting performance analysis, proposed caching strategy, token budget optimization, 
and implementation guidance for Backend Agent with measurable performance targets.
```

#### 1.1.2: Frontend Development Agent Chatmode
**File**: `.context/agents/frontend-development-agent.md`

**Content Structure**:
```markdown
# Frontend Development Agent - Chatmode Configuration

## Agent Persona
Expert Flutter mobile developer with deep knowledge of Material Design, state management patterns (Provider/Riverpod), 
offline-first architectures, and cross-platform mobile best practices.

## Primary Responsibilities
- Implement Flutter UI components following Material Design guidelines
- Build navigation flows and routing logic
- Integrate with backend APIs using http/dio packages
- Implement local data persistence and caching strategies
- Create responsive layouts for various screen sizes
- Ensure accessibility compliance (WCAG 2.1)
- Write widget tests and integration tests

## Input Sources
- Feature epics and UI/UX specifications from Architecture Agent
- API contracts and data models
- Design mockups or wireframes
- User feedback on existing UI implementations

## Output Artifacts
1. **Flutter Widgets**: Reusable components in `mobile_app/lib/widgets/`
2. **Screen Implementations**: Full screens in `mobile_app/lib/screens/`
3. **State Management**: Providers/controllers in `mobile_app/lib/providers/`
4. **API Service Clients**: HTTP integration in `mobile_app/lib/services/`
5. **Implementation Summaries**: Markdown docs describing component usage, state flow, API dependencies

## Coordination Patterns
- **Receives From**: Architecture Agent (feature specs, API contracts)
- **Provides To**: Integration Agent (completed UI implementations)
- **Collaborates With**: Backend Agent (API integration testing)

## Context Handoff Protocol
When completing a feature:
1. Document component usage patterns and props/parameters
2. List API endpoints consumed and data models expected
3. Note any local state management or caching logic
4. Provide navigation paths and integration points with existing screens
5. Include screenshots or screen recordings of implemented UI

## Flutter-Specific Guidelines
- Use `const` constructors wherever possible for performance
- Implement proper widget disposal for controllers and streams
- Follow Flutter naming conventions (lowerCamelCase for variables, UpperCamelCase for classes)
- Extract hardcoded strings to localization files
- Use theme data for consistent styling across app

## State Management Decisions
**To Be Decided in Sprint 2**: Provider vs Riverpod
- Document choice in ADR with rationale
- Ensure all state management follows chosen pattern consistently

## Error Handling Pattern
- Show user-friendly error messages via SnackBars or AlertDialogs
- Implement retry mechanisms for failed API calls
- Graceful degradation when offline (show cached data)
- Log errors to console/monitoring service

## Testing Requirements
- Widget tests for all reusable components
- Integration tests for critical user flows (search → save → generate)
- Test offline behavior with mock data
- Accessibility testing with screen readers

## AI Tool Recommendation
**Primary**: GitHub Copilot (inline code suggestions, widget scaffolding)
**Secondary**: Claude (via Cursor) for complex UI logic and refactoring

## Example Interaction
**Input**: "Implement job card widget with swipe gestures. Epic ID: EPIC-003. API: GET /jobs/:id"
**Expected Output**: 
- JobCard widget in `widgets/job_card.dart`
- Swipe gesture handling with left (save) and right (skip) actions
- Integration with JobService API client
- Widget tests covering render, tap, and swipe interactions
- Implementation summary documenting usage and props
```

#### 1.1.3: Backend Development Agent Chatmode
**File**: `.context/agents/backend-development-agent.md`

**Content Structure**:
```markdown
# Backend Development Agent - Chatmode Configuration

## Agent Persona
Expert Python backend engineer specializing in FastAPI, AI service integration, database design, 
and high-performance API development with experience in LLM pipeline orchestration.

## Primary Responsibilities
- Build RESTful API endpoints following OpenAPI 3.0 specification
- Implement AI generation pipeline (5 stages: Job Analyzer → Profile Compiler → Document Generator → Quality Validator → PDF Exporter)
- Design and implement database schemas (SQLite dev, PostgreSQL prod)
- Integrate external APIs (LLM providers, job boards)
- Implement caching strategies (in-memory dev, Redis prod)
- Write comprehensive API documentation
- Create unit and integration tests for all endpoints

## Input Sources
- Feature epics and API specifications from Architecture Agent
- Data model requirements
- LLM prompt templates from Architecture Agent
- Performance requirements and optimization targets

## Output Artifacts
1. **API Endpoints**: Route handlers in `backend/routers/`
2. **Business Logic Services**: Core logic in `backend/services/`
3. **Data Models**: Pydantic schemas in `backend/models/`
4. **Database Schemas**: SQLAlchemy/migrations in `backend/db/`
5. **Prompt Templates**: Versioned prompts in `backend/prompts/`
6. **API Documentation**: Auto-generated from FastAPI + manual guides
7. **Implementation Summaries**: Service dependencies, configuration, integration points

## Coordination Patterns
- **Receives From**: Architecture Agent (API specs, data models, prompt strategies)
- **Provides To**: Integration Agent (running services, API documentation)
- **Collaborates With**: Frontend Agent (API contract validation, integration testing)

## Context Handoff Protocol
When completing a service:
1. Document API endpoints with request/response examples
2. List service dependencies (databases, external APIs, environment variables)
3. Provide configuration requirements (API keys, connection strings)
4. Note error codes and handling strategies
5. Include performance characteristics (avg response time, rate limits)

## FastAPI Best Practices
- Use dependency injection for database sessions and services
- Implement Pydantic models for request/response validation
- Add proper HTTP status codes for all responses
- Use background tasks for long-running operations
- Implement comprehensive error handling middleware

## AI Generation Pipeline Design
**Stage 1 - Job Analyzer** (`services/job_analyzer.py`):
- Parse raw job descriptions
- Extract skills, requirements, responsibilities, ATS keywords
- Output structured JSON with confidence scores

**Stage 2 - Profile Compiler** (`services/profile_compiler.py`):
- Load master resume from database
- Score experiences/skills by relevance to job
- Select and rank content for document generation

**Stage 3 - Document Generator** (`services/document_generator.py`):
- Generate tailored resume using selected content
- Create personalized cover letter
- Apply ATS keyword optimization

**Stage 4 - Quality Validator** (`services/quality_validator.py`):
- Validate factual consistency against master resume
- Check ATS compliance (formatting, keywords)
- Assess readability and coherence

**Stage 5 - PDF Exporter** (`services/pdf_exporter.py`):
- Convert structured documents to professional PDFs
- Generate both ATS-optimized and visually-enhanced versions

## LLM Integration Standards
**Prompt Template Structure**:
```python
{
    "system_role": "Define AI persona and constraints",
    "task_specification": "Clear task with JSON output schema",
    "context": "Job description + relevant resume sections",
    "quality_constraints": "ATS keywords, factual consistency, readability",
    "few_shot_examples": "2-3 examples for complex tasks"
}
```

**Token Management**:
- Profile extraction: 2000 tokens (low temperature 0.3)
- Job analysis: 1500 tokens (low temperature 0.3)
- Resume generation: 3000 tokens (moderate temperature 0.5)
- Optimization: 1500 tokens (balanced temperature 0.4)

**Error Handling**:
- Circuit breakers for external API calls
- Exponential backoff retry (3 attempts)
- Fallback to mock data if all retries fail
- Log all LLM interactions with token usage

## Testing Requirements
- Unit tests for all service functions (pytest)
- Integration tests for API endpoints
- Mock external API responses
- Test token budget compliance
- Validate generation quality across job types

## AI Tool Recommendation
**Primary**: GitHub Copilot (function implementation, test generation)
**Secondary**: Claude (via Cursor) for complex pipeline logic and optimization

## Example Interaction
**Input**: "Implement Job Analyzer service. Epic ID: EPIC-001. Extract skills, requirements, keywords from job description using GPT-3.5-turbo."
**Expected Output**:
- JobAnalyzer service class in `services/job_analyzer.py`
- LLM prompt template in `prompts/job_analyzer_v1.txt`
- Pydantic models for input/output
- Unit tests with mock LLM responses
- API endpoint in `routers/generation.py`
- Implementation doc with token usage and example outputs
```

#### 1.1.4: Integration & Testing Agent Chatmode
**File**: `.context/agents/integration-testing-agent.md`

**Content Structure**:
```markdown
# Integration & Testing Agent - Chatmode Configuration

## Agent Persona
Expert QA engineer and systems integrator with deep knowledge of full-stack testing strategies, 
continuous integration, performance validation, and cross-component system verification.

## Primary Responsibilities
- Merge frontend and backend implementations into cohesive features
- Conduct comprehensive testing (unit, integration, end-to-end)
- Validate features against epic acceptance criteria
- Perform performance benchmarking and optimization validation
- Execute security scanning and vulnerability checks
- Generate test reports and quality metrics
- Provide feedback to Architecture Agent for next iteration planning

## Input Sources
- Completed Flutter implementations from Frontend Agent
- Completed backend services from Backend Agent
- Test criteria and acceptance criteria from feature epics
- Performance targets from Architecture Agent

## Output Artifacts
1. **Integrated Features**: Merged code with frontend/backend coordination
2. **Test Reports**: Comprehensive test results in `docs/test-reports/`
3. **Bug Reports**: Issues found with reproduction steps
4. **Performance Metrics**: Response times, generation quality, token usage
5. **Feedback Summaries**: Recommendations for next iteration to Architecture Agent

## Coordination Patterns
- **Receives From**: Frontend Agent (UI implementations), Backend Agent (services)
- **Provides To**: Architecture Agent (test results, performance data, improvement suggestions)
- **Feedback Loop**: Informs next cycle of architectural decisions and feature prioritization

## Context Handoff Protocol
When completing integration testing:
1. List all integrated features with acceptance criteria validation results
2. Provide test coverage metrics (unit, integration, e2e)
3. Report performance benchmarks vs. targets
4. Document bugs found with severity ratings and reproduction steps
5. Recommend improvements or optimizations for next sprint

## Testing Strategy

### Unit Testing
- Frontend: Widget tests for all components
- Backend: Pytest for all service functions
- Target: >80% code coverage

### Integration Testing
- API contract validation between mobile app and backend
- Database CRUD operations
- LLM integration with mock responses
- Error handling and retry logic

### End-to-End Testing
- Complete user flows (search → save → generate → edit → export)
- Cross-platform testing (iOS, Android)
- Offline behavior validation
- Performance under load

### Quality Validation Testing
- Generation quality across diverse job types (Software Engineer, Data Scientist, Business Analyst)
- ATS compliance using free scanners (Jobscan, Resume Worded)
- Factual consistency validation
- Token budget compliance

### Performance Testing
- API response times (<2s for search, <30s for generation)
- Mobile app launch time (<3s)
- PDF generation speed
- Memory usage and battery impact

## Test Report Format
```markdown
# Test Report - Sprint X Feature Y

## Summary
- Features Tested: [list]
- Test Date: [date]
- Overall Status: Pass/Fail/Partial

## Acceptance Criteria Validation
- [ ] Criterion 1: PASS/FAIL (details)
- [ ] Criterion 2: PASS/FAIL (details)

## Test Coverage
- Unit Tests: X% coverage
- Integration Tests: Y scenarios
- E2E Tests: Z user flows

## Performance Metrics
- Metric 1: Actual vs Target
- Metric 2: Actual vs Target

## Bugs Found
1. Bug Title (Severity: High/Medium/Low)
   - Reproduction steps
   - Expected vs Actual behavior
   - Proposed fix

## Recommendations
- Optimization suggestions
- Architecture improvements
- Next sprint priorities
```

## Integration Workflow
1. Pull latest code from both frontend and backend branches
2. Merge into integration branch
3. Resolve any conflicts or API mismatches
4. Run full test suite
5. Document results and create feedback report
6. Push integrated code to main branch if all tests pass

## AI Tool Recommendation
**Primary**: GitHub Copilot (test generation, test data creation)
**Secondary**: ChatGPT (test strategy design, edge case identification)

## Example Interaction
**Input**: "Integrate job search feature (frontend) with job listing API (backend). Validate against EPIC-002 acceptance criteria."
**Expected Output**:
- Merged integration branch with resolved conflicts
- Test report showing API integration successful
- Performance metrics (search response time: 1.2s vs 2s target - PASS)
- Bug report if issues found (e.g., pagination edge case)
- Feedback: "Job search working. Recommend caching frequently searched terms for next sprint."
```

### Task 1.2: Create Agent Coordination Documentation
**File**: `.context/agent-coordination-workflow.md`

**Content**:
- Workflow diagram showing agent handoff sequence
- Decision matrix for when to consult which agent
- Escalation protocol for conflicting recommendations
- Version control strategy for agent-generated artifacts

---

## Part 2: Project Structure Setup

### Task 2.1: Initialize Flutter Mobile Application

**Commands (PowerShell)**:
```powershell
# Navigate to project root
cd d:\Desktop\CPT_S483\course-project-Harry908

# Create Flutter project
flutter create mobile_app

# Navigate into Flutter project
cd mobile_app

# Test initial setup
flutter pub get
flutter run -d chrome  # Or android/ios
```

**Folder Structure to Create**:
```
mobile_app/
├── lib/
│   ├── main.dart                   # App entry point
│   ├── screens/                    # UI screens
│   │   ├── home_screen.dart
│   │   ├── job_search_screen.dart
│   │   ├── saved_jobs_screen.dart
│   │   ├── document_editor_screen.dart
│   │   └── profile_screen.dart
│   ├── widgets/                    # Reusable components
│   │   ├── job_card.dart
│   │   ├── document_preview.dart
│   │   └── loading_indicator.dart
│   ├── models/                     # Data models
│   │   ├── job.dart
│   │   ├── user_profile.dart
│   │   ├── generated_document.dart
│   │   └── api_response.dart
│   ├── services/                   # API clients
│   │   ├── job_service.dart
│   │   ├── generation_service.dart
│   │   └── storage_service.dart
│   ├── providers/                  # State management (TBD: Provider vs Riverpod)
│   │   ├── job_provider.dart
│   │   └── document_provider.dart
│   ├── utils/                      # Helper functions
│   │   ├── constants.dart
│   │   └── validators.dart
│   └── config/
│       └── api_config.dart         # API endpoints, keys
├── test/                           # Tests
│   ├── widget_test/
│   └── integration_test/
├── assets/                         # Images, fonts
├── pubspec.yaml                    # Dependencies
└── .gitignore                      # Use gitignore-flutter.txt
```

**Key Dependencies to Add in `pubspec.yaml`**:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0                      # HTTP client
  provider: ^6.0.5                  # State management (or riverpod)
  shared_preferences: ^2.2.2        # Local storage
  pdf: ^3.10.4                      # PDF generation
  path_provider: ^2.1.1             # File system access

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
```

**Deliverable**: Working Flutter app that launches successfully

---

### Task 2.2: Initialize FastAPI Backend

**Commands (PowerShell)**:
```powershell
# Navigate to project root
cd d:\Desktop\CPT_S483\course-project-Harry908

# Create backend directory
mkdir backend
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Create requirements.txt (see below)
# Then install dependencies
pip install -r requirements.txt

# Create main.py (basic FastAPI app)
# Run development server
uvicorn main:app --reload
```

**Folder Structure to Create**:
```
backend/
├── main.py                         # FastAPI app entry point
├── routers/                        # API route handlers
│   ├── __init__.py
│   ├── jobs.py                     # Job search/listing endpoints
│   ├── generation.py               # Document generation endpoints
│   └── users.py                    # User profile endpoints
├── services/                       # Business logic
│   ├── __init__.py
│   ├── job_analyzer.py             # Stage 1: Job parsing
│   ├── profile_compiler.py         # Stage 2: Profile analysis
│   ├── document_generator.py       # Stage 3: Resume/cover letter generation
│   ├── quality_validator.py        # Stage 4: Validation
│   └── pdf_exporter.py             # Stage 5: PDF export
├── models/                         # Pydantic models
│   ├── __init__.py
│   ├── job.py
│   ├── user_profile.py
│   ├── generation_request.py
│   └── generated_document.py
├── prompts/                        # LLM prompt templates
│   ├── job_analyzer_v1.txt
│   ├── profile_compiler_v1.txt
│   ├── resume_generator_v1.txt
│   └── cover_letter_generator_v1.txt
├── data/                           # Mock data
│   ├── mock_jobs.json              # 100+ job listings
│   ├── sample_profile.json
│   └── test_cases/
│       ├── software_engineer.json
│       ├── data_scientist.json
│       └── business_analyst.json
├── db/                             # Database (SQLite initially)
│   ├── models.py                   # SQLAlchemy models
│   └── database.py                 # DB connection
├── tests/                          # Backend tests
│   ├── __init__.py
│   ├── test_job_analyzer.py
│   ├── test_profile_compiler.py
│   └── test_generation_pipeline.py
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── .gitignore                      # Use gitignore-python.txt
```

**requirements.txt**:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-dotenv==1.0.0
openai==1.10.0
sqlalchemy==2.0.25
pytest==7.4.4
httpx==0.26.0                       # For testing async endpoints
```

**Basic `main.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="JobWise API",
    description="AI-powered job application assistant",
    version="1.0.0"
)

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "JobWise API v1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Deliverable**: FastAPI server running at http://localhost:8000 with health check endpoint

---

### Task 2.3: Setup .gitignore Files

**Commands**:
```powershell
# Copy Flutter .gitignore template
Copy-Item gitignore-templates\gitignore-flutter.txt mobile_app\.gitignore

# Copy Python .gitignore template
Copy-Item gitignore-templates\gitignore-python.txt backend\.gitignore
```

**Verify Exclusions**: Ensure `.env`, `venv/`, `build/`, and IDE folders are ignored

---

### Task 2.4: Create Environment Configuration

**Files to Create**:

`.env.example` (root):
```env
# LLM Provider
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Database
DATABASE_URL=sqlite:///./jobwise.db

# API Configuration
API_HOST=localhost
API_PORT=8000

# Flutter App
FLUTTER_API_URL=http://localhost:8000
```

`.env` (root, not committed):
- Copy from `.env.example` and add actual API keys

---

## Part 3: Development Documentation

### Task 3.1: Create ADR Template

**File**: `docs/adrs/ADR-TEMPLATE.md`

**Content**:
```markdown
# ADR-XXX: [Decision Title]

**Status**: Proposed | Accepted | Deprecated | Superseded  
**Date**: YYYY-MM-DD  
**Deciders**: [Agent Name(s)]  
**Epic**: [Related Epic ID if applicable]

---

## Context and Problem Statement

[Describe the context and background. What is the architectural challenge or decision that needs to be made?]

[What are the constraints? Technical limitations, budget, timeline, team expertise?]

---

## Decision Drivers

* [Driver 1 - e.g., performance requirement]
* [Driver 2 - e.g., cost constraint]
* [Driver 3 - e.g., development velocity]

---

## Considered Options

### Option 1: [Name]
**Description**: [Brief explanation]
**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1]
- [Disadvantage 2]

### Option 2: [Name]
[Same structure as Option 1]

---

## Decision Outcome

**Chosen Option**: [Selected option]

**Rationale**: [Explain why this option was selected over alternatives. Connect back to decision drivers.]

---

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Change 1]

---

## Implementation Guidance

[Specific steps or considerations for implementing this decision]

**For Frontend Agent**:
- [Specific guidance]

**For Backend Agent**:
- [Specific guidance]

**Configuration Changes**:
- [Any config or environment changes needed]

---

## Validation and Measurement

[How will we know if this decision was successful? What metrics or outcomes should we track?]

---

## References

- [Link to related documentation]
- [External resources consulted]
- [Related ADRs]
```

---

### Task 3.2: Create Epic Template

**File**: `docs/epics/EPIC-TEMPLATE.md`

**Content**:
```markdown
# EPIC-XXX: [Epic Title]

**Status**: Draft | In Progress | Review | Complete  
**Sprint**: [Sprint Number]  
**Created**: YYYY-MM-DD  
**Owner**: [Agent Name]  
**ADR**: [Related ADR if applicable]

---

## Overview

[High-level description of the feature or capability being built]

---

## User Stories

### Story 1: [Title]
**As a** [user type]  
**I want** [capability]  
**So that** [benefit]

**Acceptance Criteria**:
- [ ] Criterion 1 (measurable, testable)
- [ ] Criterion 2
- [ ] Criterion 3

### Story 2: [Title]
[Same structure]

---

## Technical Approach

### Architecture Overview
[Describe how this feature fits into the overall system architecture]

### Components Involved
- **Frontend**: [Specific screens/widgets to implement]
- **Backend**: [Specific services/endpoints to implement]
- **Database**: [Schema changes if any]
- **External Services**: [Third-party integrations]

---

## API Contracts

### Endpoint 1: [HTTP Method] /api/path
**Request**:
```json
{
  "field1": "type",
  "field2": "type"
}
```

**Response (200 Success)**:
```json
{
  "result": "data"
}
```

**Error Codes**:
- 400: Bad Request (details)
- 401: Unauthorized
- 500: Internal Server Error

---

## Data Models

### Model 1: [Name]
```python
class ModelName(BaseModel):
    field1: str
    field2: int
    field3: Optional[List[str]]
```

---

## Implementation Tasks

### Frontend Tasks
- [ ] Task 1: Create [widget/screen] (Est: Xh)
- [ ] Task 2: Implement [feature] (Est: Xh)
- [ ] Task 3: Add tests (Est: Xh)

### Backend Tasks
- [ ] Task 1: Create [endpoint] (Est: Xh)
- [ ] Task 2: Implement [service] (Est: Xh)
- [ ] Task 3: Add tests (Est: Xh)

**Total Estimated Effort**: [X hours]

---

## Testing Strategy

### Unit Tests
- [Frontend: Widget tests for components]
- [Backend: Service function tests]

### Integration Tests
- [API integration tests]
- [Database CRUD tests]

### End-to-End Tests
- [User flow: step by step]

---

## Success Metrics

- [Metric 1: e.g., Response time < 2s]
- [Metric 2: e.g., Test coverage > 80%]
- [Metric 3: e.g., Zero critical bugs in testing]

---

## Dependencies

- [Depends on Epic XXX being complete]
- [Requires API key for service Y]
- [Blocked by architectural decision Z]

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk 1 | High/Med/Low | High/Med/Low | [Strategy] |

---

## References

- [Link to ADR]
- [Link to design docs]
- [External API documentation]
```

---

### Task 3.3: Create Prompt Library Structure

**Directory**: `backend/prompts/`

**Files to Create**:

1. **`job_analyzer_v1.txt`**:
```
You are an expert job description analyzer. Extract structured information from the provided job posting.

TASK:
Parse the following job description and output a JSON object with these fields:
- job_title: string
- company_name: string
- required_skills: array of strings (technical and soft skills)
- experience_requirements: object with {years: int, domains: array}
- key_responsibilities: array of strings (main duties)
- ats_keywords: array of strings (critical terms for ATS systems)
- company_context: object with {industry: string, size: string, culture_indicators: array}

CONSTRAINTS:
- Extract only information explicitly stated in the job description
- If a field is not mentioned, use null or empty array
- Normalize skill names (e.g., "JavaScript" not "javascript" or "JS")
- Identify ATS keywords by frequency and importance

JOB DESCRIPTION:
{job_description_text}

OUTPUT FORMAT:
```json
{
  "job_title": "...",
  "company_name": "...",
  ...
}
```
```

2. **`profile_compiler_v1.txt`**:
```
You are an expert resume analyst. Analyze a master resume and score experiences based on relevance to a job.

TASK:
Given the master resume and job requirements below, score each experience/skill by relevance (0-100).

SCORING CRITERIA:
- Keyword overlap with job requirements (40%)
- Semantic similarity of responsibilities (30%)
- Recency of experience (20%)
- Quantifiable achievements matching job needs (10%)

OUTPUT FORMAT:
```json
{
  "experiences": [
    {
      "id": "exp_001",
      "title": "Software Engineer",
      "company": "TechCorp",
      "relevance_score": 85,
      "matching_keywords": ["Python", "API", "Agile"],
      "key_achievements": ["..."]
    }
  ],
  "skills": [
    {
      "name": "Python",
      "proficiency": "Expert",
      "relevance_score": 95
    }
  ]
}
```

MASTER RESUME:
{master_resume_text}

JOB REQUIREMENTS:
{job_requirements_json}
```

3. **`README.md`** (in `backend/prompts/`):
```markdown
# LLM Prompt Templates

This directory contains versioned prompt templates for the AI generation pipeline.

## Naming Convention
`[stage]_[purpose]_v[version].txt`

Example: `job_analyzer_v1.txt`

## Version Control
- Increment version number when making significant changes
- Document changes in this README
- Keep old versions for comparison and rollback

## Prompt Engineering Standards
All prompts must follow this structure:
1. **System Role**: Define AI's persona and expertise
2. **Task Specification**: Clear task with output schema
3. **Context Injection**: Placeholders for dynamic content (e.g., {job_description_text})
4. **Quality Constraints**: ATS compliance, factual accuracy, readability
5. **Output Format**: JSON schema or structured text format

## Token Budget Allocation
| Stage | Template | Target Tokens | Temperature |
|-------|----------|---------------|-------------|
| Job Analyzer | job_analyzer_v1.txt | 1500 | 0.3 |
| Profile Compiler | profile_compiler_v1.txt | 2000 | 0.3 |
| Resume Generator | resume_generator_v1.txt | 3000 | 0.5 |
| Cover Letter | cover_letter_generator_v1.txt | 2500 | 0.5 |
| Quality Validator | quality_validator_v1.txt | 1500 | 0.4 |

## Change Log
**v1 (2025-10-13)**: Initial prompt templates for Sprint 1 implementation
```

---

### Task 3.4: Create Mock Data

**File**: `backend/data/mock_jobs.json`

**Requirements**:
- At least 100 diverse job listings
- Cover multiple roles: Software Engineer, Data Scientist, Business Analyst, Product Manager, UX Designer, etc.
- Vary seniority levels: Intern, Entry-level, Mid-level, Senior, Lead
- Include different industries: Tech, Finance, Healthcare, Education, Retail
- Each job should have: title, company, description (200-500 words), requirements, responsibilities, keywords

**Sample Entry Structure**:
```json
{
  "id": "job_001",
  "title": "Software Engineer - Backend",
  "company": "TechCorp Inc.",
  "location": "Seattle, WA",
  "type": "Full-time",
  "seniority": "Mid-level",
  "industry": "Technology",
  "description": "[Full job description 200-500 words]",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
  "preferred_skills": ["Kubernetes", "GraphQL", "Redis"],
  "experience_years": 3,
  "responsibilities": [
    "Design and implement RESTful APIs",
    "Optimize database queries for performance",
    "Collaborate with frontend team on API contracts"
  ],
  "benefits": ["Health insurance", "401k matching", "Remote work"],
  "posted_date": "2025-10-01",
  "application_deadline": "2025-11-01"
}
```

**Deliverable**: JSON file with 100+ realistic job listings

---

### Task 3.5: Setup AI Coordination Log

**File**: `docs/ai-coordination-log.md`

**Initial Content**:
```markdown
# AI Coordination Log - Sprint 1

## Purpose
This log tracks interactions with AI agents during development, documenting prompts, responses, 
refinements, and lessons learned. It serves as both a development journal and a resource for 
improving agent coordination strategies.

---

## Log Entry Template
```markdown
### Entry XXX - [Date] - [Agent Name]
**Context**: [What you were trying to accomplish]
**Prompt**: [The prompt or question you gave the AI]
**Response Summary**: [Key points from the response]
**Actions Taken**: [What you implemented based on the response]
**Refinements**: [How you adjusted the prompt or approach]
**Outcome**: [Success/Partial/Failed + details]
**Lessons Learned**: [Insights for future interactions]
```

---

## Sprint 1 Entries

[Entries will be added as agent interactions occur during Sprint 1]
```

---

### Task 3.6: Create Initial ADRs

**Files to Create**:

#### ADR-001: LLM Provider Selection
**File**: `docs/adrs/ADR-001-llm-provider-selection.md`

**Key Decisions**:
- Development: OpenAI GPT-3.5-turbo (cost control, fast iteration)
- Production: GPT-4 or Claude 3 (higher quality, better reasoning)
- Fallback strategy: Graceful degradation to cached/mock responses

#### ADR-002: State Management for Flutter
**File**: `docs/adrs/ADR-002-state-management.md`

**Status**: Proposed (to be finalized in Sprint 2)
**Options**: Provider vs Riverpod
**Decision Criteria**: Team familiarity, documentation quality, performance

#### ADR-003: Database Strategy
**File**: `docs/adrs/ADR-003-database-strategy.md`

**Key Decisions**:
- Development: SQLite (lightweight, no external dependencies)
- Production: PostgreSQL (scalability, reliability)
- Migration path: Use SQLAlchemy ORM for database abstraction

---

## Part 4: Core Pipeline Implementation

### Task 4.1: Implement Job Analyzer (Stage 1)

**File**: `backend/services/job_analyzer.py`

**Requirements**:
- Parse raw job description text
- Call OpenAI API with `job_analyzer_v1.txt` prompt
- Extract structured data: skills, requirements, responsibilities, keywords
- Handle API errors with retry logic
- Validate output JSON structure
- Log token usage

**Test Coverage**:
- Unit tests with mock LLM responses
- Test with diverse job descriptions from `mock_jobs.json`
- Validate extraction accuracy

**Deliverable**: Working Job Analyzer service with >80% extraction accuracy

---

### Task 4.2: Implement Profile Compiler (Stage 2)

**File**: `backend/services/profile_compiler.py`

**Requirements**:
- Load master resume from database or mock JSON
- Score experiences and skills by relevance to job requirements
- Use semantic similarity (cosine similarity on embeddings)
- Rank and select top content for document generation
- Output structured JSON with scored items

**Test Coverage**:
- Test scoring logic with known relevant/irrelevant experiences
- Validate ranking produces expected order
- Test with edge cases (empty resume, no matching skills)

**Deliverable**: Profile Compiler that selects relevant resume content based on job requirements

---

### Task 4.3: Basic LLM Integration Setup

**File**: `backend/services/llm_client.py`

**Requirements**:
- OpenAI API client wrapper
- Load API key from environment variables
- Implement retry logic with exponential backoff
- Track token usage per request
- Log all requests/responses for debugging
- Handle rate limits and errors gracefully

**Functions**:
```python
async def call_llm(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.5,
    max_tokens: int = 2000
) -> dict:
    """Call OpenAI API with error handling and logging"""
    pass

def count_tokens(text: str) -> int:
    """Estimate token count for prompt/response"""
    pass

def load_prompt_template(template_name: str, **kwargs) -> str:
    """Load prompt from prompts/ directory and inject variables"""
    pass
```

**Test Coverage**:
- Mock API responses for testing
- Test retry logic with simulated failures
- Validate token counting accuracy

**Deliverable**: Robust LLM client utility used across all generation stages

---

### Task 4.4: Create API Endpoints

**File**: `backend/routers/generation.py`

**Endpoints to Implement**:

1. **POST /api/analyze-job**
   - Input: `{"job_description": "text"}`
   - Output: Structured job data from Job Analyzer
   - Use Case: Parse job description when user saves a job

2. **POST /api/compile-profile**
   - Input: `{"user_id": "id", "job_requirements": {...}}`
   - Output: Scored and ranked resume content
   - Use Case: Prepare content for generation

3. **GET /api/jobs**
   - Query params: `?keyword=python&seniority=mid-level`
   - Output: List of jobs from `mock_jobs.json`
   - Use Case: Job search functionality

**Test Coverage**:
- Integration tests for each endpoint
- Validate request/response schemas
- Test error handling (invalid input, missing data)

**Deliverable**: Working API endpoints consumable by Flutter app

---

## Part 5: Integration & Testing

### Task 5.1: Flutter-Backend Integration Test

**Goal**: Verify mobile app can communicate with backend

**Steps**:
1. Start backend server: `uvicorn main:app --reload`
2. Update Flutter `api_config.dart` with backend URL
3. Implement basic job search screen that calls `/api/jobs`
4. Test API call from Flutter app
5. Verify data displays correctly in UI

**Deliverable**: Flutter app successfully fetches and displays mock jobs from backend

---

### Task 5.2: Pipeline Integration Test

**Goal**: Verify Stage 1 and Stage 2 work together

**Test Scenario**:
1. Call `/api/analyze-job` with a sample job description
2. Save result in database
3. Call `/api/compile-profile` with job requirements + sample profile
4. Verify Profile Compiler uses Job Analyzer output correctly
5. Validate scored content is relevant and ranked properly

**Deliverable**: Integrated pipeline test passes, demonstrating Stages 1-2 work together

---

### Task 5.3: AI Coordination Log Update

**Action**: Document all AI agent interactions during Sprint 1

**Required Entries**:
- At least 2 entries per agent (8 total minimum)
- Include prompt refinements and lessons learned
- Document any architecture decisions influenced by AI suggestions
- Note what worked well and what didn't

**Deliverable**: Updated `docs/ai-coordination-log.md` with Sprint 1 interactions

---

## Part 6: Monday Peer Review Preparation

### Task 6.1: Update README with Sprint 1 Progress

**File**: `README.md`

**Section to Update**: Sprint 1 Status

**Content**:
```markdown
### Sprint 1: Foundation & Core Setup (Weeks 8-9)
**Goal**: Build AI generation pipeline foundation and establish development infrastructure

**Completed**:
- [✓] Project proposal and architecture documentation
- [✓] Multi-agent coordination strategy defined
- [✓] Risk assessment and mitigation planning
- [✓] 7-week timeline with sprint breakdown
- [✓] Flutter project initialized with working app
- [✓] FastAPI backend scaffolding complete
- [✓] Mock job data created (100+ listings)
- [✓] Job Analyzer implemented (Stage 1)
- [✓] Profile Compiler implemented (Stage 2)
- [✓] Basic LLM integration with prompt templates

**Challenges**:
- [Document any challenges faced and how you addressed them]

**AI Coordination**:
- Architecture Agent (ChatGPT) produced initial specifications and ADRs
- Frontend Agent (Copilot) scaffolded Flutter widgets and screens
- Backend Agent (Copilot/Claude) implemented generation pipeline services
- Integration Agent validated API contracts and tested pipeline
- See `docs/ai-coordination-log.md` for detailed interaction logs
```

---

### Task 6.2: Create Demonstration Script

**File**: `.context/demo-script-sprint1.md`

**Content**:
```markdown
# Sprint 1 Demonstration Script

## Demo Flow (3-5 minutes)

### 1. Project Structure Overview (30 seconds)
- Show folder structure in VS Code
- Highlight mobile_app/, backend/, docs/, .context/

### 2. Agent Chatmode Files (30 seconds)
- Open `.context/agents/innovation-architecture-agent.md`
- Briefly explain agent coordination approach
- Show how specs flow from Architecture → Development → Integration

### 3. Backend Services (1 minute)
- Navigate to `backend/services/job_analyzer.py`
- Explain Job Analyzer functionality
- Show prompt template in `backend/prompts/job_analyzer_v1.txt`
- Run backend: `uvicorn main:app --reload`
- Open http://localhost:8000/docs (Swagger UI)

### 4. API Testing (1 minute)
- In Swagger UI, test POST `/api/analyze-job`
- Use sample job description from `backend/data/mock_jobs.json`
- Show structured output (skills, requirements, keywords)

### 5. Flutter App (1 minute)
- Show `mobile_app/lib/screens/job_search_screen.dart`
- Run Flutter app: `flutter run -d chrome`
- Demonstrate job search calling backend API
- Show mock jobs displaying in UI

### 6. AI Coordination Evidence (30 seconds)
- Open `docs/ai-coordination-log.md`
- Highlight 2-3 entries showing agent interactions
- Show how prompts were refined based on results

### 7. Next Steps - Sprint 2 Preview (30 seconds)
- Mention Stage 3 (Document Generator) and Stage 4 (Quality Validator)
- Show epic for resume generation in `docs/epics/`
- Express confidence in Sprint 2 implementation readiness

## Backup Demos (if live demo fails)
- Screenshots of working features
- Screen recording of API tests
- Code walkthrough without running
```

---

### Task 6.3: Commit and Push All Changes

**Commands**:
```powershell
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Sprint 1 Complete: Foundation, AI agents, pipeline stages 1-2, mobile/backend setup"

# Push to GitHub
git push origin main
```

**Verify**:
- All files committed
- Repository accessible on GitHub
- README reflects current state
- AI coordination log has entries

---

### Task 6.4: Prepare for Peer Review

**Review Checklist**:

**Documentation**:
- [ ] README has Sprint 1 section with progress
- [ ] Agent chatmode files created and comprehensive
- [ ] At least 2 ADRs written
- [ ] AI coordination log has 8+ entries
- [ ] Prompt templates created with documentation

**Code**:
- [ ] Flutter app runs successfully
- [ ] Backend server runs successfully
- [ ] Job Analyzer service implemented
- [ ] Profile Compiler service implemented
- [ ] API endpoints functional and tested

**Testing**:
- [ ] Unit tests for backend services
- [ ] Integration test (Flutter → Backend API)
- [ ] Pipeline test (Stage 1 → Stage 2)

**Git**:
- [ ] All changes committed
- [ ] Pushed to GitHub
- [ ] Repository structure clear and organized

**Peer Review Deliverable**:
- [ ] GitHub repository link ready to share
- [ ] Demo script prepared for quick walkthrough
- [ ] Able to articulate Sprint 1 achievements and Sprint 2 goals

---

## Sprint 1 Success Metrics

### Must-Have (Required for Satisfactory)
- [x] All 4 agent chatmode files created with clear roles
- [x] Flutter and FastAPI projects initialized and running
- [x] Job Analyzer service extracting structured data from job descriptions
- [x] Profile Compiler scoring resume content by relevance
- [x] Mock data (100+ jobs) created
- [x] Basic LLM integration functional
- [x] API endpoints for job search and analysis
- [x] Flutter app displays jobs from backend API
- [x] AI coordination log with 8+ documented interactions
- [x] README updated with Sprint 1 progress

### Nice-to-Have (Above Satisfactory)
- [ ] Additional ADRs beyond the 3 required
- [ ] Widget tests for Flutter components
- [ ] Comprehensive unit test coverage (>80%)
- [ ] Advanced error handling and logging
- [ ] Performance optimization (response time <1s)
- [ ] More than 100 mock jobs (diversity)
- [ ] Draft implementation of Stage 3 (Document Generator)

---

## Timeline

**Friday, Oct 10 (Today)**: Planning and initial setup
- Create chatmode files
- Initialize Flutter and FastAPI projects
- Create folder structures

**Saturday-Sunday, Oct 11-12**: Implementation
- Implement Job Analyzer and Profile Compiler
- Create mock data
- Build API endpoints
- Integrate Flutter with backend

**Monday Morning, Oct 13**: Final polish and documentation
- Update README
- Finalize AI coordination log
- Test demo script
- Commit and push

**Monday Afternoon, Oct 13**: Peer Review
- Present Sprint 1 work
- Receive feedback
- Document peer review feedback for Sprint 2 planning

---

## Risk Mitigation

### Risk 1: LLM API Integration Issues
**Mitigation**: Use mock responses for testing; implement fallback to cached data

### Risk 2: Time Constraints
**Mitigation**: Prioritize must-have features; defer nice-to-haves to Sprint 2

### Risk 3: Flutter-Backend Integration Challenges
**Mitigation**: Start with simple GET endpoint test; use Postman for API validation before Flutter integration

### Risk 4: Insufficient AI Coordination Logging
**Mitigation**: Log interactions immediately after each agent session; set reminder to update log daily

---

## Sprint 1 Retrospective Questions (for Sprint 2 planning)

1. What went well in Sprint 1?
2. What challenges did we face, and how did we overcome them?
3. How effective was the multi-agent coordination approach?
4. Which agent was most helpful? Least helpful?
5. What should we improve for Sprint 2?
6. Are our acceptance criteria realistic and measurable?
7. Is the timeline sustainable, or do we need to adjust scope?

---

**END OF SPRINT 1 PLAN**

**Next Sprint Preview**: Sprint 2 will focus on Document Generator (Stage 3), Quality Validator (Stage 4), 
and refining generation quality with ATS optimization. Estimated duration: Week 10.
