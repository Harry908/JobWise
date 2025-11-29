# Sample Upload API

**Version**: 3.0
**Base Path**: `/api/v1/samples`
**Status**: ✅ Fully Implemented
**LLM Required**: No

---

## Overview

The Sample Upload API provides endpoints for managing sample documents (resumes and cover letters) that users upload to teach the AI their writing style. This API handles pure CRUD operations with no LLM integration - all endpoints are fast and deterministic.

**Key Features**:
- **Sample Document Upload**: Store example resumes and cover letters (.txt files)
- **Document Management**: List, retrieve, and delete sample documents
- **Active Sample Tracking**: Automatic management of active samples per type
- **Text Storage**: Full document text stored for later AI analysis

**Related APIs**:
- [AI Generation API](04b-ai-generation-api.md) - Uses samples for writing style extraction and generation

---

## Endpoints Summary

| # | Method | Endpoint | Description | Speed |
|---|--------|----------|-------------|-------|
| 1 | POST | `/samples/upload` | Upload sample document | <500ms |
| 2 | GET | `/samples` | List uploaded samples | <200ms |
| 3 | GET | `/samples/{id}` | Get sample details | <100ms |
| 4 | DELETE | `/samples/{id}` | Delete sample | <100ms |

---

## Endpoints

### 1. Upload Sample Document

Upload a sample resume or cover letter for writing style extraction.

**Endpoint**: `POST /api/v1/samples/upload`

**Authentication**: Required

**Request Type**: `multipart/form-data`

**Form Fields**:
| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `document_type` | string | Yes | resume, cover_letter | Type of document |
| `file` | file | Yes | .txt only | Sample document file |

**File Requirements**:
- **Format**: Plain text (.txt) only
- **Size**: Maximum 1 MB
- **Encoding**: UTF-8
- **Content**: Non-empty text

**Request Example** (cURL):
```bash
curl -X POST http://localhost:8000/api/v1/samples/upload \
  -H "Authorization: Bearer <token>" \
  -F "document_type=cover_letter" \
  -F "file=@my_cover_letter.txt"
```

**Request Example** (Python):
```python
import requests

url = "http://localhost:8000/api/v1/samples/upload"
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("my_cover_letter.txt", "rb")}
data = {"document_type": "cover_letter"}

response = requests.post(url, headers=headers, files=files, data=data)
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "word_count": 421,
  "character_count": 2847,
  "is_active": true,
  "created_at": "2025-11-15T10:30:00Z"
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique sample identifier |
| `user_id` | integer | Owner user ID |
| `document_type` | string | "resume" or "cover_letter" |
| `original_filename` | string | Original uploaded filename |
| `word_count` | integer | Number of words in document |
| `character_count` | integer | Number of characters in document |
| `is_active` | boolean | Whether this is the active sample for this type |
| `created_at` | datetime | Upload timestamp |

**Business Logic**:
1. Validate file extension is `.txt`
2. Read file content as UTF-8 text
3. Calculate `word_count` and `character_count`
4. Set previous samples of same type to `is_active=false`
5. Store new sample with `is_active=true`
6. Full text stored in database for re-analysis

**Error Responses**:

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

**413 Payload Too Large**:
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

---

### 2. List Uploaded Samples

Retrieve all uploaded sample documents for the user.

**Endpoint**: `GET /api/v1/samples`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_type` | string | No | Filter by type (resume/cover_letter) |
| `is_active` | boolean | No | Filter by active status |

**Request Example**:
```bash
# Get all samples
curl -X GET http://localhost:8000/api/v1/samples \
  -H "Authorization: Bearer <token>"

# Get only active cover letters
curl -X GET "http://localhost:8000/api/v1/samples?document_type=cover_letter&is_active=true" \
  -H "Authorization: Bearer <token>"
```

**Success Response** (200 OK):
```json
{
  "samples": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": 1,
      "document_type": "cover_letter",
      "original_filename": "my_cover_letter.txt",
      "word_count": 421,
      "character_count": 2847,
      "is_active": true,
      "created_at": "2025-11-15T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "user_id": 1,
      "document_type": "resume",
      "original_filename": "my_resume.txt",
      "word_count": 856,
      "character_count": 5234,
      "is_active": true,
      "created_at": "2025-11-14T09:00:00Z"
    }
  ],
  "total": 2
}
```

**Note**: List endpoint does NOT include `full_text` for performance. Use Get Sample Details endpoint for full content.

---

### 3. Get Sample Details

Retrieve detailed information about a specific sample document including full text.

**Endpoint**: `GET /api/v1/samples/{sample_id}`

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sample_id` | UUID | Yes | Sample document ID |

**Request Example**:
```bash
curl -X GET http://localhost:8000/api/v1/samples/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "full_text": "Dear Hiring Manager,\n\nI am writing to express my sincere interest in the Software Engineer position at TechCorp Inc. With over 8 years of experience developing scalable cloud solutions...\n\nThank you for considering my application.\n\nSincerely,\nJohn Doe",
  "word_count": 421,
  "character_count": 2847,
  "writing_style": {
    "tone": "professional yet personable",
    "vocabulary_level": "advanced",
    "sentence_structure": "varied, mix of simple and complex",
    "key_phrases": ["excited to contribute", "proven track record"]
  },
  "is_active": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Note**: `writing_style` is populated after AI analysis (via Profile Enhancement in AI Generation API).

**Error Responses**:

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

### 4. Delete Sample

Delete a sample document permanently.

**Endpoint**: `DELETE /api/v1/samples/{sample_id}`

**Authentication**: Required

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sample_id` | UUID | Yes | Sample document ID |

**Request Example**:
```bash
curl -X DELETE http://localhost:8000/api/v1/samples/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

**Success Response** (204 No Content): No body

**Error Responses**:

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

## Database Schema

### sample_documents Table

```sql
CREATE TABLE sample_documents (
    id VARCHAR PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    document_type VARCHAR NOT NULL,  -- 'resume' or 'cover_letter'
    original_filename VARCHAR NOT NULL,
    file_path VARCHAR,
    full_text TEXT NOT NULL,
    writing_style TEXT,  -- JSON (populated by AI analysis)
    word_count INTEGER,
    character_count INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, document_type, is_active),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_sample_documents_user_id ON sample_documents(user_id);
CREATE INDEX idx_sample_documents_type_active ON sample_documents(document_type, is_active);
```

---

## Data Models

### Sample (Python)

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class SampleBase(BaseModel):
    document_type: str  # 'resume' or 'cover_letter'

class SampleCreate(SampleBase):
    pass  # File is handled separately via multipart form

class SampleResponse(SampleBase):
    id: UUID
    user_id: int
    original_filename: str
    word_count: int
    character_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SampleDetailResponse(SampleResponse):
    full_text: str
    writing_style: Optional[dict] = None
    updated_at: datetime

class SampleListResponse(BaseModel):
    samples: list[SampleResponse]
    total: int
```

---

## Best Practices

### 1. Sample Document Quality

For best AI results when using samples in the AI Generation API:
- Use your best professional cover letter
- Use complete, well-formatted resume
- Ensure samples represent your desired tone
- Use plain text format (.txt)
- Avoid generic templates
- Don't use samples with placeholder text

### 2. Active Sample Management

- Only one sample per type can be active at a time
- Uploading a new sample automatically deactivates the old one
- Inactive samples are retained for history
- Delete samples to permanently remove them

### 3. File Handling

- Maximum file size: 1 MB
- Supported format: .txt only
- UTF-8 encoding required
- Empty files are rejected

---

## Performance Metrics

| Operation | Target | Actual |
|-----------|--------|--------|
| Upload sample | <500ms | ~200ms |
| List samples | <200ms | ~50ms |
| Get sample details | <100ms | ~30ms |
| Delete sample | <100ms | ~20ms |

---

## Error Handling

All endpoints follow consistent error patterns:

### Common Errors

**Authentication Required**:
```json
{
  "detail": "Not authenticated"
}
```

**Invalid Token**:
```json
{
  "detail": "Could not validate credentials"
}
```

**Resource Not Found**:
```json
{
  "detail": "Sample document not found"
}
```

---

## Related Documentation

- [AI Generation API](04b-ai-generation-api.md) - Uses samples for AI features
- [Profile API](02-profile-api.md) - Profile management
- [Database Schema](06-database-schema.md) - Complete database documentation

---

**Last Updated**: November 2025
**API Version**: 3.0
**Total Endpoints**: 4
**LLM Provider**: None (pure CRUD operations)
**Status**: Production Ready
