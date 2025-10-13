# JobWise API Specification

## Base URL
- **Prototype**: `http://localhost:8000/api/v1`
- **Production**: `https://api.jobwise.app/v1`

## Authentication
- **Prototype**: API Key in header `X-API-Key`
- **Production**: JWT Bearer token in `Authorization` header

## Core Endpoints

### Master Resume Management

#### Create Master Resume
```http
POST /profiles
Content-Type: application/json

{
    "personal_info": {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "location": "City, State"
    },
    "summary": "Experienced software engineer...",
    "experiences": [...],
    "skills": [...],
    "education": [...],
    "projects": [...]
}

Response: 201 Created
{
    "id": "profile_123",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Master Resume
```http
GET /profiles/{profile_id}

Response: 200 OK
{
    "id": "profile_123",
    "personal_info": {...},
    "summary": "...",
    "experiences": [...],
    "skills": [...],
    "education": [...],
    "projects": [...],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update Master Resume
```http
PUT /profiles/{profile_id}
Content-Type: application/json

{
    "summary": "Updated summary...",
    "experiences": [...]
    // Only include fields to update
}

Response: 200 OK
{
    "id": "profile_123",
    "updated_at": "2024-01-15T11:00:00Z"
}
```

#### Delete Master Resume
```http
DELETE /profiles/{profile_id}

Response: 204 No Content
```

### Job Management

#### List Jobs
```http
GET /jobs?search=software&location=seattle&limit=20&offset=0

Response: 200 OK
{
    "jobs": [
        {
            "id": "job_456",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Seattle, WA",
            "description": "...",
            "requirements": [...],
            "posted_date": "2024-01-10T00:00:00Z",
            "source": "indeed"
        }
    ],
    "total": 150,
    "limit": 20,
    "offset": 0
}
```

#### Get Job Details
```http
GET /jobs/{job_id}

Response: 200 OK
{
    "id": "job_456",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "Seattle, WA", 
    "description": "Full job description...",
    "requirements": [...],
    "posted_date": "2024-01-10T00:00:00Z",
    "source": "indeed",
    "analysis": {
        "required_skills": [...],
        "experience_level": "mid",
        "keywords": [...]
    }
}
```

### Resume Generation

#### Generate Tailored Resume
```http
POST /generate/resume
Content-Type: application/json

{
    "profile_id": "profile_123",
    "job_id": "job_456",
    "options": {
        "template": "ats",  // "ats" or "visual"
        "length": "one_page",  // "one_page" or "two_page"
        "focus_areas": ["technical_skills", "leadership"]
    }
}

Response: 202 Accepted
{
    "generation_id": "gen_789",
    "status": "processing",
    "estimated_completion": "2024-01-15T11:05:00Z"
}
```

#### Check Generation Status
```http
GET /generate/status/{generation_id}

Response: 200 OK
{
    "generation_id": "gen_789",
    "status": "completed",  // "processing", "completed", "failed"
    "progress": 100,
    "created_at": "2024-01-15T11:00:00Z",
    "completed_at": "2024-01-15T11:04:32Z",
    "result": {
        "document_id": "doc_101",
        "pdf_url": "/documents/doc_101/download"
    }
}
```

#### Generate Cover Letter
```http
POST /generate/cover-letter
Content-Type: application/json

{
    "profile_id": "profile_123", 
    "job_id": "job_456",
    "options": {
        "tone": "professional",  // "professional", "enthusiastic", "formal"
        "length": "medium"  // "short", "medium", "long"
    }
}

Response: 202 Accepted
{
    "generation_id": "gen_790",
    "status": "processing"
}
```

### Document Management

#### Get Generated Document
```http
GET /documents/{document_id}

Response: 200 OK
{
    "id": "doc_101",
    "type": "resume",  // "resume" or "cover_letter"
    "profile_id": "profile_123",
    "job_id": "job_456",
    "template": "ats",
    "content": {
        "sections": {
            "summary": "...",
            "experience": [...],
            "skills": [...],
            "education": [...]
        }
    },
    "metadata": {
        "ats_score": 85,
        "generation_time_ms": 24500,
        "token_usage": 6200
    },
    "created_at": "2024-01-15T11:04:32Z"
}
```

#### Download PDF
```http
GET /documents/{document_id}/download

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="John_Doe_Resume_TechCorp.pdf"

[PDF binary data]
```

#### List User Documents
```http
GET /documents?type=resume&limit=10&offset=0

Response: 200 OK
{
    "documents": [
        {
            "id": "doc_101",
            "type": "resume",
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "created_at": "2024-01-15T11:04:32Z",
            "ats_score": 85
        }
    ],
    "total": 25,
    "limit": 10,
    "offset": 0
}
```

## Error Responses

### Standard Error Format
```json
{
    "error": {
        "code": "INVALID_REQUEST",
        "message": "Missing required field: profile_id",
        "details": {
            "field": "profile_id",
            "location": "body"
        }
    },
    "request_id": "req_abc123"
}
```

### Error Codes
- `400 INVALID_REQUEST` - Malformed request or missing required fields
- `401 UNAUTHORIZED` - Invalid or missing authentication
- `403 FORBIDDEN` - Insufficient permissions
- `404 NOT_FOUND` - Resource not found
- `409 CONFLICT` - Resource already exists
- `422 VALIDATION_ERROR` - Data validation failed
- `429 RATE_LIMITED` - Too many requests
- `500 INTERNAL_ERROR` - Server error
- `503 SERVICE_UNAVAILABLE` - Temporary service unavailability

## Rate Limiting

### Prototype Limits
- 100 requests per hour per API key
- 10 resume generations per day per API key
- No burst limits

### Production Limits
- 1000 requests per hour per user
- 50 resume generations per day per user
- Burst: 20 requests per minute

## Response Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1642248000
X-Request-ID: req_abc123
```

## Webhook Support (Production Only)

### Generation Completion
```http
POST {webhook_url}
Content-Type: application/json

{
    "event": "generation.completed",
    "generation_id": "gen_789",
    "document_id": "doc_101",
    "timestamp": "2024-01-15T11:04:32Z"
}
```

## SDK Examples

### Python
```python
import jobwise

client = jobwise.Client(api_key="your_api_key")

# Create profile
profile = client.profiles.create({
    "personal_info": {"full_name": "John Doe"},
    "summary": "Experienced engineer..."
})

# Generate resume
generation = client.generate.resume(
    profile_id=profile.id,
    job_id="job_456"
)

# Download PDF
pdf_data = client.documents.download(generation.document_id)
```

### Flutter/Dart
```dart
import 'package:jobwise_api/jobwise_api.dart';

final client = JobwiseClient(apiKey: 'your_api_key');

// Create profile
final profile = await client.profiles.create(ProfileCreate(
  personalInfo: PersonalInfo(fullName: 'John Doe'),
  summary: 'Experienced engineer...'
));

// Generate resume  
final generation = await client.generate.resume(ResumeGenerateRequest(
  profileId: profile.id,
  jobId: 'job_456'
));
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- **Prototype**: `http://localhost:8000/docs`
- **Production**: `https://api.jobwise.app/docs`

## Versioning Strategy

- API versions follow semantic versioning (v1, v2, etc.)
- Breaking changes require new major version
- Backward compatibility maintained for 12 months
- Deprecation notices provided 6 months in advance