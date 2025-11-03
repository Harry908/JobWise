# Generation API Service

**Version**: 2.0
**Base Path**: `/api/v1/generations`
**Status**: ❌ **Not Implemented** (Fully specified, implementation pending Sprint 2)
**Last Updated**: November 2, 2025

## Service Overview

AI-powered resume and cover letter generation using 5-stage pipeline. Combines user profile with job description to create tailored documents. Asynchronous processing with real-time progress tracking.

## Specification

**Purpose**: AI document generation with ATS optimization
**Authentication**: Required (JWT)
**Processing**: Asynchronous (background pipeline with Celery/asyncio)
**Performance**: <6s total generation time (target p50), <10s (p95)
**Rate Limiting**: 10 generations/hour per user
**Token Budget**: 8000 tokens per generation
**Progress Tracking**: Real-time stage updates via polling (2s intervals)

## Error Codes

| Status Code | Error Type | Description |
|-------------|------------|-------------|
| 201 | Created | Generation started successfully |
| 200 | OK | Request successful (status/result retrieval) |
| 204 | No Content | Generation cancelled successfully |
| 400 | Bad Request | Invalid profile_id, job_id, or options |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | User doesn't own profile or job |
| 404 | Not Found | Generation, profile, or job not found |
| 422 | Unprocessable Entity | Pipeline stage failed |
| 429 | Too Many Requests | Rate limit exceeded (>10/hour) |
| 500 | Internal Server Error | Pipeline error |

## Validation Rules

**Required Fields:**
- `profile_id`: Must exist and belong to user (UUID format)
- `job_id`: Must exist and belong to user (UUID format)

**Optional Fields (options object):**
- `template`: One of: `modern`, `classic`, `creative` (default: `modern`)
- `length`: One of: `one_page`, `two_page` (default: `one_page`)
- `focus_areas`: Array of strings, max 5 items
- `include_cover_letter`: Boolean (default: false)
- `custom_instructions`: String, max 500 chars

**Rate Limiting:**
- 10 generations per hour per user
- `429` response includes `retry_after` seconds
- Counter resets hourly

**Pipeline Stages:**
1. **Job Analysis** (Stage 1): 1s, 1500 tokens
2. **Profile Compilation** (Stage 2): 1s, 2000 tokens
3. **Content Generation** (Stage 3): 2s, 3000 tokens
4. **Quality Validation** (Stage 4): 1s, 1500 tokens
5. **Export Preparation** (Stage 5): 0.5s, 0 tokens

## Dependencies

### Internal
- Authentication API: User identity
- Profile API: Master profile data
- Job API: Job description data
- Document API: Document storage
- LLM Service: AI generation (via ILLMService port)
- Database: GenerationModel
- Background Queue: Celery or asyncio tasks

### External
- LLM Provider: OpenAI GPT-4 or Anthropic Claude (via adapter)

## Database Schema

### GenerationModel (generations table)

**Purpose**: Tracks AI generation pipeline progress and results

**Fields**:
```sql
CREATE TABLE generations (
    id TEXT PRIMARY KEY,  -- UUID (generation_id)
    user_id INTEGER NOT NULL,
    profile_id TEXT NOT NULL,
    job_id TEXT NOT NULL,
    document_type TEXT NOT NULL,  -- 'resume', 'cover_letter'
    status TEXT DEFAULT 'pending',  -- 'pending', 'generating', 'completed', 'failed', 'cancelled'
    current_stage INTEGER DEFAULT 0,
    total_stages INTEGER DEFAULT 5,
    stage_name TEXT,
    stage_description TEXT,
    error_message TEXT,
    options TEXT,  -- JSON: {"template": "modern", "length": "one_page"}
    result TEXT,   -- JSON: {"document_id": "...", "ats_score": 0.87, ...}
    tokens_used INTEGER DEFAULT 0,
    generation_time REAL,  -- Seconds (float)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_generations_user_id ON generations(user_id);
CREATE INDEX idx_generations_status ON generations(status);
CREATE INDEX idx_generations_job_id ON generations(job_id);
CREATE INDEX idx_generations_user_status ON generations(user_id, status);
CREATE INDEX idx_generations_created_at ON generations(created_at);
```

**Field Descriptions**:
- `id`: UUID primary key (generation_id)
- `user_id`: Owner of the generation
- `profile_id`: Source profile for generation
- `job_id`: Target job for tailoring
- `document_type`: Type of document ('resume', 'cover_letter')
- `status`: Current state (pending, generating, completed, failed, cancelled)
- `current_stage`: Pipeline stage (0-5)
- `total_stages`: Total pipeline stages (always 5)
- `stage_name`: Human-readable stage name
- `stage_description`: Stage progress description
- `error_message`: Error details if failed
- `options`: JSON with generation options
- `result`: JSON with final result (document_id, ats_score, etc.)
- `tokens_used`: Total LLM tokens consumed
- `generation_time`: Total processing time in seconds
- `created_at`: Generation request timestamp
- `started_at`: Pipeline start timestamp
- `completed_at`: Pipeline completion timestamp
- `updated_at`: Last update timestamp (auto-updates)

**Constraints**:
- Foreign key cascade delete (when user/profile/job deleted, generations deleted)
- `status` must be one of: pending, generating, completed, failed, cancelled
- `document_type` must be: resume or cover_letter
- `current_stage` range: 0-5

## Data Flow

```
Generation Lifecycle:

1. Client → POST /generations/resume {profile_id, job_id, options}
2. API validates JWT → get user_id
3. API validates profile and job ownership
4. API creates GenerationModel (status: pending)
5. API ← 201 Created {generation_id, status, Location header}

Background Pipeline (5 stages):

Stage 1: Job Analysis (1s, 1500 tokens)
- Extract keywords, requirements, role expectations
- LLM prompt: "Analyze job description..."
- Output: Job analysis report

Stage 2: Profile Compilation (1s, 2000 tokens)
- Score profile sections by relevance
- Rank experiences, skills by job match
- Output: Compiled profile with relevance scores

Stage 3: Content Generation (2s, 3000 tokens)
- Generate tailored resume content
- Use template and job analysis
- Output: Resume text (text, HTML, markdown)

Stage 4: Quality Validation (1s, 1500 tokens)
- ATS compliance check
- Keyword density validation
- Grammar and consistency check
- Output: ATS score, recommendations

Stage 5: Export Preparation (0.5s, 0 tokens)
- Format content for PDF
- Calculate metrics
- Store DocumentModel
- Output: document_id, pdf_url

Progress Updates:
- Each stage updates generation.stage_progress
- Client polls GET /generations/{id} for status
- Status transitions: pending → generating → completed|failed

Final State:
- Status: completed
- Result: {document_id, ats_score, match_percentage, pdf_url}
- Metadata: tokens_used, generation_time

6. Client → GET /generations/{id}/result
7. API ← {document_id, pdf_url, ats_score, content}
```

## API Contract

### POST /generations/resume

**Description**: Start resume generation

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "options": {
    "template": "modern",
    "length": "one_page",
    "focus_areas": ["backend_development", "leadership"],
    "include_cover_letter": true,
    "custom_instructions": "Emphasize cloud architecture experience"
  }
}
```

**Response** (201 Created):
```json
{
  "generation_id": "gen-uuid",
  "status": "pending",
  "progress": {
    "current_stage": 0,
    "total_stages": 5,
    "percentage": 0,
    "stage_name": null,
    "stage_description": "Queued for processing"
  },
  "estimated_completion": "2025-10-21T10:30:30Z",
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "created_at": "2025-10-21T10:30:00Z"
}
```

**Response Headers**:
- `Location: /api/v1/generations/{generation_id}`

**Errors**:
- 400: Invalid profile_id or job_id
- 403: Not authorized (not owner of profile/job)
- 404: Profile or job not found
- 429: Rate limit exceeded (>10/hour)

### POST /generations/cover-letter

**Description**: Start cover letter generation

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "options": {
    "tone": "professional",
    "length": "standard",
    "custom_instructions": "Mention passion for open source"
  }
}
```

**Response** (201 Created): Same structure as /resume

### GET /generations/{id}

**Description**: Get generation status and progress

**Headers**: `Authorization: Bearer <token>`

**Response (In Progress)** (200 OK):
```json
{
  "generation_id": "gen-uuid",
  "status": "generating",
  "progress": {
    "current_stage": 2,
    "total_stages": 5,
    "percentage": 40,
    "stage_name": "Profile Compilation",
    "stage_description": "Scoring profile content by relevance"
  },
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "tokens_used": 3500,
  "estimated_completion": "2025-10-21T10:30:30Z",
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:20Z"
}
```

**Response (Completed)** (200 OK):
```json
{
  "generation_id": "gen-uuid",
  "status": "completed",
  "progress": {
    "current_stage": 5,
    "total_stages": 5,
    "percentage": 100,
    "stage_name": "PDF Export",
    "stage_description": "Completed"
  },
  "result": {
    "document_id": "doc-uuid",
    "ats_score": 0.87,
    "match_percentage": 82,
    "keyword_coverage": 0.91,
    "pdf_url": "/api/v1/documents/doc-uuid/download",
    "recommendations": [
      "Add AWS certification to skills",
      "Quantify team size in leadership experience"
    ]
  },
  "tokens_used": 7850,
  "generation_time": 5.2,
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "created_at": "2025-10-21T10:30:00Z",
  "completed_at": "2025-10-21T10:30:05Z",
  "updated_at": "2025-10-21T10:30:05Z"
}
```

**Response (Failed)** (200 OK):
```json
{
  "generation_id": "gen-uuid",
  "status": "failed",
  "progress": {
    "current_stage": 3,
    "total_stages": 5,
    "percentage": 60
  },
  "error_message": "LLM service unavailable. Please try again.",
  "tokens_used": 5000,
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:15Z"
}
```

**Errors**:
- 404: Generation not found
- 403: Not authorized

### GET /generations/{id}/result

**Description**: Get final generation result (completed only)

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "generation_id": "gen-uuid",
  "document_id": "doc-uuid",
  "document_type": "resume",
  "content": {
    "text": "John Doe\nSoftware Engineer\n\nPROFESSIONAL SUMMARY\n...",
    "html": "<html><body>...",
    "markdown": "# John Doe\n## Software Engineer\n..."
  },
  "ats_score": 0.87,
  "match_percentage": 82,
  "keyword_coverage": 0.91,
  "keywords_matched": 15,
  "keywords_total": 18,
  "pdf_url": "/api/v1/documents/doc-uuid/download",
  "recommendations": [
    "Add AWS certification to skills",
    "Quantify team size in leadership experience"
  ],
  "metadata": {
    "template": "modern",
    "tokens_used": 7850,
    "generation_time": 5.2
  }
}
```

**Errors**:
- 404: Generation not found or not completed
- 403: Not authorized

### POST /generations/{id}/regenerate

**Description**: Regenerate with updated options

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "options": {
    "template": "creative",
    "custom_instructions": "Focus more on leadership"
  }
}
```

**Response** (201 Created): New generation object (new generation_id)

**Errors**:
- 404: Original generation not found
- 400: Invalid options

### DELETE /generations/{id}

**Description**: Cancel ongoing generation or delete completed

**Headers**: `Authorization: Bearer <token>`

**Response** (204 No Content)

**Errors**:
- 404: Generation not found
- 400: Cannot cancel (already completed)

### GET /generations

**Description**: List user's generations

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `job_id`: string - filter by job
- `status`: string (pending, generating, completed, failed, cancelled)
- `document_type`: string (resume, cover_letter)
- `limit`: integer (1-100, default: 20)
- `offset`: integer (default: 0)

**Response** (200 OK):
```json
{
  "generations": [
    {
      "generation_id": "gen-uuid",
      "status": "completed",
      "document_type": "resume",
      "job_title": "Senior Python Developer",
      "company": "Tech Corp",
      "ats_score": 0.87,
      "created_at": "2025-10-21T10:30:00Z",
      "completed_at": "2025-10-21T10:30:05Z"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  },
  "statistics": {
    "total_generations": 25,
    "completed": 22,
    "failed": 2,
    "in_progress": 1,
    "average_ats_score": 0.84
  }
}
```

### GET /generations/templates

**Description**: List available resume templates

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "templates": [
    {
      "id": "modern",
      "name": "Modern",
      "description": "Clean, contemporary design",
      "preview_url": "/templates/modern/preview.png",
      "recommended_for": ["tech", "startup"],
      "ats_friendly": true
    },
    {
      "id": "classic",
      "name": "Classic",
      "description": "Traditional professional layout",
      "preview_url": "/templates/classic/preview.png",
      "recommended_for": ["finance", "law", "corporate"],
      "ats_friendly": true
    },
    {
      "id": "creative",
      "name": "Creative",
      "description": "Bold design for creative roles",
      "preview_url": "/templates/creative/preview.png",
      "recommended_for": ["design", "marketing"],
      "ats_friendly": false
    }
  ]
}
```

## Mobile Integration Notes

### Generation Model
```dart
class Generation {
  final String id;
  final String profileId;
  final String jobId;
  final GenerationStatus status;
  final GenerationProgress progress;
  final GenerationResult? result;
  final String? errorMessage;
  final int tokensUsed;
  final double? generationTime;
  final DateTime createdAt;
  final DateTime? completedAt;

  Generation({
    required this.id,
    required this.profileId,
    required this.jobId,
    required this.status,
    required this.progress,
    this.result,
    this.errorMessage,
    this.tokensUsed = 0,
    this.generationTime,
    required this.createdAt,
    this.completedAt,
  });

  factory Generation.fromJson(Map<String, dynamic> json) => Generation(
    id: json['generation_id'],
    profileId: json['profile_id'],
    jobId: json['job_id'],
    status: GenerationStatus.values.firstWhere(
      (e) => e.name == json['status'],
    ),
    progress: GenerationProgress.fromJson(json['progress']),
    result: json['result'] != null
        ? GenerationResult.fromJson(json['result'])
        : null,
    errorMessage: json['error_message'],
    tokensUsed: json['tokens_used'] ?? 0,
    generationTime: json['generation_time']?.toDouble(),
    createdAt: DateTime.parse(json['created_at']),
    completedAt: json['completed_at'] != null
        ? DateTime.parse(json['completed_at'])
        : null,
  );

  bool get isComplete => status == GenerationStatus.completed;
  bool get isFailed => status == GenerationStatus.failed;
  bool get isProcessing => status == GenerationStatus.generating ||
                          status == GenerationStatus.pending;
}

enum GenerationStatus { pending, generating, completed, failed, cancelled }

class GenerationProgress {
  final int currentStage;
  final int totalStages;
  final int percentage;
  final String? stageName;
  final String? stageDescription;

  GenerationProgress({
    required this.currentStage,
    required this.totalStages,
    required this.percentage,
    this.stageName,
    this.stageDescription,
  });

  factory GenerationProgress.fromJson(Map<String, dynamic> json) =>
      GenerationProgress(
        currentStage: json['current_stage'],
        totalStages: json['total_stages'],
        percentage: json['percentage'],
        stageName: json['stage_name'],
        stageDescription: json['stage_description'],
      );
}

class GenerationResult {
  final String documentId;
  final double atsScore;
  final int matchPercentage;
  final double keywordCoverage;
  final String pdfUrl;
  final List<String> recommendations;

  GenerationResult({
    required this.documentId,
    required this.atsScore,
    required this.matchPercentage,
    required this.keywordCoverage,
    required this.pdfUrl,
    this.recommendations = const [],
  });

  factory GenerationResult.fromJson(Map<String, dynamic> json) =>
      GenerationResult(
        documentId: json['document_id'],
        atsScore: json['ats_score'].toDouble(),
        matchPercentage: json['match_percentage'],
        keywordCoverage: json['keyword_coverage'].toDouble(),
        pdfUrl: json['pdf_url'],
        recommendations: List<String>.from(json['recommendations'] ?? []),
      );
}
```

### Generation Service with Polling
```dart
class GenerationService {
  final ApiClient _client;

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

  Future<Generation> getGenerationStatus(String id) async {
    final response = await _client.get('/generations/$id');
    return Generation.fromJson(response.data);
  }

  // Poll until completion
  Stream<Generation> pollGeneration(String id, {
    Duration interval = const Duration(seconds: 2),
  }) async* {
    while (true) {
      final generation = await getGenerationStatus(id);
      yield generation;

      if (!generation.isProcessing) {
        break;
      }

      await Future.delayed(interval);
    }
  }

  Future<void> cancelGeneration(String id) async {
    await _client.delete('/generations/$id');
  }

  Future<List<Generation>> getGenerations({
    String? jobId,
    GenerationStatus? status,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/generations', queryParameters: {
      if (jobId != null) 'job_id': jobId,
      if (status != null) 'status': status.name,
      'limit': limit,
      'offset': offset,
    });
    return (response.data['generations'] as List)
        .map((json) => Generation.fromJson(json))
        .toList();
  }
}
```

### UI Pattern - Progress Screen
```dart
class GenerationProgressScreen extends StatefulWidget {
  final String generationId;

  @override
  _GenerationProgressScreenState createState() => _GenerationProgressScreenState();
}

class _GenerationProgressScreenState extends State<GenerationProgressScreen> {
  late Stream<Generation> _progressStream;

  @override
  void initState() {
    super.initState();
    _progressStream = generationService.pollGeneration(widget.generationId);
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Generation>(
      stream: _progressStream,
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return LoadingIndicator();
        }

        final generation = snapshot.data!;

        if (generation.isComplete) {
          // Navigate to result screen
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
          return Container();
        }

        if (generation.isFailed) {
          return ErrorScreen(message: generation.errorMessage);
        }

        // Show progress
        return Column(
          children: [
            LinearProgressIndicator(
              value: generation.progress.percentage / 100,
            ),
            Text('${generation.progress.percentage}%'),
            Text(generation.progress.stageName ?? 'Processing...'),
            Text(
              generation.progress.stageDescription ?? '',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            TextButton(
              onPressed: () => generationService.cancelGeneration(generation.id),
              child: Text('Cancel'),
            ),
          ],
        );
      },
    );
  }
}
```

### Rate Limiting Handling
```dart
try {
  final generation = await generationService.startResumeGeneration(
    profileId: profile.id,
    jobId: job.id,
  );
  // Navigate to progress screen
} on DioError catch (e) {
  if (e.response?.statusCode == 429) {
    final retryAfter = e.response?.data['retry_after'] ?? 3600;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text('Rate Limit Exceeded'),
        content: Text('You have reached the hourly limit of 10 generations. '
                     'Try again in ${(retryAfter / 60).ceil()} minutes.'),
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

### Local State Management
- Cache generation status during polling
- Store generation_id with job for quick access
- Show recent generations in job detail
- Badge indicator for in-progress generations

## Implementation Notes

### Repository
- `app/infrastructure/repositories/generation_repository.py`
- Methods: `create()`, `get_by_id()`, `update_status()`, `update_result()`

### Services
- `app/application/services/generation_service.py` - Orchestrator
- `app/domain/services/stages/` - 5 pipeline stages

### Pipeline Stages
1. `job_analyzer.py`: Extract job requirements
2. `profile_compiler.py`: Rank profile content
3. `content_generator.py`: Generate resume text
4. `quality_validator.py`: ATS and quality checks
5. `export_preparer.py`: Format and store document

### Performance Targets
- Stage 1: 1s (Job Analysis)
- Stage 2: 1s (Profile Compilation)
- Stage 3: 2s (Content Generation)
- Stage 4: 1s (Quality Validation)
- Stage 5: 0.5s (Export Preparation)
- Total: <6s (p50), <10s (p95)

### Testing
- Test generation creation
- Test pipeline stages individually
- Test status transitions
- Test polling behavior
- Test rate limiting
- Test error handling
- Mock LLM service for fast tests
