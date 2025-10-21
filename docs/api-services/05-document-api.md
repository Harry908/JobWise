# Document API Service

**Version**: 1.0
**Base Path**: `/api/v1/documents`
**Status**: Sprint 2 (In Development)

## Service Overview

Manages generated documents (resumes and cover letters) with storage, retrieval, and PDF download capabilities. Documents are created by the Generation API and accessed by users for download and sharing.

## Specification

**Purpose**: Document storage and retrieval
**Authentication**: Required (JWT)
**Authorization**: Users can only access their own documents
**File Storage**: Local filesystem (dev), S3 (prod)
**PDF Generation**: ReportLab library
**Performance**: <2s for PDF export

## Dependencies

### Internal
- Authentication API: User identity
- Generation API: Document creation
- Database: DocumentModel
- Storage Service: File storage (via IStorageService port)
- PDF Service: PDF generation (via IPDFGenerator port)

### External
- ReportLab: PDF generation library
- AWS S3: File storage (production)

## Data Flow

```
Document Lifecycle:

1. Generation API creates document after generation completes
   - Stores content (text, HTML, markdown)
   - Generates PDF
   - Saves to storage (local or S3)
   - Creates DocumentModel record

2. Client → GET /documents?job_id={job_id}
   - API validates JWT → get user_id
   - API fetches documents where user_id = current_user.id
   - API applies filters
   - API ← Document list

3. Client → GET /documents/{id}
   - API validates JWT
   - API fetches document by id
   - API verifies ownership
   - API ← Document details (content + metadata)

4. Client → GET /documents/{id}/download
   - API validates JWT
   - API fetches document by id
   - API verifies ownership
   - API reads PDF from storage
   - API ← PDF binary with headers

5. Client → DELETE /documents/{id}
   - API validates JWT
   - API verifies ownership
   - API deletes file from storage
   - API deletes DocumentModel record
   - API ← 204 No Content
```

## API Contract

### GET /documents

**Description**: List user's generated documents

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `document_type`: string (resume, cover_letter)
- `job_id`: string - filter by job
- `profile_id`: string - filter by profile
- `created_after`: string (ISO 8601 date-time)
- `limit`: integer (1-100, default: 20)
- `offset`: integer (default: 0)

**Response** (200 OK):
```json
{
  "documents": [
    {
      "id": "doc-uuid",
      "document_type": "resume",
      "title": "Senior Python Developer - TechCorp Resume",
      "job_title": "Senior Python Developer",
      "company": "TechCorp Inc",
      "ats_score": 0.87,
      "created_at": "2025-10-21T10:30:05Z",
      "pdf_url": "/api/v1/documents/doc-uuid/download"
    }
  ],
  "pagination": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_next": false,
    "has_previous": false
  },
  "statistics": {
    "total_documents": 15,
    "resumes": 12,
    "cover_letters": 3,
    "average_ats_score": 0.84
  }
}
```

### GET /documents/{id}

**Description**: Get document details with full content

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": "doc-uuid",
  "document_type": "resume",
  "title": "Senior Python Developer - TechCorp Resume",
  "content": {
    "text": "John Doe\nSoftware Engineer\n\nPROFESSIONAL SUMMARY\nExperienced software engineer with 5+ years...\n\nEXPERIENCE\nSenior Software Engineer\nTech Corp | Seattle, WA | Jan 2021 - Present\n- Lead development of microservices...",
    "html": "<html><head><style>...</style></head><body><div class='resume'>...</div></body></html>",
    "markdown": "# John Doe\n## Software Engineer\n\n### PROFESSIONAL SUMMARY\nExperienced software engineer..."
  },
  "metadata": {
    "generation_id": "gen-uuid",
    "profile_id": "profile-uuid",
    "job_id": "job-uuid",
    "job_title": "Senior Python Developer",
    "company": "TechCorp Inc",
    "template": "modern",
    "ats_score": 0.87,
    "match_percentage": 82,
    "keyword_coverage": 0.91,
    "keywords_matched": 15,
    "keywords_total": 18,
    "tokens_used": 7850,
    "generation_time": 5.2
  },
  "pdf": {
    "url": "/api/v1/documents/doc-uuid/download",
    "size_bytes": 245678,
    "page_count": 1,
    "created_at": "2025-10-21T10:30:05Z"
  },
  "version": 1,
  "created_at": "2025-10-21T10:30:05Z",
  "updated_at": "2025-10-21T10:30:05Z"
}
```

**Errors**:
- 404: Document not found
- 403: Not authorized

### GET /documents/{id}/download

**Description**: Download document as PDF file

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="John_Doe_Resume_TechCorp.pdf"`
- Body: PDF binary data

**Errors**:
- 404: Document or PDF file not found
- 403: Not authorized

### DELETE /documents/{id}

**Description**: Delete document and associated PDF file

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

**Errors**:
- 404: Document not found
- 403: Not authorized

### PUT /documents/{id}

**Description**: Update document metadata (title, notes)

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "title": "Updated Resume Title",
  "notes": "Final version for TechCorp application"
}
```

**Response** (200 OK): Updated document object

**Errors**:
- 400: Validation error
- 404: Document not found
- 403: Not authorized

### POST /documents/{id}/export

**Description**: Re-export document to different format (future)

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "format": "docx",
  "template": "classic"
}
```

**Response** (200 OK):
```json
{
  "export_id": "export-uuid",
  "format": "docx",
  "download_url": "/api/v1/documents/doc-uuid/export/export-uuid/download",
  "created_at": "2025-10-21T11:00:00Z"
}
```

### GET /documents/export-formats

**Description**: List available export formats

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "formats": [
    {
      "id": "pdf",
      "name": "PDF",
      "description": "Portable Document Format",
      "supported": true
    },
    {
      "id": "docx",
      "name": "Word Document",
      "description": "Microsoft Word format",
      "supported": false
    },
    {
      "id": "txt",
      "name": "Plain Text",
      "description": "Plain text format",
      "supported": true
    }
  ]
}
```

## Mobile Integration Notes

### Document Model
```dart
class Document {
  final String id;
  final DocumentType documentType;
  final String title;
  final DocumentContent content;
  final DocumentMetadata metadata;
  final PDFInfo pdf;
  final int version;
  final DateTime createdAt;
  final DateTime updatedAt;

  Document({
    required this.id,
    required this.documentType,
    required this.title,
    required this.content,
    required this.metadata,
    required this.pdf,
    required this.version,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Document.fromJson(Map<String, dynamic> json) {
    return Document(
      id: json['id'],
      documentType: DocumentType.values.firstWhere(
        (e) => e.name == json['document_type'],
      ),
      title: json['title'],
      content: DocumentContent.fromJson(json['content']),
      metadata: DocumentMetadata.fromJson(json['metadata']),
      pdf: PDFInfo.fromJson(json['pdf']),
      version: json['version'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}

enum DocumentType { resume, coverLetter }

class DocumentContent {
  final String text;
  final String? html;
  final String? markdown;

  DocumentContent({
    required this.text,
    this.html,
    this.markdown,
  });

  factory DocumentContent.fromJson(Map<String, dynamic> json) =>
      DocumentContent(
        text: json['text'],
        html: json['html'],
        markdown: json['markdown'],
      );
}

class DocumentMetadata {
  final String generationId;
  final String profileId;
  final String jobId;
  final String jobTitle;
  final String company;
  final String template;
  final double atsScore;
  final int matchPercentage;
  final double keywordCoverage;
  final int keywordsMatched;
  final int keywordsTotal;

  DocumentMetadata({
    required this.generationId,
    required this.profileId,
    required this.jobId,
    required this.jobTitle,
    required this.company,
    required this.template,
    required this.atsScore,
    required this.matchPercentage,
    required this.keywordCoverage,
    required this.keywordsMatched,
    required this.keywordsTotal,
  });

  factory DocumentMetadata.fromJson(Map<String, dynamic> json) =>
      DocumentMetadata(
        generationId: json['generation_id'],
        profileId: json['profile_id'],
        jobId: json['job_id'],
        jobTitle: json['job_title'],
        company: json['company'],
        template: json['template'],
        atsScore: json['ats_score'].toDouble(),
        matchPercentage: json['match_percentage'],
        keywordCoverage: json['keyword_coverage'].toDouble(),
        keywordsMatched: json['keywords_matched'],
        keywordsTotal: json['keywords_total'],
      );
}

class PDFInfo {
  final String url;
  final int sizeBytes;
  final int pageCount;

  PDFInfo({
    required this.url,
    required this.sizeBytes,
    required this.pageCount,
  });

  factory PDFInfo.fromJson(Map<String, dynamic> json) => PDFInfo(
        url: json['url'],
        sizeBytes: json['size_bytes'],
        pageCount: json['page_count'],
      );

  String get sizeFormatted {
    if (sizeBytes < 1024) return '$sizeBytes B';
    if (sizeBytes < 1024 * 1024) return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    return '${(sizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}
```

### Document Service
```dart
class DocumentService {
  final ApiClient _client;

  Future<List<Document>> getDocuments({
    DocumentType? documentType,
    String? jobId,
    String? profileId,
    DateTime? createdAfter,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/documents', queryParameters: {
      if (documentType != null) 'document_type': documentType.name,
      if (jobId != null) 'job_id': jobId,
      if (profileId != null) 'profile_id': profileId,
      if (createdAfter != null) 'created_after': createdAfter.toIso8601String(),
      'limit': limit,
      'offset': offset,
    });
    return (response.data['documents'] as List)
        .map((json) => Document.fromJson(json))
        .toList();
  }

  Future<Document> getDocument(String id) async {
    final response = await _client.get('/documents/$id');
    return Document.fromJson(response.data);
  }

  Future<void> deleteDocument(String id) async {
    await _client.delete('/documents/$id');
  }

  Future<String> getDownloadUrl(String id) async {
    final baseUrl = _client.dio.options.baseUrl;
    return '$baseUrl/documents/$id/download';
  }

  Future<Uint8List> downloadPDF(String id) async {
    final response = await _client.dio.get(
      '/documents/$id/download',
      options: Options(responseType: ResponseType.bytes),
    );
    return Uint8List.fromList(response.data);
  }
}
```

### PDF Download and Viewing
```dart
import 'package:flutter_downloader/flutter_downloader.dart';
import 'package:open_file/open_file.dart';
import 'package:path_provider/path_provider.dart';

class DocumentViewer extends StatelessWidget {
  final Document document;

  Future<void> downloadAndView() async {
    try {
      // Show loading
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 16),
              Text('Downloading...'),
            ],
          ),
        ),
      );

      // Download PDF
      final pdfBytes = await documentService.downloadPDF(document.id);

      // Save to temp directory
      final tempDir = await getTemporaryDirectory();
      final fileName = '${document.title.replaceAll(' ', '_')}.pdf';
      final filePath = '${tempDir.path}/$fileName';
      final file = File(filePath);
      await file.writeAsBytes(pdfBytes);

      // Close loading dialog
      Navigator.pop(context);

      // Open PDF
      await OpenFile.open(filePath);
    } catch (e) {
      Navigator.pop(context); // Close loading
      showErrorDialog('Failed to download PDF: $e');
    }
  }

  Future<void> sharePDF() async {
    final pdfBytes = await documentService.downloadPDF(document.id);
    final tempDir = await getTemporaryDirectory();
    final fileName = '${document.title.replaceAll(' ', '_')}.pdf';
    final filePath = '${tempDir.path}/$fileName';
    final file = File(filePath);
    await file.writeAsBytes(pdfBytes);

    await Share.shareFiles([filePath], text: document.title);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(document.title),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: sharePDF,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Metadata
            MetadataCard(
              jobTitle: document.metadata.jobTitle,
              company: document.metadata.company,
              atsScore: document.metadata.atsScore,
              matchPercentage: document.metadata.matchPercentage,
            ),
            SizedBox(height: 16),
            // PDF Info
            PDFInfoCard(
              sizeBytes: document.pdf.sizeBytes,
              pageCount: document.pdf.pageCount,
            ),
            SizedBox(height: 16),
            // Actions
            ElevatedButton.icon(
              onPressed: downloadAndView,
              icon: Icon(Icons.download),
              label: Text('Download & View PDF'),
            ),
            SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: () => _showContentPreview(document.content.text),
              icon: Icon(Icons.visibility),
              label: Text('Preview Text'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Document List UI
```dart
class DocumentListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('My Documents')),
      body: FutureBuilder<List<Document>>(
        future: documentService.getDocuments(),
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return Center(child: CircularProgressIndicator());
          }

          final documents = snapshot.data!;

          if (documents.isEmpty) {
            return EmptyState(
              icon: Icons.description,
              message: 'No documents yet',
              action: 'Generate your first resume',
            );
          }

          return ListView.builder(
            itemCount: documents.length,
            itemBuilder: (context, index) {
              final doc = documents[index];
              return DocumentListTile(
                document: doc,
                onTap: () => Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => DocumentViewer(document: doc),
                  ),
                ),
                onDelete: () => _deleteDocument(doc),
              );
            },
          );
        },
      ),
    );
  }

  Future<void> _deleteDocument(Document doc) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Delete Document?'),
        content: Text('This cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Delete'),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await documentService.deleteDocument(doc.id);
      setState(() {}); // Refresh list
    }
  }
}
```

### Local Caching
Consider caching documents:
- Store document metadata locally
- Cache PDF files for offline viewing
- Show cached indicator in UI
- Auto-sync on network availability

### PDF Viewer Integration
Use packages:
- `flutter_pdfview`: Native PDF viewer
- `syncfusion_flutter_pdfviewer`: Advanced PDF viewing
- `open_file`: Open with system PDF viewer

## Implementation Notes

### Repository
- `app/infrastructure/repositories/document_repository.py`
- Methods: `create()`, `get_by_id()`, `get_user_documents()`, `update()`, `delete()`

### Services
- `app/application/services/document_service.py` - Document management
- `app/infrastructure/adapters/pdf/reportlab_adapter.py` - PDF generation
- `app/infrastructure/adapters/storage/local_file_adapter.py` - File storage

### PDF Generation
- ReportLab library for PDF creation
- Templates: Modern, Classic, Creative
- ATS-friendly formatting
- 1-page default (configurable)

### File Storage
- Development: Local filesystem (`backend/generated_documents/`)
- Production: AWS S3 with signed URLs
- Naming convention: `{user_id}/{document_id}.pdf`
- Automatic cleanup on document delete

### Performance
- PDF generation: <2s target
- Download streaming for large files
- Caching headers for repeated downloads

### Security
- Verify ownership before download
- Signed URLs for S3 (production)
- Rate limiting on downloads (future)
- No public access to PDF files

### Testing
- Test document CRUD
- Test PDF generation
- Test file storage/retrieval
- Test ownership verification
- Test PDF download headers
- Mock storage adapter for tests
