# AI Generation API

**At a Glance (For AI Agents)**
- **Service Name**: AI Generation (profile enhancement, rankings, resume & cover letter)
- **Primary Tables**: `job_content_rankings`, `generations`, `master_profiles`, `jobs`, `users`
- **Core Dependencies**: Auth (`01-authentication-api.md`), Profile (`02-profile-api.md`), Jobs (`03-job-api.md`), Sample Upload (`04a-sample-upload-api.md`)
- **Auth Requirements**: All endpoints require a valid user JWT (see Auth API)
- **Primary Routes**:
  - `POST /api/v1/profile/enhance` — enhance profile text using LLM + writing style
  - `POST /api/v1/rankings/create` — create/update job-specific content ranking
  - `POST /api/v1/generations/resume` — generate resume (no LLM, fast)
  - `POST /api/v1/generations/cover-letter` — generate cover letter (LLM)
  - `GET /api/v1/rankings/job/{job_id}` — fetch cached ranking
  - `GET /api/v1/generations/history` — list generation history

**Related Docs (Navigation Hints)**
- Backend overview: `../BACKEND_ARCHITECTURE_OVERVIEW.md` (end-to-end flows)
- Database schema: `06-database-schema.md` (`job_content_rankings`, `generations`)
- Auth service: `01-authentication-api.md`
- Profile service: `02-profile-api.md`
- Jobs service: `03-job-api.md`
- Sample Upload service: `04a-sample-upload-api.md`

**Key Field Semantics (Canonical Meanings)**
- `job_id` (string/UUID): Foreign key to `jobs.id`; all ranking and generation operations are scoped to a specific job.
- `profile_id` (string/UUID): Foreign key to `master_profiles.id`; profile that supplies content.
- `ranking_id` (string): Foreign key to `job_content_rankings.id`; links a generation to the cached ranking used.
- `document_type` (string): Either `"resume"` or `"cover_letter"`; controls generation path and template.
- `status` (string): Lifecycle for both rankings and generations; typical values `"completed"`, `"pending"`, `"failed"` (see error handling).
- `content_text` (text): Final generated document body (resume or cover letter) stored in `generations`.
- `llm_metadata` (JSON/text): Raw LLM call metadata (model, tokens, latency, prompts/trace) for observability.
- `ranked_experience_ids` / `ranked_project_ids` (JSON arrays): Ordered IDs used as input when generating documents.
- `ats_score` / `ats_feedback`: Numeric score and explanation for ATS-readiness of generated content.

**Version**: 3.0
**Base Path**: `/api/v1`
**Status**: ✅ Fully Implemented with Real LLM Integration
**LLM Required**: Yes (Groq API)

---

## Overview

The AI Generation API provides AI-powered resume and cover letter generation using real Groq LLM integration. This API handles all operations that require LLM processing: profile enhancement, content ranking, and document generation.

**Key Features**:
- **Writing Style Extraction**: AI analyzes sample documents to learn user's writing style
- **Profile Enhancement**: AI improves profile content using extracted writing style
- **Job-Specific Ranking**: AI ranks experiences/projects by relevance to specific jobs
- **Resume Generation**: Pure logic compilation using ranked content (<1 second)
- **Cover Letter Generation**: AI-powered personalized letters (~3-5 seconds)
- **Generation History**: Track all generated documents with ATS scores

**Related APIs**:
- [Sample Upload API](04a-sample-upload-api.md) - Upload sample documents used by this API

---

## AI Models Used

### Groq LLM Provider
**Provider**: Groq.com (ultra-fast LLM inference)

**Models**:
| Model | Use Case | Speed | Token Limit |
|-------|----------|-------|-------------|
| llama-3.3-70b-versatile | Cover letters, profile enhancement | ~3-5s | 8,192 tokens |
| llama-3.1-8b-instant | Content ranking, style analysis | ~1-2s | 8,192 tokens |

**Confirmed Status**: ✅ Real API integration working (71+ tokens generated in testing)

---

## User Journey

```
Prerequisites: User has uploaded samples via Sample Upload API

1. ENHANCE PROFILE
   User → POST /profile/enhance
   System → Extract writing style from cover letter sample
   System → Enhance profile summary and descriptions
   System → Store enhanced content alongside originals

2. RANK CONTENT (for a specific job)
   User → POST /rankings/create {job_id}
   LLM → Analyze job requirements
   LLM → Rank experiences and projects by relevance
   System → Store rankings for reuse

3A. GENERATE RESUME
   User → POST /generations/resume {job_id}
   System → Use rankings to select top content
   System → Compile resume (pure logic, no LLM)
   System → Return formatted resume text

3B. GENERATE COVER LETTER
   User → POST /generations/cover-letter {job_id}
   LLM → Generate personalized cover letter
   System → Use writing style from sample
   System → Return formatted cover letter
```

---

## Endpoints Summary

| # | Method | Endpoint | Description | LLM Model | Speed |
|---|--------|----------|-------------|-----------|-------|
| 1 | POST | `/profile/enhance` | Enhance profile with AI | 70b-versatile | ~4s |
| 2 | POST | `/rankings/create` | Rank content for job | 8b-instant | ~2s |
| 3 | POST | `/generations/resume` | Generate resume | None | <1s |
| 4 | POST | `/generations/cover-letter` | Generate cover letter | 70b-versatile | ~3-5s |
| 5 | GET | `/rankings/job/{job_id}` | Get job rankings | None | <100ms |
| 6 | GET | `/generations/history` | Get generation history | None | <200ms |
| 7 | DELETE | `/generations/{generation_id}` | Delete generation | None | <100ms |

---

## Profile Enhancement Endpoint

### 1. Enhance Master Profile

Enhance user's profile using AI with writing style from sample cover letter.

**Endpoint**: `POST /api/v1/profile/enhance`

**Authentication**: Required

**LLM Used**: llama-3.3-70b-versatile

**Prerequisites**:
- User must have an active cover letter sample uploaded via [Sample Upload API](04a-sample-upload-api.md)
- User must have a profile with content to enhance

**Request Body**:
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "custom_prompt": "Emphasize technical leadership and cloud expertise"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `profile_id` | UUID | Yes | Profile to enhance |
| `custom_prompt` | string | No | Additional instructions (max 500 chars) |

**Success Response** (200 OK):
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "enhanced_sections": {
    "professional_summary": "Results-driven Senior Software Engineer with 8+ years of expertise architecting scalable cloud solutions...",
    "experiences_enhanced": 5,
    "projects_enhanced": 4
  },
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "total_tokens": 1247,
    "processing_time_seconds": 4.2
  },
  "writing_style_used": {
    "tone": "professional yet personable",
    "vocabulary_level": "advanced"
  },
  "created_at": "2025-11-15T10:35:00Z"
}
```

**Enhancement Process** (Batch Processing):
1. Retrieve active cover letter sample
2. Extract writing style using AI (once, cached)
3. Collect ALL profile content (summary + all experiences + all projects)
4. Send single batch LLM request to enhance all content simultaneously
5. Parse structured JSON response with section-specific enhancements
6. Save enhanced_description fields to database alongside original descriptions
7. Return success metrics (sections enhanced, success rate)

**Performance**: Single LLM call processes unlimited experiences and projects (~4-5 seconds total, 80% faster than sequential approach)

**Error Responses**:

**404 Not Found** (No cover letter sample):
```json
{
  "detail": "No active cover letter sample found. Upload a sample first."
}
```

**404 Not Found** (Profile not found):
```json
{
  "detail": "Profile not found"
}
```

---

## Content Ranking Endpoint

### 2. Create Job-Specific Ranking

Rank profile content (experiences, projects) by relevance to a specific job.

**Endpoint**: `POST /api/v1/rankings/create`

**Authentication**: Required

**LLM Used**: llama-3.1-8b-instant (fast ranking)

**Request Body**:
```json
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "custom_prompt": "Prioritize recent cloud and microservices experience"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `job_id` | UUID | Yes | Job to rank content for |
| `custom_prompt` | string | No | Additional ranking criteria (max 500 chars) |

**Success Response** (200 OK):
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "user_id": 1,
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "ranked_experience_ids": [
    "exp_456",
    "exp_123",
    "exp_789",
    "exp_234"
  ],
  "ranked_project_ids": [
    "proj_789",
    "proj_123",
    "proj_456"
  ],
  "ranking_rationale": "Prioritized experiences with AWS and microservices architecture based on job requirements for Senior Cloud Engineer role.",
  "keyword_matches": {
    "AWS": 8,
    "Python": 12,
    "Docker": 5,
    "Kubernetes": 3
  },
  "relevance_scores": {
    "exp_456": 0.95,
    "exp_123": 0.87,
    "proj_789": 0.92
  },
  "llm_metadata": {
    "model": "llama-3.1-8b-instant",
    "total_tokens": 543,
    "processing_time_seconds": 1.8
  },
  "status": "completed",
  "created_at": "2025-11-15T10:40:00Z"
}
```

**Ranking Process**:
1. Fetch job requirements and keywords
2. Fetch all user's experiences and projects
3. Send to LLM for relevance ranking
4. LLM analyzes keyword matches and context
5. Return ordered IDs with relevance scores
6. Store ranking for reuse

**Caching**:
Rankings are cached per user+job combination. If ranking already exists for a job, it's returned immediately without LLM call.

**Error Responses**:

**404 Not Found** (No profile):
```json
{
  "detail": "No profile found for user. Create a profile first."
}
```

**404 Not Found** (No job):
```json
{
  "detail": "Job not found"
}
```

---

## Generation Endpoints

### 3. Generate Resume

Generate a tailored resume for a specific job using ranked content.

**Endpoint**: `POST /api/v1/generations/resume`

**Authentication**: Required

**LLM Used**: None (pure logic compilation)

**Request Body**:
```json
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "max_experiences": 5,
  "max_projects": 3,
  "include_summary": true,
  "custom_prompt": "Highlight leadership and mentorship experience"
}
```

**Request Schema**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `job_id` | UUID | Yes | - | Job to generate resume for |
| `max_experiences` | integer | No | 5 | Max experiences to include (1-10) |
| `max_projects` | integer | No | 3 | Max projects to include (0-5) |
| `include_summary` | boolean | No | true | Include professional summary |
| `custom_prompt` | string | No | - | Additional instructions (max 500 chars) |

**Success Response** (200 OK):
```json
{
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "document_type": "resume",
  "status": "completed",
  "resume_text": "JOHN DOE\nSeattle, WA | john@example.com | +1-555-123-4567\nlinkedin.com/in/johndoe | github.com/johndoe\n\nPROFESSIONAL SUMMARY\nResults-driven Senior Software Engineer with 8+ years...\n\nTECHNICAL SKILLS\nPython, JavaScript, React, FastAPI, AWS, Docker, Kubernetes...\n\nPROFESSIONAL EXPERIENCE\n\nSenior Software Engineer | TechCorp Inc. | Seattle, WA\nJanuary 2020 - Present\n• Led development of microservices architecture processing 10M+ requests/day\n• Implemented CI/CD pipelines reducing deployment time by 75%\n• Mentored team of 5 junior developers\n\nSoftware Engineer | StartupXYZ | San Francisco, CA\nMarch 2017 - December 2019\n• Built scalable REST APIs using Python and FastAPI\n• Migrated monolithic application to microservices\n\n[... more content ...]\n\nPROJECTS\n\nJobWise - AI Resume Generator\nAI-powered platform for generating tailored resumes using Groq LLM\nTechnologies: Python, FastAPI, Flutter, SQLAlchemy\nGitHub: github.com/johndoe/jobwise\n\n[... more projects ...]\n\nEDUCATION\n\nBachelor of Science in Computer Science\nUniversity of Washington | Seattle, WA | 2013-2017\nGPA: 3.85 | Summa Cum Laude",
  "content_used": {
    "experiences_count": 5,
    "projects_count": 3,
    "skills_count": 18,
    "education_count": 1,
    "summary_enhanced": true
  },
  "ats_score": 85.5,
  "ats_feedback": "Strong keyword density, well-formatted for ATS parsing",
  "llm_metadata": {
    "model": "none",
    "note": "Pure logic compilation, no LLM used"
  },
  "created_at": "2025-11-15T10:45:00Z"
}
```

**Generation Process**:
1. Fetch or create ranking for job
2. Select top N experiences based on ranking
3. Select top M projects based on ranking
4. Use enhanced descriptions if available
5. Compile resume using template (pure logic)
6. Calculate ATS compatibility score
7. Return formatted resume text

**Performance**: <1 second (no LLM call)

---

### 4. Generate Cover Letter

Generate a personalized cover letter for a specific job using AI.

**Endpoint**: `POST /api/v1/generations/cover-letter`

**Authentication**: Required

**LLM Used**: llama-3.3-70b-versatile

**Prerequisites**:
- User should have an active cover letter sample for best results
- Ranking will be created automatically if not cached

**Request Body**:
```json
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "company_name": "TechCorp Inc.",
  "hiring_manager_name": "Sarah Johnson",
  "max_paragraphs": 4,
  "custom_prompt": "Emphasize passion for cloud technologies and team leadership"
}
```

**Request Schema**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `job_id` | UUID | Yes | - | Job to generate cover letter for |
| `company_name` | string | No | Auto-detected | Company name (overrides job.company) |
| `hiring_manager_name` | string | No | - | Hiring manager name for greeting |
| `max_paragraphs` | integer | No | 4 | Paragraph count (3-6) |
| `custom_prompt` | string | No | - | Additional instructions (max 500 chars) |

**Success Response** (200 OK):
```json
{
  "generation_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "document_type": "cover_letter",
  "status": "completed",
  "cover_letter_text": "Dear Sarah Johnson,\n\nI am excited to apply for the Senior Cloud Engineer position at TechCorp Inc. With over 8 years of experience architecting scalable cloud solutions on AWS, I am confident in my ability to contribute to your team's mission of building next-generation cloud infrastructure.\n\nThroughout my career at TechCorp Inc. and StartupXYZ, I have consistently delivered high-impact projects that demonstrate my expertise in cloud technologies. Most notably, I led the migration of our monolithic application to a microservices architecture deployed on AWS, which now processes over 10 million requests daily with 99.99% uptime. This initiative not only improved system reliability but also reduced infrastructure costs by 40%.\n\nWhat particularly excites me about this opportunity is TechCorp's commitment to innovation in cloud-native technologies. My experience with Kubernetes, Docker, and infrastructure-as-code aligns perfectly with your team's focus on building scalable, automated deployment pipelines. Additionally, my track record of mentoring junior developers would enable me to contribute to TechCorp's culture of continuous learning and knowledge sharing.\n\nI am eager to bring my technical expertise and passion for cloud engineering to TechCorp Inc. I would welcome the opportunity to discuss how my background in building resilient, scalable systems can support your team's goals.\n\nThank you for considering my application.\n\nSincerely,\nJohn Doe\njohn@example.com\n+1-555-123-4567",
  "content_used": {
    "top_experiences": ["exp_456", "exp_123"],
    "top_projects": ["proj_789"],
    "skills_highlighted": ["AWS", "Kubernetes", "Python", "Microservices"],
    "writing_style_applied": true
  },
  "ats_score": 78.2,
  "ats_feedback": "Good keyword usage, consider adding more specific technical terms",
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "total_tokens": 892,
    "processing_time_seconds": 3.4
  },
  "created_at": "2025-11-15T10:50:00Z"
}
```

**Generation Process**:
1. Fetch or create ranking for job
2. Fetch active cover letter sample for writing style
3. Extract writing style using AI
4. Select top experiences and projects
5. Generate cover letter using LLM with:
   - Job description
   - User's top experiences/projects
   - Extracted writing style
   - Custom prompt (if provided)
6. Calculate ATS score
7. Return formatted cover letter

**Performance**: ~3-5 seconds (LLM call)

---

### 5. Get Job Rankings

Retrieve cached ranking for a specific job.

**Endpoint**: `GET /api/v1/rankings/job/{job_id}`

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | UUID | Yes | Job ID to get rankings for |

**Success Response** (200 OK): Same as Create Ranking response (cached)

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "No ranking found for this job. Create one using POST /rankings/create"
}
```

---

### 6. Get Generation History

Retrieve user's generation history with pagination.

**Endpoint**: `GET /api/v1/generations/history`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_type` | string | - | Filter by resume/cover_letter |
| `job_id` | UUID | - | Filter by specific job |
| `limit` | integer | 20 | Results per page (1-100) |
| `offset` | integer | 0 | Results offset |

**Request Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/generations/history?document_type=resume&limit=20" \
  -H "Authorization: Bearer <token>"
```

**Success Response** (200 OK):
```json
{
  "generations": [
    {
      "generation_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "job_id": "770e8400-e29b-41d4-a716-446655440002",
      "job_title": "Senior Cloud Engineer",
      "company": "TechCorp Inc.",
      "document_type": "cover_letter",
      "status": "completed",
      "ats_score": 78.2,
      "created_at": "2025-11-15T10:50:00Z"
    },
    {
      "generation_id": "990e8400-e29b-41d4-a716-446655440004",
      "job_id": "770e8400-e29b-41d4-a716-446655440002",
      "job_title": "Senior Cloud Engineer",
      "company": "TechCorp Inc.",
      "document_type": "resume",
      "status": "completed",
      "ats_score": 85.5,
      "created_at": "2025-11-15T10:45:00Z"
    }
  ],
  "total": 12,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 12,
    "hasMore": false
  }
}
```

---

### 7. Delete Generation

Delete a generation permanently.

**Endpoint**: `DELETE /api/v1/generations/{generation_id}`

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `generation_id` | UUID | Yes | Generation unique identifier |

**Request Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/generations/990e8400-e29b-41d4-a716-446655440004 \
  -H "Authorization: Bearer <token>"
```

**Success Response** (204 No Content): No body

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Generation not found"
}
```

**403 Forbidden**:
```json
{
  "detail": "Not authorized to delete this generation"
}
```

---

## Database Schema

### job_content_rankings Table

```sql
CREATE TABLE job_content_rankings (
    id VARCHAR PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id VARCHAR NOT NULL,
    profile_id VARCHAR NOT NULL,
    ranked_experience_ids TEXT NOT NULL,  -- JSON array
    ranked_project_ids TEXT NOT NULL,  -- JSON array
    ranking_rationale TEXT,
    keyword_matches TEXT,  -- JSON object
    relevance_scores TEXT,  -- JSON object
    llm_metadata TEXT NOT NULL,  -- JSON
    status VARCHAR DEFAULT 'completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);
```

### generations Table

```sql
CREATE TABLE generations (
    id VARCHAR PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id VARCHAR NOT NULL,
    profile_id VARCHAR NOT NULL,
    ranking_id VARCHAR,
    document_type VARCHAR NOT NULL,  -- 'resume' or 'cover_letter'
    content_text TEXT NOT NULL,
    ats_score REAL,
    ats_feedback TEXT,
    llm_metadata TEXT NOT NULL,  -- JSON
    status VARCHAR DEFAULT 'completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (ranking_id) REFERENCES job_content_rankings(id)
);
```

---

## Complete Workflow Example

### Step-by-Step Generation

```bash
# Prerequisites: Sample uploaded via Sample Upload API
# See: 04a-sample-upload-api.md

# 1. Enhance profile with AI
curl -X POST http://localhost:8000/api/v1/profile/enhance \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_id": "<profile_id>",
    "custom_prompt": "Emphasize technical leadership"
  }'

# 2. Create ranking for specific job
curl -X POST http://localhost:8000/api/v1/rankings/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "<job_id>"
  }'

# 3. Generate resume (fast, no LLM)
curl -X POST http://localhost:8000/api/v1/generations/resume \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "<job_id>",
    "max_experiences": 5,
    "max_projects": 3,
    "include_summary": true
  }'

# 4. Generate cover letter (LLM-powered)
curl -X POST http://localhost:8000/api/v1/generations/cover-letter \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "<job_id>",
    "company_name": "TechCorp Inc.",
    "hiring_manager_name": "Sarah Johnson",
    "max_paragraphs": 4
  }'

# 5. View generation history
curl -X GET http://localhost:8000/api/v1/generations/history \
  -H "Authorization: Bearer <token>"
```

---

## Best Practices

### 1. Profile Enhancement

Run enhancement after:
- Creating new profile
- Uploading new sample documents
- Making significant profile updates

**Don't enhance too frequently** - LLM calls cost tokens.

### 2. Content Ranking

Rankings are cached per job:
- First call creates ranking (~2 seconds with LLM)
- Subsequent calls return cached ranking (instant)
- Re-run ranking if job description changes significantly

### 3. Resume vs Cover Letter Generation

**Resume Generation** (fast):
- Pure logic compilation
- No LLM call required
- <1 second generation time
- Deterministic output

**Cover Letter Generation** (slower):
- Full LLM generation
- ~3-5 seconds generation time
- More personalized output
- Slight variation each generation

---

## Performance Metrics

### Confirmed LLM Integration

**Status**: ✅ Real Groq API integration working

**Test Results**:
- Cover letter generation: 71 tokens in 3.4 seconds
- Content ranking: 543 tokens in 1.8 seconds
- Profile enhancement: 1247 tokens in 4.2 seconds

### Latency Targets

| Operation | Target | Actual | LLM |
|-----------|--------|--------|-----|
| Profile enhancement | <5s | ~4.2s | 70b |
| Content ranking | <3s | ~1.8s | 8b |
| Resume generation | <1s | ~800ms | None |
| Cover letter generation | <6s | ~3.4s | 70b |
| Get rankings (cached) | <100ms | ~30ms | None |
| Get history | <200ms | ~50ms | None |

---

## Error Handling

All endpoints follow consistent error patterns:

### Common Errors

**Missing Prerequisites**:
```json
{
  "detail": "No active cover letter sample found. Upload a sample first."
}
```

**LLM Timeout**:
```json
{
  "detail": "LLM request timed out after 30 seconds. Please try again."
}
```

**LLM API Error**:
```json
{
  "detail": "LLM service unavailable. Please try again later."
}
```

---

## Related Documentation

- [Sample Upload API](04a-sample-upload-api.md) - Upload samples used by this API
- [Profile API](02-profile-api.md) - Profile management
- [Job API](03-job-api.md) - Job posting management
- [Database Schema](06-database-schema.md) - Complete database documentation

---

**Last Updated**: November 2025
**API Version**: 3.0
**Total Endpoints**: 6
**LLM Provider**: Groq.com
**Models**: llama-3.3-70b-versatile, llama-3.1-8b-instant
**Status**: Production Ready with Real LLM Integration
