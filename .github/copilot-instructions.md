
# JobWise – AI Coding Agent Instructions

## Project Status: Week 9 Sprint 1 Implementation Starting
**Current State:** Planning/documentation phase complete. Ready to begin implementation.  
**Next Step:** Create `mobile-app/` and `backend/` directories and start building.

---

## System Architecture (Planned)

### Multi-Agent Development Pattern
Five specialized AI agents coordinate via structured handoff protocols:
1. **Business Analyst Agent** (Claude 3.5 Sonnet) → Requirements analysis, user stories, acceptance criteria
2. **Solutions Architect Agent** (ChatGPT-4) → ADRs, technical architecture, API contracts
3. **Mobile Developer Agent** (GitHub Copilot) → Flutter UI, state management, widgets
4. **Backend Developer Agent** (GitHub Copilot) → FastAPI services, AI pipeline, data models  
5. **QA Engineer Agent** (GitHub Copilot/ChatGPT) → Testing strategy, integration, quality reports

**Context Handoff:** BA → SA → (MD + BD) → QA → SA (feedback loop)
See `docs/sprint1/agent-coordination-diagram-updated.md` for detailed coordination protocols.

### AI Generation Pipeline (5 Stages)
```
Job Analyzer → Profile Compiler → Document Generator → Quality Validator → PDF Exporter
```

**Token Management:** 8000 token windows, 500 token overlap between stages. Budget: Profile (2000), Job Analysis (1500), Resume Gen (3000), Optimization (1500).

**Tech Stack:** Flutter + FastAPI + OpenAI GPT-3.5-turbo (dev) / GPT-4 (prod)

---

## Getting Started: Sprint 1 Implementation

### Initial Project Structure Creation
**Backend Setup (PowerShell):**
```powershell
mkdir backend; cd backend
python -m venv venv
.\venv\Scripts\activate
# Create requirements.txt: fastapi, uvicorn, openai, pydantic
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend Setup (PowerShell):**
```powershell
flutter create mobile_app
cd mobile_app; flutter pub get; flutter run
```

### Essential Development Workflow
1. **Agent Coordination:** Follow handoff protocols in `docs/sprint1/agent-coordination-diagram-updated.md`
2. **Context Management:** Store artifacts in `.context/[agent]/` directories (ba/, sa/, md/, bd/, qa/)
3. **Documentation Approach:** BA starts requirements → SA creates ADRs → Dev agents implement → QA validates
4. **Sprint 1 Schedule:** BA (Mon) → SA (Tue) → MD+BD (Wed) → QA (Thu) → All agents (Fri)
5. **Testing Strategy:** Validate across job types with QA agent leading integration testing

### Key File Patterns
- **Context Artifacts:** `.context/ba/` (requirements), `.context/sa/` (ADRs), `.context/md/` & `.context/bd/` (implementation), `.context/qa/` (test reports)
- **Backend Structure:** `services/` (5-stage pipeline), `models/` (Pydantic), `prompts/` (versioned templates)
- **Frontend Structure:** `screens/` (UI), `widgets/` (components), `services/` (API clients)
- **Mock Data:** Store 100+ diverse job listings in `backend/data/mock_jobs.json`
- **Environment:** Use `.env` for API keys, implement dev/prod environment switching

### Agent Decision Matrix
- **New features:** Business Analyst → Solutions Architect
- **Technical architecture:** Solutions Architect (with QA input)
- **UI/UX implementation:** Mobile Developer (with BA consultation)
- **API design:** Backend Developer (with SA oversight)
- **Performance issues:** QA Engineer → Solutions Architect
- **Integration problems:** QA Engineer coordinates with both dev agents

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
1. `docs/sprint1/agent-coordination-diagram-updated.md` – 5-agent coordination with handoff protocols, context management (lines 90-160)
2. `docs/initial-docs/project-proposal.md` – Complete system design, agent specs (lines 100-200), context management (lines 360-410)
3. `docs/initial-docs/architecture-diagram.md` – Service boundaries and dev/prod environment mappings
4. `docs/initial-docs/timeline.md` – Week-by-week task breakdown with Gantt chart visualization
5. `docs/initial-docs/risk-assessment-matrix.md` – Known risks and mitigation strategies

### Active Development Tracking
- `.context/sprint1-plan.md` – Sprint status, current goals, blockers (update after every major task)
- `.context/ai-coordination-log.md` – AI interaction history with prompt refinements (log all significant AI assistance)

### Reference Materials
- `.context/sprint1-plan.md` – Template layouts for backend and mobile architecture
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
**Solution:** Document prompt evolution in `.context/ai-coordination-log.md` immediately after AI assistance sessions.

---

**Update this file when discovering new patterns. Reference specific files/line numbers for examples.**
