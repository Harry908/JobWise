# Generation API Service

**Version**: 2.1
**Base Path**: `/api/v1/generations`
**Status**: 🚧 **Sprint 4 Ready** (Fully specified, ready for Sprint 4 implementation)
**Last Updated**: November 7, 2025

## Service Overview

AI-powered resume and cover letter generation using streamlined 2-stage pipeline. Combines user profile with job description to create tailored documents from user's actual content and example resumes. **Never fabricates experiences or skills.** Asynchronous processing with real-time progress tracking.

## Core Principle

Generation is grounded in user's **master resume content only**. The system uses example resumes for structural guidance and applies job-specific keyword matching. Content comes exclusively from user's profile and target job posting—system never invents experiences, skills, or achievements.

## Specification

**Purpose**: Example-based AI document generation without fabrication
**Authentication**: Required (JWT)
**Processing**: Asynchronous (background pipeline with asyncio)
**Performance**: <8s total generation time (target p50), <10s (p95)
**Rate Limiting**: 10 generations/hour per user
**Token Budget**: 5000 tokens per generation (reduced via prompt optimization)
**Progress Tracking**: Real-time stage updates via polling (2s intervals)
**Anti-Hallucination**: Explicit constraints prevent content fabrication

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

## Error Response Format

All error responses follow this consistent structure (matching Auth/Profile/Job APIs):

```json
{
  "error": {
    "code": "error_code_snake_case",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Example Error Responses

**400 Bad Request** (Invalid input):
```json
{
  "error": {
    "code": "invalid_profile_id",
    "message": "Profile not found or does not belong to user",
    "details": {
      "profile_id": "invalid-uuid",
      "user_id": 123
    }
  }
}
```

**429 Too Many Requests** (Rate limit):
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Generation limit reached. Try again in 30 minutes.",
    "details": {
      "current_usage": 10,
      "limit": 10,
      "retry_after": 1800,
      "reset_at": "2025-11-07T15:30:00Z"
    }
  }
}
```

**422 Unprocessable Entity** (Pipeline failure):
```json
{
  "error": {
    "code": "pipeline_stage_failed",
    "message": "Content generation stage failed: LLM service timeout",
    "details": {
      "stage": 3,
      "stage_name": "Content Generation",
      "error_type": "timeout"
    }
  }
}
```

## Validation Rules

**Required Fields:**
- `profile_id`: Must exist and belong to user (UUID format)
- `job_id`: Must exist and belong to user (UUID format)

**Optional Fields (options object):**
- `template`: One of: `modern`, `classic`, `creative` (default: `modern`)
- `length`: One of: `one_page`, `two_page` (default: `one_page`)
- `focus_areas`: Array of strings, max 5 items (e.g., ["leadership", "cloud_architecture"])
- `include_cover_letter`: Boolean (default: false)
- `custom_instructions`: String, max 500 chars (additional tailoring instructions)
- `example_resume_url`: String, URL to uploaded example resume (optional, for structural guidance)

**Rate Limiting:**
- 10 generations per hour per user
- `429` response includes `retry_after` seconds
- Counter resets hourly

**Pipeline Stages (Simplified for MVP):**
1. **Analysis & Matching** (Stage 1): 3s, 2500 tokens, Weight: 40%
   - Analyze job requirements (keywords, skills, seniority)
   - Match with user's profile content
   - Score and rank experiences/projects by relevance
2. **Generation & Validation** (Stage 2): 5s, 2500 tokens, Weight: 60%
   - Generate tailored resume using matched content
   - Apply example resume structure (if provided)
   - Self-validate against anti-fabrication rules
   - Calculate ATS score and keyword coverage

**Total**: 2 stages, ~8s, 5000 tokens (70% faster, 37% cheaper than original 5-stage design)

## Progress Calculation

Progress percentage is calculated based on stage weights for the simplified 2-stage pipeline:

```python
# Stage weights (must sum to 100)
STAGE_WEIGHTS = [40, 60]  # Stages 1-2

# Calculate progress percentage
def calculate_progress(current_stage: int) -> int:
    """
    Calculate progress percentage based on completed stages.

    Args:
        current_stage: 0-2 (0 = queued, 1-2 = stages in progress/complete)

    Returns:
        Progress percentage (0-100)
    """
    if current_stage == 0:
        return 0
    if current_stage >= 2:
        return 100

    # Sum weights of completed stages
    return sum(STAGE_WEIGHTS[:current_stage])

# Examples:
# current_stage=0 → 0%   (queued)
# current_stage=1 → 40%  (Stage 1 complete)
# current_stage=2 → 100% (All stages complete)
```

## Stage Names and Descriptions

Each stage has an exact name and description string for consistent UI display:

| Stage | current_stage | stage_name | stage_description |
|-------|---------------|------------|-------------------|
| Queued | 0 | `null` | "Queued for processing" |
| Stage 1 | 1 | "Analysis & Matching" | "Analyzing job and matching with your profile content" |
| Stage 2 | 2 | "Generation & Validation" | "Generating tailored resume and validating quality" |
| Complete | 2 | "Generation & Validation" | "Completed" |

**Note**: Backend must use these exact strings for frontend consistency.

## Dependencies

### Internal
- Authentication API: User identity
- Profile API: Master profile data (source of truth - NO fabrication allowed)
- Job API: Job description data
- Document API: Document storage
- LLM Service: AI generation (via ILLMService port with anti-hallucination constraints)
- Database: GenerationModel, ProfileModel (for example resume references)
- Background Queue: asyncio tasks (no Celery for MVP)

### External
- LLM Provider: OpenAI GPT-4o-mini or Claude Haiku (cost-optimized for MVP)

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
    total_stages INTEGER DEFAULT 2,  -- Simplified to 2 stages
    stage_name TEXT,
    stage_description TEXT,
    error_message TEXT,
    options TEXT,  -- JSON: {"template": "modern", "length": "one_page", "example_resume_url": "..."}
    result TEXT,   -- JSON: {"document_id": "...", "ats_score": 0.87, "fabrication_check": "passed", ...}
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
- `id`: UUID primary key (returned as `id` in API responses, not `generation_id`)
- `user_id`: Owner of the generation
- `profile_id`: Source profile for generation (master resume content)
- `job_id`: Target job for tailoring
- `document_type`: Type of document ('resume', 'cover_letter')
- `status`: Current state (pending, generating, completed, failed, cancelled)
- `current_stage`: Pipeline stage (0-2, simplified from 5 stages)
- `total_stages`: Total pipeline stages (always 2 for MVP)
- `stage_name`: Human-readable stage name (see Stage Names table)
- `stage_description`: Stage progress description (see Stage Names table)
- `error_message`: Error details if failed
- `options`: JSON with generation options (includes example_resume_url if provided)
- `result`: JSON with final result (document_id, ats_score, fabrication_check status)
- `tokens_used`: Total LLM tokens consumed (target: <5000)
- `generation_time`: Total processing time in seconds (target: <8s)
- `created_at`: Generation request timestamp
- `started_at`: Pipeline start timestamp
- `completed_at`: Pipeline completion timestamp
- `updated_at`: Last update timestamp (auto-updates)

## Options JSON Schema

The `options` field stores generation parameters as JSON. Schema:

```json
{
  "type": "object",
  "properties": {
    "template": {
      "type": "string",
      "enum": ["modern", "classic", "creative"],
      "default": "modern",
      "description": "Resume template style"
    },
    "length": {
      "type": "string",
      "enum": ["one_page", "two_page"],
      "default": "one_page",
      "description": "Target resume length"
    },
    "focus_areas": {
      "type": "array",
      "items": {"type": "string"},
      "maxItems": 5,
      "description": "Skills/experiences to emphasize"
    },
    "include_cover_letter": {
      "type": "boolean",
      "default": false,
      "description": "Generate matching cover letter"
    },
    "custom_instructions": {
      "type": "string",
      "maxLength": 500,
      "description": "Additional generation instructions"
    }
  }
}
```

**Example stored options**:
```json
{
  "template": "modern",
  "length": "one_page",
  "focus_areas": ["leadership", "cloud_architecture"],
  "include_cover_letter": false,
  "custom_instructions": "Emphasize AWS and team management experience"
}
```

**Constraints**:
- Foreign key cascade delete (when user/profile/job deleted, generations deleted)
- `status` must be one of: pending, generating, completed, failed, cancelled
- `document_type` must be: resume or cover_letter
- `current_stage` range: 0-2 (simplified from 0-5)
- `total_stages` must be 2 for MVP (will be 5 in future enhancement)

## Data Flow

```
Generation Lifecycle:

1. Client → POST /generations/resume {profile_id, job_id, options}
2. API validates JWT → get user_id
3. API validates profile and job ownership
4. API creates GenerationModel (status: pending)
5. API ← 201 Created {generation_id, status, Location header}

Background Pipeline (2 stages - SIMPLIFIED):

Stage 1: Analysis & Matching (3s, 2500 tokens)
- Extract job keywords, requirements, seniority level
- Score user's experiences/projects by relevance to job
- Rank content for inclusion
- LLM prompt with role assignment: "Act as a resume analyzer..."
- Output: Ranked content list with relevance scores

Stage 2: Generation & Validation (5s, 2500 tokens)
- Generate tailored resume using ONLY ranked user content
- Apply example resume structure if provided
- Enforce anti-fabrication rules in prompt:
  * "Use ONLY experiences from: [user's profile]"
  * "Use ONLY skills from: [user's skill list]"
  * "DO NOT invent projects, dates, or achievements"
- Self-validate output against input content
- Calculate ATS score and keyword coverage
- Output: Resume text (text, HTML, markdown) + metrics

Progress Updates:
- Each stage updates generation.current_stage
- Client polls GET /generations/{id} for status (2s interval)
- Status transitions: pending → generating → completed|failed

Final State:
- Status: completed
- Result: {
    document_id, 
    ats_score, 
    match_percentage, 
    pdf_url,
    fabrication_check: "passed", // NEW: confirms no invented content
    keyword_coverage: 0.78,
    content_source_verification: {...} // NEW: maps generated content to source
  }
- Metadata: tokens_used (<5000), generation_time (<8s)

6. Client → GET /generations/{id}/result
7. API ← {document_id, pdf_url, ats_score, content, fabrication_check}
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
    "focus_areas": ["leadership", "cloud_architecture"],
    "include_cover_letter": false,
    "custom_instructions": "Emphasize cloud architecture experience",
    "example_resume_url": "https://storage.example.com/resumes/example.pdf"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "gen-uuid",
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
- `Location: /api/v1/generations/{id}`

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
  "id": "gen-uuid",
  "status": "generating",
  "progress": {
    "current_stage": 1,
    "total_stages": 2,
    "percentage": 40,
    "stage_name": "Analysis & Matching",
    "stage_description": "Analyzing job and matching with your profile content"
  },
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "tokens_used": 2500,
  "estimated_completion": "2025-10-21T10:30:08Z",
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:03Z"
}
```

**Response (Completed)** (200 OK):
```json
{
  "id": "gen-uuid",
  "status": "completed",
  "progress": {
    "current_stage": 2,
    "total_stages": 2,
    "percentage": 100,
    "stage_name": "Generation & Validation",
    "stage_description": "Completed"
  },
  "result": {
    "document_id": "doc-uuid",
    "ats_score": 0.87,
    "match_percentage": 82,
    "keyword_coverage": 0.78,
    "keywords_matched": 14,
    "keywords_total": 18,
    "pdf_url": "/api/v1/documents/doc-uuid/download",
    "fabrication_check": "passed",
    "recommendations": [
      "Add AWS certification to skills section",
      "Quantify team size in leadership experience"
    ]
  },
  "tokens_used": 4850,
  "generation_time": 7.8,
  "profile_id": "uuid",
  "job_id": "job-uuid",
  "created_at": "2025-10-21T10:30:00Z",
  "completed_at": "2025-10-21T10:30:08Z",
  "updated_at": "2025-10-21T10:30:08Z"
}
```

**Response (Failed)** (200 OK):
```json
{
  "id": "gen-uuid",
  "status": "failed",
  "progress": {
    "current_stage": 1,
    "total_stages": 2,
    "percentage": 40
  },
  "error_message": "LLM service unavailable. Please try again.",
  "tokens_used": 2500,
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:05Z"
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
  "id": "gen-uuid",
  "document_id": "doc-uuid",
  "document_type": "resume",
  "content": {
    "text": "John Doe\nSoftware Engineer\n\nPROFESSIONAL SUMMARY\n...",
    "html": "<html><body>...",
    "markdown": "# John Doe\n## Software Engineer\n..."
  },
  "ats_score": 0.87,
  "match_percentage": 82,
  "keyword_coverage": 0.78,
  "keywords_matched": 14,
  "keywords_total": 18,
  "pdf_url": "/api/v1/documents/doc-uuid/download",
  "fabrication_check": "passed",
  "recommendations": [
    "Add AWS certification to skills section",
    "Quantify team size in leadership experience"
  ],
  "metadata": {
    "template": "modern",
    "length": "one_page",
    "tokens_used": 4850,
    "generation_time": 7.8
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

**Response** (201 Created): New generation object (new id)

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
      "id": "gen-uuid",
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
1. `analysis_matcher.py`: Job analysis + profile content matching
2. `content_generator_validator.py`: Resume generation + quality validation

### Performance Targets
- Stage 1: 3s (Analysis & Matching)
- Stage 2: 5s (Generation & Validation)
- Total: <8s (p50), <10s (p95)
- Token usage: <5000 tokens per generation
- Cost: ~$0.10 per generation (GPT-4o-mini pricing)

### Anti-Fabrication Measures

**Critical**: System MUST NOT invent content. All resume content comes from user's profile.

**LLM Prompt Constraints**:
```python
ANTI_FABRICATION_RULES = """
CRITICAL RULES - DO NOT VIOLATE:
1. Use ONLY experiences from the provided user profile
2. Use ONLY skills explicitly listed in the user's skill list
3. DO NOT invent:
   - Projects or work experiences
   - Dates or time periods
   - Achievements or accomplishments
   - Technologies or tools not in profile
4. If job requires a skill user lacks:
   - OMIT the skill from generated resume
   - Add to recommendations: "Consider adding [skill]"
5. All bullet points must map to source content in profile

If you cannot generate quality resume from available content alone,
return error: "insufficient_profile_content"
"""
```

**Validation Process**:
1. Extract all facts from generated resume
2. Verify each fact exists in source profile
3. Flag any unmapped content as potential fabrication
4. Include `fabrication_check` in result: "passed" | "warning" | "failed"
5. If "warning" or "failed", include `fabrication_details` with unmapped content

**Example Result**:
```json
{
  "fabrication_check": "passed",
  "content_verification": {
    "experiences_verified": 3,
    "skills_verified": 12,
    "projects_verified": 2,
    "unmapped_content": []
  }
}
```

### Testing
- Test generation creation
- Test pipeline stages individually
- Test status transitions
- Test polling behavior
- Test rate limiting
- Test error handling
- Mock LLM service for fast tests
## Backend Implementation (Pydantic v2 Patterns)
### Request/Response DTOs
**File**: `app/application/dtos/generation_dtos.py`
All DTOs use **Pydantic v2** syntax (November 2025). See full implementation in GROQ_LLM_ARCHITECTURE.md for additional examples.
**Key Patterns**:
1. **model_config = ConfigDict(from_attributes=True)** for ORM conversion (replaces orm_mode=True)
2. **@field_validator** decorator with @classmethod for field validation
3. **@model_validator** for cross-field validation logic
4. **Field()** with constraints (ge, le, max_length, pattern, etc.)
5. **frozen=True** for immutable response models
6. **.model_validate()** to convert ORM models (replaces .parse_obj())
7. **.model_dump()** to serialize (replaces .dict())
### Pydantic v2 Migration Summary
| Pydantic v1 | Pydantic v2 |
|-------------|-------------|
| `class Config: orm_mode = True` | `model_config = ConfigDict(from_attributes=True)` |
| `@validator('field')` | `@field_validator('field')` with `@classmethod` |
| `@root_validator` | `@model_validator(mode='after')` |
| `.parse_obj(obj)` | `.model_validate(obj)` |
| `.dict()` | `.model_dump()` |
| `Field(alias='name')` | Same, but use `populate_by_name=True` in ConfigDict |
**Documentation**: See docs/BACKEND_DESIGN_DOCUMENT.md Section 7.4 for complete DTO pattern examples with Pydantic v2.
## Async SQLAlchemy Patterns (2025 Best Practices)
### Async Engine and Session Configuration
**File**: `app/infrastructure/database/connection.py`
``python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
# Create async engine (use asyncpg for PostgreSQL, aiosqlite for SQLite)
engine = create_async_engine(
    settings.database_url,  # e.g., "postgresql+asyncpg://user:pass@host/db"
    echo=settings.debug,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # Verify connections before use
)
# Session factory for dependency injection
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False  # Keep objects usable after commit
)
# Base class with AsyncAttrs for lazy loading support
class Base(AsyncAttrs, DeclarativeBase):
    pass
``
### Dependency Injection Pattern
**File**: `app/core/dependencies.py`
``python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.connection import async_session_maker
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session (2025 pattern).
    Usage:
        @router.post("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db here
    Pattern:
        - async with context manager ensures proper cleanup
        - yield provides session to endpoint
        - Session closed automatically after endpoint returns
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
``
### Repository Pattern with Async Methods
**File**: `app/infrastructure/repositories/generation_repository.py`
``python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.infrastructure.database.models import GenerationModel
from app.domain.entities.generation import Generation
class GenerationRepository:
    """
    Async repository for Generation entity (2025 pattern).
    All methods use async/await with proper transaction management.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
    async def create(self, generation: Generation) -> GenerationModel:
        """
        Create new generation with async transaction.
        Pattern: Add object, flush for ID assignment, refresh for relationships
        """
        model = GenerationModel(
            user_id=generation.user_id,
            profile_id=generation.profile_id,
            job_id=generation.job_id,
            document_type=generation.document_type.value,
            status="pending",
            current_stage=0,
            total_stages=2
        )
        self.session.add(model)
        await self.session.flush()  # Assign ID without commit
        await self.session.refresh(model)  # Load relationships
        return model
    async def get_by_id(
        self,
        generation_id: str,
        user_id: int
    ) -> Optional[GenerationModel]:
        """
        Get generation by ID with ownership check (async query).
        Pattern: Use select() statement with where() clause, await scalars().first()
        """
        stmt = (
            select(GenerationModel)
            .where(
                GenerationModel.id == generation_id,
                GenerationModel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
    async def get_by_user(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[GenerationModel]:
        """
        Get paginated generations for user (async query with eager loading).
        Pattern: selectinload() for N+1 query prevention, limit/offset for pagination
        """
        stmt = (
            select(GenerationModel)
            .where(GenerationModel.user_id == user_id)
            .options(
                selectinload(GenerationModel.job),  # Eager load job relationship
                selectinload(GenerationModel.profile)
            )
            .order_by(GenerationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    async def update_status(
        self,
        generation_id: str,
        status: str,
        current_stage: int,
        stage_name: Optional[str] = None,
        stage_description: Optional[str] = None
    ) -> None:
        """
        Update generation progress (async update query).
        Pattern: Use update() statement for bulk updates without loading object
        """
        stmt = (
            update(GenerationModel)
            .where(GenerationModel.id == generation_id)
            .values(
                status=status,
                current_stage=current_stage,
                stage_name=stage_name,
                stage_description=stage_description
            )
        )
        await self.session.execute(stmt)
        # Note: No commit here - let service layer control transaction boundary
    async def delete(self, generation_id: str, user_id: int) -> bool:
        """
        Delete generation with ownership check (async delete).
        Pattern: delete() statement with where() clause
        """
        stmt = (
            delete(GenerationModel)
            .where(
                GenerationModel.id == generation_id,
                GenerationModel.user_id == user_id
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0  # True if row was deleted
``
### Service Layer Transaction Management
**File**: `app/application/services/generation_service.py`
``python
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.generation_repository import GenerationRepository
class GenerationService:
    """Service with explicit transaction boundaries (2025 pattern)"""
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = GenerationRepository(session)
    async def create_generation(
        self,
        user_id: int,
        profile_id: str,
        job_id: str
    ) -> GenerationModel:
        """
        Create generation with async transaction.
        Pattern: Service controls commit/rollback, repository does I/O
        """
        # Validate ownership first
        profile = await self._validate_profile_ownership(user_id, profile_id)
        job = await self._validate_job_ownership(user_id, job_id)
        # Create generation
        generation = Generation(
            user_id=user_id,
            profile_id=profile_id,
            job_id=job_id
        )
        model = await self.repository.create(generation)
        # Commit transaction (async)
        await self.session.commit()
        return model
    async def _validate_profile_ownership(
        self,
        user_id: int,
        profile_id: str
    ) -> ProfileModel:
        """Async query with error handling"""
        stmt = select(ProfileModel).where(ProfileModel.id == profile_id)
        result = await self.session.execute(stmt)
        profile = result.scalars().first()
        if not profile:
            raise NotFoundError("Profile not found")
        if profile.user_id != user_id:
            raise ForbiddenError("Profile does not belong to user")
        return profile
``
### API Endpoint with Transaction Handling
**File**: `app/presentation/api/v1/generation.py`
``python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.application.services.generation_service import GenerationService
router = APIRouter(prefix="/generations")
@router.post("/resume")
async def create_resume_generation(
    request: CreateResumeGenerationRequest,
    db: AsyncSession = Depends(get_db)  # Dependency injection
):
    """
    API endpoint with async database operations (2025 pattern).
    Pattern:
        - FastAPI injects AsyncSession via Depends(get_db)
        - Session lifecycle managed by dependency
        - Service handles transaction commit
        - Automatic rollback on exception
    """
    service = GenerationService(session=db)
    try:
        generation = await service.create_generation(
            user_id=current_user["id"],
            profile_id=request.profile_id,
            job_id=request.job_id
        )
        return GenerationResponse.model_validate(generation)
    except Exception as e:
        # Session automatically rolled back by dependency cleanup
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
``
### Key Async SQLAlchemy Patterns
1. **Engine Creation**: Use `create_async_engine()` with async driver (asyncpg, aiosqlite)
2. **Session Factory**: Use `async_sessionmaker()` for dependency injection
3. **Queries**: Use `select()` with `await session.execute()`, then `.scalars()` for results
4. **Updates**: Use `update()` statement with `await session.execute()`
5. **Deletes**: Use `delete()` statement with `await session.execute()`
6. **Eager Loading**: Use `selectinload()` or `joinedload()` to avoid N+1 queries
7. **Transaction Control**: Service layer calls `await session.commit()` or `await session.rollback()`
8. **Dependency Injection**: Use `async with async_session_maker() as session` in FastAPI dependencies
9. **AsyncAttrs**: Use for lazy loading relationships (`await model.awaitable_attrs.relationship`)
10. **Context Managers**: Use `async with session.begin()` for auto-commit/rollback
**Documentation**: See SQLAlchemy 2.0 async documentation for complete reference.
