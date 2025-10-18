# JobWise Acceptance Criteria Summary (Sprint 1)

This document consolidates testable acceptance criteria mapped to Functional (FR) and Non-Functional Requirements (NFR), aligned to use cases and user stories. Intended for SA handoff and QA planning.

---

## Search & Discover
- AC-01 (FR-01, NFR-01): Given the Discover screen, when a user searches with a valid keyword, results render within 2 seconds for a dataset of ≤ 500 jobs on typical network.
- AC-02 (FR-02): Given location/job type/experience filters applied, when the user modifies filters, results update accordingly and a Clear All option resets filters.

## Save & Pipeline
- AC-03 (FR-03): When a user taps Save on a job, it appears in Saved Jobs immediately with status Pending.
- AC-04 (FR-04): On save, a generation task is enqueued; backend receives a payload with userId and jobId.

## Generation Pipeline
- AC-05 (FR-05): Job Analyzer output includes required fields: skills[], responsibilities[], experienceRequirements, atsKeywords[].
- AC-06 (FR-06): Profile Compiler selects experiences with relevance score ≥ threshold; tie-breaker favors recency.
- AC-07 (FR-07): Tailored resume draft includes sections: Summary, Experience (bullets), Skills, Education.
- AC-08 (FR-08): Tailored cover letter draft includes: Intro, 2–3 body paragraphs, Closing.
- AC-09 (NFR-03): Median generation time ≤ 30s; p95 ≤ 60s on dev hardware.
- AC-10 (NFR-06): LLM calls retry up to 3 times with exponential backoff.
- AC-11 (BR-01): Generated statements are traceable to master profile entries.

## Editing & Versioning
- AC-12 (FR-09): User can edit any section; changes persist after app restart.
- AC-13 (FR-10): Each save creates a new version; user can view history and revert.

## PDF Export
- AC-14 (FR-11, NFR-05): Exported PDFs pass an ATS checklist: single-column, standard fonts (e.g., Arial/Calibri), simple formatting, recognizable section headers.
- AC-15: If client export fails, server fallback succeeds with same content.

## Profile Management
- AC-16 (FR-12): Profile CRUD validated for required fields and date correctness.
- AC-17 (FR-13): When online, profile changes sync to backend within 5 seconds or are queued if offline.

## Status Dashboard
- AC-18 (FR-14): Saved Jobs shows accurate statuses updated from backend events.
- AC-19 (FR-15): User can trigger Regenerate, Export, and Remove; destructive actions require confirmation.

## Reliability & Offline
- AC-20 (NFR-02): When offline, cached job results and saved jobs remain available; operations queue for later sync.
- AC-21 (NFR-07): Error logs do not contain PII; IDs are anonymized.

---

## Handoff Checklist to SA
- All FR/NFR have at least one AC and use case coverage
- Business rules documented; traceability map exists
- Open questions noted for ADR decisions
