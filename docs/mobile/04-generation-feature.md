# Generation Feature - Mobile Design Document

**Version**: 1.1
**Feature**: AI-Powered Resume and Cover Letter Generation
**API Service**: Generation API
**Status**: 🚧 **Sprint 4 Ready** (Fully specified, ready for Sprint 4 implementation)
**Last Updated**: November 7, 2025

---

## Implementation Status

### ✅ Implemented - Generation Core Features
- Generation initiation screen (select job + options) — `generation_options_screen.dart`
- Real-time progress tracking screen with stage updates — `generation_progress_screen.dart`
- Generation result screen (ATS score, recommendations) — `generation_result_screen.dart`
- Generation history list screen — `generation_history_screen.dart`
- Template selection UI — `templatesProvider` + UI
- Generation options form (length, focus areas, custom instructions)
- Rate limit handling and user feedback (429 handling and RateLimitException)
- Generation API client (endpoints implemented in `generation_api_client.dart`)
- Generation state management (`generation_provider.dart`)
- Polling mechanism for progress updates (stream-based polling in API client)
- Error handling and retry logic (exceptions, retry patterns)

### ✅ Implemented - Preference Management Features (Partial)
- Sample resume upload screen — `upload_sample_resume_screen.dart` (multipart uploads implemented)
- Sample cover letter upload screen — `upload_cover_letter_screen.dart`
- Example resume management screen (list, delete, set primary) — `manage_example_resumes_screen.dart`
- Layout preference configuration UI partially (needs polish)
- Writing style preference UI partially (needs polish)
- User generation profile endpoints and client implemented (`preference_api_client.dart`)
- File picker integration and multipart uploads implemented
- File upload progress handling implemented in API client
- LLM preference extraction and response display implemented on upload

Remaining TODOs:
- Complete preference setup wizard/onboarding flow UI
- Improve layout/style editing screens and saving

### ✅ API Ready (Backend Fully Implemented)

**Generation API:**
- POST /generations/resume - Start resume generation
- POST /generations/cover-letter - Start cover letter generation
- GET /generations/{id} - Get generation status and progress
- GET /generations/{id}/result - Get final result with content
- GET /generations - List user's generations
- DELETE /generations/{id} - Cancel generation
- GET /generations/templates - List available templates

**Preference API:**
- POST /api/v1/preferences/upload-sample-resume - Upload and extract layout preferences
- POST /api/v1/preferences/upload-cover-letter - Upload and extract writing style
- GET /api/v1/preferences/generation-profile - Get user's generation profile
- PUT /api/v1/preferences/generation-profile - Update generation profile settings
- GET /api/v1/preferences/example-resumes - List user's example resumes
- DELETE /api/v1/preferences/example-resumes/{resume_id} - Delete example resume
- POST /api/v1/preferences/example-resumes/{resume_id}/set-primary - Set primary example

---

## Feature Overview

### Purpose
Enable users to generate AI-tailored resumes and cover letters by combining their master profile with specific job descriptions. Real-time progress tracking shows a multi-stage AI pipeline; the UI displays the number of stages as provided by the backend.

### Key Features

**Generation Core:**
1. **Job Selection** - Choose saved job for tailored generation
2. **Template Selection** - Pick resume template (Modern, Classic, Creative)
3. **Generation Options** - Configure length, focus areas, custom instructions
4. **Real-Time Progress** - Watch multi-stage pipeline with live updates (analysis → generation → validation; backend-controlled stages)
5. **ATS Scoring** - View keyword coverage and match percentage
6. **Recommendations** - Get actionable suggestions to improve resume
7. **Generation History** - Access previous generations
8. **Rate Limiting** - Handle 10 generations/hour limit gracefully

**Preference Management (NEW - Required for AI Generation):**
9. **Sample Resume Upload** - Upload PDF/DOCX resume for layout extraction
10. **Sample Cover Letter Upload** - Upload PDF/DOCX cover letter for writing style extraction
11. **Preference Setup Wizard** - First-time onboarding to configure generation preferences
12. **Example Resume Management** - View, delete, and set primary example resumes
13. **Layout Configuration** - Review and adjust extracted layout preferences (section order, bullet style)
14. **Writing Style Configuration** - Review and adjust extracted writing style (tone, formality, vocabulary)
15. **Generation Profile Settings** - Manage quality targets and generation behavior

### Core User Flows

#### Flow 1: First-Time Setup - Upload Sample Documents (NEW)
```
Prerequisites:
- User has created master profile (experiences, skills, education)
- User has NOT uploaded sample documents yet

User Journey:
1. User completes profile creation
2. App shows "Setup Preferences" prompt
3. User taps "Get Started"
4. Preference Setup Wizard appears with steps:
   
   STEP 1: Upload Sample Resume
   5. User taps "Upload Sample Resume"
   6. File picker opens (filter: PDF, DOCX, TXT)
   7. User selects well-formatted resume file
   8. Upload progress shown (0-100%)
   9. Backend extracts text from file
   10. LLM analyzes layout structure (3-5 seconds)
   11. Progress shown: "Analyzing layout preferences..."
   12. Success! Extracted preferences shown:
       - Section Order: [Summary, Experience, Education, Skills]
       - Bullet Style: "action_verb" (starts with strong verbs)
       - Content Density: "balanced" (3-5 bullets per role)
       - Contact Info Format: "header_left"
   13. User reviews preferences
   14. Optional: User can adjust preferences with toggles/dropdowns
   15. User taps "Continue"
   
   STEP 2: Upload Sample Cover Letter
   16. User taps "Upload Sample Cover Letter"
   17. File picker opens (filter: PDF, DOCX, TXT)
   18. User selects cover letter file
   19. Upload progress shown (0-100%)
   20. Backend extracts text from file
   21. LLM analyzes writing style (3-5 seconds)
   22. Progress shown: "Analyzing writing style..."
   23. Success! Extracted preferences shown:
       - Tone: "professional_enthusiastic" (7/10)
       - Formality Level: "business_professional" (8/10)
       - Sentence Complexity: "varied" (mix of short and complex)
       - Vocabulary Level: "advanced_professional"
       - Paragraph Length: 3-4 sentences average
   24. User reviews preferences
   25. Optional: User adjusts tone slider, formality level
   26. User taps "Complete Setup"
   
   27. Success screen: "Preferences Saved! Ready to Generate"
   28. User returned to main app

Data Flow:
Mobile → File picker → Select file → Upload via multipart/form-data → 
POST /api/v1/preferences/upload-sample-resume {file, is_primary: true} → 
Backend: Save file → Extract text → LLM analyzes structure → 
Create LayoutConfig entity → Save to DB → Return extraction result → 
Mobile: Display extracted preferences for review → 
User adjusts → PUT /preferences/generation-profile → 
Profile updated → Ready for generation

Backend Endpoints Used:
- POST /preferences/upload-sample-resume
- POST /preferences/upload-cover-letter
- PUT /preferences/generation-profile (to save adjustments)
```

#### Flow 2: Generate Resume from Job (Updated with Preferences)
```
User Journey:
1. User navigates to job detail screen
2. User taps "Generate Resume" button
3. Generation options screen appears
4. User selects template (Modern, Classic, Creative)
   Note: Templates now apply user's layout preferences from sample resume
5. User sets resume length (1 page, 2 pages)
6. Optional: User adds focus areas (e.g., "Leadership", "Cloud Architecture")
7. Optional: User adds custom instructions
8. User taps "Generate"
9. Progress screen shows with stage indicators (0/N stages as reported by backend)
10. Real-time polling updates progress every 2 seconds
11. Stage 1: "Analyzing job description and matching content..." (40% complete)
    - Uses user's master profile as content source
    - Applies job requirements for ranking
12. Stage 2: "Generating tailored resume and validating quality..." (100% complete)
    - Applies user's layout preferences from sample resume
    - Applies user's writing style from sample cover letter
    - Validates ATS compliance
13. Success! Result screen shows:
    - ATS Score: 87%
    - Match Percentage: 82%
    - Keyword Coverage: 15/18 keywords matched
    - Recommendations list
    - Consistency Score: 92% (how well generation matched sample preferences)
14. User can: View PDF, Download, Share, Regenerate with changes

Data Flow:
Mobile → POST /generations/resume {profile_id, job_id, options} → 
Backend: Load master profile + sample preferences + job requirements → 
Stage 1: LLM analyzes and ranks content (3s) → 
Stage 2: LLM generates using layout/style preferences (5s) → 
Generation complete (status: completed) → 
Mobile polls GET /generations/{id} every 2s → 
Progress updates received → Final status: completed → 
Mobile fetches result → Display ATS score and PDF

Key Difference from Original Flow:
- Generation now uses uploaded sample preferences
-- Backend reports the pipeline stages; the UI presents whatever number of stages are returned (default backend stages may be 5)
- Layout/style consistency tracked and reported
```

#### Flow 3: Manage Example Resumes (NEW)
```
User Journey:
1. User opens "Settings" or "Profile" screen
2. User taps "Generation Preferences"
3. Screen shows two sections:
   - Example Resumes (count badge: 2)
   - Writing Style (1 cover letter uploaded)
4. User taps "Example Resumes"
5. List displays uploaded resumes:
   - "Software Engineer Resume.pdf" (Primary) ⭐
     Uploaded: Oct 15, 2025
     Layout: Modern, Left-aligned
   - "Senior Developer Resume.docx"
     Uploaded: Nov 2, 2025
     Layout: Classic, Two-column
6. User can:
   - Tap card to preview extracted preferences
   - Swipe to delete (confirmation dialog)
   - Tap star icon to set as primary
   - Tap "Upload New" to add another example
7. User taps star on "Senior Developer Resume.docx"
8. Confirmation: "Set as Primary Example Resume?"
9. User confirms
10. Backend updates: is_primary flag + updates generation profile
11. Star moves to new primary resume
12. Toast: "Primary example updated. Future generations will use this layout."

Data Flow:
Mobile → GET /api/v1/preferences/example-resumes → 
Backend returns list with metadata → Display cards → 
User sets primary → POST /preferences/example-resumes/{id}/set-primary → 
Backend updates is_primary flags + updates generation profile → 
Success response → Refresh list
```

#### Flow 4: View Generation History
```
User Journey:
1. User opens "Generations" screen from main navigation
2. List displays previous generations with cards showing:
   - Job title and company
   - Document type (Resume/Cover Letter)
   - ATS score badge
   - Date generated
   - Status (Completed, In Progress, Failed)
   - NEW: Consistency Score badge (how well it matched preferences)
3. User can filter by:
   - Document type (Resume, Cover Letter)
   - Status (Completed, In Progress, Failed)
   - Job (dropdown of saved jobs)
4. User taps on completed generation
5. Generation detail screen shows full result
6. User can download PDF or regenerate with different options

Data Flow:
Mobile → GET /generations?limit=20&offset=0 → Backend returns list → Display cards → User taps card → Navigate to result screen
```

#### Flow 5: Handle Rate Limit
```
User Journey:
1. User attempts 11th generation in same hour
2. Backend returns 429 Too Many Requests with retry_after: 1800
3. Mobile shows friendly dialog:
   "Generation Limit Reached
   
   You've generated 10 resumes this hour. 
   Please try again in 30 minutes.
   
   Current usage: 10/10 per hour
   Resets at: 3:45 PM"
4. User taps "OK" to dismiss
5. "Generate" buttons show disabled state with countdown
6. After 30 minutes, countdown expires and buttons re-enable

Error Handling:
catch DioError with status 429 → Extract retry_after from response → Calculate reset time → Show dialog with human-readable time → Disable generation buttons → Start countdown timer → Re-enable after countdown
```

---

## API Integration

### Backend Connection
```
Base URL: http://10.0.2.2:8000/api/v1
Authentication: JWT Bearer token in Authorization header
Polling Interval: 2 seconds for progress updates
File Upload: multipart/form-data for sample documents
```

### Endpoints

**Generation Endpoints:**

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/generations/resume` | POST | Start resume generation | `{profile_id, job_id, options}` | Generation object (201) |
| `/generations/cover-letter` | POST | Start cover letter generation | `{profile_id, job_id, options}` | Generation object (201) |
| `/generations/{id}` | GET | Get generation status | - | Generation with progress (200) |
| `/generations/{id}/result` | GET | Get final result | - | Result with content (200) |
| `/generations` | GET | List generations | Query params: `status`, `job_id`, `limit`, `offset` | Generations array (200) |
| `/generations/{id}` | DELETE | Cancel generation | - | No content (204) |
| `/generations/templates` | GET | List templates | - | Templates array (200) |

**Preference Endpoints (NEW):**

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/preferences/upload-sample-resume` | POST | Upload sample resume for layout extraction | `multipart/form-data: {file, is_primary}` | Extraction result (200) |
| `/preferences/upload-cover-letter` | POST | Upload cover letter for style extraction | `multipart/form-data: {file}` | Extraction result (200) |
| `/preferences/generation-profile` | GET | Get user's generation profile | - | Profile with preferences (200) |
| `/preferences/generation-profile` | PUT | Update generation profile settings | `{layout_config_id, writing_style_config_id, targets}` | Updated profile (200) |
| `/preferences/example-resumes` | GET | List user's example resumes | - | Example resumes array (200) |
| `/preferences/example-resumes/{resume_id}` | DELETE | Delete example resume | - | No content (204) |
| `/preferences/example-resumes/{resume_id}/set-primary` | POST | Set primary example resume | - | Success response (200) |

### Error Codes

| Code | Meaning | User Action |
|------|---------|-------------|
| 400 | Invalid profile_id or job_id | Show validation error |
| 403 | Not authorized (not owner of profile/job) | Show error message |
| 404 | Generation, profile, or job not found | Show "Not found" message |
| 413 | File too large (>5MB) | Show "File size limit exceeded" message |
| 415 | Unsupported file type (not PDF/DOCX/TXT) | Show "Please upload PDF, DOCX, or TXT" message |
| 422 | Pipeline stage failed OR text extraction failed | Show error with retry option |
| 429 | Rate limit exceeded (>10/hour) | Show rate limit dialog with countdown |
| 500 | Server error | Show generic error with retry |

---

## Data Models

### Preference Models (NEW)

#### ExampleResume Model

Navigation: From settings/preferences screen to example resume management

**Purpose**: Tracks uploaded sample resumes for layout extraction

**Required Dependencies:**
- `file_picker: ^6.0.0` - For file selection UI
- `dio: ^5.0.0` - For multipart file upload
- `path: ^1.8.0` - For file path manipulation

**File Upload Constraints:**
- Allowed formats: PDF, DOCX, TXT
- Max file size: 5 MB
- Upload method: multipart/form-data
- Backend endpoint: POST /api/v1/preferences/upload-sample-resume

**Dart Model:**
```dart
class ExampleResume {
  final String id;
  final int userId;
  final String filePath;
  final String originalFilename;
  final String layoutConfigId;
  final bool isPrimary;
  final String? fileHash;
  final DateTime uploadedAt;
  final int fileSize;
  final String fileType;

  const ExampleResume({
    required this.id,
    required this.userId,
    required this.filePath,
    required this.originalFilename,
    required this.layoutConfigId,
    required this.isPrimary,
    this.fileHash,
    required this.uploadedAt,
    required this.fileSize,
    required this.fileType,
  });

  factory ExampleResume.fromJson(Map<String, dynamic> json) {
    return ExampleResume(
      id: json['id'],
      userId: json['user_id'],
      filePath: json['file_path'],
      originalFilename: json['original_filename'],
      layoutConfigId: json['layout_config_id'],
      isPrimary: json['is_primary'],
      fileHash: json['file_hash'],
      uploadedAt: DateTime.parse(json['uploaded_at']),
      fileSize: json['file_size'],
      fileType: json['file_type'],
    );
  }
}
```

#### LayoutConfig Model

**Purpose**: Stores extracted layout preferences from sample resume

**Dart Model:**
```dart
class LayoutConfig {
  final String id;
  final int userId;
  final List<String> sectionOrder;
  final String bulletStyle;
  final String contentDensity;
  final String contactInfoFormat;
  final Map<String, dynamic> extractionMetadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const LayoutConfig({
    required this.id,
    required this.userId,
    required this.sectionOrder,
    required this.bulletStyle,
    required this.contentDensity,
    required this.contactInfoFormat,
    required this.extractionMetadata,
    required this.createdAt,
    required this.updatedAt,
  });

  factory LayoutConfig.fromJson(Map<String, dynamic> json) {
    return LayoutConfig(
      id: json['id'],
      userId: json['user_id'],
      sectionOrder: List<String>.from(json['section_order']),
      bulletStyle: json['bullet_style'],
      contentDensity: json['content_density'],
      contactInfoFormat: json['contact_info_format'],
      extractionMetadata: json['extraction_metadata'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  String get bulletStyleDisplay {
    switch (bulletStyle) {
      case 'action_verb':
        return 'Action Verb Focus';
      case 'results_focused':
        return 'Results-Focused';
      case 'hybrid':
        return 'Hybrid Style';
      default:
        return bulletStyle;
    }
  }

  String get densityDisplay {
    switch (contentDensity) {
      case 'concise':
        return 'Concise (2-3 bullets)';
      case 'balanced':
        return 'Balanced (4-5 bullets)';
      case 'detailed':
        return 'Detailed (6+ bullets)';
      default:
        return contentDensity;
    }
  }
}
```

#### WritingStyleConfig Model

**Purpose**: Stores extracted writing style from sample cover letter

**Dart Model:**
```dart
class WritingStyleConfig {
  final String id;
  final int userId;
  final String tone;
  final int toneLevel;
  final int formalityLevel;
  final String sentenceComplexity;
  final String vocabularyLevel;
  final int avgParagraphLength;
  final String sourceText;
  final Map<String, dynamic> extractionMetadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const WritingStyleConfig({
    required this.id,
    required this.userId,
    required this.tone,
    required this.toneLevel,
    required this.formalityLevel,
    required this.sentenceComplexity,
    required this.vocabularyLevel,
    required this.avgParagraphLength,
    required this.sourceText,
    required this.extractionMetadata,
    required this.createdAt,
    required this.updatedAt,
  });

  factory WritingStyleConfig.fromJson(Map<String, dynamic> json) {
    return WritingStyleConfig(
      id: json['id'],
      userId: json['user_id'],
      tone: json['tone'],
      toneLevel: json['tone_level'],
      formalityLevel: json['formality_level'],
      sentenceComplexity: json['sentence_complexity'],
      vocabularyLevel: json['vocabulary_level'],
      avgParagraphLength: json['avg_paragraph_length'],
      sourceText: json['source_text'] ?? '',
      extractionMetadata: json['extraction_metadata'] ?? {},
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  String get toneDisplay {
    switch (tone) {
      case 'professional':
        return 'Professional';
      case 'professional_enthusiastic':
        return 'Professional & Enthusiastic';
      case 'authoritative':
        return 'Authoritative';
      case 'conversational':
        return 'Conversational';
      default:
        return tone;
    }
  }

  String get formalityDisplay {
    if (formalityLevel >= 8) return 'Very Formal';
    if (formalityLevel >= 6) return 'Business Professional';
    if (formalityLevel >= 4) return 'Moderate';
    return 'Casual';
  }
}
```

#### UserGenerationProfile Model

**Purpose**: Aggregates user's generation preferences and settings

**Dart Model:**
```dart
class UserGenerationProfile {
  final String id;
  final int userId;
  final String? layoutConfigId;
  final String? writingStyleConfigId;
  final double targetAtsScore;
  final int maxBulletsPerRole;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UserGenerationProfile({
    required this.id,
    required this.userId,
    this.layoutConfigId,
    this.writingStyleConfigId,
    required this.targetAtsScore,
    required this.maxBulletsPerRole,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserGenerationProfile.fromJson(Map<String, dynamic> json) {
    return UserGenerationProfile(
      id: json['id'],
      userId: json['user_id'],
      layoutConfigId: json['layout_config_id'],
      writingStyleConfigId: json['writing_style_config_id'],
      targetAtsScore: (json['target_ats_score'] as num).toDouble(),
      maxBulletsPerRole: json['max_bullets_per_role'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  bool get hasLayoutPreferences => layoutConfigId != null;
  bool get hasStylePreferences => writingStyleConfigId != null;
  bool get isFullyConfigured => hasLayoutPreferences && hasStylePreferences;
}
```

---

### Generation Model (Existing - No Changes)

```dart
// lib/models/generation.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'generation.freezed.dart';
part 'generation.g.dart';

@freezed
class Generation with _$Generation {
  const factory Generation({
    required String id,
    required String profileId,
    required String jobId,
    required DocumentType documentType,
    required GenerationStatus status,
    required GenerationProgress progress,
    GenerationResult? result,
    String? errorMessage,
    @Default(0) int tokensUsed,
    double? generationTime,
    required DateTime createdAt,
    DateTime? completedAt,
    DateTime? startedAt,
    DateTime? updatedAt,
  }) = _Generation;

  factory Generation.fromJson(Map<String, dynamic> json) => _$GenerationFromJson(json);
}

@freezed
class Pagination with _$Pagination {
  const factory Pagination({
    required int total,
    required int limit,
    required int offset,
    required bool hasNext,
    required bool hasPrevious,
  }) = _Pagination;

  factory Pagination.fromJson(Map<String, dynamic> json) => _$PaginationFromJson(json);
}

enum GenerationStatus {
  @JsonValue('pending')
  pending,
  @JsonValue('generating')
  generating,
  @JsonValue('completed')
  completed,
  @JsonValue('failed')
  failed,
  @JsonValue('cancelled')
  cancelled,
}

enum DocumentType {
  @JsonValue('resume')
  resume,
  @JsonValue('cover_letter')
  coverLetter,
}

@freezed
class GenerationProgress with _$GenerationProgress {
  const factory GenerationProgress({
    required int currentStage,
    required int totalStages,
    required int percentage,
    String? stageName,
    String? stageDescription,
  }) = _GenerationProgress;

  factory GenerationProgress.fromJson(Map<String, dynamic> json) => 
      _$GenerationProgressFromJson(json);
}

const factory GenerationProgress.initial() = GenerationProgress(
  currentStage: 0,
  totalStages: 5,
  percentage: 0,
  stageName: null,
  stageDescription: 'Queued for processing',
);

@freezed
class GenerationResult with _$GenerationResult {
  const factory GenerationResult({
    required String documentId,
    required double atsScore,
    required int matchPercentage,
    required double keywordCoverage,
    required int keywordsMatched,
    required int keywordsTotal,
    required String pdfUrl,
    @Default([]) List<String> recommendations,
  }) = _GenerationResult;

  factory GenerationResult.fromJson(Map<String, dynamic> json) => 
      _$GenerationResultFromJson(json);
}

@freezed
class GenerationOptions with _$GenerationOptions {
  const factory GenerationOptions({
    @Default('modern') String template,
    @Default('one_page') String length,
    @Default([]) List<String> focusAreas,
    @Default(false) bool includeCoverLetter,
    String? customInstructions,
  }) = _GenerationOptions;

  factory GenerationOptions.fromJson(Map<String, dynamic> json) => 
      _$GenerationOptionsFromJson(json);

  Map<String, dynamic> toJson() => {
    'template': template,
    'length': length,
    'focus_areas': focusAreas,
    'include_cover_letter': includeCoverLetter,
    if (customInstructions != null) 'custom_instructions': customInstructions,
  };
}

@freezed
class Template with _$Template {
  const factory Template({
    required String id,
    required String name,
    required String description,
    required String previewUrl,
    required List<String> recommendedFor,
    required bool atsFriendly,
  }) = _Template;

  factory Template.fromJson(Map<String, dynamic> json) => 
      _$TemplateFromJson(json);
}

// Extension for UI helpers
extension GenerationExtensions on Generation {
  bool get isComplete => status == GenerationStatus.completed;
  bool get isFailed => status == GenerationStatus.failed;
  bool get isProcessing => status == GenerationStatus.generating || 
                          status == GenerationStatus.pending;
  bool get canCancel => isProcessing;

  String get statusDisplayText {
    switch (status) {
      case GenerationStatus.pending:
        return 'Queued';
      case GenerationStatus.generating:
        return 'Generating...';
      case GenerationStatus.completed:
        return 'Completed';
      case GenerationStatus.failed:
        return 'Failed';
      case GenerationStatus.cancelled:
        return 'Cancelled';
    }
  }

  Color get statusColor {
    switch (status) {
      case GenerationStatus.pending:
      case GenerationStatus.generating:
        return Colors.blue;
      case GenerationStatus.completed:
        return Colors.green;
      case GenerationStatus.failed:
      case GenerationStatus.cancelled:
        return Colors.red;
    }
  }
}
```

---

## Service Layer

### Generation API Client

```dart
// lib/services/api/generation_api_client.dart

import 'package:dio/dio.dart';
import '../../models/generation.dart';
import 'api_client.dart';

class GenerationApiClient {
  final ApiClient _client;

  GenerationApiClient(this._client);

  /// Start resume generation
  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    final response = await _client.post('/generations/resume', data: {
      'profile_id': profileId,
      'job_id': jobId,
      if (options != null) 'options': options.toJson(),
    });
    return Generation.fromJson(response.data);
  }

  /// Start cover letter generation
  Future<Generation> startCoverLetterGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    final response = await _client.post('/generations/cover-letter', data: {
      'profile_id': profileId,
      'job_id': jobId,
      if (options != null) 'options': options.toJson(),
    });
    return Generation.fromJson(response.data);
  }

  /// Get generation status (for polling)
  Future<Generation> getGenerationStatus(String id) async {
    final response = await _client.get('/generations/$id');
    return Generation.fromJson(response.data);
  }

  /// Get final generation result
  Future<GenerationResult> getGenerationResult(String id) async {
    final response = await _client.get('/generations/$id/result');
    return GenerationResult.fromJson(response.data);
  }

  /// Regenerate with updated options
  Future<Generation> regenerateGeneration({
    required String id,
    GenerationOptions? options,
  }) async {
    final response = await _client.post('/generations/$id/regenerate', data: {
      if (options != null) 'options': options.toJson(),
    });
    return Generation.fromJson(response.data);
  }

  /// List user's generations
  Future<(List<Generation>, Pagination)> getGenerations({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/generations', queryParameters: {
      if (jobId != null) 'job_id': jobId,
      if (status != null) 'status': status.name,
      if (documentType != null) 'document_type': documentType.name,
      'limit': limit,
      'offset': offset,
    });

    final generations = (response.data['generations'] as List)
        .map((json) => Generation.fromJson(json))
        .toList();
    final pagination = Pagination.fromJson(response.data['pagination']);

    return (generations, pagination);
  }

  /// Cancel ongoing generation
  Future<void> cancelGeneration(String id) async {
    await _client.delete('/generations/$id');
  }

  /// Get available templates
  Future<List<Template>> getTemplates() async {
    final response = await _client.get('/generations/templates');
    return (response.data['templates'] as List)
        .map((json) => Template.fromJson(json))
        .toList();
  }

  /// Poll generation until completion (returns stream)
  Stream<Generation> pollGeneration(
    String id, {
    Duration interval = const Duration(seconds: 2),
    int maxAttempts = 60, // 2 minutes max (20x expected duration of 6s)
  }) async* {
    int attempts = 0;
    while (attempts < maxAttempts) {
      final generation = await getGenerationStatus(id);
      yield generation;

      if (!generation.isProcessing) {
        break; // Completed, failed, or cancelled
      }

      await Future.delayed(interval);
      attempts++;
    }

    if (attempts >= maxAttempts) {
      throw TimeoutException('Generation polling timeout after 2 minutes');
    }
  }
}
```

---

## State Management

### Generation Provider (Riverpod)

```dart
// lib/providers/generation_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/generation.dart';
import '../services/api/generation_api_client.dart';

// Provider for generation API client
final generationApiClientProvider = Provider<GenerationApiClient>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return GenerationApiClient(apiClient);
});

// Provider for templates
final templatesProvider = FutureProvider<List<Template>>((ref) async {
  final client = ref.watch(generationApiClientProvider);
  return client.getTemplates();
});

// Provider for generation list
final generationsProvider = FutureProvider.autoDispose
    .family<(List<Generation>, Pagination), GenerationFilters>(
  (ref, filters) async {
    final client = ref.watch(generationApiClientProvider);
    return client.getGenerations(
      jobId: filters.jobId,
      status: filters.status,
      documentType: filters.documentType,
      limit: filters.limit,
      offset: filters.offset,
    );
  },
);

// Provider for single generation with polling
final generationStreamProvider = StreamProvider.autoDispose
    .family<Generation, String>((ref, generationId) {
  final client = ref.watch(generationApiClientProvider);
  return client.pollGeneration(generationId);
});

// State notifier for generation creation
class GenerationNotifier extends StateNotifier<AsyncValue<Generation?>> {
  final GenerationApiClient _client;

  GenerationNotifier(this._client) : super(const AsyncValue.data(null));

  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    state = const AsyncValue.loading();
    try {
      final generation = await _client.startResumeGeneration(
        profileId: profileId,
        jobId: jobId,
        options: options,
      );
      state = AsyncValue.data(generation);
      return generation;
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
      rethrow;
    }
  }

  Future<void> cancelGeneration(String id) async {
    await _client.cancelGeneration(id);
    state = const AsyncValue.data(null);
  }
}

final generationNotifierProvider =
    StateNotifierProvider<GenerationNotifier, AsyncValue<Generation?>>((ref) {
  final client = ref.watch(generationApiClientProvider);
  return GenerationNotifier(client);
});

// Filter model
class GenerationFilters {
  final String? jobId;
  final GenerationStatus? status;
  final DocumentType? documentType;
  final int limit;
  final int offset;

  const GenerationFilters({
    this.jobId,
    this.status,
    this.documentType,
    this.limit = 20,
    this.offset = 0,
  });
}
```

---

## UI Components

### 1. Generation Options Screen

```dart
// lib/screens/generation/generation_options_screen.dart

class GenerationOptionsScreen extends ConsumerStatefulWidget {
  final Job job;
  final Profile profile;

  const GenerationOptionsScreen({
    required this.job,
    required this.profile,
  });

  @override
  ConsumerState<GenerationOptionsScreen> createState() => 
      _GenerationOptionsScreenState();
}

class _GenerationOptionsScreenState 
    extends ConsumerState<GenerationOptionsScreen> {
  String _selectedTemplate = 'modern';
  String _selectedLength = 'one_page';
  List<String> _focusAreas = [];
  final TextEditingController _customInstructionsController = 
      TextEditingController();

  @override
  Widget build(BuildContext context) {
    final templatesAsync = ref.watch(templatesProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text('Generate Resume'),
      ),
      body: templatesAsync.when(
        data: (templates) => SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Job Info Card
              _JobInfoCard(job: widget.job),
              SizedBox(height: 24),

              // Template Selection
              Text('Template', style: Theme.of(context).textTheme.titleMedium),
              SizedBox(height: 12),
              _TemplateSelector(
                templates: templates,
                selected: _selectedTemplate,
                onSelect: (template) => setState(() => _selectedTemplate = template),
              ),
              SizedBox(height: 24),

              // Length Selection
              Text('Resume Length', style: Theme.of(context).textTheme.titleMedium),
              SizedBox(height: 12),
              SegmentedButton<String>(
                segments: [
                  ButtonSegment(value: 'one_page', label: Text('1 Page')),
                  ButtonSegment(value: 'two_page', label: Text('2 Pages')),
                ],
                selected: {_selectedLength},
                onSelectionChanged: (Set<String> selection) {
                  setState(() => _selectedLength = selection.first);
                },
              ),
              SizedBox(height: 24),

              // Focus Areas (Optional)
              Text('Focus Areas (Optional)', 
                   style: Theme.of(context).textTheme.titleMedium),
              SizedBox(height: 8),
              Text('Emphasize specific skills or experiences',
                   style: Theme.of(context).textTheme.bodySmall),
              SizedBox(height: 12),
              _FocusAreasInput(
                focusAreas: _focusAreas,
                onChanged: (areas) => setState(() => _focusAreas = areas),
              ),
              SizedBox(height: 24),

              // Custom Instructions (Optional)
              Text('Custom Instructions (Optional)', 
                   style: Theme.of(context).textTheme.titleMedium),
              SizedBox(height: 12),
              TextField(
                controller: _customInstructionsController,
                decoration: InputDecoration(
                  hintText: 'e.g., Highlight leadership experience',
                  border: OutlinedInputBorder(),
                ),
                maxLines: 3,
                maxLength: 500,
              ),
              SizedBox(height: 32),

              // Generate Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _generateResume,
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: Text('Generate Resume'),
                  ),
                ),
              ),
            ],
          ),
        ),
        loading: () => Center(child: CircularProgressIndicator()),
        error: (error, stack) => ErrorView(error: error),
      ),
    );
  }

  Future<void> _generateResume() async {
    try {
      final options = GenerationOptions(
        template: _selectedTemplate,
        length: _selectedLength,
        focusAreas: _focusAreas,
        customInstructions: _customInstructionsController.text.isEmpty 
            ? null 
            : _customInstructionsController.text,
      );

      final generation = await ref
          .read(generationNotifierProvider.notifier)
          .startResumeGeneration(
            profileId: widget.profile.id,
            jobId: widget.job.id,
            options: options,
          );

      // Navigate to progress screen
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => GenerationProgressScreen(
              generationId: generation.id,
            ),
          ),
        );
      }
    } on DioError catch (e) {
      if (e.response?.statusCode == 429) {
        _showRateLimitDialog(e.response?.data);
      } else {
        _showErrorDialog(e.message ?? 'Failed to start generation');
      }
    }
  }

  void _showRateLimitDialog(Map<String, dynamic>? data) {
    final retryAfter = data?['retry_after'] ?? 3600;
    final resetTime = DateTime.now().add(Duration(seconds: retryAfter));
    
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Generation Limit Reached'),
        content: Text(
          'You\'ve generated 10 resumes this hour.\n\n'
          'Please try again at ${DateFormat('h:mm a').format(resetTime)}',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }
}
```

### 2. Generation Progress Screen

```dart
// lib/screens/generation/generation_progress_screen.dart

class GenerationProgressScreen extends ConsumerWidget {
  final String generationId;

  const GenerationProgressScreen({required this.generationId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final generationStream = ref.watch(generationStreamProvider(generationId));

    return generationStream.when(
      data: (generation) {
        // Navigate to result screen when complete
        if (generation.isComplete) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(
                builder: (_) => GenerationResultScreen(
                  generation: generation,
                ),
              ),
            );
          });
          return SizedBox(); // Placeholder during transition
        }

        // Show error screen if failed
        if (generation.isFailed) {
          return Scaffold(
            appBar: AppBar(title: Text('Generation Failed')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 64, color: Colors.red),
                  SizedBox(height: 16),
                  Text(
                    'Generation Failed',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  SizedBox(height: 8),
                  Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      generation.errorMessage ?? 'An error occurred',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ),
                  SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text('Go Back'),
                  ),
                ],
              ),
            ),
          );
        }

        // Show progress
        return Scaffold(
          appBar: AppBar(
            title: Text('Generating Resume'),
            actions: [
              if (generation.canCancel)
                TextButton(
                  onPressed: () async {
                    final confirmed = await _showCancelDialog(context);
                    if (confirmed == true) {
                      await ref
                          .read(generationNotifierProvider.notifier)
                          .cancelGeneration(generation.id);
                      Navigator.pop(context);
                    }
                  },
                  child: Text('Cancel'),
                ),
            ],
          ),
          body: Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Progress Circle
                  SizedBox(
                    width: 200,
                    height: 200,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        CircularProgressIndicator(
                          value: generation.progress.percentage / 100,
                          strokeWidth: 8,
                        ),
                        Text(
                          '${generation.progress.percentage}%',
                          style: Theme.of(context).textTheme.headlineMedium,
                        ),
                      ],
                    ),
                  ),
                  SizedBox(height: 32),

                  // Stage Name
                  Text(
                    generation.progress.stageName ?? 'Processing...',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 8),

                  // Stage Description
                  Text(
                    generation.progress.stageDescription ?? '',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                    textAlign: TextAlign.center,
                  ),
                  SizedBox(height: 32),

                  // Stage Indicator
                  _StageIndicator(
                    currentStage: generation.progress.currentStage,
                    totalStages: generation.progress.totalStages,
                  ),
                ],
              ),
            ),
          ),
        );
      },
      loading: () => Scaffold(
        appBar: AppBar(title: Text('Generating Resume')),
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
              Text('Failed to load generation status'),
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

  Future<bool?> _showCancelDialog(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Cancel Generation?'),
        content: Text('Are you sure you want to cancel this generation?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text('Yes, Cancel'),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
          ),
        ],
      ),
    );
  }
}

// Stage indicator widget
class _StageIndicator extends StatelessWidget {
  final int currentStage;
  final int totalStages;

  const _StageIndicator({
    required this.currentStage,
    required this.totalStages,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(totalStages, (index) {
        final stage = index + 1;
        final isComplete = stage <= currentStage;
        final isCurrent = stage == currentStage;

        return Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isComplete 
                    ? Theme.of(context).colorScheme.primary
                    : Colors.grey[300],
                border: isCurrent
                    ? Border.all(
                        color: Theme.of(context).colorScheme.primary,
                        width: 2,
                      )
                    : null,
              ),
              child: Center(
                child: isComplete
                    ? Icon(Icons.check, size: 16, color: Colors.white)
                    : Text(
                        '$stage',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
            ),
            if (index < totalStages - 1)
              Container(
                width: 24,
                height: 2,
                color: isComplete
                    ? Theme.of(context).colorScheme.primary
                    : Colors.grey[300],
              ),
          ],
        );
      }),
    );
  }
}
```

### 3. Generation Result Screen

```dart
// lib/screens/generation/generation_result_screen.dart

class GenerationResultScreen extends ConsumerWidget {
  final Generation generation;

  const GenerationResultScreen({required this.generation});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final result = generation.result!;

    return Scaffold(
      appBar: AppBar(
        title: Text('Generation Complete'),
        actions: [
          IconButton(
            icon: Icon(Icons.share),
            onPressed: () => _shareResume(context, result),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Success Icon
            Center(
              child: Icon(
                Icons.check_circle,
                size: 64,
                color: Colors.green,
              ),
            ),
            SizedBox(height: 16),
            Center(
              child: Text(
                'Resume Generated Successfully!',
                style: Theme.of(context).textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
            ),
            SizedBox(height: 32),

            // ATS Score Card
            _ATSScoreCard(result: result),
            SizedBox(height: 16),

            // Match Stats
            _MatchStatsCard(result: result),
            SizedBox(height: 16),

            // Recommendations
            if (result.recommendations.isNotEmpty) ...[
              Text(
                'Recommendations',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 12),
              _RecommendationsCard(recommendations: result.recommendations),
              SizedBox(height: 16),
            ],

            // Actions
            SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _viewPDF(context, result),
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
                onPressed: () => _downloadPDF(context, result),
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
    );
  }

  Future<void> _viewPDF(BuildContext context, GenerationResult result) async {
    // Navigate to document viewer
    // Implementation depends on document feature
  }

  Future<void> _downloadPDF(BuildContext context, GenerationResult result) async {
    // Download PDF implementation
  }

  Future<void> _shareResume(BuildContext context, GenerationResult result) async {
    // Share PDF implementation
  }
}

// ATS Score Card Widget
class _ATSScoreCard extends StatelessWidget {
  final GenerationResult result;

  const _ATSScoreCard({required this.result});

  @override
  Widget build(BuildContext context) {
    final scorePercentage = (result.atsScore * 100).toInt();
    final color = _getScoreColor(result.atsScore);

    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Row(
          children: [
            // Score Circle
            SizedBox(
              width: 80,
              height: 80,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: result.atsScore,
                    strokeWidth: 8,
                    valueColor: AlwaysStoppedAnimation<Color>(color),
                    backgroundColor: Colors.grey[300],
                  ),
                  Text(
                    '$scorePercentage%',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
            SizedBox(width: 16),
            // Score Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ATS Score',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  SizedBox(height: 4),
                  Text(
                    _getScoreLabel(result.atsScore),
                    style: TextStyle(color: color, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 4),
                  Text(
                    'Your resume is ${_getScoreDescription(result.atsScore)}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 0.8) return Colors.green;
    if (score >= 0.6) return Colors.orange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    return 'Needs Improvement';
  }

  String _getScoreDescription(double score) {
    if (score >= 0.8) return 'highly optimized for ATS systems';
    if (score >= 0.6) return 'well-optimized for ATS systems';
    return 'could be improved for better ATS compatibility';
  }
}
```

---

## Error Handling

### Rate Limiting
```dart
Future<void> _handleRateLimit(DioError error) async {
  if (error.response?.statusCode == 429) {
    final retryAfter = error.response?.data['retry_after'] ?? 3600;
    final resetTime = DateTime.now().add(Duration(seconds: retryAfter));
    
    // Store rate limit info in local state
    await _storageService.setRateLimitReset(resetTime);
    
    // Show user-friendly message
    _showRateLimitDialog(resetTime);
    
    // Disable generation buttons until reset
    _disableGenerationButtons(resetTime);
  }
}
```

### Pipeline Failures
```dart
if (generation.isFailed) {
  // Show error with retry option
  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: Text('Generation Failed'),
      content: Text(generation.errorMessage ?? 'An error occurred'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            _retryGeneration();
          },
          child: Text('Retry'),
        ),
      ],
    ),
  );
}
```

---

## Performance Considerations

1. **Polling Optimization**: 2-second intervals, stop on completion
2. **Memory Management**: Cancel streams when leaving progress screen
3. **Network Efficiency**: Only poll when app is active
4. **Local Caching**: Cache generation list, refresh on pull
5. **Background Handling**: Continue polling if app backgrounded

---

## Testing Strategy

### Unit Tests
- Generation model serialization
- Progress calculation logic
- Rate limit calculation
- Error handling

### Widget Tests
- Generation options form validation
- Progress screen updates
- Result screen display
- Rate limit dialog

### Integration Tests
- Full generation flow (mock backend)
- Polling mechanism
- Cancellation flow
- Error recovery

---

## Security Considerations

1. **Token Refresh**: Handle expired JWT during long-running generations
2. **Result Ownership**: Verify user owns generation before displaying
3. **Rate Limit Bypass**: Prevent client-side rate limit circumvention
4. **Secure Storage**: Don't cache sensitive generation results locally

---

## Future Enhancements

1. **Push Notifications**: Notify when generation completes (background)
2. **Batch Generation**: Generate for multiple jobs at once
3. **Template Customization**: User-editable templates
4. **A/B Testing**: Compare multiple generations for same job
5. **Generation Analytics**: Track which templates perform best
