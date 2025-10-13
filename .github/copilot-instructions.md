
# JobWise – AI Coding Agent Instructions

## Project Status: Sprint 1 Planning → Implementation Phase
**Current State:** Documentation complete, implementation not yet started. No `mobile-app/` or `backend/` directories exist yet.  
**Next Step:** Create project structure and begin Sprint 1 implementation (Week 8-9).

---

## Project Architecture Overview

### Multi-Agent Development Pattern
Four specialized AI agents coordinate via handoff artifacts:
1. **Innovation & Architecture Agent** → Produces ADRs and feature epics with acceptance criteria
2. **Frontend Development Agent** → Implements Flutter mobile UI, receives specs from Architecture Agent
3. **Backend Development Agent** → Builds FastAPI services and AI pipeline, receives specs from Architecture Agent  
4. **Integration & Testing Agent** → Validates across services, provides feedback loop to Architecture Agent

See `docs/agent-coordination-diagram.md` for detailed workflow visualization.

### System Architecture
```
Mobile App (Flutter) ↔ API Gateway ↔ Backend Services (FastAPI)
                                   ↓
                      AI Generation Pipeline (5 stages)
                                   ↓
                    Job Analyzer → Profile Compiler → Document Generator → Quality Validator → PDF Exporter
```

**AI Pipeline Context Management:** Uses sliding window approach with 8000 token windows and 500 token overlap. Token allocation per stage: Profile (2000), Job Analysis (1500), Resume Gen (3000), Optimization (1500). Details in `docs/project-proposal.md` lines 360–410.

**Environment Strategy:** Mock data (JSON) and in-memory services for development; production uses real APIs (Indeed/LinkedIn), PostgreSQL, Redis, S3. See `docs/architecture-diagram.md` for dev/prod mappings.

---

## Getting Started: Initial Setup

### Creating Project Structure
Reference layouts in `project-structure-examples/`:
- `python-structure-example.md` for backend (FastAPI)
- `react-native-structure-example.md` for mobile patterns (adapt for Flutter)

**Backend Setup (when creating `backend/`):**
```powershell
# Windows PowerShell commands
mkdir backend; cd backend
python -m venv venv
.\venv\Scripts\activate
# Then create requirements.txt with: fastapi, uvicorn, openai, pydantic, etc.
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend Setup (when creating `mobile-app/`):**
```powershell
flutter create mobile_app
cd mobile_app
flutter pub get
flutter run  # Hot reload enabled
```

### Required .gitignore
Use templates from `gitignore-templates/`:
- `gitignore-python.txt` for `backend/`
- `gitignore-flutter.txt` for `mobile-app/`

---

## Development Workflows

### Sprint Execution Pattern
1. Read current sprint in `docs/as-instructions.md` (tracks Weeks 8-14)
2. Check `docs/timeline.md` for week-specific tasks and dependencies
3. Create ADR in `docs/` for architectural decisions (format: rationale, alternatives, consequences)
4. Log all AI interactions in `docs/ai-coordination-log.md` with prompt evolution notes
5. Update sprint progress in `docs/as-instructions.md` after completing tasks

### Testing Requirements
- **Generation Quality:** Test across job types (Software Engineer, Data Scientist, Business Analyst) per Risk T6 in `docs/risk-assessment-matrix.md`
- **ATS Compliance:** Validate PDF exports with Jobscan or Resume Worded scanners (Week 10+)
- **Failure Scenarios:** Simulate LLM rate limits, API failures, circuit breaker activation (Week 12)
- **Token Management:** Monitor actual vs. budgeted token usage; adjust window sizes if exceeding limits

### LLM Prompt Engineering Standards
Every generation prompt MUST follow this structure:
1. **System Role:** Define AI's persona and constraints
2. **Task Specification:** Include JSON schema for structured output
3. **Context Injection:** Job description + relevant resume sections
4. **Quality Constraints:** ATS keywords, factual consistency, readability targets
5. **Few-Shot Examples:** 2-3 examples for complex tasks (job parsing, content selection)

**Dynamic Token Adjustment:** If context exceeds budget, prioritize in order: (1) task spec, (2) job requirements, (3) most relevant resume sections, (4) secondary context.

---

## Project-Specific Conventions

### Error Handling Patterns
- **Frontend:** Offline-first with local cache, optimistic UI updates, graceful degradation when backend unavailable
- **Backend:** Circuit breakers for external APIs (LLM/job services), exponential backoff retries (3 attempts), fallback to mock data if all fail
- **Generation Pipeline:** Failed validation triggers single stricter regen attempt; LLM timeout returns last cached version or empty state

### State Management
- **Flutter:** Use Provider or Riverpod (choose one in Sprint 2, document in ADR)
- **Backend:** PostgreSQL for generation state/history, Redis for caching job listings and LLM responses

### File Naming & Organization
- **Mock Data:** Store in `backend/data/mock_jobs.json` (100+ diverse job listings required)
- **Prompt Templates:** Keep in `backend/prompts/` with version numbers (e.g., `job_analyzer_v2.txt`)
- **Test Jobs:** Create `backend/data/test_cases/` with edge cases (missing sections, long descriptions, unusual formats)

---

## External Dependencies & Integration

### LLM Provider Configuration
- **Development:** OpenAI GPT-3.5-turbo (cost control), switch via `OPENAI_API_KEY` environment variable
- **Production:** GPT-4 or Claude 3 as primary, fallback to GPT-3.5 on rate limit (implement in Sprint 3)
- **Rate Limiting:** Track token usage per `docs/risk-assessment-matrix.md` Risk T1; set alerts at 80% of daily budget

### Job Data Sources  
- **Development:** Use mock JSON with 100+ realistic job descriptions covering diverse roles, industries, seniority levels
- **Production:** Indeed API (primary), LinkedIn API (fallback)—defer to Weeks 13-14 per timeline

### PDF Generation
- **Flutter Implementation:** `pdf` package for client-side generation (target: Sprint 3-4)
- **Backend Alternative:** Puppeteer with headless Chrome for complex layouts (if Flutter PDF insufficient)
- **ATS Requirements:** Single-column layout, standard fonts (Arial, Calibri), no images/tables in ATS version, test with free scanners

---

## Critical Files & Documentation

### Must-Read Before Coding
1. `docs/project-proposal.md` – Complete system design, agent specs (lines 100-200), context management (lines 360-410)
2. `docs/architecture-diagram.md` – Service boundaries and dev/prod environment mappings
3. `docs/timeline.md` – Week-by-week task breakdown with Gantt chart visualization
4. `docs/risk-assessment-matrix.md` – Known risks and mitigation strategies (refer when implementing related features)

### Active Development Tracking
- `docs/as-instructions.md` – Sprint status, current goals, blockers (update after every major task)
- `docs/ai-coordination-log.md` – AI interaction history with prompt refinements (log all significant AI assistance)

### Reference Materials
- `project-structure-examples/` – Template layouts for backend and mobile architecture
- `assignment-instructions/` – Course requirements and sprint workshop guidance

---

## Common Pitfalls & Solutions

**Pitfall:** Implementing features before creating ADR  
**Solution:** Always document architectural decisions in `docs/` with rationale BEFORE coding.

**Pitfall:** Exceeding LLM token budgets  
**Solution:** Use token counters (tiktoken for OpenAI), implement aggressive caching, compress context via semantic summarization.

**Pitfall:** Creating non-ATS-compatible PDFs  
**Solution:** Start with plain-text template, validate with free ATS scanners before adding visual enhancements.

**Pitfall:** Forgetting to log AI interactions  
**Solution:** Document prompt evolution in `docs/ai-coordination-log.md` immediately after AI assistance sessions.

---

**Update this file when discovering new patterns. Reference specific files/line numbers for examples.**
