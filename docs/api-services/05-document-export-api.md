# Document Export API

**At a Glance (For AI Agents)**
- **Service Name**: Document Export (PDF/DOCX/ZIP over S3)
- **Primary Table**: `exports` (plus `generations`, `users`)
- **Storage Backend**: Amazon S3 **only** (no local filesystem)
- **Core Dependencies**: Auth (`01-authentication-api.md`), V3 Generation (`04-v3-generation-api.md`), AI Generation (`04b-ai-generation-api.md`), Database schema (`06-database-schema.md`)
- **Auth Requirements**: All endpoints require an authenticated user; all queries are scoped by `user_id`
- **Primary Routes**:
  - `POST /api/v1/exports/pdf` — export a single generation to PDF
  - `POST /api/v1/exports/docx` — export a single generation to DOCX
  - `POST /api/v1/exports/batch` — batch export and optional ZIP
  - `GET /api/v1/exports/templates` / `/templates/{template_id}` — list + detail templates
  - `POST /api/v1/exports/preview` — generate a preview image
  - `GET /api/v1/exports/files` — list exported files for the user
  - `GET /api/v1/exports/files/{export_id}/download` — download via backend (S3-backed)
  - `DELETE /api/v1/exports/files/{export_id}` — delete export (and underlying S3 object)

**Related Docs (Navigation Hints)**
- Backend overview: `../BACKEND_ARCHITECTURE_OVERVIEW.md` (export & S3 flow diagrams)
- Database schema: `06-database-schema.md` (`exports` table, S3 key semantics)
- Generation services: `04-v3-generation-api.md`, `04b-ai-generation-api.md`
- Mobile feature: `../mobile-new/05-document-feature.md` (client usage and wire shapes)

**Key Field Semantics (Canonical Meanings)**
- `id` / `export_id` (UUID): Primary key for an exported artifact; used across API and DB.
- `generation_id` (string/UUID): Foreign key to `generations.id`; the source text for export.
- `document_type` (string): `"resume"`, `"cover_letter"`, or `"zip"` depending on export context.
- `format` (string): Output format such as `"pdf"`, `"docx"`, or `"zip"` (container).
- `template` (string): Template identifier (e.g., `modern`, `classic`, `creative`, `ats-optimized`).
- `filename` (string): Client-facing filename suggested in `Content-Disposition`.
- `file_path` (string): **S3 object key only** (pattern `exports/{user_id}/{export_id}.{ext}`); never a local path.
- `file_size_bytes` / `page_count`: Storage and rendering metadata (page count is PDF-only).
- `options` (JSON/text): Serialized template and export options used to create the file.
- `metadata` (JSON/text): Additional info like ATS scores, processing time, or word counts.
- `expires_at` (datetime): Hard expiry after which cleanup jobs must delete S3 object and DB row.
- `download_url` (string): Backend download route or pre-signed URL wrapper returned to clients; S3 remains private.

**Version**: 1.0
**Base Path**: `/api/v1/exports`
**Status**: 🔄 Planned (Design Complete)
**Template Engine**: Jinja2 + WeasyPrint (PDF) + python-docx (DOCX)
**Content Source**: Structured JSON from `generations.content_structured`

---

## Overview

The Document Export API converts generated resume and cover letter **structured data** into professionally formatted PDF and DOCX files. It provides multiple templates, customization options, and file management capabilities.

**Architecture**:
```
Generation Service → Structured JSON (content_structured)
         ↓
Export Service → Template Renderer (Jinja2 + HTML/CSS)
         ↓
WeasyPrint → PDF | python-docx → DOCX
         ↓
S3 Upload → Presigned URL → Client Download
```

**Key Features**:
- **PDF Export**: High-quality PDF generation with ATS-friendly formatting (WeasyPrint)
- **DOCX Export**: Editable Microsoft Word documents (python-docx)
- **Multiple Templates**: Modern, Classic, Creative, ATS-Optimized (HTML/CSS + Jinja2)
- **Customization**: Fonts, colors, spacing, margins
- **Batch Export**: Export multiple generations at once
- **File Management**: Download, list, and delete exported files
- **Template Preview**: See how content looks before exporting

**Content Storage**:
- **Plain Text** (`content_text`): For search, display, backward compatibility
- **Structured JSON** (`content_structured`): For template rendering, exports

---

## Templates

### Available Templates

| Template | Best For | ATS Score | Style |
|----------|----------|-----------|-------|
| **Modern** | Tech, Startups, Creative | 85% | Clean, minimalist, accent colors |
| **Classic** | Corporate, Finance, Legal | 95% | Traditional, black & white, serif fonts |
| **Creative** | Design, Marketing, Media | 75% | Bold headers, color accents, unique layout |
| **ATS-Optimized** | Enterprise, Government | 98% | Maximum parsability, simple formatting |

### Template Features

**Modern Template**:
- Sans-serif fonts (Helvetica, Arial)
- Accent color for headers (customizable)
- Two-column layout for skills/contact
- Clean section dividers

**Classic Template**:
- Serif fonts (Times New Roman, Georgia)
- Black text on white background only
- Single-column layout
- Conservative spacing

**Creative Template**:
- Mixed fonts (headers bold, body light)
- Multiple color accents
- Sidebar for skills/languages
- Visual section separators

**ATS-Optimized Template**:
- Standard fonts (Arial, Calibri)
- No tables, columns, or graphics
- Clear section headers
- Maximum white space
- Text-based only (no images/icons)

---

## Endpoints Summary

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | POST | `/pdf` | Export generation to PDF |
| 2 | POST | `/docx` | Export generation to DOCX |
| 3 | POST | `/batch` | Batch export multiple generations |
| 4 | GET | `/templates` | List available templates |
| 5 | GET | `/templates/{template_id}` | Get template details |
| 6 | POST | `/preview` | Preview document with template |
| 7 | GET | `/files` | List user's exported files |
| 8 | GET | `/files/{export_id}/download` | Download exported file |
| 9 | DELETE | `/files/{export_id}` | Delete exported file |

**Total Endpoints**: 9

---

## Export Endpoints

### 1. Export to PDF

Export a generated resume or cover letter to PDF format.

**Endpoint**: `POST /api/v1/exports/pdf`

**Authentication**: Required

**Request Body**:
```json
{
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "template": "modern",
  "options": {
    "font_family": "Helvetica",
    "font_size": 11,
    "accent_color": "#2563EB",
    "line_spacing": 1.15,
    "margins": {
      "top": 0.75,
      "bottom": 0.75,
      "left": 0.75,
      "right": 0.75
    },
    "include_page_numbers": false,
    "header_style": "bold"
  },
  "filename": "John_Doe_Resume_TechCorp_2025.pdf"
}
```

**Request Schema**:
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `generation_id` | UUID | Yes | - | Generation to export |
| `template` | string | No | modern | Template name |
| `options` | object | No | {} | Formatting options |
| `filename` | string | No | Auto-generated | Custom filename |

**Template Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `font_family` | string | Helvetica | Font (Helvetica, Arial, Times, Georgia, Calibri) |
| `font_size` | integer | 11 | Font size (9-14 pt) |
| `accent_color` | string | #2563EB | Hex color for headers |
| `line_spacing` | float | 1.15 | Line spacing (1.0-2.0) |
| `margins` | object | See example | Page margins in inches |
| `include_page_numbers` | boolean | false | Add page numbers |
| `header_style` | string | bold | Header style (bold, underline, both) |

**Success Response** (201 Created):
```json
{
  "export_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "document_type": "resume",
  "format": "pdf",
  "template": "modern",
  "filename": "John_Doe_Resume_TechCorp_2025.pdf",
  "file_size_bytes": 87432,
  "page_count": 2,
  "download_url": "/api/v1/exports/files/bb0e8400-e29b-41d4-a716-446655440006/download",
  "expires_at": "2025-12-15T10:30:00Z",
  "created_at": "2025-11-15T10:30:00Z",
  "metadata": {
    "ats_score": 88.5,
    "processing_time_seconds": 1.2
  }
}
```

**Processing Flow**:
1. Fetch generation text from `generations` table
2. Parse text into structured sections
3. Apply template formatting rules
4. Render PDF using library (ReportLab, WeasyPrint, or similar)
5. Upload binary file to Amazon S3 (see **S3 Storage Model**)
6. Create `exports` row with S3 object key
7. Return download URL and metadata

**Error Responses**:

**404 Not Found** (Generation not found):
```json
{
  "detail": "Generation not found or does not belong to user"
}
```

**400 Bad Request** (Invalid template):
```json
{
  "detail": "Template 'futuristic' does not exist. Available: modern, classic, creative, ats-optimized"
}
```

**422 Unprocessable Entity** (Invalid options):
```json
{
  "detail": "font_size must be between 9 and 14"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/exports/pdf \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "990e8400-e29b-41d4-a716-446655440004",
    "template": "modern",
    "options": {
      "accent_color": "#2563EB",
      "font_size": 11
    }
  }'
```

---

### 2. Export to DOCX

Export a generated document to Microsoft Word DOCX format.

**Endpoint**: `POST /api/v1/exports/docx`

**Authentication**: Required

**Request Body**:
```json
{
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "template": "classic",
  "options": {
    "font_family": "Times New Roman",
    "font_size": 12,
    "include_comments": true,
    "editable_fields": ["contact_info", "professional_summary"]
  },
  "filename": "John_Doe_Resume_TechCorp.docx"
}
```

**Additional DOCX Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `include_comments` | boolean | false | Add editing suggestions as Word comments |
| `editable_fields` | array | [] | Mark specific sections as editable (highlighting) |
| `enable_track_changes` | boolean | false | Enable Track Changes mode |
| `document_properties` | object | {} | Author, title, subject metadata |

**Success Response** (201 Created):
```json
{
  "export_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "document_type": "resume",
  "format": "docx",
  "template": "classic",
  "filename": "John_Doe_Resume_TechCorp.docx",
  "file_size_bytes": 45218,
  "download_url": "/api/v1/exports/files/cc0e8400-e29b-41d4-a716-446655440007/download",
  "expires_at": "2025-12-15T10:30:00Z",
  "created_at": "2025-11-15T10:30:00Z",
  "metadata": {
    "word_count": 487,
    "editable_sections": ["contact_info", "professional_summary"]
  }
}
```

**DOCX Benefits**:
- ✅ Fully editable in Microsoft Word
- ✅ Compatible with Google Docs
- ✅ Track changes support
- ✅ Comments for suggested edits
- ✅ Custom document properties

---

### 3. Batch Export

Export multiple generations at once (useful for exporting resume + cover letter for same job).

**Endpoint**: `POST /api/v1/exports/batch`

**Authentication**: Required

**Request Body**:
```json
{
  "exports": [
    {
      "generation_id": "990e8400-e29b-41d4-a716-446655440004",
      "format": "pdf",
      "template": "modern",
      "filename": "John_Doe_Resume_TechCorp.pdf"
    },
    {
      "generation_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "format": "pdf",
      "template": "modern",
      "filename": "John_Doe_CoverLetter_TechCorp.pdf"
    }
  ],
  "create_zip": true,
  "zip_filename": "TechCorp_Application_Package.zip"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `exports` | array | Yes | List of export requests (max 10) |
| `create_zip` | boolean | No | Combine all files into ZIP |
| `zip_filename` | string | No | Custom ZIP filename |

**Success Response** (201 Created):
```json
{
  "batch_id": "dd0e8400-e29b-41d4-a716-446655440008",
  "total_exports": 2,
  "successful": 2,
  "failed": 0,
  "exports": [
    {
      "export_id": "ee0e8400-e29b-41d4-a716-446655440009",
      "generation_id": "990e8400-e29b-41d4-a716-446655440004",
      "status": "completed",
      "filename": "John_Doe_Resume_TechCorp.pdf",
      "file_size_bytes": 87432
    },
    {
      "export_id": "ff0e8400-e29b-41d4-a716-44665544000a",
      "generation_id": "aa0e8400-e29b-41d4-a716-446655440005",
      "status": "completed",
      "filename": "John_Doe_CoverLetter_TechCorp.pdf",
      "file_size_bytes": 52341
    }
  ],
  "zip_file": {
    "export_id": "gg0e8400-e29b-41d4-a716-44665544000b",
    "filename": "TechCorp_Application_Package.zip",
    "file_size_bytes": 138456,
    "download_url": "/api/v1/exports/files/gg0e8400-e29b-41d4-a716-44665544000b/download"
  },
  "created_at": "2025-11-15T10:35:00Z"
}
```

**Use Cases**:
- Export resume + cover letter for job application
- Export multiple resume versions (different job roles)
- Create application package with all materials

---

## Template Management Endpoints

### 4. List Available Templates

Retrieve all available export templates with previews.

**Endpoint**: `GET /api/v1/exports/templates`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "templates": [
    {
      "id": "modern",
      "name": "Modern",
      "description": "Clean, minimalist design with accent colors",
      "best_for": ["Tech", "Startups", "Creative Industries"],
      "ats_score": 85,
      "preview_url": "/api/v1/exports/templates/modern/preview.png",
      "features": [
        "Two-column layout",
        "Accent color headers",
        "Sans-serif fonts",
        "Clean section dividers"
      ],
      "customizable_options": [
        "accent_color",
        "font_family",
        "font_size",
        "line_spacing"
      ]
    },
    {
      "id": "classic",
      "name": "Classic",
      "description": "Traditional, conservative format",
      "best_for": ["Corporate", "Finance", "Legal"],
      "ats_score": 95,
      "preview_url": "/api/v1/exports/templates/classic/preview.png",
      "features": [
        "Single-column layout",
        "Serif fonts",
        "Black & white only",
        "Traditional spacing"
      ],
      "customizable_options": [
        "font_family",
        "font_size",
        "margins"
      ]
    },
    {
      "id": "creative",
      "name": "Creative",
      "description": "Bold, visually striking design",
      "best_for": ["Design", "Marketing", "Media"],
      "ats_score": 75,
      "preview_url": "/api/v1/exports/templates/creative/preview.png",
      "features": [
        "Sidebar layout",
        "Multiple color accents",
        "Mixed fonts",
        "Visual separators"
      ],
      "customizable_options": [
        "primary_color",
        "secondary_color",
        "font_family",
        "sidebar_width"
      ]
    },
    {
      "id": "ats-optimized",
      "name": "ATS-Optimized",
      "description": "Maximum parsability for Applicant Tracking Systems",
      "best_for": ["Enterprise", "Government", "Large Corporations"],
      "ats_score": 98,
      "preview_url": "/api/v1/exports/templates/ats-optimized/preview.png",
      "features": [
        "Single-column layout",
        "No tables or columns",
        "Text-based only",
        "Clear section headers",
        "Maximum white space"
      ],
      "customizable_options": [
        "font_family",
        "font_size"
      ]
    }
  ],
  "total": 4
}
```

---

### 5. Get Template Details

Get detailed information about a specific template.

**Endpoint**: `GET /api/v1/exports/templates/{template_id}`

**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": "modern",
  "name": "Modern",
  "description": "Clean, minimalist design with accent colors",
  "version": "1.0",
  "ats_score": 85,
  "preview_url": "/api/v1/exports/templates/modern/preview.png",
  "sample_pdf_url": "/api/v1/exports/templates/modern/sample.pdf",
  "features": {
    "layout": "two-column",
    "fonts": ["Helvetica", "Arial"],
    "colors": ["Custom accent color", "Black text"],
    "sections": [
      "Contact Info (header)",
      "Professional Summary",
      "Work Experience",
      "Education",
      "Skills (sidebar)",
      "Projects"
    ]
  },
  "default_options": {
    "font_family": "Helvetica",
    "font_size": 11,
    "accent_color": "#2563EB",
    "line_spacing": 1.15,
    "margins": {
      "top": 0.75,
      "bottom": 0.75,
      "left": 0.75,
      "right": 0.75
    }
  },
  "option_constraints": {
    "font_family": ["Helvetica", "Arial", "Calibri"],
    "font_size": {"min": 9, "max": 14},
    "accent_color": "Hex color code",
    "line_spacing": {"min": 1.0, "max": 2.0}
  }
}
```

---

### 6. Preview Document with Template

Generate a preview image showing how content will look with a template.

**Endpoint**: `POST /api/v1/exports/preview`

**Authentication**: Required

**Request Body**:
```json
{
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "template": "modern",
  "options": {
    "accent_color": "#DC2626",
    "font_size": 12
  }
}
```

**Success Response** (200 OK):
```json
{
  "preview_id": "hh0e8400-e29b-41d4-a716-44665544000c",
  "generation_id": "990e8400-e29b-41d4-a716-446655440004",
  "template": "modern",
  "preview_url": "/api/v1/exports/previews/hh0e8400-e29b-41d4-a716-44665544000c.png",
  "preview_format": "png",
  "expires_at": "2025-11-15T11:30:00Z",
  "created_at": "2025-11-15T10:30:00Z"
}
```

**Preview Features**:
- PNG image (1200x1557 pixels, 8.5x11" at 150 DPI)
- First page only for multi-page documents
- Watermark: "PREVIEW" (removed in actual export)
- Expires after 1 hour

---

## File Management Endpoints

### 7. List Exported Files

Retrieve all exported files for the user.

**Endpoint**: `GET /api/v1/exports/files`

**Authentication**: Required

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `format` | string | - | Filter by format (pdf/docx/zip) |
| `document_type` | string | - | Filter by type (resume/cover_letter) |
| `template` | string | - | Filter by template |
| `limit` | integer | 20 | Results per page (1-100) |
| `offset` | integer | 0 | Results offset |

**Success Response** (200 OK):
```json
{
  "files": [
    {
      "export_id": "bb0e8400-e29b-41d4-a716-446655440006",
      "generation_id": "990e8400-e29b-41d4-a716-446655440004",
      "document_type": "resume",
      "format": "pdf",
      "template": "modern",
      "filename": "John_Doe_Resume_TechCorp_2025.pdf",
      "file_size_bytes": 87432,
      "page_count": 2,
      "download_url": "/api/v1/exports/files/bb0e8400-e29b-41d4-a716-446655440006/download",
      "expires_at": "2025-12-15T10:30:00Z",
      "created_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 15,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 15,
    "hasMore": false
  },
  "storage_used_bytes": 1245678,
  "storage_limit_bytes": 104857600
}
```

**Storage Limits**:
- Free tier: 100 MB
- Pro tier: 1 GB
- Files auto-delete after 30 days

---

### 8. Download Exported File

Download an exported PDF/DOCX file.

**Endpoint**: `GET /api/v1/exports/files/{export_id}/download`

**Authentication**: Required

**Path Parameters**:
- `export_id` (UUID): Export unique identifier

**Success Response** (200 OK):
- **Content-Type**: `application/pdf` or `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Content-Disposition**: `attachment; filename="John_Doe_Resume_TechCorp_2025.pdf"`
- **Body**: Binary file content

**Example cURL**:
```bash
curl -X GET http://localhost:8000/api/v1/exports/files/bb0e8400-e29b-41d4-a716-446655440006/download \
  -H "Authorization: Bearer <token>" \
  -o resume.pdf
```

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Export file not found or has expired"
}
```

**410 Gone** (File expired):
```json
{
  "detail": "Export file has expired and been deleted"
}
```

---

### 9. Delete Exported File

Delete an exported file to free up storage.

**Endpoint**: `DELETE /api/v1/exports/files/{export_id}`

**Authentication**: Required

**Success Response** (204 No Content): No body

**Error Responses**:

**404 Not Found**:
```json
{
  "detail": "Export file not found"
}
```

---

## Database Schema

### exports Table

```sql
CREATE TABLE exports (
    id VARCHAR PRIMARY KEY,  -- UUID
    user_id INTEGER NOT NULL,
    generation_id VARCHAR NOT NULL,
    document_type VARCHAR NOT NULL,  -- 'resume' or 'cover_letter'
    format VARCHAR NOT NULL,  -- 'pdf', 'docx', 'zip'
    template VARCHAR NOT NULL,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    page_count INTEGER,  -- PDF only
    options TEXT,  -- JSON
    metadata TEXT,  -- JSON (ATS score, processing time, etc.)
    download_count INTEGER DEFAULT 0,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (generation_id) REFERENCES generations(id) ON DELETE CASCADE
);

CREATE INDEX idx_exports_user_id ON exports(user_id);
CREATE INDEX idx_exports_generation_id ON exports(generation_id);
CREATE INDEX idx_exports_expires_at ON exports(expires_at);
```

---

## Implementation Technologies

### PDF Generation
**Recommended Library**: WeasyPrint or ReportLab

**WeasyPrint** (Recommended):
- HTML/CSS to PDF conversion
- Excellent typography
- CSS Paged Media support
- Easy styling with templates

```python
from weasyprint import HTML, CSS

def generate_pdf(html_content, css_styles, output_path):
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_styles)]
    )
```

**Alternative: ReportLab**:
- Low-level PDF generation
- More control over layout
- Steeper learning curve

### DOCX Generation
**Recommended Library**: python-docx

```python
from docx import Document
from docx.shared import Pt, RGBColor

def generate_docx(content, template_options, output_path):
    doc = Document()
    # Add content with formatting
    doc.save(output_path)
```

### S3 Storage Model

JobWise uses **Amazon S3 as the only storage backend** for exported files in **all environments** (development, staging, production). The local filesystem is not used for persistent storage.

**Buckets**:
- One S3 bucket per environment is recommended, for example:
  - `jobwise-exports-dev`
  - `jobwise-exports-prod`

**Object Keys**:
- Every exported file is stored under a deterministic key and tracked in the `exports` table:
  - Pattern: `exports/{user_id}/{export_id}.{ext}`
  - Example: `exports/1/bb0e8400-e29b-41d4-a716-446655440006.pdf`
- The `exports.file_path` column always stores this **S3 object key** (never a local path).

**Write Flow (PDF/DOCX/ZIP)**:
1. Generate a new `export_id` (UUID) for each export.
2. Build the S3 key using the pattern above.
3. Render the document bytes (PDF/DOCX/ZIP) in memory.
4. Call `PutObject` to upload the bytes to the configured S3 bucket.
5. Insert a new row into `exports` with:
   - `id = export_id`
   - `user_id`, `generation_id`, `document_type`, `format`, `template`, `filename`
   - `file_path =` S3 object key
   - `file_size_bytes`, `page_count` (for PDFs), `options`, `metadata`
   - `expires_at` (e.g., 30 days from creation)

**Read/Download Flow**:
1. Client calls `GET /api/v1/exports/files/{export_id}/download`.
2. Backend looks up the `exports` row by `id` and verifies:
   - The row exists and belongs to the authenticated user (`user_id`).
   - `expires_at` is in the future.
3. Backend fetches the S3 object by `file_path` and either:
   - Streams the file content through the API response, or
   - Generates a short-lived pre-signed S3 URL and redirects the client.
4. The mobile app always uses the backend download URL; it never talks to S3 directly.

**Delete Flow**:
1. Client calls `DELETE /api/v1/exports/files/{export_id}`.
2. Backend validates ownership and existence.
3. Backend deletes the S3 object at `file_path` and then deletes the `exports` row.

**Automatic Expiration & Cleanup**:
- A scheduled job (cron, Celery beat, or background task) periodically:
  1. Finds exports where `expires_at < NOW()`.
  2. Deletes corresponding S3 objects.
  3. Deletes the `exports` rows.
- This enforces storage quotas and the documented auto-delete behavior.

**Required Configuration**:
- **Environment Variables** (example names):
  - `S3_EXPORTS_BUCKET` – bucket name (e.g., `jobwise-exports-dev`).
  - `S3_EXPORTS_REGION` – AWS region (e.g., `us-west-2`).
  - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` – or use an IAM role when running on AWS.
- **IAM Permissions** for the backend service principal:
  - `s3:PutObject` on `arn:aws:s3:::${S3_EXPORTS_BUCKET}/exports/*`
  - `s3:GetObject` on `arn:aws:s3:::${S3_EXPORTS_BUCKET}/exports/*`
  - `s3:DeleteObject` on `arn:aws:s3:::${S3_EXPORTS_BUCKET}/exports/*`
  - Optionally `s3:ListBucket` for debugging/ops.

**Security Notes**:
- Exported files are **never** publicly readable from S3; access is always mediated by the backend.
- If pre-signed URLs are used, they should:
  - Have short expirations (e.g., 5–15 minutes).
  - Be generated only after verifying `user_id` ownership and `expires_at`.
- `exports.file_path` must not be exposed directly to clients.

---

## Complete Workflow Example

### Export Resume to PDF with Custom Template

```bash
# 1. List available templates
curl -X GET http://localhost:8000/api/v1/exports/templates \
  -H "Authorization: Bearer <token>"

# 2. Preview with template (optional)
curl -X POST http://localhost:8000/api/v1/exports/preview \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "990e8400-e29b-41d4-a716-446655440004",
    "template": "modern",
    "options": {
      "accent_color": "#DC2626",
      "font_size": 11
    }
  }'

# 3. Export to PDF
curl -X POST http://localhost:8000/api/v1/exports/pdf \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "990e8400-e29b-41d4-a716-446655440004",
    "template": "modern",
    "options": {
      "accent_color": "#DC2626",
      "font_size": 11,
      "line_spacing": 1.2
    },
    "filename": "John_Doe_Resume_TechCorp.pdf"
  }'

# 4. Download PDF
curl -X GET http://localhost:8000/api/v1/exports/files/{export_id}/download \
  -H "Authorization: Bearer <token>" \
  -o resume.pdf
```

### Batch Export Application Package

```bash
curl -X POST http://localhost:8000/api/v1/exports/batch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "exports": [
      {
        "generation_id": "resume_generation_id",
        "format": "pdf",
        "template": "modern"
      },
      {
        "generation_id": "cover_letter_generation_id",
        "format": "pdf",
        "template": "modern"
      }
    ],
    "create_zip": true,
    "zip_filename": "TechCorp_Application_Package.zip"
  }'
```

---

## Best Practices

### 1. Template Selection

**For Maximum ATS Compatibility**:
- ✅ Use `ats-optimized` template (98% score)
- ✅ Avoid creative templates for large corporations
- ✅ Test with ATS checkers before applying

**For Visual Appeal**:
- Use `modern` for tech/startup roles
- Use `creative` for design/marketing roles
- Balance aesthetics with parsability

### 2. File Management

**Storage Optimization**:
- Delete old exports regularly
- Use batch export to reduce file count
- Download and store locally for important applications

**File Naming**:
- Include job title and company: `John_Doe_Resume_TechCorp.pdf`
- Use underscores, not spaces
- Add date for version control: `Resume_2025_11_15.pdf`

### 3. Customization

**Font Selection**:
- **Tech/Modern**: Helvetica, Arial, Calibri
- **Corporate/Traditional**: Times New Roman, Georgia
- **ATS-Friendly**: Arial, Calibri (avoid decorative fonts)

**Color Usage**:
- Use sparingly (headers only)
- Ensure high contrast (dark on light)
- Test printability (grayscale)

### 4. Format Selection

**PDF**:
- ✅ Universal compatibility
- ✅ Preserves exact formatting
- ✅ Smaller file size
- ❌ Not editable

**DOCX**:
- ✅ Editable in Word/Google Docs
- ✅ Easy last-minute changes
- ✅ Track changes support
- ❌ May render differently across platforms

---

## Rate Limiting

| Operation | Limit | Window |
|-----------|-------|--------|
| PDF Export | 50 exports | per hour |
| DOCX Export | 50 exports | per hour |
| Batch Export | 10 batches | per hour |
| Template Preview | 100 previews | per hour |
| File Download | Unlimited | - |

---

## Future Enhancements

- [ ] HTML export for web portfolios
- [ ] LaTeX export for academic resumes
- [ ] Custom template builder (drag-and-drop)
- [ ] Template marketplace (user-created)
- [ ] Email export (send to recruiter directly)
- [ ] LinkedIn profile export
- [ ] Multi-language support
- [ ] Accessibility compliance (WCAG 2.1)
- [ ] Version comparison (diff tool)
- [ ] Collaborative editing

---

**Last Updated**: December 2025
**API Version**: 1.0
**Total Endpoints**: 9
**Status**: Design Complete - Ready for Implementation
**Required Libraries**: 
- **WeasyPrint** 62.3+ (HTML/CSS → PDF rendering)
- **python-docx** 1.1.0+ (DOCX generation)
- **Jinja2** 3.1.2+ (Template engine)
- **boto3** 1.34+ (S3 uploads)

**Template System**:
- **Format**: HTML/CSS templates with Jinja2 templating
- **Location**: `backend/app/infrastructure/templates/export/`
- **Templates**: `modern.html`, `classic.html`, `creative.html`, `ats-optimized.html`
- **Rendering**: Structured JSON → Jinja2 → HTML → WeasyPrint → PDF

**Structured Content Schema** (stored in `generations.content_structured`):
```json
{
  "header": {
    "name": "string",
    "title": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "linkedin": "string",
    "github": "string",
    "website": "string"
  },
  "sections": [
    {
      "type": "professional_summary",
      "content": "string"
    },
    {
      "type": "skills",
      "categories": [
        {
          "name": "Technical Skills",
          "items": ["Python", "JavaScript", "AWS"]
        },
        {
          "name": "Soft Skills",
          "items": ["Leadership", "Communication", "Problem Solving"]
        },
        {
          "name": "Languages",
          "items": [
            {"name": "English", "proficiency": "native"},
            {"name": "Spanish", "proficiency": "conversational"}
          ]
        },
        {
          "name": "Certifications",
          "items": [
            {
              "name": "AWS Certified Solutions Architect",
              "issuer": "Amazon Web Services",
              "date_obtained": "2024-03-15",
              "expiry_date": "2027-03-15",
              "credential_id": "AWS-12345"
            }
          ]
        }
      ]
    },
    {
      "type": "experience",
      "entries": [
        {
          "id": "uuid",
          "title": "string",
          "company": "string",
          "location": "string",
          "start_date": "string",
          "end_date": "string | null",
          "is_current": "boolean",
          "description": "string",
          "bullets": ["string"],
          "achievements": ["string"]
        }
      ]
    },
    {
      "type": "projects",
      "entries": [
        {
          "id": "uuid",
          "name": "string",
          "description": "string",
          "technologies": ["string"],
          "url": "string | null",
          "start_date": "string | null",
          "end_date": "string | null"
        }
      ]
    },
    {
      "type": "education",
      "entries": [
        {
          "id": "uuid",
          "degree": "string",
          "field_of_study": "string",
          "institution": "string",
          "start_date": "string",
          "end_date": "string | null",
          "gpa": "float | null",
          "honors": ["string"]
        }
      ]
    }
  ],
  "metadata": {
    "total_years_experience": "int",
    "top_skills": ["string"],
    "industries": ["string"],
    "total_projects": "int",
    "total_certifications": "int"
  }
}
```
