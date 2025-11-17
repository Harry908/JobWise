# API Endpoints - JobWise AI Generation System v3.0

**Version**: 3.0  
**Last Updated**: November 16, 2025  
**Status**: 🎯 **Ready for Implementation**

---

## Endpoint Overview

This document defines all API endpoints for the redesigned generation system.

### New Endpoints
1. `POST /api/v1/samples/upload` - Upload sample resume or cover letter
2. `POST /api/v1/profile/enhance` - Enhance master profile using writing style
3. `POST /api/v1/rankings/create` - Create job-specific content ranking
4. `POST /api/v1/generations/resume` - Generate tailored resume
5. `POST /api/v1/generations/cover-letter` - Generate tailored cover letter

### Modified Endpoints
- Existing generation endpoints remain for backward compatibility but will be deprecated

---

## Authentication

All endpoints require JWT authentication via `Authorization` header:

```http
Authorization: Bearer <jwt_token>
```

**Error Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

---

## 1. Upload Sample Document

Upload a sample resume or cover letter as plain text for writing style analysis.

### Endpoint
```http
POST /api/v1/samples/upload
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

### Request Body (multipart/form-data)
```
document_type: "resume" | "cover_letter"  (required)
file: <text file>  (required, .txt only)
```

### Request Example
```bash
curl -X POST http://localhost:8000/api/v1/samples/upload \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "document_type=cover_letter" \
  -F "file=@my_cover_letter.txt"
```

### Response (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "word_count": 421,
  "character_count": 2847,
  "is_active": true,
  "created_at": "2025-11-16T10:30:00Z"
}
```

### Error Responses

**400 Bad Request** (Invalid file type):
```json
{
  "detail": "Only .txt files are supported in this prototype"
}
```

**400 Bad Request** (Invalid document type):
```json
{
  "detail": "document_type must be 'resume' or 'cover_letter'"
}
```

**413 Payload Too Large** (File too large):
```json
{
  "detail": "File size exceeds 1MB limit"
}
```

**422 Unprocessable Entity** (Empty file):
```json
{
  "detail": "File is empty or contains no readable text"
}
```

### Business Logic
1. Validate file extension is `.txt`
2. Read file content as UTF-8 text
3. Calculate `word_count` and `character_count`
4. Set previous samples of same type to `is_active=FALSE`
5. Store new sample with `is_active=TRUE`
6. Return sample metadata (do NOT return full text in response)

### Rate Limiting
- Max 10 uploads per user per hour
- Max 2 active samples per user (1 resume + 1 cover letter)

---

## 2. Enhance Master Profile

Enhance user's master profile using writing style extracted from sample cover letter.

### Endpoint
```http
POST /api/v1/profile/enhance
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
  "profile_id": "profile-uuid-456",
  "custom_prompt": "Emphasize technical leadership and cloud expertise"
}
```

**Parameters**:
- `profile_id` (required): UUID of master profile to enhance
- `custom_prompt` (optional): User's additional instructions appended to base prompt

### Response (200 OK)
```json
{
  "profile_id": "profile-uuid-456",
  "status": "completed",
  "enhanced_sections": {
    "professional_summary": true,
    "experiences": 5,
    "projects": 3
  },
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "total_tokens": 12847,
    "generation_time": 12.3
  },
  "writing_style_used": {
    "tone": "professional yet conversational",
    "vocabulary_level": "technical-advanced",
    "action_verbs": ["architected", "spearheaded", "optimized"]
  },
  "created_at": "2025-11-16T10:35:00Z"
}
```

### Error Responses

**404 Not Found** (Profile not found):
```json
{
  "detail": "Master profile not found"
}
```

**404 Not Found** (No sample cover letter):
```json
{
  "detail": "No active cover letter sample found. Please upload a sample first."
}
```

**403 Forbidden** (Profile not owned by user):
```json
{
  "detail": "You do not have permission to enhance this profile"
}
```

**500 Internal Server Error** (LLM failure):
```json
{
  "detail": "Profile enhancement failed: LLM API error",
  "error_code": "LLM_API_ERROR"
}
```

### Business Logic
1. Verify user owns `profile_id`
2. Fetch active cover letter sample for writing style extraction
3. Extract writing style (tone, vocabulary, action verbs) via LLM
4. Enhance `professional_summary` → store in `enhanced_professional_summary`
5. Enhance each `experience.description` → store in `enhanced_description`
6. Enhance each `project.description` → store in `enhanced_description`
7. Use prompt template `profile_enhancement` from database
8. Append `custom_prompt` if provided
9. Store enhancement metadata in each record

### Performance Target
- Complete within 15 seconds for typical profile (1 summary + 5 experiences + 3 projects)

---

## 3. Create Job-Specific Content Ranking

Rank user's experiences and projects by relevance to a specific job posting.

### Endpoint
```http
POST /api/v1/rankings/create
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
  "job_id": "job-uuid-789",
  "custom_prompt": "Prioritize leadership experience and cloud certifications"
}
```

**Parameters**:
- `job_id` (required): UUID of job posting
- `custom_prompt` (optional): User's additional ranking instructions

### Response (200 OK)
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "job_id": "job-uuid-789",
  "ranked_experience_ids": [
    "exp-uuid-3",
    "exp-uuid-1",
    "exp-uuid-5",
    "exp-uuid-2",
    "exp-uuid-4"
  ],
  "ranked_project_ids": [
    "proj-uuid-5",
    "proj-uuid-1",
    "proj-uuid-3",
    "proj-uuid-2"
  ],
  "ranking_rationale": "Prioritized VR research experience (#3) due to strong alignment with AI/ML focus. Cloud migration project (#5) ranked first for technical stack match. Leadership experience emphasized per custom prompt.",
  "keyword_matches": {
    "Python": 3,
    "AI": 2,
    "Machine Learning": 2,
    "Cloud": 2,
    "Leadership": 1
  },
  "relevance_scores": {
    "exp-uuid-3": 0.95,
    "exp-uuid-1": 0.82,
    "exp-uuid-5": 0.78,
    "proj-uuid-5": 0.91,
    "proj-uuid-1": 0.84
  },
  "llm_metadata": {
    "model": "llama-3.1-8b-instant",
    "tokens_used": 1850,
    "generation_time": 2.3
  },
  "status": "completed",
  "created_at": "2025-11-16T10:40:00Z"
}
```

### Error Responses

**404 Not Found** (Job not found):
```json
{
  "detail": "Job posting not found"
}
```

**404 Not Found** (No master profile):
```json
{
  "detail": "No master profile found. Please create a profile first."
}
```

**422 Unprocessable Entity** (Empty profile):
```json
{
  "detail": "Master profile has no experiences or projects to rank"
}
```

**500 Internal Server Error** (LLM failure):
```json
{
  "detail": "Ranking generation failed: LLM API timeout",
  "error_code": "LLM_TIMEOUT"
}
```

### Business Logic
1. Verify user has access to `job_id`
2. Fetch job posting content (title, description, requirements)
3. Fetch user's master profile with all experiences and projects
4. Use LLM to rank experiences and projects by relevance
5. Use prompt template `content_ranking` from database
6. Append `custom_prompt` if provided
7. Extract keyword matches and relevance scores from LLM response
8. Store ranking in `job_content_rankings` table
9. If ranking already exists for this user+job, UPDATE instead of INSERT

### Performance Target
- Complete within 3 seconds for typical profile (5 experiences + 5 projects)

### Idempotency
- Calling this endpoint multiple times for the same `job_id` will regenerate and update the ranking
- Useful for re-ranking after profile updates or prompt refinement

---

## 4. Generate Tailored Resume

Generate a tailored resume for a specific job using ranked content and layout preferences.

### Endpoint
```http
POST /api/v1/generations/resume
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
  "job_id": "job-uuid-789",
  "max_experiences": 4,
  "max_projects": 3,
  "include_summary": true,
  "custom_prompt": "Use technical terminology for senior role"
}
```

**Parameters**:
- `job_id` (required): UUID of job posting
- `max_experiences` (optional, default: 5): Number of experiences to include
- `max_projects` (optional, default: 3): Number of projects to include
- `include_summary` (optional, default: true): Include professional summary
- `custom_prompt` (optional): User's additional generation instructions

### Response (200 OK)
```json
{
  "generation_id": "gen-uuid-123",
  "job_id": "job-uuid-789",
  "document_type": "resume",
  "status": "completed",
  "resume_text": "HUY KY\nSoftware Engineer\n\nPROFESSIONAL SUMMARY\nFirst-generation computer science student at Washington State University with a passion for building scalable AI-powered systems...\n\nEXPERIENCE\n\nUndergraduate Research Assistant | WSU VR Lab | Jan 2024 - Present\nArchitected an AI-powered Sommelier NPC using machine learning algorithms...\n\n...",
  "content_used": {
    "professional_summary": true,
    "experience_ids": ["exp-uuid-3", "exp-uuid-1", "exp-uuid-5", "exp-uuid-2"],
    "project_ids": ["proj-uuid-5", "proj-uuid-1", "proj-uuid-3"],
    "education_ids": ["edu-uuid-1"],
    "skills": true
  },
  "ats_score": 0.87,
  "ats_feedback": "Strong keyword alignment. Consider adding specific certifications mentioned in job posting.",
  "llm_metadata": {
    "model": "N/A - Pure logic compilation",
    "generation_time": 0.2
  },
  "created_at": "2025-11-16T10:45:00Z"
}
```

### Error Responses

**404 Not Found** (Job not found):
```json
{
  "detail": "Job posting not found"
}
```

**404 Not Found** (No ranking):
```json
{
  "detail": "No content ranking found for this job. Please create a ranking first."
}
```

**404 Not Found** (No enhanced profile):
```json
{
  "detail": "Master profile not enhanced. Please enhance your profile first."
}
```

**500 Internal Server Error** (Compilation failure):
```json
{
  "detail": "Resume generation failed: Template compilation error",
  "error_code": "TEMPLATE_ERROR"
}
```

### Business Logic
1. Verify user has access to `job_id`
2. Fetch job-specific content ranking from `job_content_rankings` table
3. Fetch enhanced profile sections (summary, experiences, projects)
4. Select top N experiences and projects based on ranking and `max_*` parameters
5. **Pure logic compilation** (NO LLM) using Jinja2 template
6. Use `ranked_experience_ids[0:max_experiences]` for content selection
7. Use enhanced descriptions from `enhanced_description` columns
8. Calculate ATS score by keyword matching
9. Store result in `generations` table
10. Return full resume text

### Performance Target
- Complete within 1 second (no LLM calls, pure template rendering)

### Template Format
- Plain text format optimized for ATS parsing
- Consistent spacing and formatting
- Keywords from job description naturally integrated

---

## 5. Generate Tailored Cover Letter

Generate a tailored cover letter for a specific job using writing style and profile content.

### Endpoint
```http
POST /api/v1/generations/cover-letter
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body
```json
{
  "job_id": "job-uuid-789",
  "company_name": "Microsoft",
  "hiring_manager_name": "Sarah Johnson",
  "max_paragraphs": 4,
  "custom_prompt": "Emphasize passion for AI research and open-source contributions"
}
```

**Parameters**:
- `job_id` (required): UUID of job posting
- `company_name` (optional): Company name for personalization
- `hiring_manager_name` (optional): Hiring manager name for greeting
- `max_paragraphs` (optional, default: 4): Length constraint
- `custom_prompt` (optional): User's additional generation instructions

### Response (200 OK)
```json
{
  "generation_id": "gen-uuid-456",
  "job_id": "job-uuid-789",
  "document_type": "cover_letter",
  "status": "completed",
  "cover_letter_text": "Dear Sarah Johnson,\n\nI am writing to express my strong interest in the Software Engineer position at Microsoft. As a first-generation computer science student at Washington State University with a passion for building AI-powered systems, I am excited about the opportunity to contribute to your team's innovative work in machine learning.\n\nThrough my research experience in the WSU VR Lab, I have architected an AI-powered Sommelier NPC that demonstrates my ability to apply cutting-edge machine learning algorithms to real-world problems...\n\nI am particularly drawn to this role because it aligns perfectly with my passion for AI research and commitment to open-source contributions. My experience with Python, TensorFlow, and cloud technologies positions me to make immediate contributions to your team.\n\nThank you for considering my application. I look forward to the opportunity to discuss how my background and enthusiasm can contribute to Microsoft's mission.\n\nSincerely,\nHuy Ky",
  "content_used": {
    "sample_cover_letter_style": true,
    "experience_ids": ["exp-uuid-3", "exp-uuid-1"],
    "project_ids": ["proj-uuid-5"],
    "skills_highlighted": ["Python", "AI", "Machine Learning", "Cloud"]
  },
  "ats_score": 0.91,
  "ats_feedback": "Excellent keyword density and natural language flow. Strong personalization.",
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "tokens_used": 3847,
    "generation_time": 4.8
  },
  "created_at": "2025-11-16T10:50:00Z"
}
```

### Error Responses

**404 Not Found** (Job not found):
```json
{
  "detail": "Job posting not found"
}
```

**404 Not Found** (No ranking):
```json
{
  "detail": "No content ranking found for this job. Please create a ranking first."
}
```

**404 Not Found** (No sample):
```json
{
  "detail": "No active cover letter sample found. Please upload a sample first."
}
```

**500 Internal Server Error** (LLM failure):
```json
{
  "detail": "Cover letter generation failed: LLM content policy violation",
  "error_code": "LLM_CONTENT_POLICY"
}
```

### Business Logic
1. Verify user has access to `job_id`
2. Fetch job posting content
3. Fetch sample cover letter for writing style reference
4. Fetch job-specific content ranking
5. Fetch top 2-3 experiences and top 1-2 projects from ranking
6. Use LLM to generate cover letter matching sample style
7. Use prompt template `cover_letter_generation` from database
8. Append `custom_prompt` if provided
9. Inject `company_name` and `hiring_manager_name` if provided
10. Enforce `max_paragraphs` constraint via prompt
11. Calculate ATS score by keyword matching
12. Store result in `generations` table
13. Return full cover letter text

### Performance Target
- Complete within 5 seconds

### Anti-Fabrication Rules
- LLM prompt includes: "ONLY use information from the provided profile"
- "DO NOT invent job titles, dates, or accomplishments"
- "DO NOT add technical skills not listed in profile"

---

## 6. Get Sample Documents

Retrieve user's uploaded sample documents.

### Endpoint
```http
GET /api/v1/samples
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### Query Parameters
```
document_type: "resume" | "cover_letter" | "all"  (optional, default: "all")
active_only: true | false  (optional, default: true)
```

### Response (200 OK)
```json
{
  "samples": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "document_type": "cover_letter",
      "original_filename": "my_cover_letter.txt",
      "word_count": 421,
      "character_count": 2847,
      "is_active": true,
      "last_used_for_generation": "2025-11-16T14:20:00Z",
      "generation_count": 3,
      "created_at": "2025-11-16T10:30:00Z"
    }
  ],
  "total": 1
}
```

**Note**: Full `original_text` is NOT returned in list view for performance. Use `GET /api/v1/samples/{id}` to retrieve full text.

---

## 7. Get Sample Document by ID

Retrieve a specific sample document with full text.

### Endpoint
```http
GET /api/v1/samples/{sample_id}
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### Response (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "original_text": "Dear Hiring Manager,\n\nI am a software engineering student at Washington State University...",
  "word_count": 421,
  "character_count": 2847,
  "is_active": true,
  "last_used_for_generation": "2025-11-16T14:20:00Z",
  "generation_count": 3,
  "created_at": "2025-11-16T10:30:00Z"
}
```

### Error Responses

**404 Not Found**:
```json
{
  "detail": "Sample document not found"
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to access this sample"
}
```

---

## 8. Delete Sample Document

Delete a sample document.

### Endpoint
```http
DELETE /api/v1/samples/{sample_id}
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### Response (204 No Content)
*Empty response body*

### Error Responses

**404 Not Found**:
```json
{
  "detail": "Sample document not found"
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to delete this sample"
}
```

---

## 9. Get Job Rankings

Retrieve content rankings for a specific job.

### Endpoint
```http
GET /api/v1/rankings/job/{job_id}
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### Response (200 OK)
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "job_id": "job-uuid-789",
  "ranked_experience_ids": ["exp-uuid-3", "exp-uuid-1", "exp-uuid-5"],
  "ranked_project_ids": ["proj-uuid-5", "proj-uuid-1", "proj-uuid-3"],
  "ranking_rationale": "Prioritized VR research experience...",
  "keyword_matches": {"Python": 3, "AI": 2},
  "relevance_scores": {"exp-uuid-3": 0.95, "proj-uuid-5": 0.91},
  "created_at": "2025-11-16T10:40:00Z",
  "updated_at": "2025-11-16T10:40:00Z"
}
```

### Error Responses

**404 Not Found**:
```json
{
  "detail": "No ranking found for this job"
}
```

---

## 10. Get Generation History

Retrieve user's document generation history.

### Endpoint
```http
GET /api/v1/generations/history
```

### Request Headers
```http
Authorization: Bearer <jwt_token>
```

### Query Parameters
```
document_type: "resume" | "cover_letter" | "all"  (optional, default: "all")
limit: integer  (optional, default: 20, max: 100)
offset: integer  (optional, default: 0)
```

### Response (200 OK)
```json
{
  "generations": [
    {
      "generation_id": "gen-uuid-123",
      "job_id": "job-uuid-789",
      "job_title": "Software Engineer",
      "company_name": "Microsoft",
      "document_type": "resume",
      "status": "completed",
      "ats_score": 0.87,
      "created_at": "2025-11-16T10:45:00Z"
    },
    {
      "generation_id": "gen-uuid-456",
      "job_id": "job-uuid-789",
      "job_title": "Software Engineer",
      "company_name": "Microsoft",
      "document_type": "cover_letter",
      "status": "completed",
      "ats_score": 0.91,
      "created_at": "2025-11-16T10:50:00Z"
    }
  ],
  "total": 2,
  "limit": 20,
  "offset": 0
}
```

**Note**: Full generated text is NOT returned in history view. Use `GET /api/v1/generations/{generation_id}` to retrieve full document.

---

## Error Handling

### Global Error Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-11-16T10:00:00Z",
  "request_id": "req-uuid-123"
}
```

### HTTP Status Codes
- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid request format or parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Authenticated but no permission
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource state conflict
- `413 Payload Too Large` - File size exceeds limit
- `422 Unprocessable Entity` - Valid format but business logic error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - LLM service unavailable

### Rate Limiting Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1700145600
```

---

## Implementation Checklist

### Phase 1: Sample Upload
- [ ] `POST /api/v1/samples/upload` endpoint
- [ ] File validation (.txt only, max 1MB)
- [ ] Text extraction and word count
- [ ] Database storage with `is_active` toggle
- [ ] `GET /api/v1/samples` endpoint
- [ ] `GET /api/v1/samples/{id}` endpoint
- [ ] `DELETE /api/v1/samples/{id}` endpoint

### Phase 2: Profile Enhancement
- [ ] `POST /api/v1/profile/enhance` endpoint
- [ ] Writing style extraction service
- [ ] Profile enhancement service
- [ ] Enhanced description storage
- [ ] Error handling for LLM failures

### Phase 3: Content Ranking
- [ ] `POST /api/v1/rankings/create` endpoint
- [ ] Job content ranking service
- [ ] Ranking storage with UPSERT logic
- [ ] `GET /api/v1/rankings/job/{job_id}` endpoint
- [ ] Keyword extraction and scoring

### Phase 4: Document Generation
- [ ] `POST /api/v1/generations/resume` endpoint
- [ ] Jinja2 resume template
- [ ] Pure logic compilation (no LLM)
- [ ] ATS scoring algorithm
- [ ] `POST /api/v1/generations/cover-letter` endpoint
- [ ] Cover letter generation service
- [ ] `GET /api/v1/generations/history` endpoint
- [ ] Anti-fabrication prompt engineering

### Phase 5: Testing
- [ ] Unit tests for all endpoints
- [ ] Integration tests for full workflow
- [ ] Load testing for LLM endpoints
- [ ] Error handling tests
- [ ] Rate limiting tests

---

## Next Steps

1. Review API specifications
2. Approve endpoint contracts
3. Implement services layer
4. Create Pydantic request/response models
5. Add comprehensive error handling
6. Proceed to [04-PROMPT-MANAGEMENT.md](04-PROMPT-MANAGEMENT.md)
