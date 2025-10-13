# JobWise Requirements Specification (MVP)

Version: 0.1 (Sprint 1)
Author: Business Analyst Agent
Derived From: `docs/initial-docs/project-proposal.md`, `README.md`

---

## 1. Scope
JobWise is a mobile app that helps job seekers find jobs, generate tailored resumes and cover letters using AI, review/edit drafts, and export ATS-compatible PDFs. Sprint 1 focuses on documentation and architecture setup; implementation begins next.

## 2. Assumptions
- MVP uses mock job data (JSON) served by backend
- LLM provider: OpenAI GPT-3.5 (dev) with token budgets per pipeline stage
- No external job APIs in MVP; PDF exported on device where possible
- User profile stored locally with optional backend sync
- Offline-first: limited functionality available without network

## 3. Constraints
- Development timeline: Weeks 8–14
- Mobile framework: Flutter; Backend: FastAPI
- Token budget windows per pipeline: 8000 with overlaps
- ATS rules: single-column, standard fonts, no images/tables (ATS version)

## 4. Definitions
- ATS: Applicant Tracking System
- Master Resume: Full profile repository of user experiences/skills
- Tailoring: Selecting/rewriting profile content for specific job

## 5. Functional Requirements (FR)
- FR-01: The system shall provide keyword search of jobs.
- FR-02: The system shall support filters (location, job type, experience level).
- FR-03: The system shall allow saving a job to the application pipeline.
- FR-04: The system shall enqueue a generation task when a job is saved.
- FR-05: The system shall analyze job descriptions to extract requirements and ATS keywords.
- FR-06: The system shall select relevant experiences/skills from the master resume.
- FR-07: The system shall generate a tailored resume draft tied to the job.
- FR-08: The system shall generate a tailored cover letter draft tied to the job.
- FR-09: The system shall allow editing generated documents section-by-section.
- FR-10: The system shall version edits and allow revert/compare.
- FR-11: The system shall export ATS-compatible PDFs (resume and cover letter).
- FR-12: The system shall allow CRUD operations on the master profile.
- FR-13: The system shall sync profile data with backend when online (if configured).
- FR-14: The system shall display a Saved Jobs dashboard with generation status.
- FR-15: The system shall allow actions on saved jobs (View, Regenerate, Export, Remove).

## 6. Non-Functional Requirements (NFR)
- NFR-01: Search results shall display within 2 seconds on a typical network.
- NFR-02: The system shall operate in degraded mode offline (cached jobs, queued saves).
- NFR-03: AI generation shall complete within 30 seconds for typical jobs (dev target).
- NFR-04: The UI shall support accessibility standards (scalable text, contrast, voiceover labels).
- NFR-05: Generated PDFs shall be ATS-compatible (single-column, standard fonts, simple layout).
- NFR-06: The system shall implement retries with exponential backoff for LLM and network calls (max 3 attempts).
- NFR-07: The system shall log generation and error events with privacy considerations; PII is not logged.

## 7. Prioritization (MoSCoW)
- Must Have: FR-01, FR-03, FR-05, FR-07, FR-09, FR-11, FR-12, NFR-02, NFR-03, NFR-05
- Should Have: FR-02, FR-04, FR-08, FR-10, FR-14, NFR-01, NFR-06, NFR-07
- Could Have: FR-13, FR-15
- Won't Have (MVP): External job APIs, multi-user auth, cloud sync across devices

## 8. Data Requirements
- Profile: experiences (role, company, dates, achievements), education, skills, summary
- Job: id, title, company, location, description, source, date
- Draft Document: jobId, type (resume/cover letter), sections, version, timestamps
- Status: generation state (Pending, Generating, Generated, Needs Review, Exported)

## 9. Business Rules (summary)
- BR-01: Do not fabricate achievements; all generated content must map to master profile facts.
- BR-02: If validation fails, perform at most one stricter regeneration.
- BR-03: If LLM calls exceed token budget, trim non-essential context per stage.
- BR-04: Prefer ATS keywords naturally; avoid keyword stuffing.
- BR-05: Offline saves queue locally and auto-sync when online.

## 10. Error Handling
- LLM/network failure → retry up to 3 times with backoff; on failure mark Needs Review and surface guidance.
- Missing master resume data → prompt user to complete required fields.
- PDF render failure → retry locally; if still failing, call backend fallback.

## 11. Security & Privacy
- Store API keys in .env; do not ship secrets in client.
- Avoid logging PII; redact or hash identifiers in logs.
- Local data protected via platform storage; future enhancement: OS keychain for sensitive tokens.

## 12. Success Metrics
- ≥80% of generated drafts pass ATS checks without manual fixes
- Median generation time ≤ 30s; p95 ≤ 60s
- ≥90% of user flows complete without error on first attempt (QA test suites)

## 13. Traceability
- Use Case Coverage: See use case matrix in `.context/ba/use-cases/jobwise-use-cases.md`
- Each FR/NFR maps to at least one use case and will map to ADRs/APIs in SA handoff

## 14. Open Items
- Authentication scope decision (local vs. basic email/password)
- State management approach ADR (Provider vs Riverpod)
- PDF templates: number and customization options for MVP
