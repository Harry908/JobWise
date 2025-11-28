# Job API

**Version**: 1.0
**Base Path**: `/api/v1/jobs`
**Status**: ✅ Fully Implemented

---

## Overview

The Job API manages job postings with intelligent text parsing capabilities. Users can create jobs from raw text, URLs, or structured data, then track application status and use them for AI-powered document generation.

**Key Features**:
- **Three Input Methods**: Raw text parsing, URL scraping, structured data
- **Intelligent Parsing**: AI-powered extraction of job details from text
- **Application Tracking**: Status management (not_applied, preparing, applied, etc.)
- **Flexible Filtering**: Filter by status, source, employment type
- **Pagination**: Efficient list handling with limit/offset
- **Unified Model**: Single table design for all job sources

---

## Job Sources

Jobs can come from multiple sources, tracked by the `source` field:

| Source | Description | Created By |
|--------|-------------|------------|
| `user_created` | Manually created by user | User via structured endpoint |
| `text_parsed` | Parsed from raw text | User via text parsing |
| `url_scraped` | Scraped from URL | User via URL scraping |
| `api` | Fetched from job boards | External API integration (future) |
| `imported` | Imported from file | Bulk import (future) |

---

## Application Status Flow

```
not_applied
    ↓
preparing
    ↓
applied
    ↓
interviewing
    ↓
offer_received
    ├→ accepted
    ├→ rejected
    └→ withdrawn
```

**Status Values**:
- `not_applied` - Job saved, no action yet
- `preparing` - Preparing application materials
- `applied` - Application submitted
- `interviewing` - In interview process
- `offer_received` - Job offer received
- `accepted` - Offer accepted
- `rejected` - Application/offer rejected
- `withdrawn` - Application withdrawn by user

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create job (text, URL, or structured) |
| GET | `/` | List user's jobs with filters |
| GET | `/{job_id}` | Get specific job details |
| PUT | `/{job_id}` | Update job information |
| DELETE | `/{job_id}` | Delete job permanently |

**Total Endpoints**: 5

---

## Endpoint Details

### 1. Create Job

Create a job posting using one of three methods: raw text parsing, URL scraping, or structured data.

**Endpoint**: `POST /api/v1/jobs`

**Authentication**: Required

**Method 1: Raw Text Parsing** (AI-powered)

Extract job details from pasted job description text.

**Request Body**:
```json
{
  "raw_text": "Senior Python Developer - TechCorp Inc.\n\nLocation: Seattle, WA (Remote Available)\n\nWe are seeking an experienced Senior Python Developer...\n\nRequirements:\n- 5+ years Python experience\n- FastAPI and Django expertise\n- AWS cloud experience\n\nBenefits:\n- Competitive salary $120k-$150k\n- Health insurance\n- 401k matching"
}
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "source": "text_parsed",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc.",
  "location": "Seattle, WA",
  "description": "We are seeking an experienced Senior Python Developer...",
  "raw_text": "Senior Python Developer - TechCorp Inc...",
  "parsed_keywords": ["Python", "FastAPI", "Django", "AWS"],
  "requirements": [
    "5+ years Python experience",
    "FastAPI and Django expertise",
    "AWS cloud experience"
  ],
  "benefits": [
    "Competitive salary $120k-$150k",
    "Health insurance",
    "401k matching"
  ],
  "salary_range": "$120k-$150k",
  "remote": true,
  "employment_type": "full_time",
  "status": "active",
  "application_status": "not_applied",
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Method 2: URL Scraping** (Future)

Fetch job details from a job posting URL.

**Request Body**:
```json
{
  "url": "https://jobs.techcorp.com/positions/senior-python-developer"
}
```

**Success Response**: Same as raw text parsing, with `source: "url_scraped"`

**Method 3: Structured Data**

Provide job details directly with all fields.

**Request Body**:
```json
{
  "source": "user_created",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc.",
  "location": "Seattle, WA",
  "description": "We are seeking an experienced Senior Python Developer to join our team...",
  "requirements": [
    "5+ years Python experience",
    "FastAPI and Django expertise",
    "AWS cloud experience"
  ],
  "benefits": [
    "Competitive salary",
    "Health insurance",
    "401k matching"
  ],
  "salary_range": "$120k-$150k",
  "remote": true,
  "employment_type": "full_time",
  "status": "active"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `raw_text` | string | Conditional | 10-15000 chars | Raw job text (Method 1) |
| `url` | string | Conditional | Valid URL | Job posting URL (Method 2) |
| `source` | string | No | Default: "user_created" | Job source identifier |
| `title` | string | Conditional | 1-200 chars | Job title (Method 3) |
| `company` | string | Conditional | 1-200 chars | Company name (Method 3) |
| `location` | string | No | Max 200 chars | Job location |
| `description` | string | No | Max 10000 chars | Job description |
| `requirements` | array | No | - | List of requirements |
| `benefits` | array | No | - | List of benefits |
| `salary_range` | string | No | Max 100 chars | Salary information |
| `remote` | boolean | No | Default: false | Remote work option |
| `employment_type` | string | No | See enum below | Employment type |
| `status` | string | No | active/archived/draft | Job status |

**Employment Type Enum**:
- `full_time` (default)
- `part_time`
- `contract`
- `internship`
- `temporary`

**Error Responses**:

**422 Unprocessable Entity** (Missing required fields):
```json
{
  "detail": "Either 'raw_text', 'url', or structured fields must be provided"
}
```

**422 Unprocessable Entity** (Invalid text length):
```json
{
  "detail": "raw_text must be between 10 and 15000 characters"
}
```

---

### 2. List User's Jobs

Retrieve all jobs for the authenticated user with filtering and pagination.

**Endpoint**: `GET /api/v1/jobs`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | - | Filter by job status (active/archived/draft) |
| `source` | string | No | - | Filter by source (user_created, text_parsed, etc.) |
| `employment_type` | string | No | - | Filter by employment type |
| `remote` | boolean | No | - | Filter remote jobs |
| `limit` | integer | No | 20 | Results per page (1-100) |
| `offset` | integer | No | 0 | Results offset |

**Example Requests**:
```
GET /api/v1/jobs
GET /api/v1/jobs?status=active&limit=10
GET /api/v1/jobs?source=text_parsed&remote=true
GET /api/v1/jobs?employment_type=full_time&offset=20
```

**Success Response** (200 OK):
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 1,
      "source": "text_parsed",
      "title": "Senior Python Developer",
      "company": "TechCorp Inc.",
      "location": "Seattle, WA",
      "description": "...",
      "parsed_keywords": ["Python", "FastAPI", "AWS"],
      "requirements": [...],
      "benefits": [...],
      "salary_range": "$120k-$150k",
      "remote": true,
      "employment_type": "full_time",
      "status": "active",
      "application_status": "applied",
      "created_at": "2025-11-15T10:30:00Z",
      "updated_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 45,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 45,
    "hasMore": true
  }
}
```

---

### 3. Get Specific Job

Retrieve detailed information for a specific job.

**Endpoint**: `GET /api/v1/jobs/{job_id}`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID): Job unique identifier

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "source": "text_parsed",
  "title": "Senior Python Developer",
  "company": "TechCorp Inc.",
  "location": "Seattle, WA",
  "description": "Full job description text...",
  "raw_text": "Original pasted text...",
  "parsed_keywords": ["Python", "FastAPI", "Django", "AWS", "Docker"],
  "requirements": [
    "5+ years Python experience",
    "FastAPI and Django expertise",
    "AWS cloud experience",
    "Docker and Kubernetes knowledge",
    "Strong communication skills"
  ],
  "benefits": [
    "Competitive salary $120k-$150k",
    "Health insurance",
    "401k matching",
    "Unlimited PTO",
    "Remote work options"
  ],
  "salary_range": "$120k-$150k",
  "remote": true,
  "employment_type": "full_time",
  "status": "active",
  "application_status": "applied",
  "applied_date": "2025-11-10T14:00:00Z",
  "notes": "Great company culture, aligned with my skills",
  "created_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-10T14:00:00Z"
}
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Job not found"
}
```

**403 Forbidden**:
```json
{
  "detail": "You do not have permission to access this job"
}
```

---

### 4. Update Job

Update job information (partial updates supported).

**Endpoint**: `PUT /api/v1/jobs/{job_id}`

**Authentication**: Required

**Request Body** (all fields optional):
```json
{
  "title": "Lead Python Developer",
  "location": "Seattle, WA (Fully Remote)",
  "status": "active",
  "application_status": "interviewing",
  "notes": "Phone interview scheduled for Nov 20th",
  "applied_date": "2025-11-10T14:00:00Z"
}
```

**Updatable Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Job title |
| `company` | string | Company name |
| `location` | string | Job location |
| `description` | string | Job description |
| `status` | string | Job status (active/archived/draft) |
| `application_status` | string | Application progress |
| `applied_date` | string | Date applied (ISO 8601) |
| `notes` | string | Personal notes about the job |
| `remote` | boolean | Remote work option |
| `employment_type` | string | Employment type |

**Success Response** (200 OK): Full updated job object

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Job not found"
}
```

**422 Unprocessable Entity** (Invalid status):
```json
{
  "detail": "Invalid application_status. Must be one of: not_applied, preparing, applied, interviewing, offer_received, accepted, rejected, withdrawn"
}
```

---

### 5. Delete Job

Permanently delete a job posting.

**Endpoint**: `DELETE /api/v1/jobs/{job_id}`

**Authentication**: Required

**Path Parameters**:
- `job_id` (UUID): Job unique identifier

**Success Response** (204 No Content): No body

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Job not found"
}
```

**409 Conflict** (Job has generated documents):
```json
{
  "detail": "Cannot delete job with associated generated documents. Delete documents first."
}
```

---

## AI Text Parsing

When creating a job from raw text, the system uses AI to intelligently extract:

### Parsed Fields
- **Title**: Job position name
- **Company**: Company/organization name
- **Location**: City, state, country, remote status
- **Description**: Full job description
- **Requirements**: Bulleted list of qualifications
- **Benefits**: Bulleted list of perks and benefits
- **Salary Range**: Extracted salary information
- **Keywords**: Technical skills and tools mentioned

### Parsing Examples

**Input Text**:
```
Software Engineer III - Acme Corp
Remote (US Only)

About the Role:
We're looking for a talented engineer to join our platform team.

Requirements:
- 5+ years of professional software development
- Strong experience with React and Node.js
- Experience with AWS or similar cloud platforms

What We Offer:
- Salary: $130,000 - $160,000
- Comprehensive health benefits
- 401(k) with company match
```

**Parsed Output**:
```json
{
  "title": "Software Engineer III",
  "company": "Acme Corp",
  "location": "Remote (US Only)",
  "remote": true,
  "description": "We're looking for a talented engineer to join our platform team.",
  "requirements": [
    "5+ years of professional software development",
    "Strong experience with React and Node.js",
    "Experience with AWS or similar cloud platforms"
  ],
  "benefits": [
    "Comprehensive health benefits",
    "401(k) with company match"
  ],
  "salary_range": "$130,000 - $160,000",
  "parsed_keywords": ["React", "Node.js", "AWS"]
}
```

---

## Database Schema

### jobs Table

```sql
CREATE TABLE jobs (
    id VARCHAR PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    source VARCHAR NOT NULL DEFAULT 'user_created',
    title VARCHAR NOT NULL,
    company VARCHAR NOT NULL,
    location VARCHAR,
    description TEXT,
    raw_text TEXT,
    parsed_keywords TEXT,  -- JSON array
    requirements TEXT,  -- JSON array
    benefits TEXT,  -- JSON array
    salary_range VARCHAR,
    remote BOOLEAN DEFAULT FALSE,
    employment_type VARCHAR DEFAULT 'full_time',
    status VARCHAR DEFAULT 'active',
    application_status VARCHAR DEFAULT 'not_applied',
    applied_date DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_application_status ON jobs(application_status);
CREATE INDEX idx_jobs_source ON jobs(source);
```

---

## Common Use Cases

### Use Case 1: Save Job from Job Board

**Scenario**: User finds a job on LinkedIn and wants to save it for later.

**Solution**: Copy job description text and paste it.

```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "<paste entire job description>"
  }'
```

AI automatically extracts all relevant fields.

---

### Use Case 2: Track Application Progress

**Scenario**: User applied to a job and wants to track interview stages.

**Solution**: Update application status as progress is made.

```bash
# Applied
curl -X PUT http://localhost:8000/api/v1/jobs/{id} \
  -H "Authorization: Bearer <token>" \
  -d '{"application_status": "applied", "applied_date": "2025-11-15"}'

# Interview scheduled
curl -X PUT http://localhost:8000/api/v1/jobs/{id} \
  -H "Authorization: Bearer <token>" \
  -d '{"application_status": "interviewing", "notes": "Phone screen on Nov 20"}'

# Offer received
curl -X PUT http://localhost:8000/api/v1/jobs/{id} \
  -H "Authorization: Bearer <token>" \
  -d '{"application_status": "offer_received"}'
```

---

### Use Case 3: Filter Active Applications

**Scenario**: User wants to see all jobs they've applied to.

**Solution**: Filter by application status.

```bash
curl -X GET "http://localhost:8000/api/v1/jobs?status=active" \
  -H "Authorization: Bearer <token>"
```

---

### Use Case 4: Archive Old Jobs

**Scenario**: User wants to clean up old job postings.

**Solution**: Update status to "archived".

```bash
curl -X PUT http://localhost:8000/api/v1/jobs/{id} \
  -H "Authorization: Bearer <token>" \
  -d '{"status": "archived"}'
```

Archived jobs don't appear in default list views.

---

## Best Practices

### 1. Text Parsing Quality

For best AI parsing results:
- ✅ Include complete job description
- ✅ Include requirements section
- ✅ Include benefits/compensation
- ✅ Keep original formatting (bullets, headings)
- ❌ Don't heavily edit or summarize

### 2. Application Tracking

Maintain accurate application status:
- Update `application_status` at each stage
- Add `notes` for interview details
- Set `applied_date` when submitting application
- Archive jobs after final decision

### 3. Job Organization

Use status field strategically:
- `active` - Jobs you're pursuing
- `draft` - Jobs you're considering
- `archived` - Jobs no longer relevant

---

## Future Enhancements

- [ ] URL scraping implementation (currently returns mock data)
- [ ] Job board API integrations (Indeed, LinkedIn, etc.)
- [ ] Bulk import from CSV/JSON
- [ ] Job alerts and notifications
- [ ] Keyword matching with user profile
- [ ] Company research integration
- [ ] Application deadline tracking
- [ ] Interview preparation materials

---

**Last Updated**: November 2025
**API Version**: 1.0
**Total Endpoints**: 5
**Status**: Production Ready (URL scraping planned)
