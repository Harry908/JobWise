# Document Export API

**Version**: 1.0
**Base Path**: `/api/v1/exports`
**Status**: 🔄 Planned (Design Complete)

---

## Overview

The Document Export API converts generated resume and cover letter text into professionally formatted PDF and DOCX files. It provides multiple templates, customization options, and file management capabilities.

**Key Features**:
- **PDF Export**: High-quality PDF generation with ATS-friendly formatting
- **DOCX Export**: Editable Microsoft Word documents
- **Multiple Templates**: Modern, Classic, Creative, ATS-Optimized
- **Customization**: Fonts, colors, spacing, margins
- **Batch Export**: Export multiple generations at once
- **File Management**: Download, list, and delete exported files
- **Template Preview**: See how content looks before exporting

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
5. Save file to storage (`uploads/{user_id}/exports/`)
6. Return download URL and metadata

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

### File Storage
**Options**:
1. **Local Filesystem**: `uploads/{user_id}/exports/`
2. **S3/Cloud Storage**: For production scalability
3. **Temporary Storage**: Auto-cleanup after 30 days

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

**Last Updated**: November 2025
**API Version**: 1.0
**Total Endpoints**: 9
**Status**: Design Complete - Ready for Implementation
**Recommended Libraries**: WeasyPrint (PDF), python-docx (DOCX)
