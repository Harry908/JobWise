# JobWise API Services Documentation

Comprehensive design specifications for all JobWise backend API services. Each document provides complete implementation and integration guidance.

## Overview

JobWise backend consists of 5 core API services following Clean Architecture with Ports & Adapters pattern.

```
User Flow:
1. Authentication → Register/Login
2. Profile → Create master resume
3. Job → Save job descriptions
4. Generation → Generate tailored resume
5. Document → Download PDF
```

## API Services

### 1. Authentication API
**File**: [01-authentication-api.md](01-authentication-api.md)
**Base Path**: `/api/v1/auth`
**Status**: Implemented

User registration, authentication, and JWT token management.

**Key Endpoints**:
- POST /register
- POST /login
- POST /refresh
- GET /me

**Dependencies**: None (foundation service)

---

### 2. Profile API
**File**: [02-profile-api.md](02-profile-api.md)
**Base Path**: `/api/v1/profiles`
**Status**: Implemented

Master resume profile management with experiences, education, skills, and projects.

**Key Endpoints**:
- POST /profiles
- GET /profiles
- GET /profiles/{id}
- PUT /profiles/{id}
- DELETE /profiles/{id}
- GET /profiles/{id}/analytics

**Dependencies**: Authentication API

---

### 3. Job API
**File**: [03-job-api.md](03-job-api.md)
**Base Path**: `/api/v1/jobs`
**Status**: Implemented

Unified job description management supporting raw text parsing and structured data.

**Key Endpoints**:
- POST /jobs (raw text or structured)
- GET /jobs (with filtering)
- GET /jobs/{id}
- PUT /jobs/{id}
- DELETE /jobs/{id}

**Dependencies**: Authentication API

**Special Features**:
- Text parsing with LLM fallback
- Multi-source support (user_created, indeed, linkedin)
- Hard delete behavior

---

### 4. Generation API
**File**: [04-generation-api.md](04-generation-api.md)
**Base Path**: `/api/v1/generations`
**Status**: Sprint 2 (In Development)

AI-powered resume generation using 5-stage pipeline with asynchronous processing.

**Key Endpoints**:
- POST /generations/resume
- POST /generations/cover-letter
- GET /generations/{id} (polling)
- GET /generations/{id}/result
- POST /generations/{id}/regenerate
- DELETE /generations/{id}
- GET /generations (list with filters)
- GET /generations/templates

**Dependencies**: Authentication API, Profile API, Job API, Document API

**Special Features**:
- 5-stage pipeline (6s target)
- Real-time progress tracking
- Rate limiting (10/hour)
- Token budget management (8000 tokens)
- ATS scoring and optimization

**Pipeline Stages**:
1. Job Analysis (1s, 1500 tokens)
2. Profile Compilation (1s, 2000 tokens)
3. Content Generation (2s, 3000 tokens)
4. Quality Validation (1s, 1500 tokens)
5. Export Preparation (0.5s, 0 tokens)

---

### 5. Document API
**File**: [05-document-api.md](05-document-api.md)
**Base Path**: `/api/v1/documents`
**Status**: Sprint 2 (In Development)

Document storage, retrieval, and PDF download.

**Key Endpoints**:
- GET /documents (with filtering)
- GET /documents/{id}
- GET /documents/{id}/download
- DELETE /documents/{id}
- PUT /documents/{id}
- GET /documents/export-formats

**Dependencies**: Authentication API, Generation API

**Special Features**:
- PDF generation with ReportLab
- Multiple content formats (text, HTML, markdown)
- File storage (local dev, S3 prod)
- Streaming downloads

---

## Service Dependencies

```
Authentication (JWT)
    ↓
    ├─→ Profile (master resume)
    ├─→ Job (job descriptions)
    │
    └─→ Generation (AI pipeline)
            ↓
            └─→ Document (PDF storage)
```

## Common Patterns

### Authentication
All endpoints (except /auth/register and /auth/login) require JWT authentication:
```
Authorization: Bearer <access_token>
```

### Error Response Format
```json
{
  "error": "error_code_snake_case",
  "message": "Human-readable message",
  "details": {
    "field": "specific error details"
  }
}
```

### Pagination
```json
{
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

### HTTP Status Codes
- 200: OK (successful GET, PUT)
- 201: Created (successful POST)
- 204: No Content (successful DELETE)
- 400: Bad Request (validation error)
- 401: Unauthorized (missing/invalid token)
- 403: Forbidden (not authorized for resource)
- 404: Not Found (resource doesn't exist)
- 409: Conflict (duplicate resource)
- 422: Unprocessable Entity (semantic validation error)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error

## Mobile Integration

Each service document includes:
- Dart/Flutter models
- Service classes with API methods
- UI patterns and examples
- Error handling strategies
- Local caching recommendations

### Quick Start - Flutter Example

```dart
// 1. Setup API client
final apiClient = ApiClient(baseUrl: 'http://localhost:8000/api/v1');

// 2. Authenticate
final authService = AuthService(apiClient);
final auth = await authService.login('user@example.com', 'password');
apiClient.setToken(auth.accessToken);

// 3. Create profile
final profileService = ProfileService(apiClient);
final profile = await profileService.createProfile(Profile(...));

// 4. Save job
final jobService = JobService(apiClient);
final job = await jobService.createFromText(pastedJobDescription);

// 5. Generate resume
final generationService = GenerationService(apiClient);
final generation = await generationService.startResumeGeneration(
  profileId: profile.id,
  jobId: job.id,
);

// 6. Poll for completion
await for (final status in generationService.pollGeneration(generation.id)) {
  print('Progress: ${status.progress.percentage}%');
  if (status.isComplete) {
    final pdfUrl = status.result!.pdfUrl;
    break;
  }
}

// 7. Download document
final documentService = DocumentService(apiClient);
final pdfBytes = await documentService.downloadPDF(
  generation.result!.documentId,
);
```

## Testing Strategy

Each service includes test coverage for:
- Unit tests (domain logic)
- Integration tests (API endpoints)
- Repository tests (database operations)
- Service tests (business logic)

### Test Markers
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - API + database tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.ai` - Tests requiring LLM services

### Coverage Targets
- Overall: 80%
- Domain Layer: 90%+
- Service Layer: 85%+
- API Layer: 75%+

## Performance Targets

| Operation | Target |
|-----------|--------|
| CRUD Operations | <200ms |
| Job Search | <2s |
| Resume Generation | <6s (5-stage pipeline) |
| PDF Export | <2s |
| PDF Download | <1s (streaming) |

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| General APIs | 100 requests/minute |
| AI Generation | 10 requests/hour |
| Document Download | 50 requests/hour |

## API Versioning

Current version: `v1`
Base URL: `/api/v1`

All endpoints are versioned. Breaking changes will result in new API version (v2).

## OpenAPI Specification

Complete OpenAPI 3.0 specification available at:
- Development: `http://localhost:8000/docs` (Swagger UI)
- File: `.context/api/openapi-spec.yaml`

## Support and Feedback

For questions or issues with API integration:
1. Check individual service documentation
2. Review OpenAPI spec at `/docs`
3. Check backend design document: `backend/BACKEND_DESIGN_DOCUMENT.md`
4. Review test examples in `backend/tests/`

## Document Version

**Version**: 1.0
**Last Updated**: October 21, 2025
**Status**: Complete for Sprint 1-2 services

## Service Status Summary

| Service | Status | Sprint | Endpoints | Tests |
|---------|--------|--------|-----------|-------|
| Authentication | Implemented | Sprint 1 | 5 | 13 |
| Profile | Implemented | Sprint 1 | 12 | 12 |
| Job | Implemented | Sprint 1 | 5 | 10 |
| Generation | In Development | Sprint 2 | 11 | Pending |
| Document | In Development | Sprint 2 | 8 | Pending |

## Next Steps for Mobile Developers

1. **Read Service Documents**: Review each API service specification
2. **Setup Development Environment**:
   - Backend API: `http://localhost:8000/api/v1`
   - Swagger UI: `http://localhost:8000/docs`
3. **Implement Models**: Create Dart models from JSON schemas
4. **Build Services**: Implement service classes with API methods
5. **Add Error Handling**: Implement retry logic and user-friendly errors
6. **Test Integration**: Use Swagger UI to verify API behavior
7. **Implement UI**: Build screens with proper state management
8. **Add Offline Support**: Cache data locally for offline access

## Architecture Diagrams

See `backend/BACKEND_DESIGN_DOCUMENT.md` for:
- System architecture diagrams
- Database ERD
- Data flow sequences
- Design patterns

## Change Log

### Version 1.0 (October 21, 2025)
- Initial comprehensive API service documentation
- Complete specifications for all 5 services
- Mobile integration examples (Flutter/Dart)
- Implementation and testing guidance
