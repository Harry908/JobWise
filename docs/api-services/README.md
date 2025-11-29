# JobWise API Documentation

**Version**: 1.0
**Base URL**: `http://localhost:8000`
**API Documentation**: `http://localhost:8000/docs` (Swagger UI)
**Last Updated**: November 2025

---

## Overview

JobWise provides a RESTful API for AI-powered job application document generation. The API consists of five main service groups plus comprehensive database documentation:

1. **Authentication API** - User registration and JWT authentication
2. **Profile API** - Master resume profile management
3. **Job API** - Job posting management and text parsing
4. **V3 Generation API** - AI-powered document generation (10 endpoints)
5. **Document Export API** - PDF/DOCX formatting and export (9 endpoints) 🔄 Planned
6. **Database Schema** - Complete database documentation (10 tables)

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     JobWise API v1.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Auth API                Profile API       Job API         │
│  /api/v1/auth/*         /api/v1/profiles/* /api/v1/jobs/*  │
│  ├─ POST /register      ├─ POST /         ├─ POST /       │
│  ├─ POST /login         ├─ GET /me        ├─ GET /        │
│  ├─ POST /refresh       ├─ PUT /{id}      ├─ GET /{id}    │
│  ├─ GET /me             ├─ DELETE /{id}   ├─ PUT /{id}    │
│  └─ POST /logout        └─ ... (15+ more) └─ DELETE /{id} │
│                                                             │
│  V3 Generation API                                          │
│  /api/v1/*                                                  │
│  ├─ POST /samples/upload                                    │
│  ├─ POST /profile/enhance                                   │
│  ├─ POST /rankings/create                                   │
│  ├─ POST /generations/resume                                │
│  ├─ POST /generations/cover-letter                          │
│  ├─ GET /samples                                            │
│  ├─ GET /samples/{id}                                       │
│  ├─ DELETE /samples/{id}                                    │
│  ├─ GET /rankings/job/{job_id}                              │
│  └─ GET /generations/history                                │
│                                                             │
│  Document Export API (Planned)                              │
│  /api/v1/exports/*                                          │
│  ├─ POST /pdf                                               │
│  ├─ POST /docx                                              │
│  ├─ POST /batch                                             │
│  ├─ GET /templates                                          │
│  ├─ GET /templates/{id}                                     │
│  ├─ POST /preview                                           │
│  ├─ GET /files                                              │
│  ├─ GET /files/{id}/download                                │
│  └─ DELETE /files/{id}                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Authentication

All endpoints except the following require JWT authentication:
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

**Authentication Header**:
```http
Authorization: Bearer <access_token>
```

**Token Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

## API Services

### 1. [Authentication API](01-authentication-api.md)
**Base Path**: `/api/v1/auth`

User registration, login, and token management.

**Endpoints**:
- `POST /register` - Create new user account
- `POST /login` - Authenticate and receive tokens
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user profile
- `POST /logout` - Invalidate session
- `POST /change-password` - Change user password
- `POST /forgot-password` - Request password reset
- `POST /reset-password` - Reset password with token
- `GET /check-email` - Check email availability

### 2. [Profile API](02-profile-api.md)
**Base Path**: `/api/v1/profiles`

Master resume profile management with experiences, education, projects, and skills.

**Features**:
- CRUD operations for profiles
- Bulk operations for experiences, education, projects
- Skills management (technical, soft, languages, certifications)
- Custom fields support
- Profile analytics and completeness scoring

**Endpoints**: 20+ endpoints for comprehensive profile management

### 3. [Job API](03-job-api.md)
**Base Path**: `/api/v1/jobs`

Job posting management with intelligent text parsing.

**Features**:
- Create from text (AI parsing)
- Create from URL (scraping)
- Create from structured data
- List and filter jobs
- Update application status
- Delete jobs

**Endpoints**: 5 core endpoints with flexible input handling

### 4. Generation APIs (Split into 2 groups)

#### 4a. [Sample Upload API](04a-sample-upload-api.md)
**Base Path**: `/api/v1/samples`

Sample document upload and management (no LLM required).

**Features**:
- Sample document upload (.txt files)
- List, retrieve, and delete samples
- Active sample tracking per document type

**Endpoints**: 4 CRUD endpoints

#### 4b. [AI Generation API](04b-ai-generation-api.md)
**Base Path**: `/api/v1`

AI-powered resume and cover letter generation using Groq LLM.

**Features**:
- Writing style extraction from samples
- AI-powered profile enhancement
- Job-specific content ranking
- Resume generation (pure logic compilation)
- Cover letter generation (LLM-powered)

**AI Models**:
- `llama-3.3-70b-versatile` - High quality (cover letters, enhancements)
- `llama-3.1-8b-instant` - Fast speed (ranking, analysis)

**Endpoints**: 6 specialized endpoints

#### [V3 Generation API](04-v3-generation-api.md) (Combined Reference)
**Note**: This is the combined documentation. Use 04a and 04b for focused agent work.

### 5. [Document Export API](05-document-export-api.md) 🔄 Planned
**Base Path**: `/api/v1/exports`

Professional PDF and DOCX export with multiple templates and customization.

**Features**:
- PDF export with 4 professional templates
- DOCX export for editable documents
- Batch export (resume + cover letter packages)
- Template preview and customization
- File management and downloads

**Templates**:
- Modern (85% ATS) - Tech/Startups
- Classic (95% ATS) - Corporate/Finance
- Creative (75% ATS) - Design/Marketing
- ATS-Optimized (98% ATS) - Enterprise

**Endpoints**: 9 endpoints for complete export workflow

### 6. [Database Schema](06-database-schema.md)
**Database**: SQLite (Dev), PostgreSQL (Prod)

Complete database schema documentation including all 10 tables, relationships, indexes, and data structures.

**Tables**:
- `users` - User authentication and accounts
- `master_profiles` - Master resume profiles
- `experiences` - Work experience history
- `education` - Educational background
- `projects` - Personal and professional projects
- `jobs` - Job postings (saved, scraped, API-sourced)
- `generations` - AI document generation tracking
- `writing_styles` - Extracted user writing styles (v3.0)
- `sample_documents` - User-uploaded sample documents (v3.0)
- `job_content_rankings` - Job-specific content rankings (v3.0)

**Features**:
- Complete schema with column types and constraints
- Foreign key relationships and cascade rules
- JSON field structures and examples
- Index optimization for query performance
- Migration management with Alembic
- Storage estimates and retention policies

---

## Error Responses

All endpoints follow consistent error response format:

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| `200 OK` | Successful GET/PUT/PATCH | Profile retrieved successfully |
| `201 Created` | Successful POST | User registered successfully |
| `204 No Content` | Successful DELETE | Job deleted successfully |
| `400 Bad Request` | Invalid request data | Missing required field |
| `401 Unauthorized` | Missing/invalid authentication | Invalid JWT token |
| `403 Forbidden` | Insufficient permissions | Cannot access other user's profile |
| `404 Not Found` | Resource not found | Profile ID does not exist |
| `409 Conflict` | Resource conflict | Email already registered |
| `422 Unprocessable Entity` | Validation error | Invalid date format |
| `500 Internal Server Error` | Server error | Database connection failed |

---

## Common Request Patterns

### Pagination

Endpoints that return lists support pagination:

**Query Parameters**:
```
?limit=20&offset=0
```

**Response**:
```json
{
  "items": [...],
  "total": 100,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 100,
    "hasMore": true
  }
}
```

### Filtering

List endpoints support filtering:

**Job Filtering**:
```
GET /api/v1/jobs?status=active&source=user_created&limit=20
```

### Bulk Operations

Profile API supports bulk operations for efficient updates:

**Bulk Create Experiences**:
```json
POST /api/v1/profiles/{id}/experiences/bulk
{
  "experiences": [
    {...},
    {...}
  ]
}
```

---

## Rate Limiting (Planned)

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| General API | 100 requests | per minute |
| Authentication | 10 requests | per minute |
| AI Generation | 10 requests | per hour |

---

## Data Formats

### Date Format
All dates use ISO 8601 format: `YYYY-MM-DD`

**Example**: `2025-11-15`

### Timestamp Format
All timestamps use ISO 8601 with UTC timezone:

**Example**: `2025-11-15T10:30:00Z`

### UUID Format
All resource IDs use UUID v4 format:

**Example**: `550e8400-e29b-41d4-a716-446655440000`

---

## Development

### Interactive API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can:
- View all endpoints
- Test API calls directly
- See request/response schemas
- Generate code samples

### Alternative Documentation

Visit `http://localhost:8000/redoc` for ReDoc documentation with:
- Clean, organized layout
- Detailed schema descriptions
- Better readability for documentation

---

## API Versioning

Current version: **v1.0**

All endpoints are prefixed with `/api/v1/` to support future versioning.

**Example**: `http://localhost:8000/api/v1/profiles/me`

---

## Quick Start

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### 3. Create Profile
```bash
curl -X POST http://localhost:8000/api/v1/profiles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "personal_info": {
      "full_name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-123-4567",
      "location": "Seattle, WA"
    },
    "professional_summary": "Senior software engineer with 8+ years...",
    "skills": {
      "technical": ["Python", "FastAPI", "React"],
      "soft": ["Leadership", "Communication"]
    }
  }'
```

### 4. Create Job
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Senior Python Developer at TechCorp..."
  }'
```

### 5. Upload Sample Document
```bash
curl -X POST http://localhost:8000/api/v1/samples/upload \
  -H "Authorization: Bearer <token>" \
  -F "document_type=cover_letter" \
  -F "file=@my_cover_letter.txt"
```

### 6. Generate Resume
```bash
curl -X POST http://localhost:8000/api/v1/generations/resume \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "max_experiences": 5,
    "max_projects": 3,
    "include_summary": true
  }'
```

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Source Code**: GitHub repository
- **Issues**: GitHub Issues

---

**Last Updated**: November 2025
**API Version**: 1.0
**Documentation Status**: Complete
