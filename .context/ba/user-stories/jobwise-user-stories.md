# JobWise User Stories (Backlog v0.1)

Author: Business Analyst Agent  
Method: INVEST, MoSCoW prioritized

---

## Epic: Job Discovery & Save

US-01: As a job seeker, I want to search jobs by keyword so that I can find relevant openings.
- Acceptance Criteria:
  - Given I am on the Discover screen, when I enter a keyword and tap Search, then I see a list of matching jobs within 2 seconds.
  - Results show title, company, location, and brief snippet.
  - Empty state shown when no results; I can clear filters.
- Priority: Must (P0)
- Story Points: 3

US-02: As a job seeker, I want to filter jobs by location, job type, and experience level so that I can narrow results.
- Acceptance Criteria:
  - I can apply one or more filters and see updated results.
  - A Clear All action resets filters.
- Priority: Should (P1)
- Story Points: 3

US-03: As a job seeker, I want to save a job so that I can generate tailored documents later.
- Acceptance Criteria:
  - Tapping Save adds the job to my Saved Jobs list and enqueues generation.
  - If job is already saved, I’m informed it exists.
- Priority: Must (P0)
- Story Points: 2

---

## Epic: AI Tailoring Pipeline

US-04: As a job seeker, I want the system to generate a tailored resume for a saved job so that I can apply faster.
- Acceptance Criteria:
  - Upon saving a job, a resume draft is created (or queued) within 30 seconds for typical jobs.
  - Draft links to the job and my profile; status updates visible.
- Priority: Must (P0)
- Story Points: 5

US-05: As a job seeker, I want the system to generate a tailored cover letter so that my application feels personalized.
- Acceptance Criteria:
  - A structured cover letter (intro, 2–3 body sections, closing) is created alongside the resume.
- Priority: Should (P1)
- Story Points: 3

US-06: As a product owner, I want validation to prevent fabricated claims so that outputs remain trustworthy.
- Acceptance Criteria:
  - Generated statements map to master profile facts; violations trigger regeneration or Needs Review.
- Priority: Must (P0)
- Story Points: 3

---

## Epic: Document Review & Export

US-07: As a job seeker, I want to edit AI-generated documents section-by-section so that I can refine the content.
- Acceptance Criteria:
  - I can edit summary, experience bullets, skills, and letter paragraphs.
  - Saving creates a new version; I can view history and revert.
- Priority: Must (P0)
- Story Points: 5

US-08: As a job seeker, I want to export an ATS-compatible PDF so that I can submit applications.
- Acceptance Criteria:
  - Export produces a single-column PDF with standard fonts; file saved or shareable.
  - If local render fails, a backend fallback succeeds.
- Priority: Must (P0)
- Story Points: 3

---

## Epic: Profile Management

US-09: As a job seeker, I want to manage my master profile so that the system can tailor accurately.
- Acceptance Criteria:
  - I can add/edit experiences, education, skills, and summary.
  - Required fields validated (dates, roles, companies, quantifiable results encouraged).
- Priority: Must (P0)
- Story Points: 5

US-10: As a job seeker, I want my profile to sync when online so that changes persist across sessions.
- Acceptance Criteria:
  - Changes saved locally and synced to backend when connected.
- Priority: Could (P3)
- Story Points: 3

---

## Epic: Pipeline & Status

US-11: As a job seeker, I want to track statuses for my saved jobs so that I know progress.
- Acceptance Criteria:
  - Dashboard shows Pending, Generating, Generated, Needs Review, Exported.
  - I can trigger Regenerate, Export, or Remove.
- Priority: Should (P1)
- Story Points: 3

---

## Non-Functional Stories

NFS-01: As a user, I want the app to work offline so that I can continue basic tasks without network.
- Acceptance Criteria:
  - Cached job lists and saved jobs accessible; saves and edits queue for sync.
- Priority: Must (P0)

NFS-02: As a user, I want fast responses so that the app feels responsive.
- Acceptance Criteria:
  - Search results in ≤2s on typical network; generation median ≤30s.
- Priority: Should (P1)

---

## Traceability
- US-01 ↔ FR-01; UC-01
- US-02 ↔ FR-02; UC-01
- US-03 ↔ FR-03/FR-04; UC-02
- US-04 ↔ FR-05/FR-06/FR-07; UC-03
- US-05 ↔ FR-08; UC-04
- US-06 ↔ FR-07; NFR-07; UC-03/UC-04
- US-07 ↔ FR-09/FR-10; UC-05
- US-08 ↔ FR-11; UC-06
- US-09 ↔ FR-12; UC-07
- US-10 ↔ FR-13; UC-07
- US-11 ↔ FR-14/FR-15; UC-08
- NFS-01 ↔ NFR-02; UC-02/UC-05
- NFS-02 ↔ NFR-01/NFR-03; UC-01/UC-03
