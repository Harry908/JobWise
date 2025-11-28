# JobWise AI Generation System - Redesign Overview

**Version**: 3.0  
**Last Updated**: November 16, 2025  
**Status**: 🎯 **Design Complete - Ready for Implementation**

---

## Executive Summary

This redesign simplifies the JobWise AI generation system based on user feedback and clarifications. The new system focuses on:

1. **Sample Document Storage**: Store original resume and cover letter documents with full text in database
2. **Job-Specific Tailoring**: All AI processing is job-specific (no generic layout preferences)
3. **Profile Enhancement**: AI-enhanced descriptions stored alongside original user content
4. **Flexible Prompt System**: Database-stored prompts with user customization support
5. **Simplified Generation**: Clear separation between LLM operations and pure logic

---

## Key Design Changes from v2.0

### ❌ Removed Concepts
- **Generic Layout Preferences**: Layout preferences without job context are meaningless
- **Example Resume Models**: No separate `ExampleResumeModel` table
- **User Generation Profile**: Overly complex orchestration layer removed
- **Consistency Scores**: Removed unnecessary validation complexity

### ✅ New Concepts
- **Sample Documents Table**: Single table for both resume and cover letter samples
- **Enhanced Descriptions**: Store both original and AI-enhanced text for experiences/projects
- **Job-Specific Rankings**: Content ranking tied to specific job postings
- **Prompt Templates**: Database-stored prompts with version control
- **User Custom Prompts**: Support for user-provided prompt additions

---

## System Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                   USER JOURNEY                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: Create Master Profile (Manual Entry)              │
│  ├── Experiences, education, skills, projects              │
│  └── Stored in: master_profiles, experiences, projects     │
│                                                             │
│  Step 2: Upload Sample Documents (One-Time Setup)          │
│  ├── Upload sample resume (.txt)                           │
│  ├── Upload sample cover letter (.txt)                     │
│  └── Stored in: sample_documents (full text + file path)   │
│                                                             │
│  Step 3: Enhance Profile (AI-Powered, One-Time)            │
│  ├── LLM analyzes sample cover letter → writing style      │
│  ├── LLM enhances profile summary using writing style      │
│  ├── LLM enhances project descriptions using writing style │
│  ├── LLM enhances experience descriptions using style      │
│  └── Stored in: enhanced columns in database               │
│                                                             │
│  Step 4: Browse/Save Jobs                                  │
│  └── Stored in: jobs table                                 │
│                                                             │
│  Step 5A: Generate Resume (Job-Specific)                   │
│  ├── LLM ranks experiences/projects for job                │
│  ├── Store ranking in: job_content_rankings                │
│  ├── Pure logic compiles resume using ranking              │
│  └── Store result in: generations table                    │
│                                                             │
│  Step 5B: Generate Cover Letter (Job-Specific)             │
│  ├── LLM generates letter using sample + job + profile     │
│  └── Store result in: generations table                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Document Structure

This design is split into 6 focused documents:

1. **[00-OVERVIEW.md](00-OVERVIEW.md)** (This document)
   - Executive summary and navigation guide

2. **[01-DATABASE-SCHEMA.md](01-DATABASE-SCHEMA.md)**
   - Complete database schema with migrations
   - Tables: sample_documents, enhanced descriptions, job_content_rankings, prompt_templates

3. **[02-AI-PIPELINE.md](02-AI-PIPELINE.md)**
   - Writing style extraction workflow
   - Profile enhancement workflow
   - Job-specific ranking workflow
   - Resume compilation logic (no LLM)
   - Cover letter generation workflow

4. **[03-API-ENDPOINTS.md](03-API-ENDPOINTS.md)**
   - REST API specifications
   - Request/response schemas
   - Error handling

5. **[04-PROMPT-MANAGEMENT.md](04-PROMPT-MANAGEMENT.md)**
   - Prompt template system design
   - User custom prompt injection
   - Version control strategy

6. **[05-LLM-ADAPTER.md](05-LLM-ADAPTER.md)**
   - LLM service abstraction
   - Groq implementation
   - Swappable provider pattern

---

## Core Principles

### 1. Job-Specific Everything
**Rationale**: Layout preferences are meaningless without job context. All AI tailoring must target a specific job posting.

**Impact**:
- No generic "layout configs" stored
- Content ranking always tied to `job_id`
- Resume generation requires `job_id` parameter

### 2. Store Original Documents
**Rationale**: Full text storage enables re-analysis, debugging, and audit trails without re-parsing files.

**Impact**:
- `sample_documents` table stores full text + file path
- Enhanced descriptions stored alongside originals
- No dependency on file system for text retrieval

### 3. Flexible Prompts
**Rationale**: Prompts evolve over time and users want customization.

**Impact**:
- Prompts stored in `prompt_templates` table
- Version control with fallback to defaults
- User custom prompts appended to base prompts
- API endpoints accept optional `custom_prompt` parameter

### 4. Clear LLM vs Logic Separation
**Rationale**: Resume compilation should be fast and deterministic after ranking.

**Impact**:
- LLM Step 1: Rank content (slow, creative)
- Logic Step 2: Compile resume (fast, templating)
- No LLM calls during final assembly

---

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (async via aiosqlite)
- **ORM**: SQLAlchemy 2.0
- **LLM Provider**: Groq (swappable via adapter pattern)
- **File Parsing**: PyPDF2, python-docx, plain text

### LLM Models (Groq)
- **Writing Style Extraction**: Llama 3.1 8B Instant
- **Profile Enhancement**: Llama 3.3 70B Versatile
- **Content Ranking**: Llama 3.1 8B Instant
- **Cover Letter Generation**: Llama 3.3 70B Versatile

### Prompt Management
- **Storage**: Database (`prompt_templates` table)
- **Format**: JSON with Jinja2 templates
- **Versioning**: Semantic versioning (1.0.0, 1.1.0, etc.)

---

## Implementation Phases

### Phase 1: Database Schema Migration
**Duration**: 1-2 days

- Create `sample_documents` table
- Add enhanced description columns to `experiences`, `projects`, `master_profiles`
- Create `job_content_rankings` table
- Create `prompt_templates` table
- Write migration scripts

### Phase 2: Sample Document Upload
**Duration**: 2-3 days

- POST `/samples/upload-resume` endpoint
- POST `/samples/upload-cover-letter` endpoint
- Text extraction service (TXT, PDF, DOCX)
- File storage + database text storage

### Phase 3: Profile Enhancement
**Duration**: 3-4 days

- POST `/profile/enhance` endpoint
- Writing style extraction from cover letter
- Profile summary enhancement
- Experience/project description enhancement
- Store enhanced text in new columns

### Phase 4: Job-Specific Ranking
**Duration**: 2-3 days

- POST `/rankings/create` endpoint
- LLM-based content ranking for job
- Store ranking in `job_content_rankings` table
- GET `/rankings/{job_id}` endpoint

### Phase 5: Resume Generation
**Duration**: 3-4 days

- POST `/generations/resume` endpoint (redesigned)
- Pure logic resume compilation using ranking
- Jinja2 templating for output formats
- Support for custom user prompts (during ranking phase)

### Phase 6: Cover Letter Generation
**Duration**: 2-3 days

- POST `/generations/cover-letter` endpoint (redesigned)
- LLM generation using sample + job + profile
- Support for custom user prompts
- Store result in `generations` table

### Phase 7: Prompt Management
**Duration**: 2-3 days

- Seed default prompts in database
- GET `/prompts` endpoint (admin)
- PUT `/prompts/{id}` endpoint (admin)
- Version control implementation

---

## Success Criteria

### Performance
- Resume generation: <5s total (ranking: 3s, compilation: 2s)
- Cover letter generation: <8s total
- Profile enhancement: <15s for all fields
- Text extraction: <2s per document

### Quality
- ATS score: >85% on average
- Keyword coverage: >80% of job requirements
- Writing style consistency: >90% match to sample
- Zero fabrication: 100% content from user profile

### User Experience
- Simple 3-step setup: profile → samples → enhance
- Clear error messages with actionable guidance
- Optional custom prompts for power users
- Progress tracking for long operations

---

## Next Steps

1. Read detailed documents in order (01 → 05)
2. Review and approve database schema
3. Begin Phase 1 implementation
4. Iterative development with testing

---

## Questions or Feedback?

This design addresses your requirements:
- ✅ Original documents stored in database
- ✅ Layout preferences removed (job-specific ranking instead)
- ✅ Prompt templates in database with user customization
- ✅ Enhanced descriptions stored alongside originals
- ✅ Clear LLM vs logic separation

If you need clarifications or modifications, let's discuss before implementation begins.
