# Generation Feature

**At a Glance (For AI Agents)**
- **Feature Name**: V3 Generation (combined pipeline UI)
- **Primary Role**: End-to-end orchestration of sample upload, profile enhancement, rankings, and generation in Flutter.
- **Key Files**: `lib/providers/samples_provider.dart`, `lib/providers/generations_provider.dart`, `lib/services/api/generations_api_client.dart`, `lib/models/sample.dart`, `lib/models/generation.dart`, `lib/models/ranking.dart`
- **Backend Contract**: `../api-services/04-v3-generation-api.md` (10 endpoints: samples + rankings + generations + history)
- **Main Screens**: `GenerationOptionsScreen`, `GenerationProgressScreen`, `GenerationResultScreen`, `GenerationHistoryScreen`

**Related Docs (Navigation Hints)**
- Backend V3 API: `../api-services/04-v3-generation-api.md`
- AI-focused backend: `../api-services/04b-ai-generation-api.md`
- Mobile AI feature split: `04a-sample-upload-feature.md`, `04b-ai-generation-feature.md`
- Jobs and profiles: `03-job-browsing-feature.md`, `02-profile-management-feature.md`

**Key Field / Property Semantics**
- `Sample` model: Represents `sample_documents` rows; `contentText` / `fullText` hold uploaded text used by LLM.
- `Generation` model: Represents `generations` rows; `documentType`, `contentText`, `atsScore`, and `metadata` drive UI.
- `Ranking` / `RankedItem`: Mirror backend ranking payloads and feed into resume/cover-letter generation stages.
- `GenerationsState` / `SamplesState`: Front-end aggregation of backend state plus UI-only progress/error fields.
- `GenerationsApiClient` methods: Map to all V3 endpoints (`/samples/*`, `/profile/enhance`, `/rankings/*`, `/generations/*`, `/generations/history`).

**Backend API**: [V3 Generation API](../api-services/04-v3-generation-api.md)
**Base Path**: `/api/v1`
**Status**: ✅ Fully Implemented  
**Provider Architecture**: Separated into `samples_provider` (uploads) and `generations_provider` (generation logic)
**Last Updated**: November 2025

---

## Overview

The Generation feature is the core AI-powered functionality of JobWise. It allows users to generate tailored resumes and cover letters for specific job postings using real Groq LLM integration.

**Architecture Note**: Sample upload handling and document generation logic are now separated into two dedicated providers:
- **samples_provider.dart**: Manages resume/cover letter sample uploads using V3 Generation API
- **generations_provider.dart**: Handles document generation, progress tracking, and history

### User Stories

**As a user**, I want to:
- Upload sample resumes and cover letters to teach the AI my writing style
- Enhance my profile content using AI
- Generate tailored resumes for specific jobs in <1 second
- Generate personalized cover letters in 3-5 seconds
- View my generation history
- See ATS (Applicant Tracking System) scores for generated documents

---

## Screens

### 1. GenerationOptionsScreen

**Route**: `/generate`
**File**: `lib/screens/generation/generation_options_screen.dart`

**Context**: User navigates here from JobDetailScreen or HomeScreen

**UI Components**:
- Job info header (company, title)
- Sample documents section:
  - Resume sample indicator (uploaded/not uploaded)
  - Cover letter sample indicator
  - "Upload Samples" button
- Profile status:
  - "Enhanced" badge if profile has AI enhancements
  - "Enhance Now" button if not enhanced
- Generation options:
  - "Generate Resume" button
  - "Generate Cover Letter" button
  - "Generate Both" button (batch)
- Resume customization (collapsible):
  - Max experiences slider (1-10, default 5)
  - Max projects slider (0-5, default 3)
  - Include professional summary toggle
  - Include skills section toggle

**User Flow**:
```
1. User selects a job
2. Navigate to GenerationOptionsScreen
3. Check if samples uploaded:
   - If no → show "Upload samples for better results" banner
4. Check if profile enhanced:
   - If no → show "Enhance profile" prompt
5. User taps "Generate Resume"
6. Navigate to GenerationProgressScreen
```

### 2. GenerationProgressScreen

**Route**: `/generate/progress`
**File**: `lib/screens/generation/generation_progress_screen.dart`

**UI Components**:
- Progress indicator (linear or circular)
- Stage labels:
  - "Analyzing job requirements..." (if ranking needed)
  - "Selecting relevant content..."
  - "Generating document..."
  - "Calculating ATS score..."
- Estimated time remaining
- Cancel button

**Real-time Progress Updates**:
```dart
// Resume generation stages (no LLM, fast)
1. "Analyzing job requirements" → 20% (1-2s) [if ranking needed]
2. "Selecting relevant content" → 60% (<0.5s)
3. "Compiling resume" → 80% (<0.5s)
4. "Calculating ATS score" → 100% (<0.5s)
Total: <3s

// Cover letter generation stages (LLM-powered)
1. "Analyzing job requirements" → 20% (1-2s) [if ranking needed]
2. "Extracting writing style" → 40% (1s)
3. "Generating cover letter" → 80% (3-5s LLM call)
4. "Calculating ATS score" → 100% (<0.5s)
Total: 5-8s
```

**User Flow**:
```
1. Show progress screen
2. Call ranking API (if not cached)
3. Call generation API (resume or cover letter)
4. Update progress in real-time
5. On completion → navigate to GenerationResultScreen
6. On error → show error dialog with retry option
```

### 3. GenerationResultScreen

**Route**: `/generate/result/:id`
**File**: `lib/screens/generation/generation_result_screen.dart`

**UI Components**:
- Document header:
  - Document type badge (Resume / Cover Letter)
  - Job title reference
  - Generation timestamp
  - ATS score badge (with color coding)
- Document content:
  - Scrollable text view
  - Keyword highlighting from job
- Action buttons:
  - "Copy to Clipboard" button
  - "Share" button
  - "Export to PDF" button (navigates to export flow)
  - "Regenerate" button (with confirmation)

**ATS Score Display**:
```dart
class ATSScoreBadge extends StatelessWidget {
  final double score;

  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getColor(score),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text('ATS Score', style: TextStyle(fontSize: 12)),
          Text('${score.toInt()}%', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
          Text(_getMessage(score), style: TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  Color _getColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }

  String _getMessage(double score) {
    if (score >= 80) return 'Excellent!';
    if (score >= 60) return 'Good';
    return 'Needs improvement';
  }
}
```

**User Flow**:
```
1. Display generated document
2. Show ATS score
3. User taps "Copy to Clipboard" → copy success message
4. User taps "Export to PDF" → navigate to template selection
5. User taps "Regenerate" → confirm → call regeneration API
```

### 4. GenerationHistoryScreen

**Route**: `/history`
**File**: `lib/screens/generation/generation_history_screen.dart`

**UI Components**:
- Filter tabs (All / Resumes / Cover Letters)
- Sort dropdown (Recent / Oldest / Highest ATS Score)
- Generation cards:
  - Document type icon
  - Job title
  - Generation date
  - ATS score badge
  - "View" button
- Empty state ("No generations yet")

**User Flow**:
```
1. Fetch generation history
2. Display list of generation cards
3. User taps filter → filter list
4. User taps card → navigate to GenerationResultScreen
5. Pull to refresh
```

---

## Backend API Integration

### API Endpoints (10 total)

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
  final sample = await generationsApiClient.uploadSample(
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

#### 2. POST /api/v1/profile/enhance - Enhance Profile

```dart
final result = await generationsApiClient.enhanceProfile(
  profileId: profileId,
  sampleIds: [sampleId], // Optional: specific samples to use
);
```

Request:
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "sample_ids": ["sample-uuid-1"]
}
```

Response:
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "enhanced_summary": "Innovative software engineer with proven track record...",
  "enhanced_experiences_count": 3,
  "enhanced_projects_count": 2,
  "processing_time_ms": 3240,
  "message": "Profile enhanced successfully using your writing style"
}
```

#### 3. POST /api/v1/rankings/create - Create Job-Specific Rankings

```dart
final rankings = await generationsApiClient.createRankings(
  jobId: jobId,
);
```

Request:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Response:
```json
{
  "ranking_id": "ranking-uuid",
  "job_id": "job-uuid",
  "ranked_experiences": [
    {
      "experience_id": "exp-uuid-1",
      "relevance_score": 0.95,
      "rank": 1,
      "reasoning": "Strong match with required Python and FastAPI skills"
    },
    {
      "experience_id": "exp-uuid-2",
      "relevance_score": 0.78,
      "rank": 2,
      "reasoning": "Relevant AWS cloud experience mentioned in job"
    }
  ],
  "ranked_projects": [
    {
      "project_id": "proj-uuid-1",
      "relevance_score": 0.88,
      "rank": 1,
      "reasoning": "Directly demonstrates FastAPI microservices architecture"
    }
  ],
  "processing_time_ms": 1820,
  "created_at": "2025-11-15T10:35:00Z"
}
```

#### 4. POST /api/v1/generations/resume - Generate Resume

```dart
final resume = await generationsApiClient.generateResume(
  jobId: jobId,
  maxExperiences: 5,
  maxProjects: 3,
  includeSummary: true,
);
```

Request:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "max_experiences": 5,
  "max_projects": 3,
  "include_summary": true
}
```

Response:
```json
{
  "id": "generation-uuid",
  "user_id": 1,
  "job_id": "job-uuid",
  "document_type": "resume",
  "content_text": "John Doe\nSenior Software Engineer\n\nPROFESSIONAL SUMMARY\n...",
  "ats_score": 87.5,
  "metadata": {
    "experiences_included": 5,
    "projects_included": 3,
    "skills_included": 12,
    "summary_included": true
  },
  "processing_time_ms": 450,
  "created_at": "2025-11-15T10:40:00Z"
}
```

**Speed**: <1 second (pure logic, no LLM)

#### 5. POST /api/v1/generations/cover-letter - Generate Cover Letter

```dart
final coverLetter = await generationsApiClient.generateCoverLetter(
  jobId: jobId,
  tone: 'professional', // professional, enthusiastic, formal
  length: 'medium', // short, medium, long
);
```

Request:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tone": "professional",
  "length": "medium"
}
```

Response:
```json
{
  "id": "generation-uuid",
  "user_id": 1,
  "job_id": "job-uuid",
  "document_type": "cover_letter",
  "content_text": "Dear Hiring Manager,\n\nI am writing to express my interest...",
  "ats_score": 82.0,
  "metadata": {
    "tone": "professional",
    "length": "medium",
    "word_count": 387,
    "paragraph_count": 4,
    "writing_style_applied": true
  },
  "processing_time_ms": 3420,
  "created_at": "2025-11-15T10:40:05Z"
}
```

**Speed**: 3-5 seconds (LLM-powered with llama-3.3-70b-versatile)

#### 6. GET /api/v1/samples - List Samples

```dart
final samples = await generationsApiClient.getSamples();
```

Response:
```json
{
  "items": [
    {
      "id": "sample-uuid",
      "document_type": "cover_letter",
      "original_filename": "my_cover_letter.txt",
      "word_count": 421,
      "is_active": true,
      "created_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### 7. GET /api/v1/samples/{id} - Get Sample Details

```dart
final sample = await generationsApiClient.getSample(sampleId);
```

Response:
```json
{
  "id": "sample-uuid",
  "user_id": 1,
  "document_type": "cover_letter",
  "original_filename": "my_cover_letter.txt",
  "content_text": "Full sample text content...",
  "word_count": 421,
  "character_count": 2847,
  "is_active": true,
  "created_at": "2025-11-15T10:30:00Z"
}
```

#### 8. DELETE /api/v1/samples/{id} - Delete Sample

```dart
await generationsApiClient.deleteSample(sampleId);
```

Response: `204 No Content`

#### 9. GET /api/v1/rankings/job/{job_id} - Get Job Rankings

```dart
final rankings = await generationsApiClient.getRankingsForJob(jobId);
```

Response: Same as create rankings response (cached)

#### 10. GET /api/v1/generations/history - Get Generation History

```dart
final history = await generationsApiClient.getGenerationHistory(
  documentType: 'resume', // optional filter
  limit: 20,
  offset: 0,
);
```

Request:
```
GET /api/v1/generations/history?document_type=resume&limit=20&offset=0
```

Response:
```json
{
  "items": [
    {
      "id": "generation-uuid",
      "job_id": "job-uuid",
      "job_title": "Senior Software Engineer",
      "company_name": "TechCorp",
      "document_type": "resume",
      "ats_score": 87.5,
      "created_at": "2025-11-15T10:40:00Z"
    }
  ],
  "total": 5,
  "limit": 20,
  "offset": 0
}
```

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
  final String? contentText;
  final int wordCount;
  final int characterCount;
  final bool isActive;
  final DateTime createdAt;

  Sample({
    required this.id,
    required this.userId,
    required this.documentType,
    required this.originalFilename,
    this.contentText,
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
      contentText: json['content_text'],
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
      'content_text': contentText,
      'word_count': wordCount,
      'character_count': characterCount,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
```

### Generation

**File**: `lib/models/generation.dart`

```dart
class Generation {
  final String id;
  final int userId;
  final String jobId;
  final String documentType; // 'resume' or 'cover_letter'
  final String contentText;
  final double atsScore;
  final Map<String, dynamic> metadata;
  final int processingTimeMs;
  final DateTime createdAt;

  Generation({
    required this.id,
    required this.userId,
    required this.jobId,
    required this.documentType,
    required this.contentText,
    required this.atsScore,
    required this.metadata,
    required this.processingTimeMs,
    required this.createdAt,
  });

  factory Generation.fromJson(Map<String, dynamic> json) {
    return Generation(
      id: json['id'],
      userId: json['user_id'],
      jobId: json['job_id'],
      documentType: json['document_type'],
      contentText: json['content_text'],
      atsScore: json['ats_score'].toDouble(),
      metadata: json['metadata'] ?? {},
      processingTimeMs: json['processing_time_ms'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'job_id': jobId,
      'document_type': documentType,
      'content_text': contentText,
      'ats_score': atsScore,
      'metadata': metadata,
      'processing_time_ms': processingTimeMs,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
```

### Ranking

**File**: `lib/models/ranking.dart`

```dart
class Ranking {
  final String rankingId;
  final String jobId;
  final List<RankedItem> rankedExperiences;
  final List<RankedItem> rankedProjects;
  final int processingTimeMs;
  final DateTime createdAt;

  Ranking({
    required this.rankingId,
    required this.jobId,
    required this.rankedExperiences,
    required this.rankedProjects,
    required this.processingTimeMs,
    required this.createdAt,
  });

  factory Ranking.fromJson(Map<String, dynamic> json) {
    return Ranking(
      rankingId: json['ranking_id'],
      jobId: json['job_id'],
      rankedExperiences: (json['ranked_experiences'] as List)
          .map((e) => RankedItem.fromJson(e))
          .toList(),
      rankedProjects: (json['ranked_projects'] as List)
          .map((e) => RankedItem.fromJson(e))
          .toList(),
      processingTimeMs: json['processing_time_ms'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class RankedItem {
  final String id; // experience_id or project_id
  final double relevanceScore;
  final int rank;
  final String reasoning;

  RankedItem({
    required this.id,
    required this.relevanceScore,
    required this.rank,
    required this.reasoning,
  });

  factory RankedItem.fromJson(Map<String, dynamic> json) {
    return RankedItem(
      id: json['experience_id'] ?? json['project_id'],
      relevanceScore: json['relevance_score'].toDouble(),
      rank: json['rank'],
      reasoning: json['reasoning'],
    );
  }
}
```

---

## State Management

**Architecture**: Separated providers for focused responsibilities

### SamplesProvider (`samples_provider.dart`)

Manages sample document uploads (resumes and cover letters) for teaching AI writing style.

**File**: `lib/providers/samples_provider.dart`

```dart
class SamplesState {
  final List<Sample> samples;
  final bool isLoading;
  final String? errorMessage;

  // Computed properties
  Sample? get activeResumeSample;
  Sample? get activeCoverLetterSample;
  List<Sample> get resumeSamples;
  List<Sample> get coverLetterSamples;
  bool get hasSamples;
  bool get hasResumeSample;
  bool get hasCoverLetterSample;
}

class SamplesNotifier extends StateNotifier<SamplesState> {
  Future<void> loadSamples();
  Future<Sample?> uploadSample({required PlatformFile file, required String documentType});
  Future<bool> deleteSample(String sampleId);
  void clearError();
}

final samplesProvider = StateNotifierProvider<SamplesNotifier, SamplesState>();
```

**Usage in Profile Screen**:
```dart
// Watch samples state
final samplesState = ref.watch(samplesProvider);
final resumeSample = samplesState.activeResumeSample;

// Upload new sample
final uploadedSample = await ref.read(samplesProvider.notifier).uploadSample(
  file: file,
  documentType: 'resume', // or 'cover_letter'
);

// Delete sample
await ref.read(samplesProvider.notifier).deleteSample(sampleId);
```

---

### GenerationsProvider (`generations_provider.dart`)

Handles document generation requests, progress tracking, and generation history.

**File**: `lib/providers/generations_provider.dart`

```dart
class GenerationsState {
  final List<GenerationListItem> history;
  final Generation? currentGeneration;
  final bool isGenerating;
  final double progress; // 0.0 to 1.0
  final String? currentStage;
  final String? errorMessage;

  // Computed properties
  List<GenerationListItem> get resumeHistory;
  List<GenerationListItem> get coverLetterHistory;
  bool get hasActiveGeneration;
}

class GenerationsNotifier extends StateNotifier<GenerationsState> {
  Future<Generation?> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  });
  
  Future<Generation?> generateCoverLetter({
    required String jobId,
    String tone = 'professional',
    String length = 'medium',
  });
  
  Future<void> fetchHistory({String? documentType, int limit = 20, int offset = 0});
  void clearError();
  void reset();
}

final generationsProvider = StateNotifierProvider<GenerationsNotifier, GenerationsState>();
```

**Usage in Generation Screens**:
```dart
// Watch generation state
final generationsState = ref.watch(generationsProvider);
final isGenerating = generationsState.isGenerating;
final progress = generationsState.progress;

// Generate resume
final generation = await ref.read(generationsProvider.notifier).generateResume(
  jobId: jobId,
  maxExperiences: 5,
);

// Generate cover letter
final generation = await ref.read(generationsProvider.notifier).generateCoverLetter(
  jobId: jobId,
  tone: 'professional',
);
```

---

### Legacy GenerationsState (Deprecated)

**Note**: The following GenerationsState class from the original docs is deprecated. Use the separated providers above.

<details>
<summary>Click to view deprecated GenerationsState (for reference only)</summary>

**File**: `lib/providers/generations/generations_state.dart`

```dart
class GenerationsState {
  final List<Sample> samples;
  final List<Generation> generationHistory;
  final Generation? currentGeneration;
  final Ranking? currentRanking;
  final bool isGenerating;
  final double progress;
  final String? currentStage;
  final String? errorMessage;

  GenerationsState({
    this.samples = const [],
    this.generationHistory = const [],
    this.currentGeneration,
    this.currentRanking,
    this.isGenerating = false,
    this.progress = 0.0,
    this.currentStage,
    this.errorMessage,
  });

  factory GenerationsState.initial() {
    return GenerationsState();
  }

  GenerationsState copyWith({
    List<Sample>? samples,
    List<Generation>? generationHistory,
    Generation? currentGeneration,
    Ranking? currentRanking,
    bool? isGenerating,
    double? progress,
    String? currentStage,
    String? errorMessage,
  }) {
    return GenerationsState(
      samples: samples ?? this.samples,
      generationHistory: generationHistory ?? this.generationHistory,
      currentGeneration: currentGeneration ?? this.currentGeneration,
      currentRanking: currentRanking ?? this.currentRanking,
      isGenerating: isGenerating ?? this.isGenerating,
      progress: progress ?? this.progress,
      currentStage: currentStage ?? this.currentStage,
      errorMessage: errorMessage,
    );
  }

  bool get hasSamples => samples.isNotEmpty;
  bool get hasResumeSample =>
      samples.any((s) => s.documentType == 'resume' && s.isActive);
  bool get hasCoverLetterSample =>
      samples.any((s) => s.documentType == 'cover_letter' && s.isActive);
}
```

### GenerationsNotifier

**File**: `lib/providers/generations/generations_notifier.dart`

```dart
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  final GenerationsApiClient _apiClient;

  GenerationsNotifier(this._apiClient) : super(GenerationsState.initial());

  Future<void> fetchSamples() async {
    try {
      final response = await _apiClient.getSamples();
      final samples = (response['items'] as List)
          .map((json) => Sample.fromJson(json))
          .toList();

      state = state.copyWith(samples: samples);
    } catch (e) {
      rethrow;
    }
  }

  Future<Sample> uploadSample({
    required PlatformFile file,
    required String documentType,
  }) async {
    try {
      final sample = await _apiClient.uploadSample(
        file: file,
        documentType: documentType,
      );

      // Refresh samples list
      await fetchSamples();

      return sample;
    } catch (e) {
      rethrow;
    }
  }

  Future<Generation> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements',
    );

    try {
      // Stage 1: Create/fetch rankings
      state = state.copyWith(progress: 0.2);
      Ranking ranking;
      try {
        ranking = await _apiClient.getRankingsForJob(jobId);
      } catch (e) {
        ranking = await _apiClient.createRankings(jobId: jobId);
      }
      state = state.copyWith(currentRanking: ranking);

      // Stage 2: Select content
      state = state.copyWith(
        progress: 0.6,
        currentStage: 'Selecting relevant content',
      );
      await Future.delayed(Duration(milliseconds: 500)); // Simulate

      // Stage 3: Generate resume
      state = state.copyWith(
        progress: 0.8,
        currentStage: 'Compiling resume',
      );
      final generation = await _apiClient.generateResume(
        jobId: jobId,
        maxExperiences: maxExperiences,
        maxProjects: maxProjects,
        includeSummary: includeSummary,
      );

      // Stage 4: Complete
      state = state.copyWith(
        progress: 1.0,
        currentStage: 'Complete',
        currentGeneration: generation,
        isGenerating: false,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<Generation> generateCoverLetter({
    required String jobId,
    String tone = 'professional',
    String length = 'medium',
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements',
    );

    try {
      // Stage 1: Create/fetch rankings
      state = state.copyWith(progress: 0.2);
      Ranking ranking;
      try {
        ranking = await _apiClient.getRankingsForJob(jobId);
      } catch (e) {
        ranking = await _apiClient.createRankings(jobId: jobId);
      }

      // Stage 2: Extract writing style
      state = state.copyWith(
        progress: 0.4,
        currentStage: 'Extracting writing style',
      );
      await Future.delayed(Duration(seconds: 1));

      // Stage 3: Generate cover letter (LLM call - 3-5s)
      state = state.copyWith(
        progress: 0.5,
        currentStage: 'Generating cover letter',
      );
      final generation = await _apiClient.generateCoverLetter(
        jobId: jobId,
        tone: tone,
        length: length,
      );

      // Stage 4: Complete
      state = state.copyWith(
        progress: 1.0,
        currentStage: 'Complete',
        currentGeneration: generation,
        isGenerating: false,
      );

      return generation;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> fetchGenerationHistory() async {
    try {
      final response = await _apiClient.getGenerationHistory();
      final history = (response['items'] as List)
          .map((json) => Generation.fromJson(json))
          .toList();

      state = state.copyWith(generationHistory: history);
    } catch (e) {
      rethrow;
    }
  }
}

// Provider
final generationsNotifierProvider =
    StateNotifierProvider<GenerationsNotifier, GenerationsState>(
  (ref) {
    final apiClient = ref.watch(generationsApiClientProvider);
    return GenerationsNotifier(apiClient);
  },
);
```

---

## Service Layer

### GenerationsApiClient

**File**: `lib/services/api/generations_api_client.dart`

```dart
class GenerationsApiClient {
  final Dio _dio;

  GenerationsApiClient(this._dio);

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

  Future<Map<String, dynamic>> enhanceProfile({
    required String profileId,
    List<String>? sampleIds,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/profile/enhance',
        data: {
          'profile_id': profileId,
          if (sampleIds != null) 'sample_ids': sampleIds,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Ranking> createRankings({required String jobId}) async {
    try {
      final response = await _dio.post(
        '/api/v1/rankings/create',
        data: {'job_id': jobId},
      );
      return Ranking.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Generation> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/generations/resume',
        data: {
          'job_id': jobId,
          'max_experiences': maxExperiences,
          'max_projects': maxProjects,
          'include_summary': includeSummary,
        },
      );
      return Generation.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Generation> generateCoverLetter({
    required String jobId,
    String tone = 'professional',
    String length = 'medium',
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/generations/cover-letter',
        data: {
          'job_id': jobId,
          'tone': tone,
          'length': length,
        },
      );
      return Generation.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getSamples() async {
    try {
      final response = await _dio.get('/api/v1/samples');
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Ranking> getRankingsForJob(String jobId) async {
    try {
      final response = await _dio.get('/api/v1/rankings/job/$jobId');
      return Ranking.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getGenerationHistory({
    String? documentType,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (documentType != null) queryParams['document_type'] = documentType;
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _dio.get(
        '/api/v1/generations/history',
        queryParameters: queryParams,
      );
      return response.data;
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
final generationsApiClientProvider = Provider<GenerationsApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return GenerationsApiClient(dio);
});
```

---

## UI Components

### Sample Upload Button

**File**: `lib/widgets/sample_upload_button.dart`

```dart
class SampleUploadButton extends StatelessWidget {
  final String documentType;
  final Function(PlatformFile) onFileSelected;

  const SampleUploadButton({
    required this.documentType,
    required this.onFileSelected,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: _pickFile,
      icon: Icon(Icons.upload_file),
      label: Text('Upload ${_getLabel()}'),
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

---

## Testing

### Unit Tests

```dart
test('GenerationsNotifier generates resume successfully', () async {
  final mockClient = MockGenerationsApiClient();
  final notifier = GenerationsNotifier(mockClient);

  when(mockClient.generateResume(jobId: any, maxExperiences: any))
      .thenAnswer((_) async => testGeneration);

  await notifier.generateResume(jobId: 'job-id');

  expect(notifier.state.currentGeneration, isNotNull);
  expect(notifier.state.isGenerating, false);
  expect(notifier.state.progress, 1.0);
});
```

---

## Performance Considerations

1. **Resume Generation**: <1 second (pure logic, no LLM)
2. **Cover Letter Generation**: 3-5 seconds (LLM-powered)
3. **Ranking Caching**: Rankings cached per job, reuse for multiple generations
4. **Progress Updates**: Real-time progress feedback for better UX

---

**Status**: ✅ Fully Implemented
**Screens**: 4 (Options, Progress, Result, History)
**API Endpoints**: 10 endpoints
**LLM Integration**: Groq API (llama-3.3-70b-versatile, llama-3.1-8b-instant)
**Dependencies**: dio, file_picker, flutter_riverpod
**Last Updated**: November 2025
