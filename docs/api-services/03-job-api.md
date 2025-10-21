# Job API Service

**Version**: 1.0
**Base Path**: `/api/v1/jobs`
**Status**: Implemented

## Service Overview

Unified CRUD API for managing job descriptions from multiple sources. Accepts raw text (auto-parsed) or structured data. Supports user-created jobs, imported jobs, and future integration with external job APIs.

## Specification

**Purpose**: Job description management with multi-source support
**Authentication**: Required (JWT)
**Authorization**: Users can only manage jobs they created (user_created source)
**Text Parsing**: LLM-powered extraction (optional, rate-limited)
**Delete Behavior**: Hard delete (immediate removal)

## Dependencies

### Internal
- Authentication API: User identity via JWT
- Database: JobModel (unified table)
- Repositories: JobRepository
- LLM Service: Text parsing (optional, via ILLMService port)

### External
- Future: Indeed API, LinkedIn API, Glassdoor API

## Data Flow

```
Create Job (Raw Text):
1. Client → POST /jobs {raw_text, source: "user_created"}
2. API validates JWT → get user_id
3. API invokes text parser (deterministic rules + optional LLM)
4. API extracts: title, company, location, requirements, benefits
5. API creates JobModel with user_id and parsed data
6. API ← Job response with parsed fields

Create Job (Structured):
1. Client → POST /jobs {title, company, description, source, ...}
2. API validates JWT → get user_id
3. API validates structured data
4. API creates JobModel with user_id
5. API ← Job response

List Jobs:
1. Client → GET /jobs?status=active&source=user_created
2. API validates JWT → get user_id
3. API fetches jobs where user_id = current_user.id
4. API applies filters (status, source)
5. API ← Job list with pagination

Update Job:
1. Client → PUT /jobs/{id} {updated_fields}
2. API validates JWT → get user_id
3. API verifies job.user_id == current_user.id
4. API updates job record
5. API ← Updated job

Delete Job:
1. Client → DELETE /jobs/{id}
2. API validates JWT → get user_id
3. API verifies ownership
4. API hard deletes job (immediate removal)
5. API ← 204 No Content
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

### GET /jobs/{id}

**Description**: Get job details

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK): Full job object (same as POST response)

**Errors**:
- 404: Job not found
- 403: Not authorized (not owner for user_created jobs)

### PUT /jobs/{id}

**Description**: Update job

**Headers**: `Authorization: Bearer <token>`

**Request**: Partial or full job object (same structure as POST)

**Response** (200 OK): Updated job

**Errors**:
- 400: Validation error
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
