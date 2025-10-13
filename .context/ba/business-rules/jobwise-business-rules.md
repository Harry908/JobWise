# JobWise Business Rules & Data Policies (v0.1)

## Business Rules
- BR-01 (Truthfulness): All generated content must be traceable to the master profile; no fabrication.
- BR-02 (Regeneration Policy): On validation failure, perform at most one stricter regeneration per document.
- BR-03 (Token Budget): Each pipeline stage adheres to token budget; trim context using relevance scoring.
- BR-04 (ATS Compliance): Use standard section headers; avoid tables/images; maintain clear bullet formatting.
- BR-05 (Keyword Strategy): Incorporate ATS keywords naturally; avoid overstuffing.
- BR-06 (Retries): LLM/network calls use exponential backoff with max 3 attempts.
- BR-07 (Fallbacks): If all retries fail, mark status "Needs Review" and surface guidance.
- BR-08 (Offline Behavior): Saves and edits queue locally and auto-sync when online.
- BR-09 (Versioning): Each edit produces a new immutable version with timestamps.

## Data Governance
- Data Minimization: Store only necessary user data; redact PII from logs.
- Local Storage: Use secure platform storage for tokens; consider OS keychain in later sprint.
- Sync Strategy: Conflict resolution favors most recent edit; manual merge for collisions in later sprint.
- Retention: Keep generated versions for 30 days by default in dev; provide delete option.

## Data Models (MVP outline)
- Profile
  - id, summary, skills[], experiences[], education[]
  - Experience: role, company, startDate, endDate, achievements[]
- Job
  - id, title, company, location, description, source, date
- DraftDocument
  - id, jobId, type (resume|cover_letter), sections{}, version, createdAt, updatedAt, status
- Status
  - enum: Pending, Generating, Generated, Needs Review, Exported

## Quality & Observability
- Metrics: generation latency (p50/p95), validation failure rate, ATS compliance score
- Logging: event-based with anonymized IDs; no raw user text in error logs when avoidable

## Open Questions
- Long-term retention policy for generated documents?
- Template customization extent in MVP?
