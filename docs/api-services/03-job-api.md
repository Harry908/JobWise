# Job API Service

**Version**: 2.1
**Base Path**: `/api/v1/jobs`
**Status**: ✅ **Implemented** (Core CRUD complete, Sprint 1-3)
**Test Coverage**: Job API endpoints operational with mobile integration
**Last Updated**: November 7, 2025

## Service Overview

Unified CRUD API for managing job descriptions from multiple sources. Accepts raw text (auto-parsed) or structured data. Supports user-created jobs, imported jobs, and future integration with external job APIs.

## Specification

**Purpose**: Job description management with multi-source support
**Authentication**: Required (JWT)
**Authorization**: Users can only manage jobs they created (user_created source)
**Text Parsing**: Deterministic regex + optional LLM enhancement (rate-limited)
**Delete Behavior**: Hard delete (immediate removal)
**Performance**: <200ms for CRUD operations, <3s for text parsing

## Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 201 | Created | Job successfully created |
| 200 | OK | Request successful |
| 204 | No Content | Delete successful (no response body) |
| 400 | Bad Request | Validation error or malformed request |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User doesn't own the resource |
| 404 | Not Found | Job doesn't exist |
| 422 | Unprocessable Entity | Parsing failed or validation error |
| 429 | Too Many Requests | LLM parsing rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Validation Rules

**Required Fields (Structured Input):**
- `source`: Must be one of: `user_created`, `indeed`, `linkedin`, `glassdoor`, `mock`, `imported`
- `title`: Required, 1-200 chars
- `company`: Required, 1-200 chars

**Optional Fields:**
- `location`: Max 200 chars, supports "Remote" keyword
- `description`: Max 10,000 chars
- `requirements`: Array of strings, max 50 items, each max 500 chars
- `benefits`: Array of strings, max 30 items, each max 500 chars
- `salary_range`: Format "min-max" (e.g., "100000-150000") or free text
- `remote`: Boolean, default false
- `status`: Must be one of: `active`, `archived`, `draft`
- `application_status`: Must be one of: `not_applied`, `preparing`, `applied`, `interviewing`, `offer_received`, `rejected`, `accepted`, `withdrawn` (default: `not_applied`)

**Raw Text Input:**
- `raw_text`: Required if structured fields not provided, min 50 chars, max 15,000 chars
- Parsing extracts: title, company, location, requirements, benefits, keywords

**Parsed Keywords:**
- Auto-extracted from description and requirements
- Lowercase, deduplicated
- Common skills, technologies, tools
- Max 50 keywords per job

## Dependencies

### Internal
- Authentication API: User identity via JWT
- Database: JobModel (unified table)
- Repositories: JobRepository
- LLM Service: Text parsing (optional, via ILLMService port)

### External
- Future: Indeed API, LinkedIn API, Glassdoor API

## Database Schema

### JobModel (jobs table)

**Purpose**: Stores job descriptions from multiple sources with parsed keywords for AI matching

**Fields**:
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER,      -- Foreign key to users.id (nullable for external jobs)
    source TEXT NOT NULL, -- 'user_created', 'indeed', 'linkedin', 'mock', etc.
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,        -- City, State or "Remote"
    description TEXT,     -- Full job description
    raw_text TEXT,        -- Original pasted text (for user_created)
    parsed_keywords TEXT, -- JSON array: ["python", "fastapi", "aws"]
    requirements TEXT,    -- JSON array: ["5+ years Python", "AWS experience"]
    benefits TEXT,        -- JSON array: ["Health insurance", "Remote work"]
    salary_range TEXT,    -- "100000-150000" or free text
    remote BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'active',  -- 'active', 'archived', 'draft'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_source ON jobs(source);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_user_status ON jobs(user_id, status);
```

**Field Descriptions**:
- `id`: UUID primary key
- `user_id`: Owner (nullable for external/mock jobs, set for user_created)
- `source`: Job origin (user_created, indeed, linkedin, mock, imported)
- `title`: Job position title
- `company`: Company name
- `location`: City/State or "Remote"
- `description`: Full job description text
- `raw_text`: Original pasted text before parsing
- `parsed_keywords`: JSON array of technical keywords (["python", "aws"])
- `requirements`: JSON array of qualification strings
- `benefits`: JSON array of benefit strings
- `salary_range`: Salary information (format: "min-max" or free text)
- `remote`: Boolean flag for remote positions
- `status`: Job status (active, archived, draft)
- `application_status`: User's application progress (not_applied, preparing, applied, interviewing, offer_received, rejected, accepted, withdrawn)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp (auto-updates)

**Constraints**:
- `source` required (identifies origin)
- `title` and `company` required
- `user_id` nullable (supports external jobs)
- `status` defaults to 'active'
- Foreign key cascade delete (when user deleted, user_created jobs deleted)

## Data Flow

```
Create Job (Raw Text):
1. Client → POST /jobs {raw_text, source: "user_created"}
2. API validates JWT → get user_id
3. API invokes text parser (deterministic regex rules)
4. API extracts: title, company, location, requirements, benefits, keywords
5. Optional: LLM enhancement for ambiguous fields (rate-limited)
6. API creates JobModel with user_id and parsed data
7. API ← Job response (201) with parsed fields

Create Job (Structured):
1. Client → POST /jobs {title, company, description, source, ...}
2. API validates JWT → get user_id
3. API validates structured data (Pydantic)
4. API extracts keywords from description
5. API creates JobModel with user_id
6. API ← Job response (201)

Browse Mock Jobs:
1. Client → GET /jobs/browse?query=Python&location=Remote&limit=20
2. API validates JWT → get user_id
3. API loads mock jobs from JSON file
4. API filters by query (title, description, keywords)
5. API filters by location (city, state, "Remote")
6. API filters by remote flag
7. API paginates results
8. API ← Mock jobs array (200) with pagination

List User Jobs:
1. Client → GET /jobs?status=active&source=user_created&limit=20
2. API validates JWT → get user_id
3. API fetches jobs where user_id = current_user.id
4. API applies filters (status, source)
5. API orders by created_at DESC
6. API paginates results
7. API ← Job list (200) with pagination

Get Job Detail:
1. Client → GET /jobs/{id}
2. API validates JWT → get user_id
3. API fetches job by id
4. API verifies ownership (if user_created source)
5. API ← Full job object (200)

Update Job:
1. Client → PUT /jobs/{id} {updated_fields}
2. API validates JWT → get user_id
3. API fetches job by id
4. API verifies job.user_id == current_user.id
5. API validates update data (Pydantic)
6. API re-extracts keywords if description changed
7. API updates job record with updated_at timestamp
8. API ← Updated job (200)

Delete Job:
1. Client → DELETE /jobs/{id}
2. API validates JWT → get user_id
3. API fetches job by id
4. API verifies ownership (job.user_id == current_user.id)
5. API hard deletes job record (immediate removal)
6. API ← 204 No Content

Save Mock Job:
1. Client browses mock jobs via GET /jobs/browse
2. User selects a mock job to save
3. Client → POST /jobs {mock_job_data, source: "user_created"}
4. API validates JWT → get user_id
5. API creates job with user_id
6. API ← Saved job (201)
```

## API Contract

### POST /jobs

**Description**: Create job (raw text or structured)

**Headers**: `Authorization: Bearer <token>`

**Request (Raw Text)**:
```json
{
  "source": "user_created",
  "raw_text": "Senior Python Developer at Tech Corp\n\nWe are looking for...\n\nRequirements:\n- 5+ years Python\n- FastAPI experience\n\nBenefits:\n- Health insurance\n- Remote work"
}
```

**Request (Structured)**:
```json
{
  "source": "user_created",
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "Seattle, WA",
  "description": "We are looking for an experienced Python developer...",
  "requirements": [
    "5+ years Python experience",
    "FastAPI or Django knowledge",
    "AWS cloud experience"
  ],
  "benefits": [
    "Health insurance",
    "401k matching",
    "Remote work"
  ],
  "salary_range": "120000-180000",
  "remote": true,
  "status": "active"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "user_id": "user-uuid",
  "source": "user_created",
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "Seattle, WA",
  "description": "We are looking for an experienced Python developer...",
  "raw_text": "Senior Python Developer at Tech Corp...",
  "parsed_keywords": ["python", "fastapi", "aws", "microservices"],
  "requirements": [...],
  "benefits": [...],
  "salary_range": "120000-180000",
  "remote": true,
  "status": "active",
  "created_at": "2025-10-21T10:00:00Z",
  "updated_at": "2025-10-21T10:00:00Z"
}
```

**Errors**:
- 400: Validation error (missing source, empty raw_text/title)
- 401: Unauthorized

### GET /jobs

**Description**: List user's jobs with filtering

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `status`: string (active, archived, draft) - filter by status
- `source`: string (user_created, indeed, linkedin) - filter by source
- `limit`: integer (1-100, default: 20)
- `offset`: integer (default: 0)

**Response** (200 OK):
```json
{
  "jobs": [
    {
      "id": "uuid",
      "source": "user_created",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "Seattle, WA",
      "remote": true,
      "status": "active",
      "created_at": "2025-10-21T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_next": false,
    "has_previous": false
  }
}
```

### GET /jobs/browse

**Description**: Browse mock/external job listings (for discovery and saving)

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `query`: string (search keywords, e.g., "Python Developer")
- `location`: string (city, state, or "Remote")
- `remote`: boolean (filter for remote jobs only)
- `limit`: integer (1-100, default: 20)
- `offset`: integer (default: 0)

**Note**: This endpoint returns jobs from a **mock JSON dataset** (not saved to user's jobs). Users can browse these jobs and save them via POST /jobs with the job data.

**Response** (200 OK):
```json
{
  "jobs": [
    {
      "source": "mock",
      "title": "Senior Python Developer",
      "company": "Tech Innovations Inc",
      "location": "San Francisco, CA",
      "description": "We are seeking an experienced Python developer to join our team...\n\nResponsibilities:\n- Design and implement scalable backend services\n- Collaborate with frontend teams\n- Mentor junior developers\n\nQualifications:\n- 5+ years Python experience\n- Strong knowledge of FastAPI or Django\n- Experience with AWS, Docker, Kubernetes",
      "requirements": [
        "5+ years Python experience",
        "FastAPI or Django framework knowledge",
        "AWS cloud services experience",
        "Docker and Kubernetes proficiency"
      ],
      "benefits": [
        "Competitive salary $140k-$180k",
        "Health, dental, vision insurance",
        "401k matching",
        "Flexible remote work",
        "Unlimited PTO"
      ],
      "parsed_keywords": ["python", "fastapi", "django", "aws", "docker", "kubernetes"],
      "salary_range": "140000-180000",
      "remote": true
    },
    {
      "source": "mock",
      "title": "Full Stack Engineer",
      "company": "Startup XYZ",
      "location": "Remote",
      "description": "Join our fast-growing startup...",
      "requirements": [
        "3+ years full-stack development",
        "React and Node.js experience"
      ],
      "benefits": [
        "Equity options",
        "Remote-first culture"
      ],
      "parsed_keywords": ["react", "nodejs", "typescript", "mongodb"],
      "salary_range": "100000-140000",
      "remote": true
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

**Errors**:
- 401: Unauthorized
- 400: Invalid query parameters

### GET /jobs/{id}

**Description**: Get job details

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Full job object (same as POST response)

**Errors**:
- 404: Job not found
- 403: Not authorized (not owner for user_created jobs)

### PUT /jobs/{id}

**Description**: Update parsed metadata (keywords, status, application status) - NOT job posting content

**Headers**: `Authorization: Bearer <token>`

**Note**: Job posting content (title, company, description, requirements from source) is READ-ONLY. 
Only user-controlled fields can be updated:
- `parsed_keywords`: Array of strings (user can refine AI-extracted keywords)
- `status`: active, archived, draft (job listing visibility)
- `application_status`: not_applied, preparing, applied, interviewing, offer_received, rejected, accepted, withdrawn (user's application progress tracking)

**Request**:
```json
{
  "parsed_keywords": ["python", "fastapi", "aws", "docker"],
  "status": "active",
  "application_status": "applied"
}
```

**Response** (200 OK): Updated job with modified fields only

**Errors**:
- 400: Validation error (e.g., trying to update read-only fields like title, company)
- 404: Job not found
- 403: Not authorized

### DELETE /jobs/{id}

**Description**: Delete job (hard delete)

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

**Errors**:
- 404: Job not found
- 403: Not authorized

## Mobile Integration Notes

### Job Model
```dart
class Job {
  final String id;
  final String? userId;
  final String source;
  final String title;
  final String company;
  final String? location;
  final String description;
  final String? rawText;
  final List<String> parsedKeywords;
  final List<String> requirements;
  final List<String> benefits;
  final String? salaryRange;
  final bool remote;
  final JobStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  Job({
    required this.id,
    this.userId,
    required this.source,
    required this.title,
    required this.company,
    this.location,
    required this.description,
    this.rawText,
    this.parsedKeywords = const [],
    this.requirements = const [],
    this.benefits = const [],
    this.salaryRange,
    this.remote = false,
    this.status = JobStatus.active,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['id'],
      userId: json['user_id'],
      source: json['source'],
      title: json['title'],
      company: json['company'],
      location: json['location'],
      description: json['description'],
      rawText: json['raw_text'],
      parsedKeywords: List<String>.from(json['parsed_keywords'] ?? []),
      requirements: List<String>.from(json['requirements'] ?? []),
      benefits: List<String>.from(json['benefits'] ?? []),
      salaryRange: json['salary_range'],
      remote: json['remote'] ?? false,
      status: JobStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => JobStatus.active,
      ),
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() => {
    'source': source,
    'title': title,
    'company': company,
    'location': location,
    'description': description,
    'raw_text': rawText,
    'requirements': requirements,
    'benefits': benefits,
    'salary_range': salaryRange,
    'remote': remote,
    'status': status.name,
  };
}

enum JobStatus { active, archived, draft }
```

### Job Service
```dart
class JobService {
  final ApiClient _client;

  // Create from raw text (paste)
  Future<Job> createFromText(String text) async {
    final response = await _client.post('/jobs', data: {
      'source': 'user_created',
      'raw_text': text,
    });
    return Job.fromJson(response.data);
  }

  // Create from structured data (form)
  Future<Job> createFromForm(Job job) async {
    final response = await _client.post('/jobs', data: job.toJson());
    return Job.fromJson(response.data);
  }

  Future<List<Job>> getJobs({
    JobStatus? status,
    String? source,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/jobs', queryParameters: {
      if (status != null) 'status': status.name,
      if (source != null) 'source': source,
      'limit': limit,
      'offset': offset,
    });
    return (response.data['jobs'] as List)
        .map((json) => Job.fromJson(json))
        .toList();
  }

  Future<Job> getJob(String id) async {
    final response = await _client.get('/jobs/$id');
    return Job.fromJson(response.data);
  }

  Future<Job> updateJob(String id, Job job) async {
    final response = await _client.put('/jobs/$id', data: job.toJson());
    return Job.fromJson(response.data);
  }

  Future<void> deleteJob(String id) async {
    await _client.delete('/jobs/$id');
  }

  Future<void> archiveJob(String id) async {
    await _client.put('/jobs/$id', data: {'status': 'archived'});
  }
}
```

### UI Patterns

**Create Job - Two Methods**:
1. Paste text input:
   - Large text area
   - "Paste job description" hint
   - Loading indicator during parsing
   - Show parsed results for review
   - Allow editing parsed fields

2. Manual form:
   - Title, company (required)
   - Location, remote checkbox
   - Description text area
   - Add requirements (list builder)
   - Add benefits (list builder)
   - Salary range

**Job List**:
- Show title, company, location
- Filter chips: Active, Archived
- Sort by: Created date, Company name
- Swipe actions: Archive, Delete
- Pull to refresh

**Job Detail**:
- Show all fields
- Highlight keywords
- Actions: Edit, Archive, Delete, Generate Resume
- Show parsed data quality indicator

### Error Handling
```dart
try {
  final job = await jobService.createFromText(pastedText);
  showSuccess('Job created successfully');
  return job;
} on DioError catch (e) {
  if (e.response?.statusCode == 400) {
    final errors = e.response?.data['details'];
    showValidationErrors(errors);
  } else {
    showError('Failed to create job');
  }
  rethrow;
}
```

### Local Storage
Consider caching jobs:
- Store recent jobs locally (Hive/SQLite)
- Sync on network availability
- Show cached jobs with sync indicator
- Draft support for offline creation

## LLM-Optimized Data Structure

The job data model is specifically designed for easy LLM/AI processing:

### Key LLM-Friendly Fields

1. **`description`** (string): Full job description text
   - Used in prompts: "The job description is: {description}"
   - Raw, unstructured format that LLMs handle well

2. **`parsed_keywords`** (array of strings): Extracted technical keywords
   - Used in prompts: "Key technologies: {', '.join(parsed_keywords)}"
   - Example: `["python", "fastapi", "aws", "docker", "kubernetes"]`
   - Helps LLM focus on relevant skills from profile

3. **`requirements`** (array of strings): Structured list of qualifications
   - Used in prompts: "Job requirements:\n- {'\n- '.join(requirements)}"
   - Each item is a complete sentence/phrase
   - Example: `["5+ years Python experience", "Strong AWS knowledge"]`

4. **`benefits`** (array of strings): Company perks and benefits
   - Optional in prompts, but useful for cover letter generation
   - Example: `["Remote work", "Health insurance", "401k matching"]`

5. **`raw_text`** (string): Original pasted text before parsing
   - Fallback if parsing fails
   - Used for re-parsing or manual review

### LLM Prompt Template Example

```
Generate a tailored resume for this candidate:

CANDIDATE PROFILE:
{profile.professional_summary}

Skills: {', '.join(profile.skills.technical)}
Experience: {experience_summary}

TARGET JOB:
Title: {job.title} at {job.company}
Location: {job.location}

Key Technologies: {', '.join(job.parsed_keywords)}

Job Requirements:
{'\n'.join(f'- {req}' for req in job.requirements)}

Job Description:
{job.description}

Please highlight relevant experience and skills that match the job requirements.
Focus on technologies: {', '.join(job.parsed_keywords)}
```

### Why This Structure Works for LLMs

- **Hierarchical**: Description → Keywords → Requirements flows from general to specific
- **Structured Arrays**: Easy to iterate and inject into prompts with proper formatting
- **Keywords Pre-extracted**: Reduces LLM token usage, faster matching against profile
- **Requirements as Bullets**: Natural language format that LLMs handle well
- **Raw Text Preserved**: Allows re-parsing with different strategies

## Mock JSON System Implementation

### Mock Data Structure

Store mock jobs in `backend/data/mock_jobs.json`:

```json
{
  "tech_jobs": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Innovations Inc",
      "location": "San Francisco, CA",
      "description": "We are seeking an experienced Python developer...\n\n[Full description]",
      "requirements": [
        "5+ years Python experience",
        "FastAPI or Django knowledge",
        "AWS cloud services"
      ],
      "benefits": [
        "Competitive salary $140k-$180k",
        "Health insurance",
        "Remote work"
      ],
      "parsed_keywords": ["python", "fastapi", "django", "aws", "docker"],
      "salary_range": "140000-180000",
      "remote": true
    }
  ],
  "total_count": 50
}
```

### Browse Endpoint Implementation Strategy

```python
# app/application/services/job_service.py

class JobService:
    def __init__(self, job_repository, mock_data_loader):
        self.job_repository = job_repository
        self.mock_jobs = mock_data_loader.load_jobs()  # Load from JSON

    async def browse_jobs(
        self,
        query: str = None,
        location: str = None,
        remote: bool = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[Job], int]:
        """Browse mock jobs with filtering."""
        filtered_jobs = self.mock_jobs

        # Simple keyword filtering
        if query:
            keywords = query.lower().split()
            filtered_jobs = [
                job for job in filtered_jobs
                if any(kw in job['title'].lower() or
                      kw in job['description'].lower() or
                      kw in job['parsed_keywords']
                      for kw in keywords)
            ]

        if location:
            filtered_jobs = [
                job for job in filtered_jobs
                if location.lower() in job.get('location', '').lower()
            ]

        if remote is not None:
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('remote') == remote
            ]

        total = len(filtered_jobs)
        paginated = filtered_jobs[offset:offset + limit]

        return paginated, total
```

### Mock Job Categories

Organize mock data by job categories:
- **tech_jobs**: Software engineering, DevOps, Data Science
- **product_jobs**: Product Manager, UX Designer, Project Manager
- **marketing_jobs**: Marketing Manager, Content Creator, SEO Specialist

Each category should have 15-20 diverse job listings with:
- Varied skill requirements
- Different seniority levels (junior, mid, senior)
- Mix of remote and on-site positions
- Representative salary ranges

## Implementation Notes

### Repository
- `app/infrastructure/repositories/job_repository.py`
- Methods: `create()`, `get_by_id()`, `get_user_jobs()`, `update()`, `delete()`

### Service
- `app/application/services/job_service.py`
- Text parsing logic with deterministic rules + LLM fallback

### Text Parser
Extraction rules (deterministic):
1. Title: First line or pattern matching (e.g., "Job Title:", "Position:")
2. Company: Pattern matching (e.g., "at Company Name", "Company:")
3. Location: City/State patterns, remote keywords
4. Requirements: Bullet points after "Requirements:", "Qualifications:"
5. Benefits: Bullet points after "Benefits:", "We offer:"

LLM fallback (rate-limited):
- Used for ambiguous or complex descriptions
- Structured prompt for extraction
- Validated output format

### Database Schema
Single unified JobModel table:
- `user_id`: Nullable (null for external API jobs, set for user_created)
- `source`: String (user_created, indeed, linkedin, static, scraped, imported)
- `status`: Enum (active, archived, draft, expired)
- All other fields support both manual and parsed data

### Validation Rules
- `source` field required (identifies origin)
- For user_created: either `raw_text` OR structured fields required
- Title, company, description required
- Keywords extracted automatically
- Status defaults to "active"

### Testing
- Test raw text parsing
- Test structured creation
- Test ownership verification
- Test filtering by status/source
- Test hard delete behavior
- Test LLM parsing fallback
