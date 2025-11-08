# Generation Feature - Mobile Design Document

**Version**: 1.1
**Feature**: AI-Powered Resume and Cover Letter Generation
**API Service**: Generation API
**Status**: 🚧 **Sprint 4 Ready** (Fully specified, ready for Sprint 4 implementation)
**Last Updated**: November 7, 2025

---

## Implementation Status

### ❌ Not Implemented
- Generation initiation screen (select job + options)
- Real-time progress tracking screen with stage updates
- Generation result screen (ATS score, recommendations)
- Generation history list screen
- Template selection UI
- Generation options form (length, focus areas, custom instructions)
- Rate limit handling and user feedback
- Generation API client (all endpoints)
- Generation state management (Riverpod provider)
- Polling mechanism for progress updates
- Error handling and retry logic

### ✅ API Ready (Backend Specified)
- POST /generations/resume - Start resume generation
- POST /generations/cover-letter - Start cover letter generation
- GET /generations/{id} - Get generation status and progress
- GET /generations/{id}/result - Get final result with content
- GET /generations - List user's generations
- DELETE /generations/{id} - Cancel generation
- GET /generations/templates - List available templates

---

## Feature Overview

### Purpose
Enable users to generate AI-tailored resumes and cover letters by combining their master profile with specific job descriptions. Real-time progress tracking shows the 5-stage AI pipeline in action.

### Key Features
1. **Job Selection** - Choose saved job for tailored generation
2. **Template Selection** - Pick resume template (Modern, Classic, Creative)
3. **Generation Options** - Configure length, focus areas, custom instructions
4. **Real-Time Progress** - Watch 5-stage pipeline with live updates
5. **ATS Scoring** - View keyword coverage and match percentage
6. **Recommendations** - Get actionable suggestions to improve resume
7. **Generation History** - Access previous generations
8. **Rate Limiting** - Handle 10 generations/hour limit gracefully

### Core User Flows

#### Flow 1: Generate Resume from Job
```
User Journey:
1. User navigates to job detail screen
2. User taps "Generate Resume" button
3. Generation options screen appears
4. User selects template (Modern, Classic, Creative)
5. User sets resume length (1 page, 2 pages)
6. Optional: User adds focus areas (e.g., "Leadership", "Cloud Architecture")
7. Optional: User adds custom instructions
8. User taps "Generate"
9. Progress screen shows with stage indicators (0/5 stages)
10. Real-time polling updates progress every 2 seconds
11. Stage 1: "Analyzing job description..." (20% complete)
12. Stage 2: "Compiling your profile..." (40% complete)
13. Stage 3: "Generating tailored content..." (60% complete)
14. Stage 4: "Validating quality and ATS compliance..." (80% complete)
15. Stage 5: "Preparing PDF export..." (100% complete)
16. Success! Result screen shows:
    - ATS Score: 87%
    - Match Percentage: 82%
    - Keyword Coverage: 15/18 keywords matched
    - Recommendations list
17. User can: View PDF, Download, Share, Regenerate with changes

Data Flow:
Mobile → POST /generations/resume {profile_id, job_id, options} → Backend creates generation (status: pending) → Background pipeline runs → Mobile polls GET /generations/{id} every 2s → Progress updates received → Final status: completed → Mobile fetches result → Display ATS score and PDF
```

#### Flow 2: View Generation History
```
User Journey:
1. User opens "Generations" screen from main navigation
2. List displays previous generations with cards showing:
   - Job title and company
   - Document type (Resume/Cover Letter)
   - ATS score badge
   - Date generated
   - Status (Completed, In Progress, Failed)
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

#### Flow 3: Handle Rate Limit
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
```

### Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/generations/resume` | POST | Start resume generation | `{profile_id, job_id, options}` | Generation object (201) |
| `/generations/cover-letter` | POST | Start cover letter generation | `{profile_id, job_id, options}` | Generation object (201) |
| `/generations/{id}` | GET | Get generation status | - | Generation with progress (200) |
| `/generations/{id}/result` | GET | Get final result | - | Result with content (200) |
| `/generations` | GET | List generations | Query params: `status`, `job_id`, `limit`, `offset` | Generations array (200) |
| `/generations/{id}` | DELETE | Cancel generation | - | No content (204) |
| `/generations/templates` | GET | List templates | - | Templates array (200) |

### Error Codes

| Code | Meaning | User Action |
|------|---------|-------------|
| 400 | Invalid profile_id or job_id | Show validation error |
| 403 | Not authorized (not owner of profile/job) | Show error message |
| 404 | Generation, profile, or job not found | Show "Not found" message |
| 422 | Pipeline stage failed | Show error with retry option |
| 429 | Rate limit exceeded (>10/hour) | Show rate limit dialog with countdown |
| 500 | Server error | Show generic error with retry |

---

## Data Models

### Generation Model

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
