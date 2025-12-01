# JobWise AI Generation System - Complete Reference

**Version**: 2.0  
**Last Updated**: November 11, 2025  
**Status**: 🎯 **Sprint 4 Implementation Ready**

---

## Executive Summary

JobWise uses AI to generate tailored resumes and cover letters by combining:
1. **Master Profile** (user's factual career data) - CONTENT source
2. **Sample Resume** (uploaded formatting example) - STRUCTURE template
3. **Sample Cover Letter** (uploaded writing example) - STYLE template
4. **Selected Job** (target job posting) - TAILORING requirements

**Generation Pipeline**: 2-stage Groq LLM architecture targeting <8s total time
- **Stage 1**: Analysis & Matching (3s, Llama 3.1 8B Instant)
- **Stage 2**: Generation & Validation (5s, Llama 3.3 70B Versatile)

**Current Status**:
- ✅ Master Profile & Job Management: FULLY IMPLEMENTED (Sprint 1-3)
- ⚠️ Sample Upload & Preference Extraction: BACKEND ONLY (Sprint 4 needed)
- ✅ Security: PRODUCTION READY (multi-layer protection)

---

## Table of Contents

1. [Core Terminology](#core-terminology)
2. [System Architecture](#system-architecture)
3. [Implementation Status](#implementation-status)
4. [User Workflows](#user-workflows)
5. [Security Implementation](#security-implementation)
6. [Sprint 4 Implementation Guide](#sprint-4-implementation-guide)

---

## Core Terminology

### 1. Master Profile (✅ IMPLEMENTED)

**Definition**: User's comprehensive career data created by **manually entering** information through JobWise UI forms.

**Key Characteristics**:
- **Data Entry**: Manual input via forms (NOT file upload)
- **Content Type**: Structured JSON/relational data in database
- **Purpose**: Single source of truth for ALL factual content (prevents LLM hallucination)
- **Database Tables**: `master_profiles`, `experiences`, `education`, `projects`
- **API**: `/api/v1/profiles` (CRUD operations)
- **Mobile UI**: Profile creation/edit screens (Sprint 1-2 complete)

**What It Contains**:
```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "location": "Seattle, WA"
  },
  "professional_summary": "Senior backend engineer with 8 years...",
  "experiences": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "start_date": "2020-01",
      "achievements": ["Led migration to microservices...", "..."]
    }
  ],
  "education": [...],
  "skills": ["Python", "FastAPI", "PostgreSQL"],
  "projects": [...]
}
```

**Workflow**:
1. User creates account
2. User navigates to "Create Profile" screen
3. User manually fills forms (experiences, education, skills, projects)
4. System saves to database as structured data
5. Master profile ready for AI generation

---

### 2. Sample Resume / Example Resume (⚠️ BACKEND ONLY)

**Definition**: A **well-formatted resume file** (PDF/DOCX) that user **uploads** to teach LLM their preferred resume structure and formatting.

**Key Characteristics**:
- **Data Entry**: File upload (PDF, DOCX, TXT)
- **Content Type**: Uploaded document + extracted text
- **Purpose**: Extract layout preferences (section order, bullet style, density)
- **Database Tables**: `example_resumes`, `layout_configs`
- **API**: ❌ NOT IMPLEMENTED (needs `/api/v1/preferences/upload-sample-resume`)
- **Mobile UI**: ❌ NOT IMPLEMENTED

**What LLM Extracts**:
```json
{
  "layout_preferences": {
    "section_order": ["summary", "experience", "skills", "education"],
    "bullet_style": "achievement_focused",
    "bullets_per_experience": {"min": 3, "max": 5},
    "date_format": "MMM YYYY",
    "header_style": "centered",
    "target_page_count": 1,
    "ats_optimization_level": "balanced"
  }
}
```

**Workflow** (when implemented):
1. User uploads polished resume they like
2. LLM extracts structural characteristics
3. System creates `LayoutConfig` in database
4. User reviews/adjusts preferences
5. Future resumes follow this structure

**Clarification**: This is NOT the user's career data (that's Master Profile). This is a formatting reference.

---

### 3. Sample Cover Letter (⚠️ BACKEND ONLY)

**Definition**: A **general-purpose cover letter** (PDF/DOCX) that user **uploads** to teach LLM their writing style and tone.

**Key Characteristics**:
- **Data Entry**: File upload (PDF, DOCX, TXT)
- **Content Type**: Uploaded file (saved to disk) + extracted text (saved to database)
- **Purpose**: Extract writing style (tone, vocabulary, sentence structure)
- **File Storage**: `uploads/cover_letters/` directory
- **Database Storage**: 
  - `writing_style_configs` table stores extracted preferences AND full verbatim text
  - `source_text` column contains the complete cover letter text for future reference
- **API**: ✅ IMPLEMENTED (`/api/v1/preferences/upload-cover-letter`)
- **Mobile UI**: ❌ NOT IMPLEMENTED

**Important Note**: Cover letter files are saved to disk at `uploads/cover_letters/`, and the **full verbatim text is ALSO stored in the database** in the `writing_style_configs.source_text` column. This allows for future re-analysis without needing to re-extract text from the file.

**What LLM Extracts**:
```json
{
  "writing_style": {
    "tone": "professional_enthusiastic",
    "formality_level": 7,
    "vocabulary_complexity": 8,
    "sentence_structure": "varied_medium_length",
    "active_voice_ratio": 0.85,
    "first_person_usage": "moderate",
    "action_verbs": ["developed", "implemented", "optimized"],
    "transition_phrases": ["Furthermore", "Additionally"],
    "technical_jargon_usage": "balanced"
  },
  "metadata": {
    "source_text": "Full verbatim cover letter text stored for future reference...",
    "extraction_confidence": 0.92
  }
}
```

**Workflow** (when implemented):
1. User uploads cover letter they wrote previously
2. LLM analyzes writing characteristics
3. System creates `WritingStyleConfig`
4. User adjusts preferences (tone slider, formality)
5. Future documents use this writing style

**Clarification**: Can be generic or from any job. Used ONLY for style extraction, not content.

---

### 4. Selected Job / Target Job (✅ IMPLEMENTED)

**Definition**: A **specific job posting** that user wants to apply to (scraped, searched, or manually created).

**Key Characteristics**:
- **Data Entry**: Job search/scraping OR manual creation
- **Content Type**: Structured job data (title, company, description, requirements)
- **Purpose**: Target for tailored resume/cover letter generation
- **Database Table**: `jobs`
- **API**: `/api/v1/jobs` (CRUD operations)
- **Mobile UI**: Job browsing/detail screens (Sprint 3 complete)

**What It Contains**:
```json
{
  "title": "Senior Python Developer",
  "company": "Tech Startup Inc",
  "location": "Remote",
  "description": "We're looking for a senior backend engineer...",
  "requirements": [
    "5+ years Python experience",
    "FastAPI or Django expertise",
    "PostgreSQL/MongoDB"
  ],
  "keywords": ["Python", "FastAPI", "microservices", "AWS"],
  "seniority_level": "senior",
  "source": "scraped"
}
```

---

## System Architecture

### AI Generation Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUTS (4 Components)                       │
├─────────────────────────────────────────────────────────────────┤
│ 1. Master Profile (DB) → FACTUAL CONTENT                        │
│    ✅ Experiences, skills, education, projects                  │
│                                                                  │
│ 2. Sample Resume (File) → FORMATTING RULES                      │
│    ⚠️ Section order, bullet style, layout                       │
│                                                                  │
│ 3. Sample Cover Letter (File) → WRITING STYLE                   │
│    ⚠️ Tone, vocabulary, sentence structure                      │
│                                                                  │
│ 4. Selected Job (DB) → TAILORING TARGET                         │
│    ✅ Requirements, keywords, job description                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 1: Analysis & Matching (3s)                  │
├─────────────────────────────────────────────────────────────────┤
│ Model: Llama 3.1 8B Instant (840 TPS)                           │
│ Tasks:                                                           │
│   - Parse job description → extract keywords/requirements       │
│   - Score master profile content by relevance (0.0-1.0)         │
│   - Rank experiences/projects (highest scores first)            │
│   - Identify skill gaps                                         │
│ Output: Ranked content + job analysis                           │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│           STAGE 2: Generation & Validation (5s)                 │
├─────────────────────────────────────────────────────────────────┤
│ Model: Llama 3.3 70B Versatile (394 TPS)                        │
│ Tasks:                                                           │
│   - Apply layout preferences (from sample resume)               │
│   - Apply writing style (from sample cover letter)              │
│   - Generate tailored resume using ranked content               │
│   - Validate ATS compliance                                     │
│   - Self-check for fabrication (all content from master)        │
│ Output: Tailored resume + cover letter + validation report      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUTS (3 Artifacts)                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Tailored Resume (PDF/DOCX + JSON)                            │
│    - Content: From master profile (ZERO fabrication)            │
│    - Structure: From sample resume layout                       │
│    - Optimized: For selected job keywords                       │
│                                                                  │
│ 2. Tailored Cover Letter (PDF/DOCX + JSON)                      │
│    - Writing style: From sample cover letter                    │
│    - Content: From master profile achievements                  │
│    - Customized: For selected job/company                       │
│                                                                  │
│ 3. Generation Report                                            │
│    - Keyword coverage: 12/15 matched                            │
│    - ATS score: 0.87                                            │
│    - Consistency with examples: 0.92                            │
│    - Recommendations for improvement                            │
└─────────────────────────────────────────────────────────────────┘
```

---

### Groq LLM Integration

**Technology Stack**:
- **SDK**: `groq==0.33.0` (Official Python SDK)
- **Authentication**: Environment variable `GROQ_API_KEY`
- **Client**: `AsyncGroq` for async/await support
- **Timeout**: 30s default
- **Retry Logic**: 3 attempts with exponential backoff

**Model Selection Strategy**:

| Stage | Model | Speed | Cost (per 1M tokens) | Purpose |
|-------|-------|-------|---------------------|---------|
| **Stage 1** | `llama-3.1-8b-instant` | 840 TPS | $0.05 / $0.08 | Fast keyword extraction, profile scoring |
| **Stage 2** | `llama-3.3-70b-versatile` | 394 TPS | $0.59 / $0.79 | High-quality resume generation |
| **Alternative** | `llama-4-scout-17bx16e` | 594 TPS | $0.11 / $0.34 | Faster Stage 2 with moderate quality |

**Configuration** (`.env`):
```bash
# Groq API
GROQ_API_KEY=gsk_your_api_key_here
GROQ_TIMEOUT=30.0
GROQ_MAX_RETRIES=3

# Model Selection
LLM_STAGE1_MODEL=llama-3.1-8b-instant
LLM_STAGE2_MODEL=llama-3.3-70b-versatile

# Token Budgets
LLM_STAGE1_MAX_TOKENS=2500
LLM_STAGE2_MAX_TOKENS=2500

# Temperature
LLM_STAGE1_TEMPERATURE=0.2  # Deterministic analysis
LLM_STAGE2_TEMPERATURE=0.4  # Balanced generation
```

**Domain Port Interface** (`backend/app/domain/ports/llm_service.py`):
```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    generation_time: float

class ILLMService(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        pass
```

**Infrastructure Adapter** (`backend/app/infrastructure/adapters/groq_llm_adapter.py`):
```python
from groq import AsyncGroq
from app.domain.ports.llm_service import ILLMService, LLMMessage, LLMResponse

class GroqLLMAdapter(ILLMService):
    def __init__(self, api_key: str, timeout: float = 30.0, max_retries: int = 3):
        self.client = AsyncGroq(api_key=api_key, timeout=timeout)
        self.max_retries = max_retries
    
    async def generate(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": msg.role, "content": msg.content} for msg in messages],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    tokens_used=response.usage.total_tokens,
                    finish_reason=response.choices[0].finish_reason,
                    generation_time=time.time() - start_time
                )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"Generation failed: {str(e)}")
                await asyncio.sleep((2 ** attempt) * 1.0)
```

---

### Anti-Fabrication Prompt Engineering

**Stage 1: Analysis & Matching Prompt**:
```python
STAGE1_SYSTEM_PROMPT = """CRITICAL CONSTRAINTS (DO NOT VIOLATE):
- ANALYSIS ONLY - Do not generate any new content
- EXACT MATCHING - Only reference skills/experiences explicitly in user's profile
- STRUCTURED OUTPUT - Return valid JSON matching the schema below
- NO ASSUMPTIONS - If information is missing, mark as null/empty

YOUR ROLE: Resume content analyzer

TASKS:
1. Extract job requirements (keywords, skills, seniority)
2. Score user's experiences/projects by relevance (0.0-1.0)
3. Rank content for resume inclusion (highest first)
4. Identify gaps between job and user's profile

OUTPUT SCHEMA (STRICT JSON):
{
  "job_requirements": {
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill3"],
    "seniority_level": "senior",
    "top_keywords": ["keyword1", "keyword2"]
  },
  "ranked_experiences": [
    {
      "experience_id": "exp_123",
      "relevance_score": 0.92,
      "matching_keywords": ["Python", "FastAPI"]
    }
  ],
  "ranked_projects": [...],
  "recommended_skills": ["Python", "FastAPI"],
  "missing_skills": ["Kubernetes"]
}

VALIDATION: Verify all IDs reference actual user content, scores are 0.0-1.0.
"""
```

**Stage 2: Generation & Validation Prompt**:
```python
STAGE2_SYSTEM_PROMPT = """CRITICAL CONSTRAINTS (HIGHEST PRIORITY):
1. ZERO FABRICATION - Use ONLY content from provided ranked experiences/projects
2. SOURCE TRACING - Every resume bullet MUST map to a source content ID
3. EXACT SKILLS - Use ONLY skills from recommended_skills list
4. STRICT VALIDATION - Self-check output against source material
5. STRUCTURED OUTPUT - Return valid JSON

YOUR ROLE: Professional resume writer (ATS-optimized)

LAYOUT PREFERENCES (from user's sample resume):
{layout_config_json}

WRITING STYLE (from user's cover letter):
{writing_style_config_json}

TASKS:
1. Select top 3-5 experiences/projects from ranked list
2. Rewrite bullets to emphasize job-relevant keywords
3. Apply user's layout preferences (section order, bullet style)
4. Apply user's writing style (tone, vocabulary, structure)
5. Generate professional summary from selected experiences
6. VALIDATE: Cross-reference every sentence against source material

OUTPUT SCHEMA:
{
  "resume": {
    "summary": "...",
    "experiences": [
      {
        "source_id": "exp_123",
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "bullets": [
          {
            "text": "Developed microservices architecture...",
            "source_achievement_id": "ach_456",
            "keywords_emphasized": ["microservices", "Python"]
          }
        ]
      }
    ],
    "skills": ["Python", "FastAPI"],
    "education": [...]
  },
  "validation": {
    "fabrication_check": "PASS",
    "all_content_sourced": true,
    "layout_consistency_score": 0.95,
    "ats_score": 0.87
  }
}
"""
```

---

## Implementation Status

### ✅ Fully Implemented (Sprint 1-3)

**Master Profile Management**:
- Database: `master_profiles`, `experiences`, `education`, `projects`
- Domain Entities: `MasterProfile`, `Experience`, `Education`, `Project`
- Repositories: `ProfileRepository`, `ExperienceRepository`, etc.
- API Endpoints: `/api/v1/profiles` (GET, POST, PUT, DELETE)
- Mobile UI: Profile creation/edit screens
- Status: **Production-ready**

**Job Management**:
- Database: `jobs`
- Domain Entity: `Job`
- Repository: `JobRepository`
- API Endpoints: `/api/v1/jobs` (CRUD, search)
- Mobile UI: Job browsing/detail screens
- Status: **Production-ready**

---

### ⚠️ Partially Implemented (Backend Only)

**Preference System** (Database & Entities exist, NO API/UI):

| Component | Database Table | Domain Entity | Repository | API | Mobile UI |
|-----------|---------------|---------------|------------|-----|-----------|
| Sample Resume | ✅ `example_resumes` | ✅ `ExampleResume` | ✅ `ExampleResumeRepository` | ✅ Implemented | ❌ Missing |
| Layout Config | ✅ `layout_configs` | ✅ `LayoutConfig` | ✅ `LayoutConfigRepository` | ✅ Implemented | ❌ Missing |
| Sample Cover Letter | ✅ File storage only (NOT in `example_resumes`) | ❌ No entity (file only) | ❌ N/A | ✅ Implemented | ❌ Missing |
| Writing Style | ✅ `writing_style_configs` | ✅ `WritingStyleConfig` | ✅ `WritingStyleConfigRepository` | ✅ Implemented | ❌ Missing |
| Generation Profile | ✅ `user_generation_profiles` | ✅ `UserGenerationProfile` | ✅ `UserGenerationProfileRepository` | ✅ Implemented | ❌ Missing |
| Consistency Scores | ✅ `consistency_scores` | ✅ `ConsistencyScore` | ❌ Missing | ❌ Missing | ❌ Missing |
| Job Overrides | ✅ `job_type_overrides` | ✅ `JobTypeOverride` | ❌ Missing | ❌ Missing | ❌ Missing |

**Preference Extraction Service**:
- ✅ `PreferenceExtractionService` implemented
- ✅ Methods: `extract_writing_style_from_cover_letter()`, `extract_layout_from_resume()`, `create_user_generation_profile()`
- ✅ Connected to API endpoints (`/api/v1/preferences/*`)

---

### ❌ Not Implemented (Sprint 4 Required)

**Missing Repositories**:
- ❌ `ConsistencyScoreRepository` (for generation validation tracking)
- ❌ `JobTypeOverrideRepository` (for job-specific preference rules)

**Missing Mobile UI** (Sprint 5):
- ❌ Preference setup screen
- ❌ File upload screen
- ❌ Generation profile screen
- ❌ Example resume management screen

---

## Implementation Status Summary

### ✅ Fully Implemented (Backend - Sprint 4 Complete)

**Preference System API Endpoints**:
```
✅ POST   /api/v1/preferences/upload-sample-resume
✅ POST   /api/v1/preferences/upload-cover-letter
✅ GET    /api/v1/preferences/generation-profile
✅ PUT    /api/v1/preferences/generation-profile
✅ GET    /api/v1/preferences/example-resumes
✅ DELETE /api/v1/preferences/example-resumes/{resume_id}
✅ POST   /api/v1/preferences/example-resumes/{resume_id}/set-primary
```

**File Upload Infrastructure**:
- ✅ File upload service (multipart/form-data handling)
- ✅ File validation (PDF, DOCX, TXT formats, 5MB limit)
- ✅ File storage (`uploads/cover_letters/`, `uploads/example_resumes/`)
- ✅ Text extraction service (PyPDF2, python-docx)

**Repositories**:
- ✅ `WritingStyleConfigRepository`
- ✅ `LayoutConfigRepository`
- ✅ `UserGenerationProfileRepository`
- ✅ `ExampleResumeRepository`

**Services**:
- ✅ `PreferenceExtractionService` (LLM-based extraction)
- ✅ `FileUploadService` (upload handling + text extraction)

**Status**: Backend preference system is **PRODUCTION READY**. Mobile UI implementation needed in Sprint 5.

---

## User Workflows

### Phase 1: Initial Profile Setup (One-Time)

**Step 1.1: Create Master Profile** (✅ Implemented)
1. User creates account
2. User navigates to "Create Profile" screen
3. User manually fills forms:
   - Personal info (name, email, phone, location)
   - Professional summary
   - Work experiences (title, company, dates, achievements)
   - Education (degree, institution, graduation date)
   - Skills (technical, soft skills)
   - Projects (name, description, technologies)
4. System saves to database as structured data
5. Master profile complete

**Step 1.2: Upload Sample Resume** (⚠️ Sprint 4 - Not Implemented)
1. User uploads polished resume (PDF/DOCX)
2. System extracts text using PyPDF2/python-docx
3. LLM analyzes structure:
   - Section order
   - Bullet point style
   - Date format
   - Header style
   - Content density
4. System creates `LayoutConfig` in database
5. User reviews/adjusts extracted preferences:
   - Drag-and-drop section reordering
   - Choose bullet format with live preview
   - Set target page count (1 or 2 pages)
   - Configure ATS optimization level
6. Save layout preferences

**Step 1.3: Upload Sample Cover Letter** (⚠️ Sprint 4 - Not Implemented)
1. User uploads cover letter (PDF/DOCX)
2. System extracts text
3. LLM analyzes writing style:
   - Tone (formal/enthusiastic/authoritative)
   - Vocabulary complexity (1-10)
   - Sentence structure patterns
   - Active/passive voice ratio
   - Common action verbs
   - Transition phrases
4. System creates `WritingStyleConfig` in database
5. User reviews/adjusts preferences:
   - Adjust tone slider (1-10)
   - Toggle technical jargon usage
   - Preview sample paragraphs
6. Save writing style preferences

**Step 1.4: Finalize Generation Profile** (⚠️ Sprint 4 - Not Implemented)
1. System creates `UserGenerationProfile` linking:
   - Master profile (factual content)
   - Layout config (structure)
   - Writing style config (tone)
2. User sets quality targets:
   - Target ATS score (0.8-0.95)
   - Keyword density preference
   - Skill emphasis strategy
3. Profile ready for job-specific generation

---

### Phase 2: Job-Specific Generation (Per Application)

**Step 2.1: Select Target Job** (✅ Implemented)
1. User searches for jobs OR manually creates job posting
2. User saves job to JobWise
3. Job stored with: title, company, location, description, requirements, keywords

**Step 2.2: Generate Tailored Documents** (⚠️ Sprint 4 - LLM Integration)
1. User taps "Generate Resume for This Job"
2. System executes AI pipeline:

   **Stage 1 (3s)**: Analysis & Matching
   - LLM parses job description → extract requirements
   - Score master profile content by relevance
   - Rank experiences/projects (highest scores first)
   - Identify skill gaps

   **Stage 2 (5s)**: Generation & Validation
   - Apply layout preferences (from sample resume)
   - Apply writing style (from sample cover letter)
   - Generate tailored resume using ranked content
   - Generate cover letter
   - Validate ATS compliance
   - Self-check for fabrication

3. System returns:
   - Tailored resume (PDF + JSON)
   - Tailored cover letter (PDF + JSON)
   - Generation report:
     - Keyword coverage: 12/15 matched
     - ATS score: 0.87
     - Consistency with examples: 0.92
     - Recommendations for improvement

**Step 2.3: Review & Refine** (Future Enhancement)
1. User reviews generated documents
2. User provides feedback:
   - **Quick adjustments**: "too formal" / "emphasize ML experience"
   - **Manual edits**: Direct text changes
   - **Preference updates**: Adjust tone slider, keyword density
3. System response options:

   **Option A: Quick Regeneration**
   - User clicks "Too formal" → system regenerates with tone -2
   - Regeneration time: ~3-5 seconds

   **Option B: Learn from Edits**
   - User manually edits generated resume
   - System analyzes edits: "User prefers 'developed' over 'created'"
   - Offers to update preferences: "Apply these changes to future generations?"
   - Updates `WritingStyleConfig` if accepted

   **Option C: Comparative Refinement**
   - User uploads manually edited version
   - System performs diff analysis
   - Extracts preference adjustments automatically
   - Updates profile settings

4. User saves final version

**Step 2.4: Job-Specific Overrides** (Future Enhancement)
1. User can create job-type-specific rules:
   - "For data science roles, emphasize ML projects 2x"
   - "For startup roles, use more enthusiastic tone (+2)"
   - "For finance roles, omit Project X"
2. System stores in `job_type_overrides` table
3. Rules apply automatically to matching future jobs

---

### Phase 3: Continuous Improvement (Future Enhancement)

**Incremental Profile Updates**:
1. User uploads new master resume → re-extract content strengths
2. User uploads new example resume → LLM re-analyzes layout
3. User uploads new cover letter → LLM re-generates writing style
4. System compares with existing preferences (shows diff)
5. User approves/rejects changes
6. Merge approved updates

**A/B Testing & Manual Tuning**:
1. **Style Lab**: Test writing style settings on sample content
2. **Layout Designer**: Visual editor for section order
3. **Skill Manager**: Tag skills, set proficiency levels
4. **Generation Presets**: Save configurations for different job types

---

## Security Implementation

### Multi-Layer Security (✅ PRODUCTION READY)

**Layer 1: Authentication (JWT)**
- All endpoints require valid JWT token
- Implementation: `current_user: UserResponse = Depends(get_current_user)`
- Coverage: ALL preference endpoints

**Layer 2: User ID Filtering (Database)**
- All queries filter by `current_user.id`
- Example: `examples = await example_repo.get_by_user_id(current_user.id)`
- Guarantee: Users can ONLY query their own data

**Layer 3: Ownership Verification (Application Logic)**
- Explicit ownership checks before modifications
- Example:
  ```python
  example = await example_repo.get_by_id(resume_id)
  if example.user_id != current_user.id:
      logger.warning(f"Unauthorized delete attempt: user {current_user.id} tried to delete resume {resume_id}")
      raise HTTPException(status_code=403, detail="Not authorized")
  ```
- Guarantee: Users cannot modify resources they don't own

**Layer 4: File Path Security (Filesystem)**
- User ID embedded in filename: `{user_id}_{uuid}.{extension}`
- Example: User 123 → `123_a1b2c3d4-e5f6-7890-abcd-ef1234567890.pdf`
- Ownership verification:
  ```python
  def verify_file_ownership(file_path: str, user_id: int) -> bool:
      filename = Path(file_path).name
      return filename.startswith(f"{user_id}_")
  ```
- Guarantee: File paths reveal ownership

**Layer 5: Logging & Audit Trail**
- All security events logged
- Logged events:
  ```python
  logger.info(f"User {current_user.id} uploading sample resume: {file.filename}")
  logger.warning(f"Unauthorized delete attempt: user {current_user.id} tried to delete resume {resume_id}")
  ```
- Guarantee: Security incidents traceable

---

### Attack Vector Defense

**❌ Attack 1: Direct Resume ID Access**
- **Attempt**: User A tries to access User B's resume by ID
- **Defense**: Repository filters by User A's ID → User B's resumes never returned
- **Result**: BLOCKED

**❌ Attack 2: Resume Deletion by Another User**
- **Attempt**: User A tries to delete User B's resume
- **Defense**: Ownership check fails → HTTP 403 + logged
- **Result**: BLOCKED + LOGGED

**❌ Attack 3: File Path Traversal**
- **Attempt**: User A tries to access User B's file directly
- **Defense**: File ownership verification fails → HTTP 403
- **Result**: BLOCKED + LOGGED

**❌ Attack 4: Profile Injection**
- **Attempt**: User A tries to view User B's generation profile
- **Defense**: Query filtered by User A's ID → User B's profile never accessible
- **Result**: BLOCKED

---

### Security Best Practices Implemented

✅ **Principle of Least Privilege**: Users can ONLY access their own resources  
✅ **Defense in Depth**: Multiple independent security layers  
✅ **Fail Secure**: Generic error messages (no data leakage)  
✅ **Audit Trail**: All sensitive operations logged  
✅ **Input Validation**: File size limits (5MB), type validation (PDF/DOCX/TXT), content type verification

---

### Future Security Enhancements

**Priority 1: Rate Limiting**
```python
from slowapi import Limiter
@router.post("/upload-sample-resume")
@limiter.limit("10/hour")
async def upload_sample_resume(...):
```

**Priority 2: File Content Scanning**
```python
scan_result = await virus_scanner.scan(file_content)
if not scan_result.is_safe:
    raise SecurityException("Malicious content detected")
```

**Priority 3: Encryption at Rest**
```python
encrypted_content = encryptor.encrypt(file_content, user_key)
```

**Priority 4: Access Logging to Database**
```python
await audit_repo.log_access(
    user_id=current_user.id,
    action="delete_resume",
    resource_id=resume_id,
    success=True
)
```

---

## Sprint 4 Implementation Guide

### Estimated Effort: 8 days backend + 4 days mobile (Sprint 5)

### Phase 1: Infrastructure Setup (2 days)

**Task 1.1: File Upload Service**
```python
# backend/app/application/services/file_upload/file_upload_service.py
class FileUploadService:
    async def save_upload(
        self,
        file: UploadFile,
        user_id: int,
        file_type: str
    ) -> str:
        # Validate file size (max 5MB)
        # Validate file type (PDF, DOCX, TXT)
        # Generate secure filename: {user_id}_{uuid}.{ext}
        # Save to storage directory
        # Return storage path
```

**Task 1.2: Text Extraction Service**
```python
# backend/app/application/services/file_upload/text_extraction_service.py
class TextExtractionService:
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        # Detect file type
        # Extract text (PyPDF2 for PDF, python-docx for DOCX)
        # Parse metadata (page count, word count)
        # Return extracted text + metadata
```

**Dependencies Required** (`requirements.txt`):
```txt
python-multipart==0.0.6  # File uploads
python-docx==1.1.0       # DOCX text extraction
PyPDF2==3.0.1            # PDF text extraction
```

**PowerShell Commands**:
```powershell
cd backend ; .\venv\Scripts\Activate.ps1 ; pip install python-multipart python-docx PyPDF2
```

---

### Phase 2: Repository Layer (1 day)

**Task 2.1: Create Missing Repositories**
```python
# backend/app/infrastructure/repositories/writing_style_config_repository.py
class WritingStyleConfigRepository:
    async def create(self, config: WritingStyleConfig) -> WritingStyleConfig
    async def get_by_id(self, config_id: str) -> Optional[WritingStyleConfig]
    async def get_by_user_id(self, user_id: int) -> List[WritingStyleConfig]
    async def update(self, config: WritingStyleConfig) -> WritingStyleConfig
    async def delete(self, config_id: str, user_id: int) -> bool

# backend/app/infrastructure/repositories/layout_config_repository.py
class LayoutConfigRepository:
    async def create(self, config: LayoutConfig) -> LayoutConfig
    async def get_by_id(self, config_id: str) -> Optional[LayoutConfig]
    async def get_by_user_id(self, user_id: int) -> List[LayoutConfig]
    async def update(self, config: LayoutConfig) -> LayoutConfig
    async def delete(self, config_id: str, user_id: int) -> bool

# backend/app/infrastructure/repositories/user_generation_profile_repository.py
class UserGenerationProfileRepository:
    async def create(self, profile: UserGenerationProfile) -> UserGenerationProfile
    async def get_by_user_id(self, user_id: int) -> Optional[UserGenerationProfile]
    async def update(self, profile: UserGenerationProfile) -> UserGenerationProfile
    async def delete(self, user_id: int) -> bool
```

**Task 2.2: Write Unit Tests**
```powershell
cd backend ; python -m pytest tests/repositories/test_writing_style_config_repository.py -v
cd backend ; python -m pytest tests/repositories/test_layout_config_repository.py -v
cd backend ; python -m pytest tests/repositories/test_user_generation_profile_repository.py -v
```

---

### Phase 3: LLM Prompt Engineering (1 day)

**Task 3.1: Writing Style Prompts**
```python
# backend/app/domain/prompts/writing_style_prompts.py
class WritingStylePrompts:
    @staticmethod
    def create_style_analysis_prompt(cover_letter_text: str) -> str:
        return f"""Analyze the following cover letter and extract writing style characteristics:

{cover_letter_text}

Extract and return as JSON:
1. Tone (formal/semi-formal/enthusiastic/authoritative)
2. Formality level (1-10)
3. Vocabulary complexity (1-10)
4. Sentence structure patterns
5. Active vs passive voice ratio (0.0-1.0)
6. First-person usage frequency
7. Top 10 action verbs used
8. Common transition phrases
9. Technical jargon usage (minimal/balanced/heavy)

Return valid JSON matching this schema: {{...}}
"""
```

**Task 3.2: Structural Analysis Prompts**
```python
# backend/app/domain/prompts/structural_analysis_prompts.py
class StructuralAnalysisPrompts:
    @staticmethod
    def create_layout_analysis_prompt(resume_text: str) -> str:
        return f"""Analyze the following resume and extract structural characteristics:

{resume_text}

Extract and return as JSON:
1. Section order (exact sequence)
2. Bullet point style (standard/CAR/STAR/achievement-focused)
3. Average bullets per experience (min-max range)
4. Date format pattern
5. Location display style
6. Summary/objective length and format
7. Project description style
8. Skill categorization approach
9. Overall layout structure (single-column/two-column)
10. White space and density assessment

Return valid JSON matching this schema: {{...}}
"""
```

**Task 3.3: Test with Groq LLM**
```python
# Test prompt effectiveness
llm_service = GroqLLMAdapter(api_key=os.getenv("GROQ_API_KEY"))
response = await llm_service.generate(
    messages=[
        LLMMessage(role="system", content=WritingStylePrompts.create_style_analysis_prompt(sample_text)),
        LLMMessage(role="user", content="Analyze this cover letter.")
    ],
    model="llama-3.1-8b-instant",
    temperature=0.2,
    max_tokens=2000
)
```

---

### Phase 4: API Endpoints (2 days)

**Task 4.1: Create Preferences Router**
```python
# backend/app/presentation/api/preferences.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.application.services.preference_extraction_service import PreferenceExtractionService
from app.application.services.file_upload.file_upload_service import FileUploadService

router = APIRouter(prefix="/preferences", tags=["preferences"])

@router.post("/upload-sample-resume", status_code=201)
async def upload_sample_resume(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_upload_service),
    pref_service: PreferenceExtractionService = Depends(get_preference_extraction_service)
):
    """
    Upload sample resume file and extract layout preferences.
    
    - **file**: Resume file (PDF, DOCX, or TXT, max 5MB)
    - **Returns**: ExampleResume ID + extracted LayoutConfig
    """
    logger.info(f"User {current_user.id} uploading sample resume: {file.filename}")
    
    # Save upload
    storage_path = await file_service.save_upload(file, current_user.id, "resume")
    
    # Extract text
    extracted_text = await file_service.extract_text(storage_path)
    
    # Create ExampleResume record
    example_resume = await pref_service.create_example_resume(
        user_id=current_user.id,
        file_type="resume",
        storage_path=storage_path,
        extracted_text=extracted_text["text"],
        metadata=extracted_text["metadata"]
    )
    
    # Extract layout preferences using LLM
    layout_config = await pref_service.extract_layout_from_resume(
        user_id=current_user.id,
        resume_text=extracted_text["text"]
    )
    
    return {
        "example_resume_id": example_resume.id,
        "layout_config_id": layout_config.id,
        "extracted_preferences": layout_config.to_dict(),
        "message": "Layout preferences extracted successfully"
    }

@router.post("/upload-cover-letter", status_code=201)
async def upload_cover_letter(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    file_service: FileUploadService = Depends(get_file_upload_service),
    pref_service: PreferenceExtractionService = Depends(get_preference_extraction_service)
):
    """
    Upload sample cover letter and extract writing style preferences.
    
    - **file**: Cover letter file (PDF, DOCX, or TXT, max 5MB)
    - **Returns**: WritingStyleConfig ID + extracted preferences
    """
    logger.info(f"User {current_user.id} uploading cover letter: {file.filename}")
    
    storage_path = await file_service.save_upload(file, current_user.id, "cover_letter")
    extracted_text = await file_service.extract_text(storage_path)
    
    # Create ExampleResume record (type: cover_letter)
    example_resume = await pref_service.create_example_resume(
        user_id=current_user.id,
        file_type="cover_letter",
        storage_path=storage_path,
        extracted_text=extracted_text["text"],
        metadata=extracted_text["metadata"]
    )
    
    # Extract writing style using LLM
    writing_style = await pref_service.extract_writing_style_from_cover_letter(
        user_id=current_user.id,
        cover_letter_text=extracted_text["text"]
    )
    
    return {
        "writing_style_config_id": writing_style.id,
        "extracted_preferences": writing_style.to_dict(),
        "message": "Writing style preferences extracted successfully"
    }

@router.get("/generation-profile")
async def get_generation_profile(
    current_user = Depends(get_current_user),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """Get user's complete generation preferences."""
    logger.info(f"Fetching generation profile for user {current_user.id}")
    
    profile = await profile_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Generation profile not found")
    
    return profile.to_dict()

@router.put("/generation-profile")
async def update_generation_profile(
    updates: Dict[str, Any],
    current_user = Depends(get_current_user),
    profile_repo: UserGenerationProfileRepository = Depends(get_profile_repo)
):
    """Update generation preferences manually."""
    profile = await profile_repo.get_by_user_id(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Generation profile not found")
    
    # Apply updates
    for key, value in updates.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    updated = await profile_repo.update(profile)
    return updated.to_dict()

@router.get("/example-resumes")
async def list_example_resumes(
    current_user = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_repo)
):
    """List user's uploaded example resumes and cover letters."""
    examples = await example_repo.get_by_user_id(current_user.id)
    return [example.to_dict() for example in examples]

@router.delete("/example-resumes/{resume_id}")
async def delete_example_resume(
    resume_id: str,
    current_user = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_repo),
    file_service: FileUploadService = Depends(get_file_upload_service)
):
    """Delete an uploaded example resume."""
    example = await example_repo.get_by_id(resume_id)
    if not example:
        raise HTTPException(status_code=404, detail="Example resume not found")
    
    # Security: Verify ownership
    if example.user_id != current_user.id:
        logger.warning(f"Unauthorized delete attempt: user {current_user.id} tried to delete resume {resume_id}")
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Delete file from storage
    await file_service.delete_file(example.storage_path)
    
    # Delete database record
    await example_repo.delete(resume_id, current_user.id)
    
    return {"message": "Example resume deleted successfully"}

@router.post("/example-resumes/{resume_id}/set-primary")
async def set_primary_example(
    resume_id: str,
    current_user = Depends(get_current_user),
    example_repo: ExampleResumeRepository = Depends(get_example_repo)
):
    """Mark an example resume as primary reference."""
    example = await example_repo.get_by_id(resume_id)
    if not example:
        raise HTTPException(status_code=404, detail="Example resume not found")
    
    # Security: Verify ownership
    if example.user_id != current_user.id:
        logger.warning(f"Unauthorized modification attempt: user {current_user.id} tried to modify resume {resume_id}")
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Set as primary
    await example_repo.set_primary(resume_id, current_user.id)
    
    return {"message": "Primary example set successfully"}
```

**Task 4.2: Register Router**
```python
# backend/app/main.py
from app.presentation.api import preferences

app.include_router(preferences.router, prefix="/api/v1")
```

**Task 4.3: Write Integration Tests**
```python
# tests/api/test_preferences.py
@pytest.mark.asyncio
async def test_upload_sample_resume():
    with open("tests/fixtures/sample_resume.pdf", "rb") as f:
        files = {"file": ("resume.pdf", f, "application/pdf")}
        response = client.post(
            "/api/v1/preferences/upload-sample-resume",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 201
    data = response.json()
    assert "example_resume_id" in data
    assert "layout_config_id" in data
```

**PowerShell Test Commands**:
```powershell
cd backend ; python -m pytest tests/api/test_preferences.py -v
```

---

### Phase 5: Service Integration (1 day)

**Task 5.1: Connect Services to API**
- Dependency injection for services
- Background task for LLM analysis (async)
- Progress tracking for extraction process

**Task 5.2: Error Handling & Retry Logic**
```python
# Handle LLM failures gracefully
try:
    writing_style = await pref_service.extract_writing_style_from_cover_letter(...)
except LLMServiceError as e:
    logger.error(f"LLM extraction failed: {e}")
    # Return partial result with manual configuration option
    return {"error": "Automatic extraction failed", "fallback": "manual_configuration"}
```

---

### Phase 6: Testing (1 day)

**Task 6.1: Unit Tests**
```powershell
cd backend ; python -m pytest tests/services/test_preference_extraction_service.py -v
cd backend ; python -m pytest tests/services/test_file_upload_service.py -v
```

**Task 6.2: Integration Tests**
```powershell
cd backend ; python -m pytest tests/api/test_preferences.py -v
```

**Task 6.3: End-to-End Tests**
```powershell
cd backend ; python -m pytest tests/e2e/test_preference_setup_flow.py -v
```

**Task 6.4: Load Testing**
```python
# Test LLM rate limits (Groq free tier: 30 RPM, 40,000 TPM)
# Verify retry logic handles rate limit errors
```

---

### Sprint 4 Checklist

**Infrastructure Setup**:
- [ ] Create `FileUploadService` with multipart/form-data handling
- [ ] Implement `TextExtractionService` (PDF, DOCX, TXT extraction)
- [ ] Create file storage directory structure
- [ ] Add file validation utilities (size, type, content)
- [ ] Install dependencies: `python-multipart`, `python-docx`, `PyPDF2`

**Repository Layer**:
- [ ] Create `WritingStyleConfigRepository`
- [ ] Create `LayoutConfigRepository`
- [ ] Create `UserGenerationProfileRepository`
- [ ] Write unit tests for all repositories

**LLM Prompt Engineering**:
- [ ] Create `WritingStylePrompts` class with extraction prompts
- [ ] Create `StructuralAnalysisPrompts` class with layout prompts
- [ ] Test prompts with Groq LLM
- [ ] Optimize for JSON-mode output

**API Endpoints**:
- [ ] Create `backend/app/presentation/api/preferences.py`
- [ ] Implement `/upload-sample-resume` endpoint
- [ ] Implement `/upload-cover-letter` endpoint
- [ ] Implement `/generation-profile` GET/PUT endpoints
- [ ] Implement example resume management endpoints
- [ ] Add authentication middleware
- [ ] Write integration tests

**Service Integration**:
- [ ] Connect `PreferenceExtractionService` to API endpoints
- [ ] Implement background task for LLM analysis (async)
- [ ] Add progress tracking for extraction process
- [ ] Implement error handling and retry logic

**Testing**:
- [ ] Unit tests for preference extraction service
- [ ] Integration tests for file upload flow
- [ ] End-to-end tests for full preference setup
- [ ] Load testing for LLM calls (rate limits)

**Documentation**:
- [ ] Update API documentation (OpenAPI spec)
- [ ] Document file upload requirements
- [ ] Document LLM prompt templates
- [ ] Document security implementation

---

## Performance Targets

**LLM Analysis Time**:
- Writing Style Extraction: ~3-5 seconds (Llama 3.1 8B)
- Layout Analysis: ~3-5 seconds (Llama 3.1 8B)
- Total Setup Time: ~10 seconds for both uploads

**Generation Pipeline Time**:
- Stage 1 (Analysis): <3 seconds (p50: 1.5s)
- Stage 2 (Generation): <5 seconds (p50: 4s)
- **Total Pipeline**: <8 seconds (p50: 5.5s)

**Optimization Strategies**:
1. **Async Processing**: Run LLM analysis in background, return immediately
2. **Polling**: Mobile polls for extraction status every 2 seconds
3. **Caching**: Cache extracted preferences, only re-extract on new upload
4. **Batch Analysis**: If user uploads multiple examples, analyze in parallel

---

## Dependencies Summary

**Python Packages** (`requirements.txt`):
```txt
# LLM Integration
groq==0.33.0

# File Handling
python-multipart==0.0.6  # File uploads
python-docx==1.1.0       # DOCX text extraction
PyPDF2==3.0.1            # PDF text extraction

# Already Installed
fastapi==0.x
pydantic==2.x
sqlalchemy==2.x
python-dotenv==1.0.0
```

**PowerShell Installation**:
```powershell
cd backend ; .\venv\Scripts\Activate.ps1 ; pip install groq python-multipart python-docx PyPDF2
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Master Profile** | User's manually entered career data (experiences, education, skills, projects) stored in database |
| **Sample Resume** | User-uploaded resume file (PDF/DOCX) used to extract layout/structure preferences |
| **Sample Cover Letter** | User-uploaded cover letter file used to extract writing style/tone preferences |
| **Selected Job** | Target job posting the user wants to apply to |
| **Layout Config** | Extracted structural preferences (section order, bullet style, formatting) |
| **Writing Style Config** | Extracted writing preferences (tone, vocabulary, sentence structure) |
| **Generation Profile** | Combined user preferences linking Master Profile + Layout Config + Writing Style Config |
| **ATS** | Applicant Tracking System - software used by employers to filter resumes |
| **Groq** | Ultra-fast LLM inference service (10x-100x faster than traditional providers) |
| **TPS** | Tokens Per Second - LLM generation speed metric |

---

**Document Status**: ✅ COMPLETE - All 5 source documents condensed into single reference

**Next Steps**: Execute Sprint 4 implementation checklist (8 days estimated)
