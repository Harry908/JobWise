# Document Feature - Mobile Design Document

**Version**: 1.0
**Feature**: Generated Document Management and PDF Viewing
**API Service**: Document API
**Status**: ⚠️ **Partially Implemented** - generation result download and local caching implemented; full Documents feature and API client are pending
**Last Updated**: November 2, 2025

---

## Implementation Status

### ✅ Implemented / Partially Implemented
- PDF download & local caching: DocumentStorageService supports saving and caching of PDFs
- Generation result screen supports viewing generation text and exposes PDF URLs from generation result
- Download/Share/View actions are present in UI (generation result screen) but contain TODOs to complete platform-specific code (open/save/share implementation)

### ❌ Not Implemented (Remaining)
- Dedicated Documents tab & list screen with API-driven document list
- Document API client (`DocumentApiClient`) – not implemented in current codebase
- Document detail screen with full metadata (ATS, keyword coverage) and editing
- In-app PDF viewer integration for direct PDF render (currently TODO placeholders)
- Offline cache management UI, clear cache, and sync logic

### ✅ API Ready (Backend Specified)
- GET /documents - List user's documents with filtering
- GET /documents/{id} - Get document details with content
- GET /documents/{id}/download - Download PDF file
- DELETE /documents/{id} - Delete document
- PUT /documents/{id} - Update document metadata (title, notes)

---

## Feature Overview

### Purpose
Enable users to view, download, share, and manage their AI-generated resumes and cover letters. Provides easy access to PDF exports with metadata like ATS scores and keyword coverage.

### Key Features
1. **Document Library** - View all generated documents with filtering
2. **PDF Viewer** - In-app PDF viewing with zoom and scroll
3. **PDF Download** - Save to device storage for offline access
4. **PDF Sharing** - Share via email, messaging, cloud storage
5. **Document Details** - View metadata (ATS score, match %, keywords)
6. **Search and Filter** - Find documents by job, date, or type
7. **Document Management** - Delete unwanted documents
8. **Offline Access** - Cache PDFs for offline viewing

### Core User Flows

#### Flow 1: View Document Library
```
User Journey:
1. User opens "Documents" tab from bottom navigation
2. Document list screen appears with cards showing:
   - Document title (e.g., "Senior Python Developer - TechCorp Resume")
   - Document type badge (Resume / Cover Letter)
   - ATS score badge (87%)
   - Date generated (e.g., "2 hours ago")
   - Thumbnail preview
3. User can:
   - Pull to refresh → reload from server
   - Tap filter icon → show filters (type, date range, job)
   - Tap search icon → search by job title or company
   - Scroll to see more documents (lazy loading)
4. User taps document card
5. Navigate to document detail screen

Data Flow:
Mobile → GET /documents?limit=20&offset=0 → Backend returns list → Display cards → User taps card → Navigate to detail screen
```

#### Flow 2: View and Download Document
```
User Journey:
1. User opens document detail screen
2. Screen shows:
   - Document title (editable)
   - Job info (title, company)
   - ATS metrics card:
     * ATS Score: 87% (circular progress)
     * Match Percentage: 82%
     * Keyword Coverage: 15/18 keywords
   - PDF info:
     * File size: 245 KB
     * Page count: 1 page
   - Action buttons:
     * "View PDF" (primary)
     * "Download" (secondary)
     * "Share" (secondary)
     * "Delete" (destructive)
3. User taps "View PDF"
4. PDF viewer opens with in-app rendering
5. User can zoom, scroll, and navigate pages
6. User taps "Download" button in viewer
7. System dialog: "Save PDF to Downloads?"
8. User confirms
9. PDF saved to device storage
10. Success snackbar: "PDF saved to Downloads"
11. User can now access PDF offline

Data Flow:
Mobile → GET /documents/{id} → Backend returns full document → Display metadata → User taps "Download" → Mobile → GET /documents/{id}/download → Backend streams PDF binary → Save to local storage → Show success message
```

#### Flow 3: Share Document
```
User Journey:
1. User opens document detail screen
2. User taps "Share" button
3. Loading indicator shows "Preparing PDF..."
4. PDF downloaded to temp storage
5. System share sheet appears with options:
   - Email
   - Messages
   - WhatsApp
   - Google Drive
   - Copy Link
6. User selects "Email"
7. Email composer opens with PDF attached
8. Email pre-filled:
   Subject: "My Resume - [Name]"
   Body: "Please find my resume attached."
   Attachment: [Document_Title].pdf
9. User sends email
10. Success message: "Resume shared via email"

Data Flow:
Mobile → GET /documents/{id}/download → Backend streams PDF → Save to temp storage → Open system share sheet with file path → User shares → Clean up temp file
```

#### Flow 4: Delete Document
```
User Journey:
1. User opens document detail screen
2. User taps "Delete" button (or swipe-to-delete on list)
3. Confirmation dialog appears:
   "Delete This Document?
   
   This will permanently delete:
   - Senior Python Developer Resume
   - PDF file
   
   This cannot be undone."
4. User taps "Delete" (red button)
5. Loading indicator shown
6. Document and PDF deleted from server
7. Navigate back to document list
8. Success snackbar: "Document deleted"
9. Document removed from list

Data Flow:
Mobile → DELETE /documents/{id} → Backend deletes document record and PDF file → Success response (204) → Navigate back → Refresh list
```

#### Flow 5: Offline PDF Viewing
```
User Journey:
1. User previously downloaded PDF (cached locally)
2. User loses internet connection
3. User opens Documents tab
4. Cached documents show with offline indicator
5. User taps cached document
6. PDF opens from local storage (no network call)
7. User can view, but cannot:
   - Download again (already cached)
   - Share (requires network)
   - Delete (requires network)
8. Banner shows: "Viewing cached version. Connect to update."
9. User reconnects to internet
10. Cache auto-syncs with server
11. Offline indicator disappears

Data Flow:
App starts → Check local cache → Display cached documents → User taps → Load from local storage → No network call
```

---

## API Integration

### Backend Connection
```
Base URL: http://10.0.2.2:8000/api/v1
Authentication: JWT Bearer token in Authorization header
PDF Streaming: Binary response with Content-Disposition header
```

### Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/documents` | GET | List user's documents | Query params: `document_type`, `job_id`, `limit`, `offset` | Documents array (200) |
| `/documents/{id}` | GET | Get document details | - | Document object (200) |
| `/documents/{id}/download` | GET | Download PDF | - | PDF binary (200) |
| `/documents/{id}` | PUT | Update metadata | `{title, notes}` | Updated document (200) |
| `/documents/{id}` | DELETE | Delete document | - | No content (204) |

### Error Codes

| Code | Meaning | User Action |
|------|---------|-------------|
| 400 | Validation error | Show validation errors |
| 401 | Unauthorized (invalid/expired token) | Redirect to login |
| 403 | Forbidden (not document owner) | Show "Access denied" message |
| 404 | Document or PDF not found | Show "Document not found" message |
| 500 | Server error | Show error with retry option |

---

## Data Models

### Document Model

```dart
// lib/models/document.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'document.freezed.dart';
part 'document.g.dart';

@freezed
class Document with _$Document {
  const factory Document({
    required String id,
    required DocumentType documentType,
    required String title,
    required DocumentContent content,
    required DocumentMetadata metadata,
    required PDFInfo pdf,
    String? notes,
    @Default(1) int version,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Document;

  factory Document.fromJson(Map<String, dynamic> json) => 
      _$DocumentFromJson(json);
}

enum DocumentType {
  @JsonValue('resume')
  resume,
  @JsonValue('cover_letter')
  coverLetter,
}

@freezed
class DocumentContent with _$DocumentContent {
  const factory DocumentContent({
    required String text,
    String? html,
    String? markdown,
  }) = _DocumentContent;

  factory DocumentContent.fromJson(Map<String, dynamic> json) => 
      _$DocumentContentFromJson(json);
}

@freezed
class DocumentMetadata with _$DocumentMetadata {
  const factory DocumentMetadata({
    required String generationId,
    required String profileId,
    required String jobId,
    required String jobTitle,
    required String company,
    required String template,
    required double atsScore,
    required int matchPercentage,
    required double keywordCoverage,
    required int keywordsMatched,
    required int keywordsTotal,
    int? tokensUsed,
    double? generationTime,
  }) = _DocumentMetadata;

  factory DocumentMetadata.fromJson(Map<String, dynamic> json) => 
      _$DocumentMetadataFromJson(json);
}

@freezed
class PDFInfo with _$PDFInfo {
  const factory PDFInfo({
    required String url,
    required int sizeBytes,
    @Default(1) int pageCount,
    DateTime? createdAt,
  }) = _PDFInfo;

  factory PDFInfo.fromJson(Map<String, dynamic> json) => 
      _$PDFInfoFromJson(json);
}

// Extension for UI helpers
extension DocumentExtensions on Document {
  String get typeDisplayText {
    switch (documentType) {
      case DocumentType.resume:
        return 'Resume';
      case DocumentType.coverLetter:
        return 'Cover Letter';
    }
  }

  String get sizeFormatted {
    final bytes = pdf.sizeBytes;
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  Color get typeColor {
    switch (documentType) {
      case DocumentType.resume:
        return Colors.blue;
      case DocumentType.coverLetter:
        return Colors.purple;
    }
  }

  String get relativeTime {
    final now = DateTime.now();
    final difference = now.difference(createdAt);

    if (difference.inMinutes < 1) return 'Just now';
    if (difference.inMinutes < 60) return '${difference.inMinutes}m ago';
    if (difference.inHours < 24) return '${difference.inHours}h ago';
    if (difference.inDays < 7) return '${difference.inDays}d ago';
    return DateFormat('MMM d, yyyy').format(createdAt);
  }
}

extension PDFInfoExtensions on PDFInfo {
  String get sizeFormatted {
    if (sizeBytes < 1024) return '$sizeBytes B';
    if (sizeBytes < 1024 * 1024) {
      return '${(sizeBytes / 1024).toStringAsFixed(1)} KB';
    }
    return '${(sizeBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }
}
```

### Document List Response

```dart
@freezed
class DocumentListResponse with _$DocumentListResponse {
  const factory DocumentListResponse({
    required List<Document> documents,
    required Pagination pagination,
    DocumentStatistics? statistics,
  }) = _DocumentListResponse;

  factory DocumentListResponse.fromJson(Map<String, dynamic> json) => 
      _$DocumentListResponseFromJson(json);
}

@freezed
class DocumentStatistics with _$DocumentStatistics {
  const factory DocumentStatistics({
    required int totalDocuments,
    required int resumes,
    required int coverLetters,
    required double averageAtsScore,
  }) = _DocumentStatistics;

  factory DocumentStatistics.fromJson(Map<String, dynamic> json) => 
      _$DocumentStatisticsFromJson(json);
}
```

---

## Service Layer

### Document API Client

```dart
// lib/services/api/document_api_client.dart

import 'dart:typed_data';
import 'package:dio/dio.dart';
import '../../models/document.dart';
import '../../models/pagination.dart';
import 'api_client.dart';

class DocumentApiClient {
  final ApiClient _client;

  DocumentApiClient(this._client);

  /// List user's documents with filtering
  Future<DocumentListResponse> getDocuments({
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
      if (createdAfter != null) 
        'created_after': createdAfter.toIso8601String(),
      'limit': limit,
      'offset': offset,
    });
    return DocumentListResponse.fromJson(response.data);
  }

  /// Get document details with full content
  Future<Document> getDocument(String id) async {
    final response = await _client.get('/documents/$id');
    return Document.fromJson(response.data);
  }

  /// Download PDF as bytes
  Future<Uint8List> downloadPDF(String id) async {
    final response = await _client.dio.get(
      '/documents/$id/download',
      options: Options(
        responseType: ResponseType.bytes,
        headers: {
          'Authorization': _client.dio.options.headers['Authorization'],
        },
      ),
    );
    return Uint8List.fromList(response.data);
  }

  /// Get PDF download URL (for external viewers)
  String getDownloadUrl(String id) {
    final baseUrl = _client.dio.options.baseUrl;
    return '$baseUrl/documents/$id/download';
  }

  /// Update document metadata
  Future<Document> updateDocument(String id, {
    String? title,
    String? notes,
  }) async {
    final response = await _client.put('/documents/$id', data: {
      if (title != null) 'title': title,
      if (notes != null) 'notes': notes,
    });
    return Document.fromJson(response.data);
  }

  /// Delete document and PDF
  Future<void> deleteDocument(String id) async {
    await _client.delete('/documents/$id');
  }
}
```

### Document Storage Service (Local Caching)

```dart
// lib/services/storage/document_storage_service.dart

import 'dart:io';
import 'dart:typed_data';
import 'package:path_provider/path_provider.dart';
import '../../models/document.dart';

class DocumentStorageService {
  /// Save PDF to local storage
  Future<String> savePDF(String documentId, Uint8List pdfBytes, String title) async {
    final directory = await getApplicationDocumentsDirectory();
    final pdfDir = Directory('${directory.path}/pdfs');
    if (!await pdfDir.exists()) {
      await pdfDir.create(recursive: true);
    }

    final fileName = '${documentId}_${_sanitizeFileName(title)}.pdf';
    final filePath = '${pdfDir.path}/$fileName';
    final file = File(filePath);
    await file.writeAsBytes(pdfBytes);

    return filePath;
  }

  /// Get cached PDF path
  Future<String?> getCachedPDFPath(String documentId) async {
    final directory = await getApplicationDocumentsDirectory();
    final pdfDir = Directory('${directory.path}/pdfs');
    
    if (!await pdfDir.exists()) return null;

    final files = await pdfDir.list().toList();
    for (var file in files) {
      if (file.path.contains(documentId)) {
        return file.path;
      }
    }
    return null;
  }

  /// Check if PDF is cached
  Future<bool> isPDFCached(String documentId) async {
    final path = await getCachedPDFPath(documentId);
    return path != null && await File(path).exists();
  }

  /// Delete cached PDF
  Future<void> deleteCachedPDF(String documentId) async {
    final path = await getCachedPDFPath(documentId);
    if (path != null) {
      final file = File(path);
      if (await file.exists()) {
        await file.delete();
      }
    }
  }

  /// Clear all cached PDFs
  Future<void> clearCache() async {
    final directory = await getApplicationDocumentsDirectory();
    final pdfDir = Directory('${directory.path}/pdfs');
    if (await pdfDir.exists()) {
      await pdfDir.delete(recursive: true);
    }
  }

  /// Get cache size
  Future<int> getCacheSize() async {
    final directory = await getApplicationDocumentsDirectory();
    final pdfDir = Directory('${directory.path}/pdfs');
    
    if (!await pdfDir.exists()) return 0;

    int totalSize = 0;
    await for (var file in pdfDir.list(recursive: true)) {
      if (file is File) {
        totalSize += await file.length();
      }
    }
    return totalSize;
  }

  String _sanitizeFileName(String name) {
    return name.replaceAll(RegExp(r'[^\w\s-]'), '').replaceAll(' ', '_');
  }
}
```

---

## State Management

### Document Provider (Riverpod)

```dart
// lib/providers/document_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/document.dart';
import '../services/api/document_api_client.dart';
import '../services/storage/document_storage_service.dart';

// Provider for document API client
final documentApiClientProvider = Provider<DocumentApiClient>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return DocumentApiClient(apiClient);
});

// Provider for document storage service
final documentStorageServiceProvider = Provider<DocumentStorageService>((ref) {
  return DocumentStorageService();
});

// Provider for document list
final documentsProvider = FutureProvider.autoDispose
    .family<DocumentListResponse, DocumentFilters>(
  (ref, filters) async {
    final client = ref.watch(documentApiClientProvider);
    return client.getDocuments(
      documentType: filters.documentType,
      jobId: filters.jobId,
      profileId: filters.profileId,
      createdAfter: filters.createdAfter,
      limit: filters.limit,
      offset: filters.offset,
    );
  },
);

// Provider for single document
final documentProvider = FutureProvider.autoDispose
    .family<Document, String>((ref, documentId) async {
  final client = ref.watch(documentApiClientProvider);
  return client.getDocument(documentId);
});

// Provider for PDF cache status
final pdfCacheStatusProvider = FutureProvider.autoDispose
    .family<bool, String>((ref, documentId) async {
  final storage = ref.watch(documentStorageServiceProvider);
  return storage.isPDFCached(documentId);
});

// State notifier for document operations
class DocumentNotifier extends StateNotifier<AsyncValue<void>> {
  final DocumentApiClient _client;
  final DocumentStorageService _storage;

  DocumentNotifier(this._client, this._storage) 
      : super(const AsyncValue.data(null));

  /// Download and cache PDF
  Future<String> downloadPDF(String documentId, String title) async {
    state = const AsyncValue.loading();
    try {
      final pdfBytes = await _client.downloadPDF(documentId);
      final filePath = await _storage.savePDF(documentId, pdfBytes, title);
      state = const AsyncValue.data(null);
      return filePath;
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  /// Delete document
  Future<void> deleteDocument(String documentId) async {
    state = const AsyncValue.loading();
    try {
      await _client.deleteDocument(documentId);
      await _storage.deleteCachedPDF(documentId);
      state = const AsyncValue.data(null);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  /// Update document metadata
  Future<Document> updateDocument(String id, {
    String? title,
    String? notes,
  }) async {
    state = const AsyncValue.loading();
    try {
      final document = await _client.updateDocument(
        id,
        title: title,
        notes: notes,
      );
      state = const AsyncValue.data(null);
      return document;
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }
}

final documentNotifierProvider =
    StateNotifierProvider<DocumentNotifier, AsyncValue<void>>((ref) {
  final client = ref.watch(documentApiClientProvider);
  final storage = ref.watch(documentStorageServiceProvider);
  return DocumentNotifier(client, storage);
});

// Filter model
class DocumentFilters {
  final DocumentType? documentType;
  final String? jobId;
  final String? profileId;
  final DateTime? createdAfter;
  final int limit;
  final int offset;

  const DocumentFilters({
    this.documentType,
    this.jobId,
    this.profileId,
    this.createdAfter,
    this.limit = 20,
    this.offset = 0,
  });

  DocumentFilters copyWith({
    DocumentType? documentType,
    String? jobId,
    String? profileId,
    DateTime? createdAfter,
    int? limit,
    int? offset,
  }) {
    return DocumentFilters(
      documentType: documentType ?? this.documentType,
      jobId: jobId ?? this.jobId,
      profileId: profileId ?? this.profileId,
      createdAfter: createdAfter ?? this.createdAfter,
      limit: limit ?? this.limit,
      offset: offset ?? this.offset,
    );
  }
}
```

---

## UI Components

### 1. Document List Screen

```dart
// lib/screens/documents/document_list_screen.dart

class DocumentListScreen extends ConsumerStatefulWidget {
  const DocumentListScreen();

  @override
  ConsumerState<DocumentListScreen> createState() => 
      _DocumentListScreenState();
}

class _DocumentListScreenState extends ConsumerState<DocumentListScreen> {
  DocumentFilters _filters = const DocumentFilters();

  @override
  Widget build(BuildContext context) {
    final documentsAsync = ref.watch(documentsProvider(_filters));

    return Scaffold(
      appBar: AppBar(
        title: Text('My Documents'),
        actions: [
          IconButton(
            icon: Icon(Icons.filter_list),
            onPressed: _showFilters,
          ),
          IconButton(
            icon: Icon(Icons.search),
            onPressed: _showSearch,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(documentsProvider(_filters));
        },
        child: documentsAsync.when(
          data: (response) {
            final documents = response.documents;

            if (documents.isEmpty) {
              return _EmptyState();
            }

            return CustomScrollView(
              slivers: [
                // Statistics Card
                if (response.statistics != null)
                  SliverToBoxAdapter(
                    child: _StatisticsCard(
                      statistics: response.statistics!,
                    ),
                  ),

                // Document List
                SliverPadding(
                  padding: EdgeInsets.all(16),
                  sliver: SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        if (index >= documents.length) {
                          // Load more trigger
                          if (response.pagination.hasNext) {
                            _loadMore();
                          }
                          return SizedBox(height: 80);
                        }

                        final document = documents[index];
                        return _DocumentCard(
                          document: document,
                          onTap: () => _navigateToDetail(document),
                          onDelete: () => _confirmDelete(document),
                        );
                      },
                      childCount: documents.length + 1,
                    ),
                  ),
                ),
              ],
            );
          },
          loading: () => Center(child: CircularProgressIndicator()),
          error: (error, stack) => _ErrorView(
            error: error,
            onRetry: () => ref.invalidate(documentsProvider(_filters)),
          ),
        ),
      ),
    );
  }

  void _navigateToDetail(Document document) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => DocumentDetailScreen(documentId: document.id),
      ),
    );
  }

  Future<void> _confirmDelete(Document document) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Delete Document?'),
        content: Text(
          'This will permanently delete:\n'
          '- ${document.title}\n'
          '- PDF file\n\n'
          'This cannot be undone.',
        ),
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
      try {
        await ref
            .read(documentNotifierProvider.notifier)
            .deleteDocument(document.id);
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Document deleted')),
          );
          ref.invalidate(documentsProvider(_filters));
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to delete document')),
          );
        }
      }
    }
  }

  void _loadMore() {
    setState(() {
      _filters = _filters.copyWith(
        offset: _filters.offset + _filters.limit,
      );
    });
  }

  void _showFilters() {
    // Show filter bottom sheet
  }

  void _showSearch() {
    // Show search screen
  }
}

// Document Card Widget
class _DocumentCard extends ConsumerWidget {
  final Document document;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _DocumentCard({
    required this.document,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isCachedAsync = ref.watch(pdfCacheStatusProvider(document.id));

    return Dismissible(
      key: Key(document.id),
      direction: DismissDirection.endToStart,
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: EdgeInsets.only(right: 16),
        child: Icon(Icons.delete, color: Colors.white),
      ),
      confirmDismiss: (_) async {
        return await showDialog<bool>(
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
      },
      onDismissed: (_) => onDelete(),
      child: Card(
        margin: EdgeInsets.only(bottom: 12),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                // Type Icon
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: document.typeColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    document.documentType == DocumentType.resume
                        ? Icons.description
                        : Icons.mail,
                    color: document.typeColor,
                  ),
                ),
                SizedBox(width: 16),

                // Document Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        document.title,
                        style: Theme.of(context).textTheme.titleMedium,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      SizedBox(height: 4),
                      Text(
                        '${document.metadata.company} • ${document.relativeTime}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      SizedBox(height: 8),
                      Row(
                        children: [
                          // Type Badge
                          _Badge(
                            label: document.typeDisplayText,
                            color: document.typeColor,
                          ),
                          SizedBox(width: 8),
                          // ATS Score Badge
                          _Badge(
                            label: 'ATS ${(document.metadata.atsScore * 100).toInt()}%',
                            color: _getATSColor(document.metadata.atsScore),
                          ),
                          SizedBox(width: 8),
                          // Cached Indicator
                          isCachedAsync.when(
                            data: (isCached) => isCached
                                ? Icon(Icons.offline_pin, 
                                       size: 16, 
                                       color: Colors.green)
                                : SizedBox(),
                            loading: () => SizedBox(),
                            error: (_, __) => SizedBox(),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Arrow Icon
                Icon(Icons.chevron_right, color: Colors.grey),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getATSColor(double score) {
    if (score >= 0.8) return Colors.green;
    if (score >= 0.6) return Colors.orange;
    return Colors.red;
  }
}

class _Badge extends StatelessWidget {
  final String label;
  final Color color;

  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
```

### 2. Document Detail Screen

```dart
// lib/screens/documents/document_detail_screen.dart

class DocumentDetailScreen extends ConsumerWidget {
  final String documentId;

  const DocumentDetailScreen({required this.documentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final documentAsync = ref.watch(documentProvider(documentId));

    return documentAsync.when(
      data: (document) => Scaffold(
        appBar: AppBar(
          title: Text('Document Details'),
          actions: [
            IconButton(
              icon: Icon(Icons.share),
              onPressed: () => _shareDocument(context, ref, document),
            ),
            IconButton(
              icon: Icon(Icons.delete),
              onPressed: () => _deleteDocument(context, ref, document),
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title (Editable)
              _EditableTitle(document: document),
              SizedBox(height: 16),

              // Job Info Card
              _JobInfoCard(metadata: document.metadata),
              SizedBox(height: 16),

              // ATS Metrics Card
              _ATSMetricsCard(metadata: document.metadata),
              SizedBox(height: 16),

              // PDF Info Card
              _PDFInfoCard(pdf: document.pdf),
              SizedBox(height: 24),

              // Action Buttons
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _viewPDF(context, ref, document),
                  icon: Icon(Icons.visibility),
                  label: Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text('View PDF'),
                  ),
                ),
              ),
              SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => _downloadPDF(context, ref, document),
                  icon: Icon(Icons.download),
                  label: Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text('Download PDF'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
      loading: () => Scaffold(
        appBar: AppBar(title: Text('Loading...')),
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => Scaffold(
        appBar: AppBar(title: Text('Error')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, size: 64, color: Colors.red),
              SizedBox(height: 16),
              Text('Failed to load document'),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: Text('Go Back'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _viewPDF(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    // Check if cached
    final isCached = await ref
        .read(documentStorageServiceProvider)
        .isPDFCached(document.id);

    String? filePath;

    if (isCached) {
      filePath = await ref
          .read(documentStorageServiceProvider)
          .getCachedPDFPath(document.id);
    } else {
      // Download and cache
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => Center(child: CircularProgressIndicator()),
      );

      try {
        filePath = await ref
            .read(documentNotifierProvider.notifier)
            .downloadPDF(document.id, document.title);
        Navigator.pop(context); // Close loading dialog
      } catch (e) {
        Navigator.pop(context);
        _showError(context, 'Failed to download PDF');
        return;
      }
    }

    if (filePath != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => PDFViewerScreen(
            filePath: filePath!,
            title: document.title,
          ),
        ),
      );
    }
  }

  Future<void> _downloadPDF(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => Center(child: CircularProgressIndicator()),
    );

    try {
      final filePath = await ref
          .read(documentNotifierProvider.notifier)
          .downloadPDF(document.id, document.title);
      
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('PDF saved to Downloads'),
          action: SnackBarAction(
            label: 'Open',
            onPressed: () => OpenFile.open(filePath),
          ),
        ),
      );
    } catch (e) {
      Navigator.pop(context);
      _showError(context, 'Failed to download PDF');
    }
  }

  Future<void> _shareDocument(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Preparing PDF...'),
          ],
        ),
      ),
    );

    try {
      final pdfBytes = await ref
          .read(documentApiClientProvider)
          .downloadPDF(document.id);

      final tempDir = await getTemporaryDirectory();
      final fileName = '${document.title.replaceAll(' ', '_')}.pdf';
      final filePath = '${tempDir.path}/$fileName';
      final file = File(filePath);
      await file.writeAsBytes(pdfBytes);

      Navigator.pop(context);

      await Share.shareFiles(
        [filePath],
        subject: document.title,
        text: 'Here is my ${document.typeDisplayText.toLowerCase()}',
      );
    } catch (e) {
      Navigator.pop(context);
      _showError(context, 'Failed to share PDF');
    }
  }

  Future<void> _deleteDocument(
    BuildContext context,
    WidgetRef ref,
    Document document,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Delete Document?'),
        content: Text(
          'This will permanently delete:\n'
          '- ${document.title}\n'
          '- PDF file\n\n'
          'This cannot be undone.',
        ),
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
      try {
        await ref
            .read(documentNotifierProvider.notifier)
            .deleteDocument(document.id);
        
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Document deleted')),
        );
      } catch (e) {
        _showError(context, 'Failed to delete document');
      }
    }
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}
```

### 3. PDF Viewer Screen

```dart
// lib/screens/documents/pdf_viewer_screen.dart

import 'package:flutter_pdfview/flutter_pdfview.dart';

class PDFViewerScreen extends StatefulWidget {
  final String filePath;
  final String title;

  const PDFViewerScreen({
    required this.filePath,
    required this.title,
  });

  @override
  _PDFViewerScreenState createState() => _PDFViewerScreenState();
}

class _PDFViewerScreenState extends State<PDFViewerScreen> {
  int _currentPage = 0;
  int _totalPages = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: () => Share.shareFiles([widget.filePath]),
          ),
        ],
      ),
      body: Stack(
        children: [
          PDFView(
            filePath: widget.filePath,
            enableSwipe: true,
            swipeHorizontal: false,
            autoSpacing: true,
            pageFling: true,
            onRender: (pages) {
              setState(() {
                _totalPages = pages ?? 0;
              });
            },
            onPageChanged: (page, total) {
              setState(() {
                _currentPage = page ?? 0;
                _totalPages = total ?? 0;
              });
            },
          ),
          if (_totalPages > 1)
            Positioned(
              bottom: 16,
              left: 0,
              right: 0,
              child: Center(
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.black87,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Page ${_currentPage + 1} of $_totalPages',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
```

---

## Error Handling

### Network Errors
```dart
try {
  final document = await documentApiClient.getDocument(id);
  // Success
} on DioError catch (e) {
  if (e.type == DioErrorType.connectionTimeout) {
    showError('Connection timeout. Please check your internet.');
  } else if (e.response?.statusCode == 404) {
    showError('Document not found');
  } else {
    showError('Failed to load document');
  }
}
```

### Storage Errors
```dart
try {
  await documentStorage.savePDF(id, bytes, title);
} catch (e) {
  if (e is FileSystemException) {
    showError('Not enough storage space');
  } else {
    showError('Failed to save PDF');
  }
}
```

---

## Performance Considerations

1. **Lazy Loading**: Load documents in pages (20 at a time)
2. **PDF Caching**: Cache recently viewed PDFs locally
3. **Thumbnail Generation**: Consider generating PDF thumbnails
4. **Memory Management**: Dispose PDF viewer when leaving screen
5. **Network Optimization**: Use compression for PDF transfer

---

## Testing Strategy

### Unit Tests
- Document model serialization
- PDF path sanitization
- Cache size calculation
- File operations

### Widget Tests
- Document card rendering
- Filter application
- Delete confirmation dialog
- PDF viewer controls

### Integration Tests
- Full download flow
- Share flow
- Delete flow with cache cleanup
- Offline viewing

---

## Security Considerations

1. **File Permissions**: Request storage permissions properly
2. **Secure Deletion**: Overwrite PDF files before deleting (sensitive data)
3. **Cache Expiry**: Implement cache expiration policy
4. **Ownership Verification**: Always verify user owns document before operations

---

## Future Enhancements

1. **Thumbnail Previews**: Generate and display PDF thumbnails
2. **Full-Text Search**: Search within PDF content
3. **Annotations**: Add notes/highlights to PDFs
4. **Version History**: Track document revisions
5. **Batch Operations**: Delete/download multiple documents
6. **Cloud Sync**: Sync cached PDFs across devices
7. **Print Support**: Print PDFs directly from app
