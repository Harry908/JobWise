# JobWise System Design - Clean Architecture

## Executive Summary

JobWise remains aligned with **Clean Architecture** and **Hexagonal** patterns while tracking the complete API surface defined in `docs/api-services/01-06`. Although only subsets may be feature-flagged on in a given environment, the system design documents how authentication, profiles, jobs, sample upload, AI generation, document export, and database schema interact end-to-end so teams can toggle capabilities without architectural drift.

### API Coverage Snapshot
| Spec | Domain | Runtime Status |
|------|--------|----------------|
| 01 | Authentication | Active across all environments |
| 02 | Profile Management | Active |
| 03 | Job Management | Active |
| 04a | Sample Upload & Writing Style | Active with LLM integration |
| 04b | AI Generation & Ranking | Active with Groq LLM |
| 05 | Document Export | **Design Complete - S3 Integration Ready** |
| 06 | Database Schema | Canonical for every deployment |

**Export Feature Status**:
- ✅ S3 Storage Adapter implemented with security best practices
- ✅ User-scoped authorization (exports/{user_id}/{export_id}.{ext})
- ✅ Presigned URL generation for cross-platform downloads
- ✅ Encryption at rest (SSE-S3) and in transit (HTTPS/TLS)
- ✅ Security documentation complete
- 📋 Export service implementation pending
- 📋 PDF/DOCX rendering engines pending

## Core Design Principles

### 1. Clean Architecture Layers
```
┌─────────────────────────────────────┐
│         Presentation Layer          │ ← Flutter UI, FastAPI routers
├─────────────────────────────────────┤
│         Application Layer           │ ← Use cases, services, DTOs
├─────────────────────────────────────┤
│            Domain Layer             │ ← Entities, aggregates, rules
├─────────────────────────────────────┤
│        Infrastructure Layer         │ ← SQLAlchemy, adapters
└─────────────────────────────────────┘
```

### 2. Dependency Direction
- Controllers depend on application services, which in turn depend on domain interfaces.
- Domain entities have no knowledge of FastAPI, SQLAlchemy, or external APIs.
- Repositories and gateways implement interfaces defined in the domain/application layers (Ports & Adapters).
- Dependency injection (FastAPI + custom factories) binds concrete implementations at runtime.

### 3. Configuration Strategy
- Environment-driven settings distinguish local (SQLite) vs. deployed (PostgreSQL) stacks.
- JWT, database URL, and observability toggles live in `.env` and are surfaced through Pydantic settings objects.
- No model-provider or object-storage secrets remain, simplifying deployment.

## System Context (C4 Model Level 1)

```
                ┌─────────────────┐
                │   Job Seeker    │
                │ (Mobile Client) │
                └────────┬────────┘
                         │ HTTPS/JSON
                ┌────────▼────────┐
                │   JobWise API   │
                │ (FastAPI App)   │
                └────────┬────────┘
                         │ SQL/HTTP
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐               ┌────────▼────────┐
│  SQL Database  │               │ Optional Job    │
│ (SQLite/PG)    │               │ Feed Adapters   │
└────────────────┘               └─────────────────┘
```

## Container Architecture (C4 Model Level 2)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                     JobWise Platform                                      │
│                                                                           │
│  ┌────────────────────────┐    HTTPS/JSON   ┌─────────────────┐          │
│  │    Flutter App         │◄───────────────►│  FastAPI API    │          │
│  │  (Android/iOS/Web)     │                 │   (Backend)     │          │
│  │                        │                 │                 │          │
│  │ ┌──────────────────┐   │                 │ ┌─────────────┐ │          │
│  │ │ Riverpod State   │   │                 │ │  Routers    │ │          │
│  │ │ Management       │   │                 │ │  Services   │ │          │
│  │ └──────────────────┘   │                 │ │ Repositories│ │          │
│  │ ┌──────────────────┐   │                 │ └──────┬──────┘ │          │
│  │ │ Freezed Models   │   │                 │        │        │          │
│  │ │ (Immutable DTOs) │   │                 │  ┌─────▼──────┐ │          │
│  │ └──────────────────┘   │                 │  │ S3 Adapter │ │          │
│  │ ┌──────────────────┐   │                 │  └─────┬──────┘ │          │
│  │ │ Dio HTTP Client  │   │                 │        │        │          │
│  │ │ (Auto-refresh)   │   │                 │        │        │          │
│  │ └──────────────────┘   │                 │        │        │          │
│  │ ┌──────────────────┐   │    Presigned    │        │        │          │
│  │ │ File Downloader  │◄──┼─────URLs────────┼────────┘        │          │
│  │ └──────────────────┘   │    (HTTPS)      │                 │          │
│  └────────────────────────┘                 └────────┬────────┘          │
│                                                      │                    │
│                                      ┌───────────────┴─────────┐          │
│                                      │                         │          │
│                              ┌───────▼─────────┐    ┌──────────▼────────┐ │
│                              │ PostgreSQL/     │    │  AWS S3 Bucket    │ │
│                              │ SQLite DB       │    │  (Private)        │ │
│                              │ (SQLAlchemy)    │    │  exports/{user}/  │ │
│                              └─────────────────┘    └───────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture (C4 Model Level 3)

### Flutter Client Architecture

#### State Management: Hybrid Riverpod Pattern

The app uses a **hybrid state management approach** combining:
- **Riverpod Code Generation** (`@riverpod`) for auth, profile, and jobs
- **Traditional StateNotifier** for generations and samples

**Code Generation Providers** (with `riverpod_annotation`):
```dart
@Riverpod(keepAlive: true)
class Auth extends _$Auth {
  @override
  Future<User?> build() async {
    // Auto-loads user from stored tokens
    final hasTokens = await _storage.hasTokens();
    if (hasTokens) {
      return await _api.getCurrentUser();
    }
    return null;
  }
}
```

**Traditional StateNotifier** (for complex flows):
```dart
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  Future<Map<String, dynamic>?> generateResume({
    required String jobId,
    int maxExperiences = 5,
  }) async {
    // Progressive state updates with stages
    state = state.copyWith(
      isGenerating: true,
      progress: 0.2,
      currentStage: 'Analyzing job requirements...',
    );
    // ...
  }
}
```

**Key Providers**:
- `authProvider` → `AsyncValue<User?>` (code generation)
- `profileProvider` → `AsyncValue<Profile?>` (code generation)
- `userJobsProvider` → `AsyncValue<List<Job>>` (code generation)
- `generationsProvider` → `GenerationsState` (StateNotifier)
- `samplesProvider` → `SamplesState` (StateNotifier)
- `settingsProvider` → `SettingsState` (code generation)

#### Data Models: Freezed + Manual Classes

**Freezed Models** (immutable with code generation):
- `Job` - User's saved jobs with enums for status/source
- `Generation` - AI generation results and metadata
- All models include `.freezed.dart` + `.g.dart` generated files

**Manual Models** (custom implementation):
- `User` - Authentication user entity
- `Profile` - Master resume profile with nested collections
- `Sample` - Uploaded sample documents
- Nested classes: `PersonalInfo`, `Experience`, `Education`, `Skills`, `Project`

#### File Structure
```
lib/
├── main.dart                    # App entry, loads AppConfig
├── app.dart                     # GoRouter setup, theme, auth guards
├── config/
│   └── app_config.dart         # Env vars (API_BASE_URL from .env)
├── constants/
│   ├── colors.dart             # AppColors palette
│   └── text_styles.dart        # AppTextStyles typography
├── models/
│   ├── user.dart               # Manual model
│   ├── auth_response.dart      # Manual model
│   ├── profile.dart            # Manual model with nested classes
│   ├── job.dart + .freezed + .g.dart      # Freezed model
│   └── generation.dart + .freezed + .g.dart
├── providers/
│   ├── auth_provider.dart + .g.dart       # Code generation
│   ├── profile_provider.dart + .g.dart
│   ├── job_provider.dart + .g.dart + .freezed.dart
│   ├── generations_provider.dart          # StateNotifier
│   ├── samples_provider.dart              # StateNotifier
│   └── settings_provider.dart + .g.dart
├── screens/                     # Flat structure (no feature folders)
│   ├── auth_screens.dart       # Login + Register in one file
│   ├── profile_view_screen.dart
│   ├── profile_edit_screen.dart
│   ├── job_list_screen.dart
│   ├── job_detail_screen.dart  # Two tabs: Details + AI Generation
│   ├── job_paste_screen.dart
│   ├── job_browse_screen.dart
│   ├── settings_screen.dart
│   └── debug_screen.dart
├── services/
│   ├── storage_service.dart    # SharedPreferences wrapper
│   ├── settings_service.dart   # User preferences
│   └── api/
│       ├── base_http_client.dart    # Dio + interceptors
│       ├── auth_api_client.dart
│       ├── profiles_api_client.dart
│       ├── jobs_api_client.dart
│       └── generations_api_client.dart
├── utils/
│   └── validators.dart         # Form validation helpers
└── widgets/                     # Reusable UI components
    ├── loading_overlay.dart
    ├── error_display.dart
    ├── job_card.dart
    ├── job_detail_view.dart
    ├── job_generation_tab.dart  # Integrated into JobDetailScreen
    ├── profile_cards.dart
    └── tag_input.dart
```

#### HTTP Client Architecture

**BaseHttpClient** (Dio-based with interceptors):
```dart
class BaseHttpClient {
  final Dio _dio;
  final StorageService _storage;

  // Request Interceptor: Auto-inject Bearer token
  onRequest: (options, handler) async {
    final token = await _storage.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  // Error Interceptor: 401 → auto-refresh → retry
  onError: (error, handler) async {
    if (error.response?.statusCode == 401 && 
        !error.requestOptions.path.contains('/auth/refresh')) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Retry with new token
        final newToken = await _storage.getToken();
        opts.headers['Authorization'] = 'Bearer $newToken';
        final response = await _dio.fetch(opts);
        return handler.resolve(response);
      }
    }
    handler.next(error);
  }
}
```

**Key Features**:
- Automatic JWT injection on all authenticated requests
- Token refresh on 401 with transparent retry
- Snake case ↔ camel case conversion in API clients
- User-friendly error message extraction
- Request/response logging for debugging

#### Routing (GoRouter)

**Routes**:
```
/login              → LoginScreen
/register           → RegisterScreen
/home               → HomeScreen (auth required)
/profile/view       → ProfileViewScreen
/profile/edit       → ProfileEditScreen
/jobs               → JobListScreen
/jobs/:id           → JobDetailScreen (with tabs)
/jobs/paste         → JobPasteScreen
/jobs/browse        → JobBrowseScreen
/settings           → SettingsScreen
/debug              → DebugScreen
```

**Auth Guards**: Redirects to `/login` if `authProvider` returns null user.

#### UI Architecture Patterns

**Widget Composition over Separate Screens**:
- Generation UI integrated into `JobDetailScreen` via `JobGenerationTab` widget
- Two-tab interface: "Job Details" + "AI Generation"
- Benefits: Better context, less navigation, unified UX

**Optimistic Updates with Rollback**:
```dart
Future<void> updateJob(Job job) async {
  final previousState = state;
  
  // Optimistic update
  state.whenData((jobs) {
    state = AsyncValue.data([
      for (final j in jobs)
        if (j.id == job.id) job else j
    ]);
  });

  try {
    final updatedJob = await _jobsApi.updateJob(...);
    // Confirm with server response
  } catch (e) {
    state = previousState; // Rollback on error
    rethrow;
  }
}
```

#### Module Breakdown

**Auth Module**:
- `LoginScreen`, `RegisterScreen` (combined file)
- `authProvider` with auto-login from stored tokens
- Token refresh flow handled by BaseHttpClient
- Email availability check during registration

**Profile Module**:
- `ProfileViewScreen` with completeness indicator
- `ProfileEditScreen` multi-section form
- Bulk operations for experiences, education, projects
- Analytics display (completeness score, missing sections)

**Jobs Module**:
- `JobListScreen` with filters (status, source)
- `JobDetailScreen` with dual tabs
- `JobBrowseScreen` for mock/external jobs
- `JobPasteScreen` for text input (AI parsing)
- Optimistic updates for status changes

**Generation Module** (integrated):
- `JobGenerationTab` widget within JobDetailScreen
- Resume generation options (max experiences/projects)
- Cover letter generation (company name, hiring manager)
- Progress dialogs with stage indicators
- Generation history list per job
- Copy to clipboard, ATS score display

**Samples Module** (integrated):
- File picker integration for `.txt` uploads
- Sample management in profile settings
- Active sample indicators
- Upload prompts in generation tab

**Shared Services**:
- `StorageService` - Secure token storage (SharedPreferences)
- `SettingsService` - User preferences (theme, date format)
- HTTP client - Dio with automatic refresh
- Validators - Form validation helpers

### FastAPI Backend
```
┌────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│ │ Auth Router  │ │ ProfileRouter│ │ Job Router   │          │
│ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘          │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ AuthSvc   │    │ ProfileSvc│    │ JobSvc    │            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │UserRepo   │    │ProfileRepo│    │ JobRepo   │            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ TokenSvc  │    │ SampleSvc │    │ RankingSvc│            │
│  └─────┬─────┘    └─────┬─────┘    └─────┬─────┘            │
│        │                │                │                  │
│  ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐            │
│  │ LLMAdapter│    │ ExportSvc │◄───┤ Generation │            │
│  └───────────┘    └─────┬─────┘    └─────┬─────┘            │
│                          │                │                  │
│                     ┌────▼────┐      ┌────▼────┐             │
│                     │ S3Adapter│      │ History │            │
│                     └─────────┘      └─────────┘            │
└────────────────────────────────────────────────────────────┘
```
Routers for Sample Upload, Generation, and Export remain available behind feature flags; their services plug into shared repositories and adapters.

## Domain Model

### MasterProfile (Aggregate Root)
```
Attributes: id, user_id, personal_info, professional_summary,
skills, custom_fields, created_at, updated_at
Child Collections: experiences, education, projects

Rules:
- personal_info must contain contact methods.
- at least one of experiences or education is required for a publishable profile.
- timestamps are managed centrally to avoid client drift.
```

### Job (Entity)
```
Attributes: id, user_id, source, title, company, location,
description, parsed_keywords, requirements, benefits,
salary_range, employment_type, status, application_status,
created_at, updated_at

Rules:
- title/company are mandatory.
- application_status transitions must follow the allowed state machine defined in services.
- mock jobs have `user_id` null and are read-only.
```

### ProfileAnalytics (Value Object)

### SampleDocument (Entity)
```
Attributes: id, user_id, document_type, original_filename,
word_count, character_count, line_count, is_active,
text_blob, created_at, updated_at

Rules:
- only `.txt` samples accepted in prototype.
- uploading a new active sample of the same type deactivates the previous one.
```

### WritingStyle (Value Object)
```
Attributes: user_id, tone, structure, vocabulary, cadence,
model_metadata, source_sample_id, extracted_at

Rules:
- computed from the latest active cover-letter sample.
- cached for reuse across multiple generations.
```

### JobContentRanking (Entity)
```
Attributes: id, user_id, job_id, ranked_experience_ids,
ranked_project_ids, ranked_skill_clusters, model_name,
confidence_scores, created_at

Rules:
- generated per job/context pair.
- reused until job description changes or user invalidates it.
```

### Generation (Aggregate Root)
```
Attributes: id, user_id, job_id, profile_id, ranking_id,
document_type, status, ats_score, ats_feedback,
content_text, options, llm_metadata, created_at

Rules:
- resume generation is deterministic; cover letter generation leverages LLM adapter and writing style.
- history must remain immutable; retries create new records.
```

### Export (Entity)
```
Attributes: id, user_id, generation_id, document_type,
format, template, filename, file_path, file_size_bytes,
page_count, options, metadata, expires_at, download_count

Rules:
- exports require completed generations.
- `expires_at` enforced by scheduled cleanup jobs.
```
```
Attributes: completeness_score, missing_sections, warning_flags,
last_evaluated_at

Rules:
- Derived entirely from persisted profile data.
- Contains no external-model metadata.
```

## Application Layer Architecture

### Auth Use Cases
- **RegisterUserCommand** → creates user, hashes password, returns auth tokens.
- **LoginCommand** → validates credentials, issues JWT + refresh pair.
- **ResetPasswordCommand** → validates token, replaces password hash.

### Profile Use Cases
- **CreateOrUpdateProfileCommand** → upserts master profile and nested records within a transaction.
- **BulkExperienceCommand / BulkEducationCommand** → batch operations that enforce ownership and ordering.
- **GetProfileAnalyticsQuery** → materializes `ProfileAnalytics` for UI consumption.

### Job Use Cases
- **CreateJobCommand** → saves user-created or parsed jobs.
- **BrowseJobsQuery** → returns mock feed with pagination and total counts.
- **UpdateJobStatusCommand** → sets `status` or `application_status` with validation.

### Sample Upload & Style Use Cases (04a)
- **UploadSampleCommand** → validates `.txt` payloads, calculates stats, stores text, toggles `is_active`.
- **ListSamplesQuery** / **DeleteSampleCommand** → manage stored samples per user.
- **ExtractWritingStyleJob** → asynchronous process that updates `writing_styles` from the latest cover-letter sample.

### Ranking & Generation Use Cases (04b)
- **EnhanceProfileCommand** → applies LLM prompts to enrich summaries/descriptions, writes to `enhanced_*` columns.
- **CreateRankingCommand** → runs LLM analysis on job postings and persists `job_content_rankings`.
- **GenerateResumeCommand** → compiles ranked content without LLM usage, stores `generations` row.
- **GenerateCoverLetterCommand** → calls Groq LLM, injects writing style, and records metadata plus ATS feedback.
- **ListGenerationHistoryQuery** → filters generations for dashboards and export hand-offs.

### Export Use Cases (05)
- **CreateExportCommand** → renders PDF/DOCX/ZIP files, streams to S3/local storage, and logs metadata.
- **ListExportsQuery** → surfaces stored files with pagination and storage usage metrics.
- **DownloadExportCommand** → validates ownership/expiry and either streams bytes or returns pre-signed URLs.
- **DeleteExportCommand** → removes files and metadata, freeing quota.
- **CreateJobCommand** → saves user-created or parsed jobs.
- **BrowseJobsQuery** → returns mock feed with pagination and total counts.
- **UpdateJobStatusCommand** → sets `status` or `application_status` with validation.

DTOs mirror the payloads documented in `docs/api-services/01-03`. No DTO references generation options anymore.

## Infrastructure Layer Design

### Repositories
- **UserRepository** - CRUD for `users`, unique email enforcement.
- **ProfileRepository** - manages `master_profiles` plus child tables using SQLAlchemy relationships.
- **JobRepository** - user job CRUD, mock feed querying, aggregation helpers.
- **SampleRepository** - stores `sample_documents`, enforces active-sample toggles, streams text blobs.
- **WritingStyleRepository** - persists extracted style metadata per user.
- **RankingRepository** - manages `job_content_rankings` with invalidation helpers.
- **GenerationRepository** - handles `generations` lifecycle and history filters.
- **ExportRepository** - stores export metadata, retention states, and download counters.

### Gateways / Adapters
- **PasswordHasher** - wraps Bcrypt and centralizes cost factors.
- **TokenService** - encapsulates JWT signing, verification, and rotation policies.
- **MockJobSourceAdapter** - optional adapter that reads from `data/mock_jobs.json` to seed demo data.
- **LLMAdapter** - handles Groq/OpenAI calls with retry/backoff and telemetry hooks.
- **StyleExtractionWorker** - background worker bridging samples to writing styles.
- **ExportRenderer** - orchestrates WeasyPrint/python-docx templating and packaging.
- **ObjectStorageAdapter** - encapsulates S3 (or local filesystem) interactions, including pre-signed URLs and lifecycle policies.

### Configuration Management
- `Settings` class (Pydantic) loads from environment with sensible defaults and exposes feature flags (`ENABLE_SAMPLES`, `ENABLE_GENERATION`, `ENABLE_EXPORTS`).
- Factory helpers select SQLite vs. PostgreSQL engines based on `APP_ENV` while ensuring optional tables remain migrated.
- Observability toggles enable structured logging levels and request timing metrics, plus opt-in tracing for LLM calls and S3 uploads.

## Frontend-Backend Integration

### API Client Patterns

All API clients follow consistent patterns:

**Snake Case ↔ Camel Case Conversion**:
```dart
Map<String, dynamic> _toCamelCase(Map<String, dynamic> json) {
  final result = <String, dynamic>{};
  json.forEach((key, value) {
    final camelKey = key.replaceAllMapped(
      RegExp(r'_([a-z])'),
      (match) => match.group(1)!.toUpperCase(),
    );
    // Special handling for type conversions
    if (camelKey == 'userId' && value is int) {
      result[camelKey] = value.toString();
    } else {
      result[camelKey] = value;
    }
  });
  return result;
}
```

**Type Conversions**:
- Backend `user_id: int` → Frontend `userId: String`
- Backend `parsed_keywords: List<str>` → Frontend `parsedKeywords: List<String>`
- All date fields use ISO 8601 strings, parsed to `DateTime` on frontend

### Error Handling Strategy

**Backend Error Format**:
```json
{
  "detail": "User-friendly message",
  "error_code": "EMAIL_ALREADY_EXISTS",
  "field_errors": {"email": ["Email already registered"]}
}
```

**Frontend Error Extraction**:
```dart
String _extractErrorMessage(dynamic data, int? statusCode) {
  if (data is Map) {
    if (data['detail'] != null) return data['detail'];
    if (data['message'] != null) return data['message'];
  }
  return 'An error occurred. Please try again.';
}
```

**User-Facing Error Display**:
- Form validation errors inline below fields
- API errors in SnackBars
- Loading overlays dismissed on error
- Retry options for failed operations

### State Synchronization

**Provider Dependencies**:
```dart
// Profile auto-reloads when auth changes
@override
Future<Profile?> build() async {
  final authState = ref.watch(authProvider);
  if (authState.valueOrNull == null) {
    return null;
  }
  return await _api.getCurrentUserProfile();
}
```

**Invalidation Patterns**:
```dart
// After updating a job, invalidate detail view
await ref.read(userJobsProvider.notifier).updateJob(updatedJob);
ref.invalidate(selectedJobProvider(job.id));
```

### Code Generation Workflow

**Required Commands**:
```bash
# Generate all code (Riverpod + Freezed + JSON)
dart run build_runner build --delete-conflicting-outputs

# Watch mode for development
dart run build_runner watch --delete-conflicting-outputs
```

**Generated Files**:
- `*.g.dart` - Riverpod providers + JSON serialization
- `*.freezed.dart` - Freezed immutable models

**Dependencies**:
```yaml
dependencies:
  flutter_riverpod: ^2.x
  freezed_annotation: ^2.x
  json_annotation: ^4.x
  dio: ^5.x
  go_router: ^13.x
  
dev_dependencies:
  build_runner: ^2.x
  riverpod_generator: ^2.x
  freezed: ^2.x
  json_serializable: ^6.x
```

## Data Flow Architecture

### Authentication Flow
```
Client → /auth/register → UserService (validates + hashes password) → UserRepo
Client → /auth/login → TokenService issues JWT/refresh → response headers/body
Client refreshes token before expiry via /auth/refresh
```

### Profile Lifecycle Flow
```
Client → /profiles (POST/PUT) with profile DTO
ProfileService validates ownership + schema
ProfileRepository persists master profile + nested tables in one transaction
ProfileAnalyticsService recomputes summary used by /profiles/{id}/analytics
```

### Job Lifecycle Flow
### Sample → Style Flow
```
Client → /samples/upload with `.txt` payload
SampleService validates + stores text
StyleExtractionWorker triggers (async) and updates writing_styles
Analytics endpoints reuse cached style metadata
```

### Generation Flow
```
Client → /rankings/create (job_id)
RankingService calls LLM, stores job_content_rankings
Client → /generations/resume or /generations/cover-letter
GenerationService composes resume (logic) or invokes LLM for cover letter
Results persisted in generations; history endpoints surface them
```

### Export Flow

**Cross-Platform Document Export with S3 Storage**:

```
1. Generation Phase (Mobile App)
   Client → /generations/resume or /cover-letter
   GenerationService creates generation entity
   Results stored in database with user_id ownership

2. Export Request (Mobile or Web)
   Client → /exports/pdf with {generation_id, template, options}
   ExportService validates:
     - User owns generation (user_id match)
     - Generation exists and is complete
     - Template and options are valid
   
3. Document Rendering
   ExportRenderer fetches generation content
   Applies template formatting (Modern/Classic/Creative/ATS)
   Generates PDF/DOCX binary
   Validates file size (<100 MB)

4. S3 Upload (Secure Storage)
   S3Adapter.upload_file() with user-scoped key:
     - s3_key = "exports/{user_id}/{export_id}.{format}"
     - ServerSideEncryption: AES256 (SSE-S3)
     - ContentType: application/pdf or application/vnd...
     - Metadata: template, ats_score, page_count
   Returns: {s3_key, size_bytes, etag}

5. Database Record
   ExportRepository creates export entity:
     - id: export_id (UUID)
     - user_id: current_user.id (ownership)
     - generation_id: source generation
     - s3_key: S3 object key (user-scoped)
     - file_size_bytes, page_count, format, template
     - expires_at: now + 30 days
   
6. Response to Client
   Returns ExportResponse:
     - export_id: for future download/delete
     - filename: suggested download name
     - download_url: backend endpoint (not S3 direct)
     - file_size_bytes, page_count
     - expires_at

7. Download Flow (Same Device or Cross-Platform)
   Mobile → Web → Desktop (any combination)
   
   Client → /exports/files (list exports)
   Backend queries: SELECT * FROM exports WHERE user_id = current_user.id
   Returns list of exports owned by user
   
   Client → /exports/files/{export_id}/download
   Backend validates:
     - User owns export (query filters by user_id)
     - Export exists and not expired
   
   S3Adapter.generate_presigned_url():
     - Verifies s3_key ownership (exports/{user_id}/...)
     - Generates time-limited URL (default 1 hour, max 7 days)
     - Adds Content-Disposition for custom filename
   
   Backend returns presigned URL
   Client downloads directly from S3 via HTTPS
   
8. Cleanup (Automated Daily Job)
   Scheduled task runs: DELETE FROM exports WHERE expires_at < NOW()
   For each expired export:
     - S3Adapter.delete_file(user_id, export_id, format)
     - Removes S3 object
     - Removes database record
```

**Security Enforcement Points**:
- ✅ JWT authentication required (user_id extraction)
- ✅ Generation ownership verified before export
- ✅ S3 keys scoped by user_id (prevents cross-user access)
- ✅ Database queries filter by user_id (row-level security)
- ✅ Presigned URLs time-limited (no permanent access)
- ✅ Private S3 bucket (no public ACLs)
- ✅ Encryption at rest (SSE-S3) and in transit (HTTPS)
ObjectStorageAdapter uploads file, repository stores metadata
Client retrieves list/download using exports API; cleanup jobs enforce expires_at
```
```
Client → /jobs (POST) to save a job or /jobs/browse to view mock feed
JobService normalizes payload (keywords, requirements lists)
JobRepository writes/reads with pagination + filtering
Application status updates reuse JobService validation to guard transitions
```

## Security Architecture

- **Authentication**: Short-lived JWT access tokens, refresh tokens stored securely on client. Tokens embed `user_id`, `email`, and roles (currently `user` only).
- **Authorization**: Route-level dependencies ensure resources are filtered by `user_id`. Mock browse endpoints remain public but capped via throttling; generation/export APIs require ownership of upstream artifacts.
- **Data Protection**: Passwords hashed with Bcrypt, TLS enforced by the hosting layer, and logs scrub sensitive fields before emission. Export binaries live in private buckets with per-user keys and presigned URL expirations.
- **LLM Governance**: Prompt/response payloads are filtered for PII, and telemetry captures token usage for audit and billing.

## Performance & Scalability

- SQL indexes on `users.email`, `jobs.user_id`, `jobs.status`, `jobs.application_status`, `sample_documents.user_id`, `generations.job_id`, and `exports.user_id` keep lookups bounded.
- Repository queries cap page size (default 20, max 100) to thwart accidental full-table scans.
- Mock job data can be cached in memory for read-heavy demos without affecting user-owned rows; ranking/generation/export queues scale horizontally if high throughput is needed.
- Async FastAPI stack plus background workers keep the service responsive even while LLM or rendering tasks run.
- Feature flags allow horizontal scaling of costly APIs independently from core CRUD traffic.

## Deployment Architecture

### Backend Deployment

- **Prototype / Dev**: Single FastAPI process, SQLite DB, local storage for exports, mocked LLM adapter. Feature flags for APIs 04-05 default to off.
- **Staging**: FastAPI + worker queue + PostgreSQL + MinIO/S3. Sample/generation/export routes toggled on for verification.
- **Production-ready**: Containerized FastAPI app behind an API gateway, PostgreSQL managed service, Redis/Queue for async work, and S3 for exports. Observability includes tracing for LLM and storage calls.
- **CI/CD hooks**: Pytest, coverage, static checks, schema diffing, and contract tests per API spec; feature-flag matrix ensures dormant routes continue to compile.

### Frontend Deployment

**Development**:
```bash
# Install dependencies
flutter pub get

# Generate code
dart run build_runner build --delete-conflicting-outputs

# Run on Android emulator
flutter run

# Run on iOS simulator
flutter run -d ios
```

**Environment Configuration**:
- `.env` file in `mobile_app/` directory
- `API_BASE_URL` environment variable
- Platform-specific defaults:
  - Android Emulator: `http://10.0.2.2:8000/api/v1`
  - iOS Simulator: `http://localhost:8000/api/v1`
  - Physical Device: Actual network IP

**Build Targets**:
```bash
# Android APK
flutter build apk --release

# iOS IPA (requires Mac + Xcode)
flutter build ios --release

# Web (future)
flutter build web --release
```

**CI/CD Pipeline** (planned):
- Automated code generation verification
- Widget and integration tests
- Platform-specific builds
- Deployment to app stores

## Architecture Decision Records (ADRs)

### Backend ADRs

- **ADR-005 - Clean Architecture**: Still in effect; retiring generation features reduced complexity but boundaries remain for future expansion.
- **ADR-006 - Configuration Strategy**: Simplified inputs (JWT + DB) but still uses environment-based instantiation.
- **ADR-007 - Domain-Driven Design**: DDD continues to drive profile/job models so reintroducing AI or exports later will only require new adapters, not rewrites.

### Frontend ADRs

- **ADR-F001 - Hybrid State Management**: 
  - **Decision**: Use Riverpod code generation for simple CRUD, StateNotifier for complex flows
  - **Rationale**: Code generation reduces boilerplate for standard patterns; StateNotifier provides fine-grained control for multi-stage processes (generation with progress tracking)
  - **Status**: Active, documented for future standardization
  - **Trade-offs**: Consistency vs flexibility; new developers must learn both patterns

- **ADR-F002 - Mixed Model Patterns**:
  - **Decision**: Freezed for entities with complex behavior (Job, Generation), manual for simple DTOs (User, Profile)
  - **Rationale**: Freezed provides immutability and pattern matching where needed; manual classes offer control for nested structures
  - **Status**: Active, consider migrating all to Freezed for consistency
  - **Trade-offs**: Less boilerplate vs standardization

- **ADR-F003 - Flat File Structure**:
  - **Decision**: Single `screens/` folder instead of feature-based organization
  - **Rationale**: Small team, rapid development, easy navigation
  - **Status**: Active, may reorganize as app grows
  - **Trade-offs**: Simplicity now vs scalability later

- **ADR-F004 - Widget Composition over Screens**:
  - **Decision**: Integrate complex features (generation) as widgets within related screens (JobDetailScreen)
  - **Rationale**: Better UX with context preservation, reduced navigation
  - **Status**: Active for generation feature
  - **Trade-offs**: Less deep linking capability, larger screen files

- **ADR-F005 - Optimistic Updates with Rollback**:
  - **Decision**: Update UI immediately, rollback on error
  - **Rationale**: Perceived performance improvement, better UX
  - **Status**: Active for job updates
  - **Trade-offs**: Complexity vs responsiveness

- **ADR-F006 - GoRouter for Navigation**:
  - **Decision**: Use GoRouter instead of Navigator 2.0 directly
  - **Rationale**: Declarative routing, type-safe navigation, auth guards
  - **Status**: Active
  - **Benefits**: Deep linking ready, cleaner code

- **ADR-F007 - Dio over http package**:
  - **Decision**: Use Dio for HTTP client
  - **Rationale**: Interceptors for auth, better error handling, request/response logging
  - **Status**: Active
  - **Key Feature**: Automatic token refresh with transparent retry

## Quality Attributes

### Backend Quality Attributes

- **Testability**: Unit tests cover services/repositories; integration tests spin up in-memory FastAPI clients instead of remote HTTP calls; LLM and S3 adapters are mocked behind interfaces; coverage tracked in `htmlcov/`.
- **Maintainability**: Modules map 1:1 to APIs (auth, profiles, jobs, samples, generation, exports) with shared utilities kept in `app/core`; feature flags prevent dead code while retaining design artifacts.
- **Reliability**: Validation + transactional writes guarantee data integrity; health/readiness endpoints monitor DB, LLM, and S3 dependencies; logging includes correlation IDs and request metadata.
- **Security**: JWT best practices, dependency overrides for tests, strict ownership checks, encrypted storage of sample text, and limited lifetimes for export downloads keep data safe even when advanced APIs are enabled.

### Frontend Quality Attributes

- **Testability**: 
  - Unit tests for providers (planned)
  - Widget tests for key screens (planned)
  - Integration tests for critical flows (planned)
  - Mock API clients for isolated testing
  - Current status: Manual testing complete for all features

- **Maintainability**:
  - Flat file structure (no deep nesting)
  - Clear separation: screens, providers, models, services
  - Consistent naming conventions
  - Code generation reduces boilerplate
  - Mix of patterns documented for future standardization

- **Performance**:
  - Optimistic UI updates reduce perceived latency
  - Cached provider state prevents redundant API calls
  - AsyncValue handles loading/error states efficiently
  - Pagination on list endpoints (20/50/100 items)
  - Lazy loading for expensive operations

- **User Experience**:
  - Real-time progress indicators during AI generation
  - Inline validation with immediate feedback
  - Error messages contextualized to user actions
  - Offline-first patterns for form drafts (planned)
  - Smooth transitions with optimistic updates

- **Security**:
  - Tokens stored securely in SharedPreferences
  - Automatic token refresh prevents session expiry
  - No sensitive data in logs
  - API responses validated before use
  - User-scoped data prevents cross-user leaks

- **Scalability**:
  - Provider architecture supports feature flags
  - Modular design allows independent feature development
  - API clients can be swapped without UI changes
  - State management patterns handle complex flows

This streamlined system design documents the post-cleanup baseline so future contributors understand the active architecture and the deliberate omission of AI generation components.