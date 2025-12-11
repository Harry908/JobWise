# Document Export Feature

**At a Glance (For AI Agents)**
- **Feature Name**: Document Export (Flutter front-end)
- **Primary Role**: Let users choose templates, customize options, call export APIs, and manage/download S3-backed files.
- **Key Files**: `lib/providers/exports/exports_notifier.dart`, `lib/providers/exports/exports_state.dart`, `lib/services/api/exports_api_client.dart`, `lib/models/exported_file.dart`, `lib/models/template.dart`
- **Backend Contract**: `../api-services/05-document-export-api.md` (PDF/DOCX/ZIP + S3-only storage)
- **Main Screens**: `TemplateSelectionScreen`, `ExportOptionsScreen`, `ExportedFilesScreen`

**Related Docs (Navigation Hints)**
- Backend Export API: `../api-services/05-document-export-api.md`
- Mobile Generation Feature: `04-generation-feature.md`, `04b-ai-generation-feature.md` (sources for `generation_id`)
- Backend architecture: `../BACKEND_ARCHITECTURE_OVERVIEW.md` (S3 storage model)

**Key Field / Property Semantics**
- `ExportedFile.exportId` ↔ backend `export_id`: Used for download/delete and correlates to `exports.id`.
- `ExportedFile.generationId` ↔ `generation_id`: Foreign key to a generation; used to link export to source doc.
- `ExportedFile.format` / `template`: Must align with backend enum-like strings (`"pdf"`, `"docx"`, `"zip"`, template ids).
- `ExportedFile.downloadUrl`: Backend route or pre-signed URL wrapper; always treated as opaque by the app.
- `Template.id` / `Template.atsScore` / `Template.industries`: Mirror backend template catalog and drive filtering/UX.
- `ExportsState.storageUsedBytes` / `storageLimitBytes`: Reflect backend storage usage and free-tier limits.
- `ExportsApiClient` methods: Map directly to `/exports/pdf`, `/exports/docx`, `/exports/batch`, `/exports/templates*`, `/exports/preview`, `/exports/files*`.

**Backend API**: [Document Export API](../api-services/05-document-export-api.md)
**Base Path**: `/api/v1/exports`
**Status**: 🔄 Design Complete - Implementation Pending
**Last Updated**: December 2025
**Template System**: Jinja2 + HTML/CSS → WeasyPrint (PDF) / python-docx (DOCX)
**Content Source**: Structured JSON from backend (`generations.content_structured`)

---

## Overview

The Document Export feature converts generated resumes and cover letters from plain text to professionally formatted PDF and DOCX files using multiple ATS-optimized templates.

### User Stories

**As a user**, I want to:
- Export my generated resume to PDF with professional formatting
- Export my cover letter to DOCX for easy editing
- Choose from multiple templates optimized for different industries
- Preview templates before exporting
- Download exported files to my device
- Share exported files via email or messaging apps
- Export resume + cover letter as a package (batch export)
- See ATS compatibility scores for each template

---

## Screens

### 1. TemplateSelectionScreen

**Route**: `/export/templates`
**File**: `lib/screens/export/template_selection_screen.dart`

**Context**: User navigates here from GenerationResultScreen after tapping "Export to PDF"

**UI Components**:
- Document preview header:
  - Document type (Resume / Cover Letter)
  - Job title reference
- Template cards grid (2 columns):
  - Template preview thumbnail
  - Template name
  - ATS score badge
  - Industry tags
  - "Select" button
- Template filters:
  - All templates
  - High ATS score (90%+)
  - By industry (Tech, Corporate, Creative)

**Template Options**:

1. **Modern Template**
   - ATS Score: 85%
   - Industries: Tech, Startups, Software
   - Style: Clean, minimalist, sans-serif fonts
   - Colors: Accent color for headers

2. **Classic Template**
   - ATS Score: 95%
   - Industries: Corporate, Finance, Legal
   - Style: Traditional, serif fonts, conservative
   - Colors: Black and white only

3. **Creative Template**
   - ATS Score: 75%
   - Industries: Design, Marketing, Media
   - Style: Bold headers, creative layout
   - Colors: Customizable color schemes

4. **ATS-Optimized Template**
   - ATS Score: 98%
   - Industries: Enterprise, Government
   - Style: Ultra-simple, maximum parsability
   - Colors: Black text only, no graphics

**User Flow**:
```
1. User taps "Export to PDF" on GenerationResultScreen
2. Navigate to TemplateSelectionScreen
3. Display 4 template options with previews
4. User taps template card to preview
5. User taps "Select" → navigate to ExportOptionsScreen
```

### 2. ExportOptionsScreen

**Route**: `/export/options`
**File**: `lib/screens/export/export_options_screen.dart`

**UI Components**:
- Selected template preview
- Export format selector:
  - PDF (default)
  - DOCX
- Template customization (collapsible):
  - Font family dropdown (if supported by template)
  - Accent color picker (Modern/Creative only)
  - Line spacing slider (Normal, Tight, Relaxed)
  - Margins slider (Narrow, Normal, Wide)
- File options:
  - Custom filename text field
  - Include generation metadata toggle
- Action buttons:
  - "Preview" button (shows preview modal)
  - "Export" button (primary action)
  - "Back" button

**Customization Options**:
```dart
class ExportOptions {
  final String templateId;
  final String format; // 'pdf' or 'docx'
  final String? fontFamily; // 'Arial', 'Calibri', 'Times New Roman'
  final String? accentColor; // Hex color code
  final String lineSpacing; // 'tight', 'normal', 'relaxed'
  final String margins; // 'narrow', 'normal', 'wide'
  final String? customFilename;
  final bool includeMetadata;

  ExportOptions({
    required this.templateId,
    this.format = 'pdf',
    this.fontFamily,
    this.accentColor,
    this.lineSpacing = 'normal',
    this.margins = 'normal',
    this.customFilename,
    this.includeMetadata = false,
  });
}
```

**User Flow**:
```
1. Display selected template and export options
2. User customizes options (optional)
3. User taps "Preview" → show preview modal
4. User taps "Export" button
5. Show loading overlay
6. Call export API
7. On success:
   - Download file to device
   - Show success message with "Open" and "Share" buttons
   - Navigate to ExportedFilesScreen
8. On error:
   - Show error dialog
   - Offer retry
```

### 3. ExportedFilesScreen

**Route**: `/export/files`
**File**: `lib/screens/export/exported_files_screen.dart`

**UI Components**:
- Sort/filter controls:
  - Sort by: Recent, Oldest, Name
  - Filter by: PDF, DOCX
- File list cards:
  - File icon (PDF/DOCX)
  - Filename
  - Document type badge (Resume / Cover Letter)
  - Job title
  - File size
  - Export date
  - ATS score (from generation)
  - Actions:
    - Open file
    - Share file
    - Delete file
- Storage usage indicator:
  - "X MB used of 100 MB free tier"
- Empty state ("No exported files yet")

**User Flow**:
```
1. Display list of exported files
2. User taps "Open" → open file with system viewer
3. User taps "Share" → open system share sheet
4. User taps "Delete" → confirm → delete file
5. Pull to refresh
```

---

## Backend API Integration

### API Endpoints (9 total)

#### 1. POST /api/v1/exports/pdf - Export to PDF

```dart
final exportedFile = await exportsApiClient.exportToPDF(
  generationId: generationId,
  template: 'modern',
  options: ExportOptions(
    accentColor: '#3498db',
    lineSpacing: 'normal',
    margins: 'normal',
  ),
);
```

Request:
```json
{
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "template": "modern",
  "options": {
    "accent_color": "#3498db",
    "line_spacing": "normal",
    "margins": "normal"
  }
}
```

Response:
```json
{
  "export_id": "export-uuid",
  "generation_id": "generation-uuid",
  "format": "pdf",
  "template": "modern",
  "file_size_bytes": 125840,
  "download_url": "https://api.jobwise.app/api/v1/exports/files/export-uuid/download",
  "expires_at": "2025-12-15T10:30:00Z",
  "created_at": "2025-11-15T10:30:00Z"
}
```

#### 2. POST /api/v1/exports/docx - Export to DOCX

```dart
final exportedFile = await exportsApiClient.exportToDOCX(
  generationId: generationId,
  template: 'classic',
  options: ExportOptions(
    fontFamily: 'Calibri',
    lineSpacing: 'relaxed',
  ),
);
```

Request:
```json
{
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "template": "classic",
  "options": {
    "font_family": "Calibri",
    "line_spacing": "relaxed"
  }
}
```

Response: Same as PDF export

#### 3. POST /api/v1/exports/batch - Batch Export

Export resume + cover letter together as a ZIP package.

```dart
final batchExport = await exportsApiClient.batchExport(
  exports: [
    BatchExportItem(
      generationId: resumeId,
      format: 'pdf',
      template: 'modern',
    ),
    BatchExportItem(
      generationId: coverLetterId,
      format: 'pdf',
      template: 'modern',
    ),
  ],
  createZip: true,
  zipFilename: 'application_package_2025-11-15.zip',
);
```

Request:
```json
{
  "exports": [
    {
      "generation_id": "resume-generation-uuid",
      "format": "pdf",
      "template": "modern",
      "filename": "resume_modern_2025-11-15.pdf"
    },
    {
      "generation_id": "cover-letter-generation-uuid",
      "format": "pdf",
      "template": "modern",
      "filename": "cover_letter_modern_2025-11-15.pdf"
    }
  ],
  "create_zip": true,
  "zip_filename": "application_package_2025-11-15.zip"
}
```

Response:
```json
{
  "batch_id": "batch-export-uuid",
  "total_exports": 2,
  "successful": 2,
  "failed": 0,
  "exports": [
    {
      "export_id": "export-uuid-1",
      "generation_id": "resume-generation-uuid",
      "status": "completed",
      "filename": "resume_modern_2025-11-15.pdf",
      "file_size_bytes": 125840
    },
    {
      "export_id": "export-uuid-2",
      "generation_id": "cover-letter-generation-uuid",
      "status": "completed",
      "filename": "cover_letter_modern_2025-11-15.pdf",
      "file_size_bytes": 122720
    }
  ],
  "zip_file": {
    "export_id": "batch-export-uuid",
    "filename": "application_package_2025-11-15.zip",
    "file_size_bytes": 248560,
    "download_url": "https://api.jobwise.app/api/v1/exports/files/batch-export-uuid/download"
  },
  "expires_at": "2025-12-15T10:30:00Z",
  "created_at": "2025-11-15T10:30:00Z"
}
```

#### 4. GET /api/v1/exports/templates - List Templates

```dart
final templates = await exportsApiClient.getTemplates();
```

Response:
```json
{
  "templates": [
    {
      "id": "modern",
      "name": "Modern",
      "description": "Clean and minimalist design for tech and startups",
      "ats_score": 85,
      "industries": ["Tech", "Startups", "Software"],
      "supports_customization": {
        "accent_color": true,
        "font_family": false
      },
      "preview_url": "https://api.jobwise.app/templates/modern/preview.png"
    },
    {
      "id": "classic",
      "name": "Classic",
      "description": "Traditional professional format",
      "ats_score": 95,
      "industries": ["Corporate", "Finance", "Legal"],
      "supports_customization": {
        "accent_color": false,
        "font_family": true
      },
      "preview_url": "https://api.jobwise.app/templates/classic/preview.png"
    },
    {
      "id": "creative",
      "name": "Creative",
      "description": "Bold and eye-catching for creative roles",
      "ats_score": 75,
      "industries": ["Design", "Marketing", "Media"],
      "supports_customization": {
        "accent_color": true,
        "font_family": true
      },
      "preview_url": "https://api.jobwise.app/templates/creative/preview.png"
    },
    {
      "id": "ats-optimized",
      "name": "ATS-Optimized",
      "description": "Maximum ATS compatibility",
      "ats_score": 98,
      "industries": ["Enterprise", "Government"],
      "supports_customization": {
        "accent_color": false,
        "font_family": false
      },
      "preview_url": "https://api.jobwise.app/templates/ats-optimized/preview.png"
    }
  ]
}
```

#### 5. GET /api/v1/exports/templates/{id} - Get Template Details

```dart
final template = await exportsApiClient.getTemplate(templateId);
```

Response: Single template object from list above

#### 6. POST /api/v1/exports/preview - Preview Export

Generate a preview of the exported document without saving.

```dart
final previewUrl = await exportsApiClient.previewExport(
  generationId: generationId,
  templateId: 'modern',
  options: options,
);
```

Request:
```json
{
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "template_id": "modern",
  "options": {
    "accent_color": "#3498db"
  }
}
```

Response:
```json
{
  "preview_url": "https://api.jobwise.app/previews/temp_preview_12345.png",
  "preview_type": "image/png",
  "expires_in_seconds": 300
}
```

#### 7. GET /api/v1/exports/files - List Exported Files

```dart
final files = await exportsApiClient.getExportedFiles(
  format: 'pdf',
  limit: 20,
  offset: 0,
);
```

Request:
```
GET /api/v1/exports/files?format=pdf&limit=20&offset=0
```

Response:
```json
{
  "files": [
    {
      "export_id": "export-uuid",
      "generation_id": "generation-uuid",
      "format": "pdf",
      "template": "modern",
      "filename": "resume_modern_2025-11-15.pdf",
      "file_size_bytes": 125840,
      "download_url": "https://api.jobwise.app/api/v1/exports/files/export-uuid/download",
      "created_at": "2025-11-15T10:30:00Z",
      "expires_at": "2025-12-15T10:30:00Z"
    }
  ],
  "total": 5,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 5,
    "hasMore": false
  },
  "storage_used_bytes": 1245600,
  "storage_limit_bytes": 104857600
}
```

#### 8. GET /api/v1/exports/files/{id}/download - Download File

```dart
await exportsApiClient.downloadFile(
  exportId: exportId,
  savePath: '/path/to/save/file.pdf',
);
```

Request:
```
GET /api/v1/exports/files/export-uuid/download
```

Response: Binary file data (PDF or DOCX)

**Mobile Implementation**:
```dart
Future<void> downloadFile(String exportId, String filename) async {
  // Get download directory
  final directory = await getApplicationDocumentsDirectory();
  final filePath = '${directory.path}/$filename';

  // Download file
  await _dio.download(
    '/api/v1/exports/files/$exportId/download',
    filePath,
    onReceiveProgress: (received, total) {
      if (total != -1) {
        final progress = (received / total * 100).toStringAsFixed(0);
        print('Download progress: $progress%');
      }
    },
  );

  // Open file with system viewer
  await OpenFile.open(filePath);
}
```

#### 9. DELETE /api/v1/exports/files/{id} - Delete File

```dart
await exportsApiClient.deleteFile(exportId);
```

Response: `204 No Content`

---

## Data Models

### ExportedFile

**File**: `lib/models/exported_file.dart`

```dart
class ExportedFile {
  final String exportId;
  final String generationId;
  final String format; // 'pdf', 'docx', 'zip'
  final String template;
  final String filename;
  final int fileSizeBytes;
  final String downloadUrl;
  final DateTime createdAt;
  final DateTime expiresAt;

  ExportedFile({
    required this.exportId,
    required this.generationId,
    required this.format,
    required this.template,
    required this.filename,
    required this.fileSizeBytes,
    required this.downloadUrl,
    required this.createdAt,
    required this.expiresAt,
  });

  factory ExportedFile.fromJson(Map<String, dynamic> json) {
    return ExportedFile(
      exportId: json['export_id'],
      generationId: json['generation_id'],
      format: json['format'],
      template: json['template'],
      filename: json['filename'],
      fileSizeBytes: json['file_size_bytes'],
      downloadUrl: json['download_url'],
      createdAt: DateTime.parse(json['created_at']),
      expiresAt: DateTime.parse(json['expires_at']),
    );
  }

  String get formattedFileSize {
    final kb = fileSizeBytes / 1024;
    if (kb < 1024) {
      return '${kb.toStringAsFixed(1)} KB';
    }
    final mb = kb / 1024;
    return '${mb.toStringAsFixed(1)} MB';
  }

  bool get isExpired => DateTime.now().isAfter(expiresAt);
}
```

### Template

**File**: `lib/models/template.dart`

```dart
class Template {
  final String id;
  final String name;
  final String description;
  final int atsScore;
  final List<String> industries;
  final TemplateCustomization supportsCustomization;
  final String previewUrl;

  Template({
    required this.id,
    required this.name,
    required this.description,
    required this.atsScore,
    required this.industries,
    required this.supportsCustomization,
    required this.previewUrl,
  });

  factory Template.fromJson(Map<String, dynamic> json) {
    return Template(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      atsScore: json['ats_score'],
      industries: List<String>.from(json['industries']),
      supportsCustomization: TemplateCustomization.fromJson(
        json['supports_customization'],
      ),
      previewUrl: json['preview_url'],
    );
  }
}

class TemplateCustomization {
  final bool accentColor;
  final bool fontFamily;

  TemplateCustomization({
    required this.accentColor,
    required this.fontFamily,
  });

  factory TemplateCustomization.fromJson(Map<String, dynamic> json) {
    return TemplateCustomization(
      accentColor: json['accent_color'],
      fontFamily: json['font_family'],
    );
  }
}
```

---

## State Management

### ExportsState

**File**: `lib/providers/exports/exports_state.dart`

```dart
class ExportsState {
  final List<Template> templates;
  final List<ExportedFile> exportedFiles;
  final Template? selectedTemplate;
  final ExportOptions? exportOptions;
  final bool isExporting;
  final double exportProgress;
  final String? errorMessage;
  final int storageUsedBytes;
  final int storageLimitBytes;

  ExportsState({
    this.templates = const [],
    this.exportedFiles = const [],
    this.selectedTemplate,
    this.exportOptions,
    this.isExporting = false,
    this.exportProgress = 0.0,
    this.errorMessage,
    this.storageUsedBytes = 0,
    this.storageLimitBytes = 104857600, // 100 MB
  });

  factory ExportsState.initial() {
    return ExportsState();
  }

  ExportsState copyWith({
    List<Template>? templates,
    List<ExportedFile>? exportedFiles,
    Template? selectedTemplate,
    ExportOptions? exportOptions,
    bool? isExporting,
    double? exportProgress,
    String? errorMessage,
    int? storageUsedBytes,
  }) {
    return ExportsState(
      templates: templates ?? this.templates,
      exportedFiles: exportedFiles ?? this.exportedFiles,
      selectedTemplate: selectedTemplate ?? this.selectedTemplate,
      exportOptions: exportOptions ?? this.exportOptions,
      isExporting: isExporting ?? this.isExporting,
      exportProgress: exportProgress ?? this.exportProgress,
      errorMessage: errorMessage,
      storageUsedBytes: storageUsedBytes ?? this.storageUsedBytes,
      storageLimitBytes: storageLimitBytes,
    );
  }

  double get storageUsagePercent =>
      (storageUsedBytes / storageLimitBytes * 100).clamp(0, 100);
}
```

### ExportsNotifier

**File**: `lib/providers/exports/exports_notifier.dart`

```dart
class ExportsNotifier extends StateNotifier<ExportsState> {
  final ExportsApiClient _apiClient;

  ExportsNotifier(this._apiClient) : super(ExportsState.initial());

  Future<void> fetchTemplates() async {
    try {
      final response = await _apiClient.getTemplates();
      final templates = (response['templates'] as List)
          .map((json) => Template.fromJson(json))
          .toList();

      state = state.copyWith(templates: templates);
    } catch (e) {
      rethrow;
    }
  }

  void selectTemplate(Template template) {
    state = state.copyWith(
      selectedTemplate: template,
      exportOptions: ExportOptions(templateId: template.id),
    );
  }

  void updateExportOptions(ExportOptions options) {
    state = state.copyWith(exportOptions: options);
  }

  Future<ExportedFile> exportToPDF({
    required String generationId,
    required ExportOptions options,
  }) async {
    state = state.copyWith(isExporting: true, exportProgress: 0.0);

    try {
      final exportedFile = await _apiClient.exportToPDF(
        generationId: generationId,
        templateId: options.templateId,
        options: options.toJson(),
        onProgress: (progress) {
          state = state.copyWith(exportProgress: progress);
        },
      );

      state = state.copyWith(
        isExporting: false,
        exportProgress: 1.0,
      );

      // Refresh files list
      await fetchExportedFiles();

      return exportedFile;
    } catch (e) {
      state = state.copyWith(
        isExporting: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> fetchExportedFiles() async {
    try {
      final response = await _apiClient.getExportedFiles();
      final files = (response['files'] as List)
          .map((json) => ExportedFile.fromJson(json))
          .toList();

      state = state.copyWith(
        exportedFiles: files,
        storageUsedBytes: response['storage_used_bytes'],
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<void> downloadFile(ExportedFile file) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final filePath = '${directory.path}/${file.filename}';

      await _apiClient.downloadFile(
        exportId: file.exportId,
        savePath: filePath,
      );

      // Open file
      await OpenFile.open(filePath);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> deleteFile(String exportId) async {
    try {
      await _apiClient.deleteFile(exportId);

      // Remove from list
      state = state.copyWith(
        exportedFiles: state.exportedFiles
        .where((f) => f.exportId != exportId)
            .toList(),
      );
    } catch (e) {
      rethrow;
    }
  }
}

// Provider
final exportsNotifierProvider =
    StateNotifierProvider<ExportsNotifier, ExportsState>(
  (ref) {
    final apiClient = ref.watch(exportsApiClientProvider);
    return ExportsNotifier(apiClient);
  },
);
```

---

## Service Layer

### ExportsApiClient

**File**: `lib/services/api/exports_api_client.dart`

```dart
class ExportsApiClient {
  final Dio _dio;

  ExportsApiClient(this._dio);

  Future<ExportedFile> exportToPDF({
    required String generationId,
    required String templateId,
    required Map<String, dynamic> options,
    Function(double)? onProgress,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/exports/pdf',
        data: {
          'generation_id': generationId,
          'template_id': templateId,
          'options': options,
        },
        onSendProgress: (sent, total) {
          if (onProgress != null && total != -1) {
            onProgress(sent / total);
          }
        },
      );

      return ExportedFile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getTemplates() async {
    try {
      final response = await _dio.get('/api/v1/exports/templates');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getExportedFiles({
    String? format,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (format != null) queryParams['format'] = format;
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _dio.get(
        '/api/v1/exports/files',
        queryParameters: queryParams,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> downloadFile({
    required String exportId,
    required String savePath,
  }) async {
    try {
      await _dio.download(
        '/api/v1/exports/files/$exportId/download',
        savePath,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteFile(String exportId) async {
    try {
      await _dio.delete('/api/v1/exports/files/$exportId');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    if (error.response != null) {
      final message = error.response?.data['detail'] ?? 'An error occurred';
      return Exception(message);
    }
    return Exception('Network error occurred');
  }
}

// Provider
final exportsApiClientProvider = Provider<ExportsApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return ExportsApiClient(dio);
});
```

---

## UI Components

### Template Card

**File**: `lib/widgets/template_card.dart`

```dart
class TemplateCard extends StatelessWidget {
  final Template template;
  final VoidCallback onSelect;
  final bool isSelected;

  const TemplateCard({
    required this.template,
    required this.onSelect,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: isSelected ? 8 : 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Template preview image
          AspectRatio(
            aspectRatio: 0.75,
            child: CachedNetworkImage(
              imageUrl: template.previewUrl,
              fit: BoxFit.cover,
              placeholder: (context, url) => Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      template.name,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    ATSScoreBadge(score: template.atsScore.toDouble()),
                  ],
                ),
                SizedBox(height: 4),
                Text(
                  template.description,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                SizedBox(height: 8),
                Wrap(
                  spacing: 4,
                  children: template.industries
                      .take(2)
                      .map((industry) => Chip(
                            label: Text(industry, style: TextStyle(fontSize: 10)),
                            padding: EdgeInsets.zero,
                          ))
                      .toList(),
                ),
                SizedBox(height: 8),
                ElevatedButton(
                  onPressed: onSelect,
                  child: Text(isSelected ? 'Selected' : 'Select'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

---

## Testing

### Unit Tests

```dart
test('ExportsNotifier exports to PDF successfully', () async {
  final mockClient = MockExportsApiClient();
  final notifier = ExportsNotifier(mockClient);

  when(mockClient.exportToPDF(
    generationId: any,
    templateId: any,
    options: any,
  )).thenAnswer((_) async => testExportedFile);

  await notifier.exportToPDF(
    generationId: 'gen-id',
    options: testOptions,
  );

  expect(notifier.state.isExporting, false);
  expect(notifier.state.exportProgress, 1.0);
});
```

---

## Performance Considerations

1. **Export Time**: PDF generation takes 2-5 seconds depending on document size
2. **Preview Caching**: Cache template previews to avoid repeated downloads
3. **File Storage**: Auto-delete expired files after 30 days
4. **Download Progress**: Show progress bar for large file downloads

---

## Future Enhancements

1. **Cloud Storage Integration**: Google Drive, Dropbox sync
2. **Custom Templates**: User-created templates
3. **Batch Operations**: Export multiple documents at once
4. **Email Integration**: Send documents directly via email
5. **Version History**: Track document revisions

---

**Status**: 🔄 Design Complete - Implementation Pending
**Screens**: 3 (Template Selection, Export Options, Exported Files)
**API Endpoints**: 9 endpoints
**Templates**: 4 professional templates
**Dependencies**: dio, open_file, share_plus, path_provider, cached_network_image
**Last Updated**: November 2025
