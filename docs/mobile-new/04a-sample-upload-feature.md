# Sample Upload Feature

**At a Glance (For AI Agents)**
- **Feature Name**: Sample Upload (Flutter front-end)
- **Primary Role**: Manage resume/cover-letter text samples used for writing-style extraction
- **Key Files**: `lib/providers/samples_provider.dart`, `lib/services/api/samples_api_client.dart`, `lib/models/sample.dart`
- **Backend Contract**: `../api-services/04a-sample-upload-api.md` (`/api/v1/samples`)
- **Main Screens/Widgets**:
  - `SampleUploadScreen` — list + upload/delete samples
  - `SampleDetailScreen` — view full text and stats
  - `SampleCard`, `SampleUploadButton`, `EmptySampleState` — reusable UI components

**Related Docs (Navigation Hints)**
- Backend API: `../api-services/04a-sample-upload-api.md`
- AI Generation feature: `04b-ai-generation-feature.md` (consumes active samples)
- V3 Generation feature: `04-generation-feature.md` (end-to-end pipeline)
- Profile feature: `02-profile-management-feature.md`

**Key Field / Property Semantics**
- `Sample.id` ↔ backend `id` (UUID): Unique sample identifier used across routes.
- `Sample.documentType` ↔ `document_type`: Either `"resume"` or `"cover_letter"`; exactly one active per type.
- `Sample.fullText` ↔ `full_text`: Only present in detail responses; omitted from list for performance.
- `Sample.isActive` ↔ `is_active`: Determines which sample the backend will use for style extraction.
- `SamplesState.activeResumeSample` / `activeCoverLetterSample`: Convenience getters to drive UI and validation.
- `SamplesApiClient` methods map 1:1 to backend endpoints: `uploadSample`, `getSamples`, `getSample`, `deleteSample`.

**Backend API**: [Sample Upload API](../api-services/04a-sample-upload-api.md)
**Base Path**: `/api/v1/samples`
**Status**: ✅ Fully Implemented
**Provider**: `samples_provider.dart`
**Last Updated**: November 2025

---

## Overview

The Sample Upload feature allows users to upload sample resumes and cover letters to teach the AI their writing style. This feature handles pure CRUD operations with no LLM integration - all operations are fast and deterministic.

**Architecture Note**: Sample upload handling is separated from document generation logic:
- **samples_provider.dart**: Manages resume/cover letter sample uploads (this feature)
- **generations_provider.dart**: Handles AI-powered document generation (see [04b-ai-generation-feature.md](04b-ai-generation-feature.md))

### User Stories

**As a user**, I want to:
- Upload sample resumes to teach the AI my resume writing style
- Upload sample cover letters to teach the AI my cover letter writing style
- View my uploaded samples
- Delete samples I no longer want to use
- See which sample is currently active for each document type

---

## Screens

### 1. SampleUploadScreen

**Route**: `/samples`
**File**: `lib/screens/samples/sample_upload_screen.dart`

**Context**: User navigates here from ProfileViewScreen or GenerationOptionsScreen

**UI Components**:
- Header: "My Sample Documents"
- Resume sample section:
  - Sample card (if uploaded) showing filename, word count, date
  - "Upload Resume Sample" button
  - "Delete" button (if sample exists)
- Cover letter sample section:
  - Sample card (if uploaded) showing filename, word count, date
  - "Upload Cover Letter Sample" button
  - "Delete" button (if sample exists)
- Info banner: "Upload samples to teach the AI your writing style"
- Loading indicator during upload

**User Flow**:
```
1. User navigates to SampleUploadScreen
2. App loads existing samples via GET /samples
3. Display current samples (or empty states)
4. User taps "Upload Resume Sample"
5. File picker opens (filter: .txt files only)
6. User selects file
7. App uploads via POST /samples/upload
8. Show success message
9. Refresh sample list
```

### 2. SampleDetailScreen

**Route**: `/samples/:id`
**File**: `lib/screens/samples/sample_detail_screen.dart`

**Context**: User taps on a sample card to view details

**UI Components**:
- Header with document type badge (Resume / Cover Letter)
- Original filename
- Upload date
- Word count and character count
- Full text content (scrollable)
- "Delete" button
- "Back" button

**User Flow**:
```
1. User taps sample card
2. Navigate to SampleDetailScreen
3. Load sample details via GET /samples/{id}
4. Display full text content
5. User can read or delete sample
```

---

## Backend API Integration

### API Endpoints (4 total)

#### 1. POST /api/v1/samples/upload - Upload Sample Document

**File Upload** (multipart/form-data):
```dart
import 'package:file_picker/file_picker.dart';

final result = await FilePicker.platform.pickFiles(
  type: FileType.custom,
  allowedExtensions: ['txt'],
);

if (result != null) {
  final file = result.files.single;
  final sample = await samplesApiClient.uploadSample(
    file: file,
    documentType: 'cover_letter', // or 'resume'
  );
}
```

Request:
```dart
final formData = FormData.fromMap({
  'document_type': documentType,
  'file': await MultipartFile.fromFile(
    file.path!,
    filename: file.name,
  ),
});

final response = await _dio.post('/api/v1/samples/upload', data: formData);
```

Response:
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

#### 2. GET /api/v1/samples - List Samples

```dart
final samples = await samplesApiClient.getSamples();
```

Response:
```json
{
  "samples": [
    {
      "id": "sample-uuid",
      "user_id": 1,
      "document_type": "cover_letter",
      "original_filename": "my_cover_letter.txt",
      "word_count": 421,
      "character_count": 2847,
      "is_active": true,
      "created_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### 3. GET /api/v1/samples/{id} - Get Sample Details

```dart
final sample = await samplesApiClient.getSample(sampleId);
```

Response:
```json
{
  "id": "sample-uuid",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "full_text": "Full sample text content...",
  "word_count": 421,
  "character_count": 2847,
  "is_active": true,
  "created_at": "2025-11-15T10:30:00Z"
}
```

#### 4. DELETE /api/v1/samples/{id} - Delete Sample

```dart
await samplesApiClient.deleteSample(sampleId);
```

Response: `204 No Content`

---

## Data Models

### Sample

**File**: `lib/models/sample.dart`

```dart
class Sample {
  final String id;
  final int userId;
  final String documentType; // 'resume' or 'cover_letter'
  final String originalFilename;
  final String? fullText; // Only included in detail response
  final int wordCount;
  final int characterCount;
  final bool isActive;
  final DateTime createdAt;

  Sample({
    required this.id,
    required this.userId,
    required this.documentType,
    required this.originalFilename,
    this.fullText,
    required this.wordCount,
    required this.characterCount,
    this.isActive = true,
    required this.createdAt,
  });

  factory Sample.fromJson(Map<String, dynamic> json) {
    return Sample(
      id: json['id'],
      userId: json['user_id'],
      documentType: json['document_type'],
      originalFilename: json['original_filename'],
      fullText: json['full_text'],
      wordCount: json['word_count'],
      characterCount: json['character_count'],
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'document_type': documentType,
      'original_filename': originalFilename,
      'full_text': fullText,
      'word_count': wordCount,
      'character_count': characterCount,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }

  bool get isResume => documentType == 'resume';
  bool get isCoverLetter => documentType == 'cover_letter';
}
```

---

## State Management

### SamplesProvider (`samples_provider.dart`)

Manages sample document uploads for teaching AI writing style.

**File**: `lib/providers/samples_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:file_picker/file_picker.dart';
import '../models/sample.dart';
import '../services/api/samples_api_client.dart';

// State class
class SamplesState {
  final List<Sample> samples;
  final bool isLoading;
  final bool isUploading;
  final String? errorMessage;

  SamplesState({
    this.samples = const [],
    this.isLoading = false,
    this.isUploading = false,
    this.errorMessage,
  });

  SamplesState copyWith({
    List<Sample>? samples,
    bool? isLoading,
    bool? isUploading,
    String? errorMessage,
  }) {
    return SamplesState(
      samples: samples ?? this.samples,
      isLoading: isLoading ?? this.isLoading,
      isUploading: isUploading ?? this.isUploading,
      errorMessage: errorMessage,
    );
  }

  // Computed properties
  Sample? get activeResumeSample => samples
      .where((s) => s.documentType == 'resume' && s.isActive)
      .firstOrNull;

  Sample? get activeCoverLetterSample => samples
      .where((s) => s.documentType == 'cover_letter' && s.isActive)
      .firstOrNull;

  List<Sample> get resumeSamples =>
      samples.where((s) => s.documentType == 'resume').toList();

  List<Sample> get coverLetterSamples =>
      samples.where((s) => s.documentType == 'cover_letter').toList();

  bool get hasSamples => samples.isNotEmpty;
  bool get hasResumeSample => activeResumeSample != null;
  bool get hasCoverLetterSample => activeCoverLetterSample != null;
}

// State notifier
class SamplesNotifier extends StateNotifier<SamplesState> {
  final SamplesApiClient _apiClient;

  SamplesNotifier(this._apiClient) : super(SamplesState());

  Future<void> loadSamples() async {
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final response = await _apiClient.getSamples();
      final samples = (response['samples'] as List)
          .map((json) => Sample.fromJson(json))
          .toList();

      state = state.copyWith(samples: samples, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  Future<Sample?> uploadSample({
    required PlatformFile file,
    required String documentType,
  }) async {
    state = state.copyWith(isUploading: true, errorMessage: null);

    try {
      final sample = await _apiClient.uploadSample(
        file: file,
        documentType: documentType,
      );

      // Refresh samples list to get updated active status
      await loadSamples();

      state = state.copyWith(isUploading: false);
      return sample;
    } catch (e) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  Future<bool> deleteSample(String sampleId) async {
    try {
      await _apiClient.deleteSample(sampleId);

      // Remove from local state
      final updatedSamples =
          state.samples.where((s) => s.id != sampleId).toList();
      state = state.copyWith(samples: updatedSamples);

      return true;
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
      return false;
    }
  }

  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}

// Provider
final samplesProvider = StateNotifierProvider<SamplesNotifier, SamplesState>(
  (ref) {
    final apiClient = ref.watch(samplesApiClientProvider);
    return SamplesNotifier(apiClient);
  },
);
```

**Usage in Screens**:
```dart
// Watch samples state
final samplesState = ref.watch(samplesProvider);
final resumeSample = samplesState.activeResumeSample;
final isUploading = samplesState.isUploading;

// Load samples on screen init
@override
void initState() {
  super.initState();
  Future.microtask(() {
    ref.read(samplesProvider.notifier).loadSamples();
  });
}

// Upload new sample
Future<void> _uploadSample(String documentType) async {
  final result = await FilePicker.platform.pickFiles(
    type: FileType.custom,
    allowedExtensions: ['txt'],
  );

  if (result != null && result.files.single.path != null) {
    final sample = await ref.read(samplesProvider.notifier).uploadSample(
      file: result.files.single,
      documentType: documentType,
    );

    if (sample != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sample uploaded successfully')),
      );
    }
  }
}

// Delete sample
Future<void> _deleteSample(String sampleId) async {
  final confirmed = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text('Delete Sample'),
      content: Text('Are you sure you want to delete this sample?'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: Text('Cancel'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(context, true),
          child: Text('Delete'),
        ),
      ],
    ),
  );

  if (confirmed == true) {
    final success = await ref.read(samplesProvider.notifier).deleteSample(sampleId);
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Sample deleted')),
      );
    }
  }
}
```

---

## Service Layer

### SamplesApiClient

**File**: `lib/services/api/samples_api_client.dart`

```dart
import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/sample.dart';
import 'base_http_client.dart';

class SamplesApiClient {
  final Dio _dio;

  SamplesApiClient(this._dio);

  /// Upload a sample document (resume or cover letter)
  Future<Sample> uploadSample({
    required PlatformFile file,
    required String documentType,
  }) async {
    try {
      final formData = FormData.fromMap({
        'document_type': documentType,
        'file': await MultipartFile.fromFile(
          file.path!,
          filename: file.name,
        ),
      });

      final response = await _dio.post(
        '/api/v1/samples/upload',
        data: formData,
      );

      return Sample.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get all samples for the current user
  Future<Map<String, dynamic>> getSamples({
    String? documentType,
    bool? isActive,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (documentType != null) queryParams['document_type'] = documentType;
      if (isActive != null) queryParams['is_active'] = isActive;

      final response = await _dio.get(
        '/api/v1/samples',
        queryParameters: queryParams,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get sample details including full text
  Future<Sample> getSample(String sampleId) async {
    try {
      final response = await _dio.get('/api/v1/samples/$sampleId');
      return Sample.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete a sample document
  Future<void> deleteSample(String sampleId) async {
    try {
      await _dio.delete('/api/v1/samples/$sampleId');
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
final samplesApiClientProvider = Provider<SamplesApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return SamplesApiClient(dio);
});
```

---

## UI Components

### SampleCard

**File**: `lib/widgets/sample_card.dart`

```dart
import 'package:flutter/material.dart';
import '../models/sample.dart';

class SampleCard extends StatelessWidget {
  final Sample sample;
  final VoidCallback? onTap;
  final VoidCallback? onDelete;

  const SampleCard({
    required this.sample,
    this.onTap,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              // Document type icon
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: sample.isResume
                      ? Colors.blue.shade100
                      : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  sample.isResume ? Icons.description : Icons.mail,
                  color: sample.isResume ? Colors.blue : Colors.green,
                ),
              ),
              SizedBox(width: 16),
              // Sample info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      sample.originalFilename,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    SizedBox(height: 4),
                    Text(
                      '${sample.wordCount} words',
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(height: 4),
                    Row(
                      children: [
                        if (sample.isActive)
                          Container(
                            padding: EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.green.shade100,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              'Active',
                              style: TextStyle(
                                color: Colors.green.shade700,
                                fontSize: 12,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              // Delete button
              if (onDelete != null)
                IconButton(
                  icon: Icon(Icons.delete_outline, color: Colors.red),
                  onPressed: onDelete,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### SampleUploadButton

**File**: `lib/widgets/sample_upload_button.dart`

```dart
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';

class SampleUploadButton extends StatelessWidget {
  final String documentType;
  final bool isLoading;
  final Function(PlatformFile) onFileSelected;

  const SampleUploadButton({
    required this.documentType,
    required this.onFileSelected,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: isLoading ? null : _pickFile,
      icon: isLoading
          ? SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Icon(Icons.upload_file),
      label: Text(isLoading ? 'Uploading...' : 'Upload ${_getLabel()}'),
      style: ElevatedButton.styleFrom(
        padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ),
    );
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['txt'],
    );

    if (result != null && result.files.single.path != null) {
      onFileSelected(result.files.single);
    }
  }

  String _getLabel() {
    return documentType == 'resume' ? 'Resume Sample' : 'Cover Letter Sample';
  }
}
```

### EmptySampleState

**File**: `lib/widgets/empty_sample_state.dart`

```dart
import 'package:flutter/material.dart';

class EmptySampleState extends StatelessWidget {
  final String documentType;
  final VoidCallback onUpload;

  const EmptySampleState({
    required this.documentType,
    required this.onUpload,
  });

  @override
  Widget build(BuildContext context) {
    final isResume = documentType == 'resume';

    return Container(
      padding: EdgeInsets.all(24),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300, width: 2),
        borderRadius: BorderRadius.circular(12),
        color: Colors.grey.shade50,
      ),
      child: Column(
        children: [
          Icon(
            isResume ? Icons.description_outlined : Icons.mail_outline,
            size: 48,
            color: Colors.grey.shade400,
          ),
          SizedBox(height: 16),
          Text(
            'No ${isResume ? "Resume" : "Cover Letter"} Sample',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w500,
              color: Colors.grey.shade700,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Upload a sample to teach the AI your writing style',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.grey.shade600,
            ),
          ),
          SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onUpload,
            icon: Icon(Icons.upload_file),
            label: Text('Upload Sample'),
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
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

test('SamplesNotifier loads samples successfully', () async {
  final mockClient = MockSamplesApiClient();
  final notifier = SamplesNotifier(mockClient);

  when(mockClient.getSamples()).thenAnswer((_) async => {
    'samples': [
      {
        'id': 'sample-1',
        'user_id': 1,
        'document_type': 'cover_letter',
        'original_filename': 'cover_letter.txt',
        'word_count': 421,
        'character_count': 2847,
        'is_active': true,
        'created_at': '2025-11-15T10:30:00Z',
      }
    ],
    'total': 1,
  });

  await notifier.loadSamples();

  expect(notifier.state.samples.length, 1);
  expect(notifier.state.hasCoverLetterSample, true);
  expect(notifier.state.isLoading, false);
});

test('SamplesNotifier uploads sample successfully', () async {
  final mockClient = MockSamplesApiClient();
  final notifier = SamplesNotifier(mockClient);

  final mockFile = MockPlatformFile();
  when(mockFile.path).thenReturn('/path/to/file.txt');
  when(mockFile.name).thenReturn('file.txt');

  when(mockClient.uploadSample(file: any, documentType: any))
      .thenAnswer((_) async => Sample(
            id: 'new-sample',
            userId: 1,
            documentType: 'resume',
            originalFilename: 'file.txt',
            wordCount: 500,
            characterCount: 3000,
            createdAt: DateTime.now(),
          ));

  final sample = await notifier.uploadSample(
    file: mockFile,
    documentType: 'resume',
  );

  expect(sample, isNotNull);
  expect(notifier.state.isUploading, false);
});

test('SamplesNotifier deletes sample successfully', () async {
  final mockClient = MockSamplesApiClient();
  final notifier = SamplesNotifier(mockClient);

  // Pre-populate with a sample
  notifier.state = SamplesState(samples: [
    Sample(
      id: 'sample-1',
      userId: 1,
      documentType: 'resume',
      originalFilename: 'resume.txt',
      wordCount: 500,
      characterCount: 3000,
      createdAt: DateTime.now(),
    ),
  ]);

  when(mockClient.deleteSample('sample-1')).thenAnswer((_) async {});

  final success = await notifier.deleteSample('sample-1');

  expect(success, true);
  expect(notifier.state.samples.length, 0);
});
```

### Widget Tests

```dart
testWidgets('SampleCard displays sample info correctly', (tester) async {
  final sample = Sample(
    id: 'sample-1',
    userId: 1,
    documentType: 'cover_letter',
    originalFilename: 'my_cover_letter.txt',
    wordCount: 421,
    characterCount: 2847,
    isActive: true,
    createdAt: DateTime.now(),
  );

  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: SampleCard(sample: sample),
      ),
    ),
  );

  expect(find.text('my_cover_letter.txt'), findsOneWidget);
  expect(find.text('421 words'), findsOneWidget);
  expect(find.text('Active'), findsOneWidget);
});
```

---

## Performance Considerations

1. **Fast Operations**: All endpoints are pure CRUD with no LLM calls
2. **File Size Limit**: Maximum 1 MB per file to prevent slow uploads
3. **List Optimization**: List endpoint excludes `full_text` for faster response
4. **Local State Updates**: Delete updates local state immediately without waiting for refresh

---

## Error Handling

### Common Errors

**Invalid File Type**:
```dart
// Error: Only .txt files are supported
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('Please select a .txt file'),
    backgroundColor: Colors.red,
  ),
);
```

**File Too Large**:
```dart
// Error: File size exceeds 1MB limit
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('File must be smaller than 1MB'),
    backgroundColor: Colors.red,
  ),
);
```

**Empty File**:
```dart
// Error: File is empty or contains no readable text
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('File is empty'),
    backgroundColor: Colors.red,
  ),
);
```

---

## Related Documentation

- [Sample Upload API](../api-services/04a-sample-upload-api.md) - Backend API specification
- [AI Generation Feature](04b-ai-generation-feature.md) - Uses samples for AI features
- [Profile Management Feature](02-profile-management-feature.md) - Profile context

---

**Status**: ✅ Fully Implemented
**Screens**: 2 (Upload, Detail)
**API Endpoints**: 4 endpoints
**Dependencies**: dio, file_picker, flutter_riverpod
**Last Updated**: November 2025
