# Sprint Status – Business Analyst Handoff to Solutions Architect

Date: 2025-10-18
Owner: Business Analyst
Project: JobWise – AI-powered Job Application Assistant

## Current Sprint Scope
- MVP slices for: Profile Management, Job Browsing/Saving, AI Generation Pipeline, Document Management
- Non-functionals emphasized: performance (generation <30s p50), reliability (retries/backoff), offline-first with sync

## New/Updated Artifacts
- .context/requirements/user-stories.feature – Consolidated BDD scenarios mapped to SRS (FR/NFR)
- .context/ba/* – Prior detailed requirements, use cases, business rules, acceptance criteria, and user stories (kept as reference)

## Requirements Handoff Checklist
- [x] All user stories have acceptance criteria (see feature file scenarios)
- [x] Requirements are validated and prioritized (MoSCoW tags in scenarios)
- [x] Technical constraints are documented (see SRS §2.4, referenced in feature tags)
- [x] Dependencies are identified (AI provider, backend, PDF libs, job data source)
- [x] Success metrics are defined (performance scenarios, keyword coverage)
- [x] Business rules are clear (see .context/ba/business-rules)
- [x] Data requirements specified (profile schema, documents metadata per SRS FR-3.1/3.4)

## Open Questions / Risks
- Token budget guardrails per environment and per-user quotas
- PDF template catalog finalization and font licensing
- Conflict resolution UX when last-write-wins overwrites local edits
- Post-MVP: external job APIs and auth strategy

## Next Steps for Solutions Architect
1. Produce API contracts for: profile CRUD/sync, jobs (static proto), generation request/streaming progress, documents store/versioning
2. Define AI pipeline service boundaries and queueing model; specify retry/backoff policies
3. Select PDF generation approach (Flutter vs backend) and storage model
4. Draft data model ERD (profiles, experiences, skills, education, jobs, documents, versions)
5. Provide sequence diagrams for the generation flow and offline sync

## Links
- SRS: `docs/software-requirements-specification.md`
- BA detailed docs: `.context/ba/`
- Feature file: `.context/requirements/user-stories.feature`
