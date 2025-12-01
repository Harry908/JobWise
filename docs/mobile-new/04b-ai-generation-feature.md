# AI Generation Feature

**At a Glance (For AI Agents)**
- **Feature Name**: AI Generation (Flutter front-end)
- **Primary Role**: Drive profile enhancement, content ranking, resume and cover-letter generation, and history views.
- **Key Files**: `lib/providers/generations_provider.dart`, `lib/services/api/generations_api_client.dart`, `lib/models/generation.dart`, `lib/models/ranking.dart`
- **Backend Contract**: `../api-services/04b-ai-generation-api.md` (and `04-v3-generation-api.md` for shared endpoints)
- **Main Screens/Widgets**:
  - `GenerationOptionsScreen`, `GenerationProgressScreen`, `GenerationResultScreen`, `GenerationHistoryScreen`
  - `ATSScoreBadge`, `GenerationProgressIndicator`, `GenerationCard`

**Related Docs (Navigation Hints)**
- Backend AI API: `../api-services/04b-ai-generation-api.md`
- V3 Generation API: `../api-services/04-v3-generation-api.md`
- Sample Upload feature: `04a-sample-upload-feature.md`
- Job browsing feature: `03-job-browsing-feature.md`
- Profile feature: `02-profile-management-feature.md`

**Key Field / Property Semantics**
- `Generation.id` ↔ `generation_id`/`id`: Single generation run identifier used by history and exports.
- `Generation.documentType` ↔ `document_type`: `"resume"` or `"cover_letter"`; controls UI labels and export options.
- `Generation.contentText` ↔ `resume_text` / `cover_letter_text` / `content_text`: The actual generated body.
- `Generation.atsScore` / `atsFeedback`: Maps to backend ATS metrics; used by `ATSScoreBadge` and result screens.
- `Ranking.id` ↔ backend `id`: Links UI state to `job_content_rankings` rows for a `job_id`.
- `GenerationsState.progress` / `currentStage`: UI-only progress model that mirrors the backend pipeline stages.
- `GenerationsApiClient` methods: Straight mappings to `/profile/enhance`, `/rankings/create`, `/rankings/job/{job_id}`, `/generations/resume`, `/generations/cover-letter`, `/generations/history`.

**Backend API**: [AI Generation API](../api-services/04b-ai-generation-api.md)
**Base Path**: `/api/v1`
**Status**: ✅ Fully Implemented
**Provider**: `generations_provider.dart`
**LLM Integration**: Groq API (llama-3.3-70b-versatile, llama-3.1-8b-instant)
**Last Updated**: November 2025

---

## Overview

The AI Generation feature is the core AI-powered functionality of JobWise. It allows users to generate tailored resumes and cover letters for specific job postings using real Groq LLM integration.

**Architecture Note**: Document generation logic is separated from sample upload handling:
- **samples_provider.dart**: Manages resume/cover letter sample uploads (see [04a-sample-upload-feature.md](04a-sample-upload-feature.md))
- **generations_provider.dart**: Handles AI-powered document generation (this feature)

### User Stories

**As a user**, I want to:
- Enhance my profile content using AI and my writing style
- Generate tailored resumes for specific jobs in <1 second
- Generate personalized cover letters in 3-5 seconds
- View real-time progress during generation
- See ATS (Applicant Tracking System) scores for generated documents
- View my generation history

---

## Screens

### 1. GenerationOptionsScreen

**Route**: `/generate`
**File**: `lib/screens/generation/generation_options_screen.dart`

**Context**: User navigates here from JobDetailScreen or HomeScreen

**UI Components**:
- Job info header (company, title)
- Sample documents status:
  - Resume sample indicator (uploaded/not uploaded)
  - Cover letter sample indicator (uploaded/not uploaded)
  - "Upload Samples" link (navigates to SampleUploadScreen)
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

### API Endpoints (6 total)

#### 1. POST /api/v1/profile/enhance - Enhance Profile

```dart
final result = await generationsApiClient.enhanceProfile(
  profileId: profileId,
  customPrompt: 'Emphasize technical leadership',
);
```

Request:
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "custom_prompt": "Emphasize technical leadership"
}
```

Response:
```json
{
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "enhanced_sections": {
    "professional_summary": "Results-driven Senior Software Engineer with 8+ years of expertise architecting scalable cloud solutions...",
    "experiences_enhanced": 3,
    "projects_enhanced": 2
  },
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "total_tokens": 1247,
    "processing_time_seconds": 4.2
  },
  "writing_style_used": {
    "tone": "professional yet personable",
    "vocabulary_level": "advanced"
  },
  "created_at": "2025-11-15T10:35:00Z"
}
```

**Enhancement Process** (Batch Processing):
1. Retrieve active cover letter sample
2. Extract writing style using AI (once, cached)
3. Collect ALL profile content (summary + all experiences + all projects)
4. Send single batch LLM request to enhance all content simultaneously
5. Parse structured JSON response with section-specific enhancements
6. Save enhanced_description fields to database alongside original descriptions
7. Return success metrics (sections enhanced, success rate)

**Performance**: Single LLM call processes unlimited experiences and projects (~4-5 seconds total, 80% faster than sequential approach)

**Note**: Enhanced descriptions are stored in the `enhanced_description` field for each experience and project, while original descriptions remain in the `description` field. Resume generation automatically uses enhanced descriptions when available.

**Speed**: ~4 seconds (LLM-powered)

#### 2. POST /api/v1/rankings/create - Create Job-Specific Rankings

```dart
final rankings = await generationsApiClient.createRankings(
  jobId: jobId,
  customPrompt: 'Prioritize cloud experience',
);
```

Request:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "custom_prompt": "Prioritize cloud experience"
}
```

Response:
```json
{
  "id": "ranking-uuid",
  "job_id": "job-uuid",
  "ranked_experience_ids": ["exp-1", "exp-2", "exp-3"],
  "ranked_project_ids": ["proj-1", "proj-2"],
  "relevance_scores": {
    "exp-1": 0.95,
    "exp-2": 0.87
  },
  "llm_metadata": {
    "model": "llama-3.1-8b-instant",
    "total_tokens": 543,
    "processing_time_seconds": 1.8
  },
  "created_at": "2025-11-15T10:35:00Z"
}
```

**Speed**: ~2 seconds (LLM-powered, cached for reuse)

#### 3. POST /api/v1/generations/resume - Generate Resume

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
  "generation_id": "generation-uuid",
  "job_id": "job-uuid",
  "document_type": "resume",
  "resume_text": "JOHN DOE\nSenior Software Engineer\n\nPROFESSIONAL SUMMARY\n...",
  "ats_score": 87.5,
  "ats_feedback": "Strong keyword density, well-formatted for ATS parsing",
  "content_used": {
    "experiences_count": 5,
    "projects_count": 3,
    "summary_enhanced": true
  },
  "created_at": "2025-11-15T10:40:00Z"
}
```

**Speed**: <1 second (pure logic, no LLM)

#### 4. POST /api/v1/generations/cover-letter - Generate Cover Letter

```dart
final coverLetter = await generationsApiClient.generateCoverLetter(
  jobId: jobId,
  companyName: 'TechCorp Inc.',
  hiringManagerName: 'Sarah Johnson',
  maxParagraphs: 4,
);
```

Request:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_name": "TechCorp Inc.",
  "hiring_manager_name": "Sarah Johnson",
  "max_paragraphs": 4
}
```

Response:
```json
{
  "generation_id": "generation-uuid",
  "job_id": "job-uuid",
  "document_type": "cover_letter",
  "cover_letter_text": "Dear Sarah Johnson,\n\nI am excited to apply...",
  "ats_score": 82.0,
  "ats_feedback": "Good keyword usage",
  "content_used": {
    "top_experiences": ["exp-1", "exp-2"],
    "writing_style_applied": true
  },
  "llm_metadata": {
    "model": "llama-3.3-70b-versatile",
    "total_tokens": 892,
    "processing_time_seconds": 3.4
  },
  "created_at": "2025-11-15T10:40:05Z"
}
```

**Speed**: 3-5 seconds (LLM-powered)

#### 5. GET /api/v1/rankings/job/{job_id} - Get Job Rankings

```dart
final rankings = await generationsApiClient.getRankingsForJob(jobId);
```

Response: Same as create rankings response (cached)

#### 6. GET /api/v1/generations/history - Get Generation History

```dart
final history = await generationsApiClient.getGenerationHistory(
  documentType: 'resume', // optional filter
  limit: 20,
  offset: 0,
);
```

Response:
```json
{
  "generations": [
    {
      "generation_id": "gen-uuid",
      "job_id": "job-uuid",
      "job_title": "Senior Software Engineer",
      "company": "TechCorp",
      "document_type": "resume",
      "ats_score": 87.5,
      "created_at": "2025-11-15T10:40:00Z"
    }
  ],
  "total": 5,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "hasMore": false
  }
}
```

---

## Data Models

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
  final String? atsFeedback;
  final Map<String, dynamic> metadata;
  final Map<String, dynamic>? llmMetadata;
  final DateTime createdAt;

  Generation({
    required this.id,
    required this.userId,
    required this.jobId,
    required this.documentType,
    required this.contentText,
    required this.atsScore,
    this.atsFeedback,
    required this.metadata,
    this.llmMetadata,
    required this.createdAt,
  });

  factory Generation.fromJson(Map<String, dynamic> json) {
    return Generation(
      id: json['generation_id'] ?? json['id'],
      userId: json['user_id'] ?? 0,
      jobId: json['job_id'],
      documentType: json['document_type'],
      contentText: json['resume_text'] ?? json['cover_letter_text'] ?? json['content_text'] ?? '',
      atsScore: (json['ats_score'] ?? 0).toDouble(),
      atsFeedback: json['ats_feedback'],
      metadata: json['content_used'] ?? json['metadata'] ?? {},
      llmMetadata: json['llm_metadata'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  bool get isResume => documentType == 'resume';
  bool get isCoverLetter => documentType == 'cover_letter';
}
```

### GenerationListItem

**File**: `lib/models/generation_list_item.dart`

```dart
class GenerationListItem {
  final String id;
  final String jobId;
  final String jobTitle;
  final String company;
  final String documentType;
  final double atsScore;
  final DateTime createdAt;

  GenerationListItem({
    required this.id,
    required this.jobId,
    required this.jobTitle,
    required this.company,
    required this.documentType,
    required this.atsScore,
    required this.createdAt,
  });

  factory GenerationListItem.fromJson(Map<String, dynamic> json) {
    return GenerationListItem(
      id: json['generation_id'],
      jobId: json['job_id'],
      jobTitle: json['job_title'],
      company: json['company'],
      documentType: json['document_type'],
      atsScore: (json['ats_score'] ?? 0).toDouble(),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

### Ranking

**File**: `lib/models/ranking.dart`

```dart
class Ranking {
  final String id;
  final String jobId;
  final List<String> rankedExperienceIds;
  final List<String> rankedProjectIds;
  final Map<String, double> relevanceScores;
  final String? rationale;
  final DateTime createdAt;

  Ranking({
    required this.id,
    required this.jobId,
    required this.rankedExperienceIds,
    required this.rankedProjectIds,
    required this.relevanceScores,
    this.rationale,
    required this.createdAt,
  });

  factory Ranking.fromJson(Map<String, dynamic> json) {
    return Ranking(
      id: json['id'],
      jobId: json['job_id'],
      rankedExperienceIds: List<String>.from(json['ranked_experience_ids'] ?? []),
      rankedProjectIds: List<String>.from(json['ranked_project_ids'] ?? []),
      relevanceScores: Map<String, double>.from(
        (json['relevance_scores'] ?? {}).map(
          (k, v) => MapEntry(k, (v as num).toDouble()),
        ),
      ),
      rationale: json['ranking_rationale'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

---

## State Management

### GenerationsProvider (`generations_provider.dart`)

Handles document generation requests, progress tracking, and generation history.

**File**: `lib/providers/generations_provider.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/generation.dart';
import '../models/generation_list_item.dart';
import '../models/ranking.dart';
import '../services/api/generations_api_client.dart';

// State class
class GenerationsState {
  final List<GenerationListItem> history;
  final Generation? currentGeneration;
  final Ranking? currentRanking;
  final bool isGenerating;
  final bool isEnhancing;
  final double progress; // 0.0 to 1.0
  final String? currentStage;
  final String? errorMessage;

  GenerationsState({
    this.history = const [],
    this.currentGeneration,
    this.currentRanking,
    this.isGenerating = false,
    this.isEnhancing = false,
    this.progress = 0.0,
    this.currentStage,
    this.errorMessage,
  });

  GenerationsState copyWith({
    List<GenerationListItem>? history,
    Generation? currentGeneration,
    Ranking? currentRanking,
    bool? isGenerating,
    bool? isEnhancing,
    double? progress,
    String? currentStage,
    String? errorMessage,
  }) {
    return GenerationsState(
      history: history ?? this.history,
      currentGeneration: currentGeneration ?? this.currentGeneration,
      currentRanking: currentRanking ?? this.currentRanking,
      isGenerating: isGenerating ?? this.isGenerating,
      isEnhancing: isEnhancing ?? this.isEnhancing,
      progress: progress ?? this.progress,
      currentStage: currentStage ?? this.currentStage,
      errorMessage: errorMessage,
    );
  }

  // Computed properties
  List<GenerationListItem> get resumeHistory =>
      history.where((g) => g.documentType == 'resume').toList();

  List<GenerationListItem> get coverLetterHistory =>
      history.where((g) => g.documentType == 'cover_letter').toList();

  bool get hasActiveGeneration => isGenerating;
}

// State notifier
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  final GenerationsApiClient _apiClient;

  GenerationsNotifier(this._apiClient) : super(GenerationsState());

  /// Enhance profile with AI
  Future<bool> enhanceProfile({
    required String profileId,
    String? customPrompt,
  }) async {
    state = state.copyWith(isEnhancing: true, errorMessage: null);

    try {
      await _apiClient.enhanceProfile(
        profileId: profileId,
        customPrompt: customPrompt,
      );
      state = state.copyWith(isEnhancing: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isEnhancing: false,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  /// Generate resume for a specific job
  Future<Generation?> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements',
      errorMessage: null,
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
      await Future.delayed(Duration(milliseconds: 300));

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
      return null;
    }
  }

  /// Generate cover letter for a specific job
  Future<Generation?> generateCoverLetter({
    required String jobId,
    String? companyName,
    String? hiringManagerName,
    int maxParagraphs = 4,
  }) async {
    state = state.copyWith(
      isGenerating: true,
      progress: 0.0,
      currentStage: 'Analyzing job requirements',
      errorMessage: null,
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
        companyName: companyName,
        hiringManagerName: hiringManagerName,
        maxParagraphs: maxParagraphs,
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
      return null;
    }
  }

  /// Fetch generation history
  Future<void> fetchHistory({
    String? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final response = await _apiClient.getGenerationHistory(
        documentType: documentType,
        limit: limit,
        offset: offset,
      );

      final items = (response['generations'] as List)
          .map((json) => GenerationListItem.fromJson(json))
          .toList();

      state = state.copyWith(history: items);
    } catch (e) {
      state = state.copyWith(errorMessage: e.toString());
    }
  }

  void clearError() {
    state = state.copyWith(errorMessage: null);
  }

  void reset() {
    state = GenerationsState();
  }
}

// Provider
final generationsProvider =
    StateNotifierProvider<GenerationsNotifier, GenerationsState>(
  (ref) {
    final apiClient = ref.watch(generationsApiClientProvider);
    return GenerationsNotifier(apiClient);
  },
);
```

**Usage in Generation Screens**:
```dart
// Watch generation state
final generationsState = ref.watch(generationsProvider);
final isGenerating = generationsState.isGenerating;
final progress = generationsState.progress;
final currentStage = generationsState.currentStage;

// Generate resume
Future<void> _generateResume() async {
  final generation = await ref.read(generationsProvider.notifier).generateResume(
    jobId: widget.jobId,
    maxExperiences: _maxExperiences,
    maxProjects: _maxProjects,
    includeSummary: _includeSummary,
  );

  if (generation != null) {
    Navigator.pushNamed(
      context,
      '/generate/result/${generation.id}',
    );
  }
}

// Generate cover letter
Future<void> _generateCoverLetter() async {
  final generation = await ref.read(generationsProvider.notifier).generateCoverLetter(
    jobId: widget.jobId,
    companyName: _companyName,
    hiringManagerName: _hiringManagerName,
  );

  if (generation != null) {
    Navigator.pushNamed(
      context,
      '/generate/result/${generation.id}',
    );
  }
}
```

---

## Service Layer

### GenerationsApiClient

**File**: `lib/services/api/generations_api_client.dart`

```dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/generation.dart';
import '../../models/ranking.dart';
import 'base_http_client.dart';

class GenerationsApiClient {
  final Dio _dio;

  GenerationsApiClient(this._dio);

  /// Enhance profile with AI
  Future<Map<String, dynamic>> enhanceProfile({
    required String profileId,
    String? customPrompt,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/profile/enhance',
        data: {
          'profile_id': profileId,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create job-specific rankings
  Future<Ranking> createRankings({
    required String jobId,
    String? customPrompt,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/rankings/create',
        data: {
          'job_id': jobId,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return Ranking.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get cached rankings for a job
  Future<Ranking> getRankingsForJob(String jobId) async {
    try {
      final response = await _dio.get('/api/v1/rankings/job/$jobId');
      return Ranking.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate resume for a job
  Future<Generation> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
    String? customPrompt,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/generations/resume',
        data: {
          'job_id': jobId,
          'max_experiences': maxExperiences,
          'max_projects': maxProjects,
          'include_summary': includeSummary,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return Generation.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate cover letter for a job
  Future<Generation> generateCoverLetter({
    required String jobId,
    String? companyName,
    String? hiringManagerName,
    int maxParagraphs = 4,
    String? customPrompt,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/generations/cover-letter',
        data: {
          'job_id': jobId,
          if (companyName != null) 'company_name': companyName,
          if (hiringManagerName != null) 'hiring_manager_name': hiringManagerName,
          'max_paragraphs': maxParagraphs,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return Generation.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get generation history
  Future<Map<String, dynamic>> getGenerationHistory({
    String? documentType,
    String? jobId,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (documentType != null) queryParams['document_type'] = documentType;
      if (jobId != null) queryParams['job_id'] = jobId;

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

### ATSScoreBadge

**File**: `lib/widgets/ats_score_badge.dart`

```dart
import 'package:flutter/material.dart';

class ATSScoreBadge extends StatelessWidget {
  final double score;
  final bool showMessage;

  const ATSScoreBadge({
    required this.score,
    this.showMessage = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getColor(score).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _getColor(score)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'ATS Score',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
          SizedBox(height: 4),
          Text(
            '${score.toInt()}%',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: _getColor(score),
            ),
          ),
          if (showMessage) ...[
            SizedBox(height: 4),
            Text(
              _getMessage(score),
              style: TextStyle(
                fontSize: 12,
                color: _getColor(score),
              ),
            ),
          ],
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

### GenerationProgressIndicator

**File**: `lib/widgets/generation_progress_indicator.dart`

```dart
import 'package:flutter/material.dart';

class GenerationProgressIndicator extends StatelessWidget {
  final double progress;
  final String? stage;

  const GenerationProgressIndicator({
    required this.progress,
    this.stage,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Circular progress
        SizedBox(
          width: 120,
          height: 120,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CircularProgressIndicator(
                value: progress,
                strokeWidth: 8,
                backgroundColor: Colors.grey.shade200,
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        SizedBox(height: 24),
        // Stage label
        if (stage != null)
          Text(
            stage!,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade700,
            ),
          ),
      ],
    );
  }
}
```

### GenerationCard

**File**: `lib/widgets/generation_card.dart`

```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/generation_list_item.dart';

class GenerationCard extends StatelessWidget {
  final GenerationListItem generation;
  final VoidCallback? onTap;

  const GenerationCard({
    required this.generation,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isResume = generation.documentType == 'resume';

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
                  color: isResume
                      ? Colors.blue.shade100
                      : Colors.green.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  isResume ? Icons.description : Icons.mail,
                  color: isResume ? Colors.blue : Colors.green,
                ),
              ),
              SizedBox(width: 16),
              // Generation info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      generation.jobTitle,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    SizedBox(height: 4),
                    Text(
                      generation.company,
                      style: TextStyle(
                        color: Colors.grey.shade600,
                        fontSize: 14,
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      DateFormat('MMM d, yyyy').format(generation.createdAt),
                      style: TextStyle(
                        color: Colors.grey.shade500,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              // ATS score
              ATSScoreBadge(
                score: generation.atsScore,
                showMessage: false,
              ),
            ],
          ),
        ),
      ),
    );
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

  when(mockClient.getRankingsForJob(any)).thenThrow(Exception('Not found'));
  when(mockClient.createRankings(jobId: any)).thenAnswer((_) async => testRanking);
  when(mockClient.generateResume(
    jobId: any,
    maxExperiences: any,
    maxProjects: any,
    includeSummary: any,
  )).thenAnswer((_) async => testGeneration);

  final result = await notifier.generateResume(jobId: 'job-id');

  expect(result, isNotNull);
  expect(notifier.state.currentGeneration, isNotNull);
  expect(notifier.state.isGenerating, false);
  expect(notifier.state.progress, 1.0);
});

test('GenerationsNotifier handles generation error', () async {
  final mockClient = MockGenerationsApiClient();
  final notifier = GenerationsNotifier(mockClient);

  when(mockClient.getRankingsForJob(any)).thenThrow(Exception('Not found'));
  when(mockClient.createRankings(jobId: any)).thenThrow(Exception('API error'));

  final result = await notifier.generateResume(jobId: 'job-id');

  expect(result, isNull);
  expect(notifier.state.isGenerating, false);
  expect(notifier.state.errorMessage, isNotNull);
});
```

### Widget Tests

```dart
testWidgets('ATSScoreBadge displays correct color for high score', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: ATSScoreBadge(score: 85.0),
      ),
    ),
  );

  expect(find.text('85%'), findsOneWidget);
  expect(find.text('Excellent!'), findsOneWidget);
});

testWidgets('GenerationProgressIndicator shows correct progress', (tester) async {
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: GenerationProgressIndicator(
          progress: 0.5,
          stage: 'Generating cover letter',
        ),
      ),
    ),
  );

  expect(find.text('50%'), findsOneWidget);
  expect(find.text('Generating cover letter'), findsOneWidget);
});
```

---

## Performance Considerations

1. **Resume Generation**: <1 second (pure logic, no LLM)
2. **Cover Letter Generation**: 3-5 seconds (LLM-powered)
3. **Ranking Caching**: Rankings cached per job, reuse for multiple generations
4. **Progress Updates**: Real-time progress feedback for better UX
5. **History Pagination**: Load history in batches of 20

---

## Error Handling

### Common Errors

**No Cover Letter Sample**:
```dart
// Error: No active cover letter sample found
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(
    content: Text('Upload a cover letter sample for best results'),
    action: SnackBarAction(
      label: 'Upload',
      onPressed: () => Navigator.pushNamed(context, '/samples'),
    ),
  ),
);
```

**LLM Timeout**:
```dart
// Error: LLM request timed out
showDialog(
  context: context,
  builder: (context) => AlertDialog(
    title: Text('Generation Timeout'),
    content: Text('The AI is taking longer than expected. Would you like to retry?'),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: Text('Cancel'),
      ),
      TextButton(
        onPressed: () {
          Navigator.pop(context);
          _retryGeneration();
        },
        child: Text('Retry'),
      ),
    ],
  ),
);
```

---

## Related Documentation

- [AI Generation API](../api-services/04b-ai-generation-api.md) - Backend API specification
- [Sample Upload Feature](04a-sample-upload-feature.md) - Upload samples for AI
- [Profile Management Feature](02-profile-management-feature.md) - Profile context

---

**Status**: ✅ Fully Implemented
**Screens**: 4 (Options, Progress, Result, History)
**API Endpoints**: 6 endpoints
**LLM Integration**: Groq API (llama-3.3-70b-versatile, llama-3.1-8b-instant)
**Dependencies**: dio, flutter_riverpod
**Last Updated**: November 2025
