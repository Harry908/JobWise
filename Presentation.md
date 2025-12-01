# Current App Overview

## Feature Outline

### JobWise - AI-Powered Job Application Assistant
**Status**: Sprints 1-5 Complete | **Platform**: Flutter Mobile + FastAPI Backend

**Core Capabilities**:
- **Authentication & User Management**: JWT-based auth, secure password hashing, token refresh
- **Profile Management**: Master resume CRUD with AI enhancement, comprehensive fields (personal info, experiences, education, skills, projects)
- **Job Management**: Save jobs from text input, browse mock jobs, track application status (8-status pipeline)
- **AI Generation**: Profile enhancement, content ranking, resume/cover letter generation using Groq LLM
- **Sample Management**: Upload resume/cover letter samples for writing style extraction

**Technical Highlights**:
- **AI Integration**: Live Groq LLM (llama-3.3-70b-versatile) for profile enhancement and generation
- **Performance**: Resume generation <3s, Cover letter 5-8s, ATS scoring 70-95%
- **Architecture**: Clean domain-driven design, async FastAPI, Riverpod state management
- **Testing**: 77+ backend tests passing, comprehensive end-to-end validation

**Current Status**: Production-ready for core job application workflow | **Next**: Sprint 6 Document Export & S3 Storage

---

# AI workflow

#### Agent 1: Business Analyst Agent (ChatGPT-5)
- **Primary Responsibility**: Requirements analysis, user story creation, business rule definition
- **Input**: Project proposal/overview
- **Output**: Requirements specifications, user stories
- **MCP Tool**: Web search
- **Coordination**: hands off output to Solutions Architect Agent

#### Agent 2: Solutions Architect Agent  (Opus 4.5 Sonnet 4.5)
- **Primary Responsibility**: Technical architecture design, system implementation and integration planning, API contract definition
- **Input**: Requirements , user features from Business Analyst, technical constraints, performance targets
- **Output**: System architecture diagrams, 
- **MCP Tool**: web search
- **Coordination**: Receives requirements from BA, create general architecture desing and handoff to Backend Developer 

#### Agent 3: Backend Developer Agent (Claude 4.5/4.0)
- **Primary Responsibility**: FastAPI endpoints, AI generation pipeline, database design, external service integration
- **Input**: API specifications, data models, business logic requirements from Solutions Architect
- **Output**:  database schemas, service integrations, API documentations
- **MCP Tool**: Python, pylance,...
- **Coordination**: Receives specs from SA, coordinates with Mobile Developer, delivers to QA Engineer

#### Agent 4: Mobile Developer Agent (Claude 4.5/4.0)
- **Primary Responsibility**: Flutter UI implementation, state management, mobile-specific features, offline capabilities
- **Input**:  API contracts from Backend Developer, technical requirements from Solutions Architect
- **Output**: Flutter widgets, screens, navigation logic, state management, mobile app implementation
- **AI Tool**: DART, web,...
- **Coordination**: Receives specs from SA, coordinates with Backend Developer, delivers to QA Engineer


#### Agent 5: QA Engineer Agent (Claude)
- **Primary Responsibility**: Integration testing, quality validation, performance testing, bug reporting, acceptance verification
- **Input**: Implemented features from development agents, acceptance criteria from BA, technical specs from SA
- **Output**: Test reports, performance metrics, bug reports, quality assessments, feedback for architecture improvements
- **MCP Tool**: Tests
- **Coordination**: Receives implementations from developers, provides feedback to Solutions Architect, validates against BA requirements

---

# Sprint 6: Document Export & Formatting System

## Key Features

**4 Professional Templates:**
- Modern (85% ATS) - Tech/Startups, clean design
- Classic (95% ATS) - Corporate/Finance, traditional
- Creative (75% ATS) - Design/Marketing, bold layout
- ATS-Optimized (98% ATS) - Enterprise, maximum parsability

**Export Capabilities:**
- PDF & DOCX generation with template styling
- Batch export (resume + cover letter as ZIP)
- Template customization (fonts, colors, spacing, margins)
- Preview before export
- Progress tracking during export

**File Management:**
- Download files to device
- Share via system share sheet
- View/export history with sorting/filtering
- Storage usage tracking (100MB free tier)
- Auto-delete expired files (30 days)

**Technical Highlights:**
- S3-backed cloud storage
- 9 API endpoints for full export workflow
- ATS-optimized formatting
- Cross-platform mobile support (iOS/Android)

**Sprint Duration**: 3 weeks  
**Status**: 🚀 Ready for Implementation

---

