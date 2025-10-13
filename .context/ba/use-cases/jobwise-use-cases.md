# JobWise Use Cases

Version: 0.1 (Sprint 1)  
Author: Business Analyst Agent  
Scope: MVP from job discovery to AI-tailored document export

---

## Actors
- Primary User (Job Seeker)
- Mobile App (Flutter Client)
- Backend Service (FastAPI)
- LLM Provider (OpenAI/Claude)
- Storage (Local/Cloud)
- PDF Exporter (Flutter pdf / Backend Puppeteer)

## UC-01: Discover Jobs
- Goal: Find relevant job postings via search and filters
- Primary Actor: Job Seeker
- Preconditions:
  - App installed and launched
  - Network connectivity available (fallback: cached jobs if offline)
- Triggers:
  - User enters keywords or opens Discover screen
- Main Flow:
  1. User enters keyword(s) and optional filters (location, type, experience level)
  2. App requests job list from Backend (mock JSON in dev)
  3. Backend returns paginated list of jobs
  4. App displays swipeable job cards with title, company, location, snippet
  5. User swipes or taps into job details
- Alternative Flows:
  - A1: Offline → App loads cached results; shows offline banner
  - A2: No results → App suggests broader keywords; offer Clear filters
  - A3: Backend error → Show retry, and graceful fallback to cached data
- Postconditions (Success):
  - User views list of relevant jobs or appropriate message
- Postconditions (Failure):
  - Error surfaced with retry and fallback options
- Non-Functional Notes: Results within 2s on typical network; accessible design

## UC-02: Save Job to Pipeline
- Goal: Save a job posting for later and initiate tailoring pipeline
- Primary Actor: Job Seeker
- Preconditions:
  - UC-01 completed; job details visible
- Triggers:
  - User taps "Save" or "Add to Applications"
- Main Flow:
  1. User taps Save on a job
  2. App persists job to local store and notifies backend
  3. Backend enqueues generation task (resume and cover letter) for this job
  4. App updates Saved Jobs dashboard
- Alternative Flows:
  - A1: Duplicate save → Inform job already saved
  - A2: Offline save → Queue locally and sync when online
- Postconditions (Success):
  - Job appears in Saved Jobs with status: Pending Generation

## UC-03: Generate Tailored Resume
- Goal: Create a job-specific resume draft from master resume
- Primary Actor: Backend Service
- Preconditions:
  - UC-02 triggered; master resume exists for user
- Triggers:
  - Save job event or explicit user action "Generate Resume"
- Main Flow (5-Stage Pipeline excerpt):
  1. Job Analyzer extracts requirements/keywords from job description
  2. Profile Compiler selects relevant experiences/skills from master resume
  3. Document Generator writes tailored resume emphasizing match
  4. Quality Validator checks factual consistency, ATS compliance, readability
  5. Result stored as Draft v1; status updated to "Generated"
- Alternative Flows:
  - A1: LLM timeout → Retry up to 3x with backoff; fall back to previous cache
  - A2: Validation failed → Regenerate once with stricter constraints; else mark Needs Review
  - A3: Missing master resume → Return actionable error to client
- Postconditions (Success):
  - Draft resume saved and associated with job

## UC-04: Generate Tailored Cover Letter
- Goal: Create a job-specific cover letter draft
- Preconditions:
  - UC-02 triggered; minimal profile exists
- Triggers:
  - Save job event or explicit action "Generate Cover Letter"
- Main Flow:
  1. Use analyzed job insights and profile selections
  2. Generate structured cover letter (intro, 2–3 body paragraphs, closing)
  3. Validate for tone, coherence, ATS keyword presence
  4. Store Draft v1; update status
- Alternative Flows:
  - A1: Same as UC-03 A1/A2
- Postconditions (Success):
  - Draft cover letter saved and associated with job

## UC-05: Review and Edit Documents
- Goal: User reviews and edits generated drafts before export
- Preconditions:
  - UC-03 and/or UC-04 successful
- Triggers:
  - User opens Saved Job and taps Resume/Cover Letter
- Main Flow:
  1. App displays editable sections (summary, experience, skills, etc.)
  2. User edits text; app runs local coherence checks
  3. User saves changes; versioning creates v2, v3, etc.
  4. User can compare versions and revert if needed
- Alternative Flows:
  - A1: Long edits offline → Save locally; sync on reconnection
- Postconditions (Success):
  - Updated draft stored with version metadata

## UC-06: Export as ATS-Compatible PDF
- Goal: Produce and download/share a professional PDF
- Preconditions:
  - Edited or generated document exists
- Triggers:
  - User taps Export
- Main Flow:
  1. User chooses template (ATS single-column vs visually enhanced)
  2. System renders PDF with standard fonts, spacing, and sections
  3. PDF file saved to device storage and/or shared
- Alternative Flows:
  - A1: Rendering on device fails → Backend fallback render service
  - A2: Storage permission denied → Prompt user with instructions
- Postconditions (Success):
  - PDF available on device or shared via OS intents

## UC-07: Manage Master Profile
- Goal: Maintain a comprehensive master resume/profile
- Preconditions:
  - User profile created
- Triggers:
  - User edits profile, adds experiences, skills, education
- Main Flow:
  1. CRUD operations for profile data
  2. Validation for dates, required fields, quantifiable achievements
  3. Store locally and sync with backend
- Postconditions (Success):
  - Updated master resume content available for tailoring

## UC-08: View Application Pipeline
- Goal: Track saved jobs and generation statuses
- Triggers:
  - User opens Saved Jobs
- Main Flow:
  1. Display list with statuses: Pending, Generating, Generated, Needs Review, Exported
  2. Allow actions: View, Edit, Regenerate, Export, Remove
- Postconditions (Success):
  - User understands progress and next steps

## UC-09: Error Handling & Fallbacks
- Goal: Ensure graceful degradation and transparency
- Triggers:
  - Any operation fails (network, LLM, storage)
- Main Flow:
  1. Detect errors; show human-readable messages
  2. Apply retries/backoff; fall back to cached data or mock outputs
  3. Log events for diagnostics (privacy-aware)
- Postconditions (Success):
  - User keeps control; minimal disruption

---

## Use Case Coverage Matrix (to Requirements)
- UC-01 → FR-01, FR-02, NFR-01
- UC-02 → FR-03, FR-04, NFR-02
- UC-03 → FR-05, FR-06, FR-07, NFR-03
- UC-04 → FR-05, FR-06, FR-08, NFR-03
- UC-05 → FR-09, FR-10, NFR-04
- UC-06 → FR-11, NFR-05
- UC-07 → FR-12, FR-13, NFR-04
- UC-08 → FR-14, FR-15
- UC-09 → NFR-02, NFR-06, NFR-07

---

## Open Questions
1. Authentication scope in MVP (local only vs. email/password)?
2. Template selection count for Sprint 2 (1 ATS + 1 enhanced?)
3. State management choice (Provider vs Riverpod) timing (ADR in Sprint 2)
4. Data sync frequency and conflict resolution rules
5. PDF generation location preference (client-first with backend fallback?)
