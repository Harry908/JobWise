# JobWise Frontend Architecture Overview

**Version**: 1.0  
**Platform**: Flutter (iOS & Android)  
**State Management**: Riverpod (Hybrid: Code Generation + StateNotifier)  
**Last Updated**: December 2025

---

## 1. Frontend Architecture Layers

The Flutter mobile app follows a **layered architecture** with clear separation of concerns, inspired by Clean Architecture principles adapted for Flutter/Riverpod.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                │
│  Screens: auth_screens.dart, profile_*.dart, job_*.dart                     │
│  Widgets: Reusable UI components, form fields, layouts                      │
│  UI logic, user interactions, navigation                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                       STATE MANAGEMENT LAYER                                │
│  Providers: auth_provider.dart, profile_provider.dart, job_provider.dart    │
│  State management with Riverpod (StateNotifier + Code Generation)           │
│  Business logic orchestration, data transformations                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                            SERVICE LAYER                                    │
│  API Clients: auth_api_client.dart, profiles_api_client.dart                │
│  HTTP communication, request/response handling, error mapping               │
│  BaseHttpClient with Dio (interceptors, auto-refresh, snake_case)          │
├─────────────────────────────────────────────────────────────────────────────┤
│                             DATA LAYER                                      │
│  Models: user.dart, profile.dart, job.dart, generation.dart                 │
│  Data classes (Freezed + Manual), JSON serialization                        │
│  Local storage: SharedPreferences, flutter_secure_storage                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
   Presentation ─────► State Management ─────► Services ─────► Data Models
        │                     │                     │                │
        │                     │                     │                │
        ▼                     ▼                     ▼                ▼
     Widgets             Providers            API Clients        Storage
```

- **Presentation** depends on Providers (never directly on API clients).
- **State Management** orchestrates API calls and manages UI state transitions.
- **Services** handle HTTP communication and data serialization/deserialization.
- **Data** contains pure data classes with no business logic.

---

## 2. Frontend Folder Structure (Actual Implementation)

This folder structure reflects the **actual current implementation** of the Flutter mobile app.

```
mobile_app/
├── lib/
│   ├── main.dart                      # App entry point, loads AppConfig, initializes ProviderScope
│   ├── app.dart                       # Root widget, GoRouter setup, theme configuration
│   │
│   ├── config/
│   │   └── app_config.dart            # Environment variables (API_BASE_URL from .env)
│   │
│   ├── constants/
│   │   ├── colors.dart                # AppColors color palette
│   │   └── text_styles.dart           # AppTextStyles typography definitions
│   │
│   ├── models/                        # DATA LAYER - Data Models
│   │   ├── user.dart                  # User entity (manual implementation)
│   │   ├── auth_response.dart         # AuthResponse DTO (manual)
│   │   ├── profile.dart               # MasterProfile with nested classes (manual)
│   │   │                              # - PersonalInfo, Experience, Education, Skills, Project
│   │   ├── job.dart + .freezed + .g   # Job entity (Freezed + JSON serialization)
│   │   │                              # - Enums: JobSource, JobStatus, ApplicationStatus
│   │   └── generation.dart + .freezed + .g  # Generation entity (Freezed)
│   │
│   ├── providers/                     # STATE MANAGEMENT LAYER
│   │   │
│   │   │   # Code Generation Providers (@riverpod)
│   │   ├── auth_provider.dart + .g.dart       # Auth state with auto-login
│   │   ├── profile_provider.dart + .g.dart    # Profile CRUD operations
│   │   ├── job_provider.dart + .g + .freezed  # Jobs with optimistic updates
│   │   ├── settings_provider.dart + .g.dart   # User preferences
│   │   ├── api_provider.dart + .g.dart        # API client instances
│   │   │
│   │   │   # StateNotifier Providers (traditional pattern)
│   │   ├── generations_provider.dart          # AI generation with progress tracking
│   │   └── samples_provider.dart              # Sample document management
│   │
│   ├── services/                      # SERVICE LAYER
│   │   ├── storage_service.dart       # SharedPreferences wrapper
│   │   ├── settings_service.dart      # User preferences persistence
│   │   ├── job_service.dart           # Job-specific business logic
│   │   │
│   │   └── api/                       # HTTP API Clients
│   │       ├── base_http_client.dart  # Dio client with interceptors
│   │       │                          # - JWT injection
│   │       │                          # - Auto token refresh on 401
│   │       │                          # - Snake case ↔ camel case conversion
│   │       │                          # - Error handling & logging
│   │       ├── auth_api_client.dart   # /api/v1/auth/* endpoints
│   │       ├── profiles_api_client.dart # /api/v1/profiles/* endpoints
│   │       ├── jobs_api_client.dart   # /api/v1/jobs/* endpoints
│   │       ├── samples_api_client.dart # /api/v1/samples/* endpoints
│   │       ├── generations_api_client.dart # /api/v1/generations/* endpoints
│   │       └── exports_api_client.dart # /api/v1/exports/* endpoints (S3 downloads)
│   │
│   ├── screens/                       # PRESENTATION LAYER - Screens
│   │   │                              # Note: Flat structure (no feature folders)
│   │   │
│   │   │   # Authentication (2 screens in 1 file)
│   │   ├── auth_screens.dart          # LoginScreen + RegisterScreen
│   │   │
│   │   │   # Profile Management (3 screens)
│   │   ├── profile_view_screen.dart   # Profile display with completeness
│   │   ├── profile_edit_screen.dart   # Multi-section profile editor
│   │   ├── settings_screen.dart       # Account settings, preferences
│   │   │
│   │   │   # Job Management (4 screens)
│   │   ├── job_list_screen.dart       # User's saved jobs with filters
│   │   ├── job_detail_screen.dart     # Two tabs: Details + AI Generation
│   │   ├── job_paste_screen.dart      # Paste job text for AI parsing
│   │   ├── job_browse_screen.dart     # Browse mock/external jobs
│   │   │
│   │   │   # Document Export (3 screens)
│   │   ├── template_selection_screen.dart  # Template picker with previews
│   │   ├── export_options_screen.dart      # Customization & export
│   │   ├── exported_files_screen.dart      # File management & downloads
│   │   │
│   │   │   # Utilities
│   │   └── debug_screen.dart          # Developer tools & diagnostics
│   │
│   ├── widgets/                       # Reusable UI Components
│   │   ├── loading_overlay.dart       # Full-screen loading indicator
│   │   ├── custom_text_field.dart     # Styled text input
│   │   ├── custom_button.dart         # Primary/secondary buttons
│   │   ├── job_card.dart              # Job list item widget
│   │   ├── job_detail_view.dart       # Job details tab content
│   │   ├── job_generation_tab.dart    # AI generation UI (embedded in JobDetailScreen)
│   │   ├── experience_form.dart       # Experience editor form
│   │   ├── education_form.dart        # Education editor form
│   │   ├── project_form.dart          # Project editor form
│   │   ├── skills_section.dart        # Skills management widget
│   │   └── tag_input.dart             # Chip-based tag input
│   │
│   └── utils/
│       └── validators.dart            # Form validation helpers
│
├── android/                           # Android platform code
├── ios/                               # iOS platform code
├── web/                               # Web platform code (future)
├── test/                              # Unit & widget tests
├── .env                               # Environment configuration (API_BASE_URL)
├── pubspec.yaml                       # Flutter dependencies
├── analysis_options.yaml              # Linting rules
└── README.md                          # Mobile app documentation
```

---

## 3. Layer Responsibilities

### 3.1 Config & Constants (`lib/config/`, `lib/constants/`)

| File | Purpose |
|------|---------|
| `app_config.dart` | Loads `.env` variables (API_BASE_URL), provides app-wide configuration |
| `colors.dart` | Defines `AppColors` palette (primary, secondary, accent, backgrounds, text) |
| `text_styles.dart` | Defines `AppTextStyles` typography (headings, body, captions) |

### 3.2 Data Layer (`lib/models/`)

| Model | Implementation | Purpose |
|-------|----------------|---------|
| `user.dart` | Manual | User entity (id, email, fullName) |
| `auth_response.dart` | Manual | Authentication response (accessToken, refreshToken, user) |
| `profile.dart` | Manual with nested classes | Master resume profile with PersonalInfo, Experience, Education, Skills, Project |
| `job.dart` | **Freezed** + JSON | Job entity with enums (JobSource, JobStatus, ApplicationStatus) |
| `generation.dart` | **Freezed** + JSON | AI generation results with metadata |
| `exported_file.dart` | Manual | Exported file metadata with S3 presigned download URLs |
| `template.dart` | Manual | Export template definitions (Modern, Classic, Creative, ATS-Optimized) |
| `exported_file.dart` | Manual | Exported file metadata with S3 download URLs |
| `template.dart` | Manual | Export template definitions and customization options |

**Pattern Decision**: 
- **Freezed** for entities with complex behavior (Job, Generation) → immutability, copy-with, equality
- **Manual** for simple DTOs (User, Profile) → less boilerplate, easier to understand

### 3.3 State Management Layer (`lib/providers/`)

#### Hybrid Riverpod Approach

The app uses **two state management patterns**:

##### A. Code Generation Pattern (`@riverpod`)

Used for: **Simple CRUD operations** (Auth, Profile, Jobs, Settings)

**Advantages**:
- Less boilerplate code
- Automatic disposal
- Better performance with fine-grained reactivity
- Type-safe generated code

**Example**:
```dart
@Riverpod(keepAlive: true)
class Auth extends _$Auth {
  @override
  Future<User?> build() async {
    // Auto-login from stored tokens
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      return await _api.getCurrentUser();
    }
    return null;
  }

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final response = await _api.login(email, password);
      await _saveTokens(response);
      return response.user;
    });
  }
}
```

##### B. StateNotifier Pattern (Traditional)

Used for: **Complex flows with multiple stages** (Generations, Samples)

**Advantages**:
- Explicit state transitions
- Better for progress tracking
- Easier to debug complex flows
- More control over state updates

**Example**:
```dart
class GenerationsNotifier extends StateNotifier<GenerationsState> {
  GenerationsNotifier(this._api) : super(GenerationsState.initial());

  Future<Map<String, dynamic>?> generateResume({
    required String jobId,
    required int maxExperiences,
    required int maxProjects,
  }) async {
    state = state.copyWith(
      isLoading: true,
      currentStage: 'Analyzing job posting...',
      progress: 0.1,
    );

    // Multi-stage generation with progress updates
    // ...
  }
}
```

#### Key Providers

| Provider | Pattern | State Type | Responsibility |
|----------|---------|------------|----------------|
| `authProvider` | Code Gen | `AsyncValue<User?>` | Auth state, auto-login, token refresh |
| `profileProvider` | Code Gen | `AsyncValue<Profile?>` | Profile CRUD, auto-reload on auth change |
| `userJobsProvider` | Code Gen | `AsyncValue<List<Job>>` | Jobs with optimistic updates |
| `settingsProvider` | Code Gen | `AsyncValue<Settings>` | User preferences |
| `generationsProvider` | StateNotifier | `GenerationsState` | AI generation with progress tracking |
| `samplesProvider` | StateNotifier | `SamplesState` | Sample document management |
| `exportsProvider` | StateNotifier | `ExportsState` | Document export with S3 downloads |

### 3.4 Service Layer (`lib/services/`)

#### HTTP Client Architecture (`lib/services/api/`)

**BaseHttpClient** - Foundation for all API clients

**Key Features**:
1. **JWT Injection**: Automatically adds `Authorization: Bearer <token>` to all requests
2. **Auto Token Refresh**: Intercepts 401 errors, refreshes token, retries original request
3. **Case Conversion**: Converts camel case (Dart) ↔ snake case (Python backend)
4. **Error Handling**: Extracts user-friendly messages from API responses
5. **Logging**: Request/response logging for debugging

**Interceptor Flow**:
```
Request → JWT Injection → Send to Backend
                            ↓
                       401 Response?
                            ↓
                    Refresh Token → Retry Original Request
                            ↓
                       Success/Error
```

**API Client Pattern**:
```dart
class JobsApiClient {
  final BaseHttpClient _client;

  Future<List<Job>> getUserJobs({
    String? status,
    String? applicationStatus,
  }) async {
    final response = await _client.get('/jobs', queryParameters: {
      if (status != null) 'status': status,
      if (applicationStatus != null) 'application_status': applicationStatus,
    });

    return (response.data as List)
        .map((json) => Job.fromJson(_client.toCamelCase(json)))
        .toList();
  }
}
```

#### Storage Services

| Service | Purpose | Technology |
|---------|---------|------------|
| `StorageService` | Secure token storage | flutter_secure_storage |
| `SettingsService` | User preferences | SharedPreferences |

### 3.5 Presentation Layer (`lib/screens/`, `lib/widgets/`)

#### Screen Architecture

**Design Decision**: **Flat structure** instead of feature-based folders

**Rationale**:
- Simpler navigation for small-to-medium apps
- Easier file discovery
- Less deep nesting
- All screens visible at a glance

**Trade-offs**:
- ✅ Simplicity now
- ❌ Scalability later (may need refactor if app grows significantly)

#### Key Screens

| Screen | Route | Purpose |
|--------|-------|---------|
| `LoginScreen` | `/login` | User authentication |
| `RegisterScreen` | `/register` | New user signup |
| `ProfileViewScreen` | `/profile/view` | Display profile with completeness indicator |
| `ProfileEditScreen` | `/profile/edit` | Multi-section profile editor |
| `JobListScreen` | `/jobs` | User's saved jobs with filters |
| `JobDetailScreen` | `/jobs/:id` | **Two-tab interface**: Job Details + AI Generation |
| `JobPasteScreen` | `/jobs/paste` | Paste job text for AI parsing |
| `JobBrowseScreen` | `/jobs/browse` | Browse mock/external jobs |
| `SettingsScreen` | `/settings` | Account settings, sample management |
| `DebugScreen` | `/debug` | Developer tools |
| `TemplateSelectionScreen` | `/export/templates` | Choose export template with previews |
| `ExportOptionsScreen` | `/export/options` | Customize and export documents |
| `ExportedFilesScreen` | `/export/files` | Manage and download exports from S3 |

#### Widget Composition Pattern

**Design Decision**: **Widget composition over separate screens** for complex features

**Example**: AI Generation integrated into `JobDetailScreen` via `JobGenerationTab` widget

**Benefits**:
- Better context (job details visible during generation)
- Less navigation complexity
- Unified user experience
- Shared state between tabs

**Implementation**:
```dart
// JobDetailScreen with TabController
TabBarView(
  controller: _tabController,
  children: [
    JobDetailView(job: job),           // Tab 1: Job Details
    JobGenerationTab(job: job),        // Tab 2: AI Generation
  ],
)
```

---

## 4. Core Features Implementation

### 4.1 Authentication Flow

**Endpoints**: `/api/v1/auth/*`  
**Provider**: `authProvider` (Code Generation)  
**Screens**: `LoginScreen`, `RegisterScreen`

**Key Features**:
- User registration with email validation
- Login with JWT token management
- Automatic token refresh on 401 errors
- Auto-login from stored tokens on app start
- Password strength validation
- Email availability checking
- Secure token storage (flutter_secure_storage)

**State Transitions**:
```
Unauthenticated → Loading → Authenticated
                    ↓
                  Error
```

**Auto-Login Flow**:
```
1. App starts → main.dart loads AppConfig
2. ProviderScope initializes → authProvider.build() called
3. Read access_token from secure storage
4. If token exists → Call /auth/me
5. Success → Set user in state
6. Failure → Clear tokens, stay unauthenticated
```

### 4.2 Profile Management

**Endpoints**: `/api/v1/profiles/*`  
**Provider**: `profileProvider` (Code Generation)  
**Screens**: `ProfileViewScreen`, `ProfileEditScreen`

**Key Features**:
- Master resume profile CRUD operations
- Multi-section editing (Personal Info, Experiences, Education, Skills, Projects)
- Bulk operations for nested collections
- Profile completeness analytics
- Auto-reload when auth state changes
- Optimistic updates with rollback

**Profile Auto-Reload**:
```dart
@riverpod
class Profile extends _$Profile {
  @override
  Future<Profile?> build() async {
    // Watch auth state changes
    final authState = ref.watch(authProvider);
    
    if (authState.value == null) return null;
    
    return await _api.getCurrentUserProfile();
  }
}
```

### 4.3 Job Management

**Endpoints**: `/api/v1/jobs/*`  
**Provider**: `userJobsProvider` (Code Generation)  
**Screens**: `JobListScreen`, `JobDetailScreen`, `JobPasteScreen`, `JobBrowseScreen`

**Key Features**:
- Job CRUD with filters (status, application_status)
- Mock job browsing
- Text paste with AI parsing
- Two-tab job detail view
- Optimistic updates for status changes
- Real-time job list updates

**Optimistic Update Pattern**:
```dart
Future<void> updateJob(Job updatedJob) async {
  final previousState = state;
  
  // Optimistically update UI
  state = AsyncValue.data(
    state.value!.map((job) => 
      job.id == updatedJob.id ? updatedJob : job
    ).toList(),
  );

  try {
    // Persist to backend
    await _api.updateJob(updatedJob.id, updatedJob);
  } catch (e) {
    // Rollback on error
    state = previousState;
    rethrow;
  }
}
```

### 4.4 AI Generation (Integrated Feature)

**Endpoints**: `/api/v1/generations/*`, `/api/v1/rankings/*`  
**Provider**: `generationsProvider` (StateNotifier)  
**Widget**: `JobGenerationTab` (embedded in `JobDetailScreen`)

**Key Features**:
- Resume generation with customization (max experiences/projects)
- Cover letter generation (company name, hiring manager)
- Progress dialogs with multi-stage indicators
- Generation history per job
- Copy to clipboard
- ATS score display

**Progress Tracking**:
```dart
class GenerationsState {
  final bool isLoading;
  final String? currentStage;  // "Analyzing job...", "Generating resume..."
  final double progress;       // 0.0 to 1.0
  final List<Generation> history;
  final String? error;
}
```

**Generation Stages**:
```
1. Analyzing job posting... (10%)
2. Ranking your experiences... (30%)
3. Selecting best projects... (50%)
4. Generating resume content... (70%)
5. Finalizing document... (90%)
6. Complete! (100%)
```

### 4.5 Sample Management (Integrated Feature)

**Endpoints**: `/api/v1/samples/*`  
**Provider**: `samplesProvider` (StateNotifier)  
**Integration**: Settings screen + Generation tab prompts

**Key Features**:
- Upload `.txt` resume/cover letter samples
- File picker integration
- Active sample indicators
- Sample management in settings
- Upload prompts in generation UI

### 4.6 Document Export (Cross-Platform Feature)

**Endpoints**: `/api/v1/exports/*`  
**Provider**: `exportsProvider` (StateNotifier)  
**Screens**: `TemplateSelectionScreen`, `ExportOptionsScreen`, `ExportedFilesScreen`

**Key Features**:
- **PDF/DOCX Export**: Professional formatting with 4 templates
- **Template Selection**: Modern, Classic, Creative, ATS-Optimized
- **Customization**: Fonts, colors, spacing, margins
- **S3 Cloud Storage**: Files stored in AWS S3 bucket
- **Cross-Platform Access**: Generate on mobile, download on web/desktop
- **Presigned URLs**: Secure, time-limited download links
- **File Management**: List, download, delete exports
- **Storage Quotas**: 100 MB free tier, auto-cleanup after 30 days

**Security Architecture**:
```dart
// User-scoped S3 keys prevent cross-user access
s3_key = "exports/{user_id}/{export_id}.{format}"

// Examples:
// - exports/user-123/export-456.pdf  ✅ User 123 can access
// - exports/user-999/export-456.pdf  ❌ User 123 CANNOT access
```

**Export Flow**:
```
1. User completes generation on JobDetailScreen
2. Tap "Export to PDF" → Navigate to TemplateSelectionScreen
3. Choose template (Modern/Classic/Creative/ATS-Optimized)
4. Navigate to ExportOptionsScreen
5. Customize options (font, colors, spacing)
6. Tap "Export" → exportsProvider.exportToPDF()
7. ExportsApiClient calls POST /api/v1/exports/pdf
8. Backend generates PDF, uploads to S3
9. Backend stores export metadata with s3_key
10. Backend returns export_id and download_url (presigned)
11. Mobile app downloads file or stores export_id
12. User switches to web app on laptop
13. Web app calls GET /api/v1/exports/files (lists user's exports)
14. User clicks download → GET /api/v1/exports/files/{export_id}/download
15. Backend verifies user owns export (user_id match)
16. Backend generates fresh presigned URL
17. Web browser downloads from S3
```

**Download Options**:
- **Mobile**: Download to device, open with system viewer, share via apps
- **Web**: Browser download, email attachment, cloud storage save
- **Desktop**: Direct download, save to Documents folder

**Data Models**:
```dart
class ExportedFile {
  final String exportId;           // UUID from backend
  final String generationId;       // Source generation
  final String format;             // 'pdf', 'docx', 'zip'
  final String template;           // 'modern', 'classic', etc.
  final String filename;           // User-facing filename
  final String downloadUrl;        // Presigned S3 URL (expires in 1 hour)
  final int fileSizeBytes;
  final DateTime createdAt;
  final DateTime expiresAt;        // Auto-delete date (30 days)
  final int downloadCount;
}

class Template {
  final String id;
  final String name;
  final String description;
  final int atsScore;              // 75-98%
  final List<String> industries;   // ['Tech', 'Corporate', ...]
  final String previewUrl;         // Template preview image
  final TemplateCustomization customization;
}
```

**State Management**:
```dart
class ExportsState {
  final List<Template> templates;
  final List<ExportedFile> exports;
  final bool isExporting;
  final double exportProgress;     // 0.0 to 1.0
  final String? currentStage;      // "Generating PDF...", "Uploading..."
  final int storageUsedBytes;
  final int storageLimitBytes;     // 100 MB free tier
  final String? error;
}
```

**Authorization Security**:
- ✅ JWT required for all export endpoints
- ✅ S3 keys scoped by user_id → prevents cross-user access
- ✅ Database queries filter by user_id
- ✅ Presigned URLs time-limited (1 hour default, 7 days max)
- ✅ Private S3 bucket → no public access
- ✅ HTTPS/TLS encryption in transit
- ✅ SSE-S3 encryption at rest

---

## 5. Data Flow Architecture

### 5.1 Authentication Flow
```
LoginScreen → authProvider.login()
    ↓
AuthApiClient.login() → POST /api/v1/auth/login
    ↓
Backend returns {access_token, refresh_token, user}
    ↓
StorageService saves tokens
    ↓
authProvider updates state with user
    ↓
GoRouter redirects to /home
```

### 5.2 Profile Lifecycle Flow
```
ProfileEditScreen → Submit form
    ↓
profileProvider.updateProfile(profile)
    ↓
ProfilesApiClient.updateProfile() → PUT /api/v1/profiles/{id}
    ↓
Backend validates and persists
    ↓
profileProvider updates state
    ↓
ProfileViewScreen shows updated data
```

### 5.3 Job Update with Optimistic UI
```
JobListScreen → User changes status
    ↓
userJobsProvider.updateJob(updatedJob)
    ↓
Immediately update UI (optimistic)
    ↓
JobsApiClient.updateJob() → PUT /api/v1/jobs/{id}
    ↓
Success: UI already updated
Failure: Rollback UI + show error
```

### 5.4 Token Refresh Flow
```
Any API call → 401 Unauthorized
    ↓
BaseHttpClient error interceptor catches 401
    ↓
Read refresh_token from storage
    ↓
POST /api/v1/auth/refresh
    ↓
Backend returns new {access_token, refresh_token}
    ↓
Save new tokens
    ↓
Retry original request with new token
    ↓
Success → Return response to caller
Failure → Logout user, redirect to login
```

### 5.5 AI Generation Flow
```
JobDetailScreen → JobGenerationTab → Tap "Generate Resume"
    ↓
generationsProvider.generateResume(jobId, options)
    ↓
Update state: isLoading=true, stage="Analyzing job..."
    ↓
GenerationsApiClient.generateResume() → POST /api/v1/generations/resume
    ↓
Backend: Create ranking → Generate resume → Calculate ATS score
    ↓
Update state: stage="Generating resume..." (progress updates)
    ↓
Backend returns Generation object
    ↓
Update state: isLoading=false, add to history
    ↓
JobGenerationTab displays result with copy button
```

---

## 6. Navigation Architecture (GoRouter)

### Route Configuration

```dart
final router = GoRouter(
  initialLocation: '/login',
  redirect: (context, state) {
    final isAuthenticated = ref.read(authProvider).value != null;
    final isAuthRoute = state.location.startsWith('/auth');

    if (!isAuthenticated && !isAuthRoute) {
      return '/login';  // Redirect to login
    }
    if (isAuthenticated && isAuthRoute) {
      return '/home';   // Redirect to home
    }
    return null;  // No redirect
  },
  routes: [
    GoRoute(path: '/login', builder: (context, state) => LoginScreen()),
    GoRoute(path: '/register', builder: (context, state) => RegisterScreen()),
    GoRoute(path: '/home', builder: (context, state) => HomeScreen()),
    GoRoute(path: '/profile/view', builder: (context, state) => ProfileViewScreen()),
    GoRoute(path: '/profile/edit', builder: (context, state) => ProfileEditScreen()),
    GoRoute(path: '/jobs', builder: (context, state) => JobListScreen()),
    GoRoute(path: '/jobs/:id', builder: (context, state) => JobDetailScreen(
      jobId: state.pathParameters['id']!,
    )),
    GoRoute(path: '/jobs/paste', builder: (context, state) => JobPasteScreen()),
    GoRoute(path: '/jobs/browse', builder: (context, state) => JobBrowseScreen()),
    GoRoute(path: '/settings', builder: (context, state) => SettingsScreen()),
    GoRoute(path: '/debug', builder: (context, state) => DebugScreen()),
  ],
);
```

**Auth Guard**: Automatically redirects unauthenticated users to login

---

## 7. Error Handling Strategy

### Backend Error Format
```json
{
  "detail": "User-friendly message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Email already registered"]
  }
}
```

### Frontend Error Extraction
```dart
String _extractErrorMessage(dynamic data, int? statusCode) {
  if (data is Map) {
    if (data.containsKey('detail')) return data['detail'];
    if (data.containsKey('message')) return data['message'];
    if (data.containsKey('field_errors')) {
      final errors = data['field_errors'] as Map;
      return errors.values.first.first;
    }
  }
  return 'An error occurred. Please try again.';
}
```

### User-Facing Error Display

**Form Validation Errors**: Inline below fields
```dart
TextFormField(
  decoration: InputDecoration(
    errorText: state.emailError,
  ),
)
```

**API Errors**: SnackBars
```dart
ScaffoldMessenger.of(context).showSnackBar(
  SnackBar(content: Text(errorMessage)),
);
```

**Loading States**: Overlays
```dart
if (isLoading)
  const LoadingOverlay(message: 'Saving profile...'),
```

---

## 8. Code Generation Workflow

### Required Commands

```bash
# Generate all code (Riverpod + Freezed + JSON)
dart run build_runner build --delete-conflicting-outputs

# Watch mode for development
dart run build_runner watch --delete-conflicting-outputs
```

### Generated Files

| Pattern | Purpose | Example |
|---------|---------|---------|
| `*.g.dart` | Riverpod providers + JSON serialization | `auth_provider.g.dart`, `job.g.dart` |
| `*.freezed.dart` | Freezed immutable models | `job.freezed.dart`, `generation.freezed.dart` |

### Dependencies

```yaml
dependencies:
  flutter_riverpod: ^2.x
  riverpod_annotation: ^2.x
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

---

## 9. Security Architecture

- **Token Storage**: JWT tokens stored in `flutter_secure_storage` (encrypted platform storage)
- **Auto Token Refresh**: Transparent refresh on 401, no user intervention
- **Secure Communication**: HTTPS only (enforced by backend)
- **No Sensitive Data in Logs**: Error messages sanitized before display
- **Session Management**: Logout clears all tokens and navigates to login

---

## 10. Performance & Scalability

### Optimization Strategies

**1. Optimistic Updates**
- Immediate UI feedback
- Rollback on error
- Better perceived performance

**2. Fine-Grained Reactivity**
- Riverpod auto-dispose unused providers
- Watch only necessary state slices
- Minimize rebuilds

**3. Pagination**
- Job lists support pagination (default 20, max 100)
- Generation history paginated

**4. Caching**
- Provider results cached automatically
- Manual cache invalidation when needed

**5. Lazy Loading**
- Screens loaded on demand
- Images lazy-loaded with placeholders

---

## 11. Testing Strategy

### Test Coverage

**Unit Tests**:
- Model serialization/deserialization
- Validation logic
- Business logic in providers

**Widget Tests**:
- Screen rendering
- User interactions
- Form validation

**Integration Tests**:
- API client responses
- Provider state transitions
- End-to-end flows

**Example Unit Test**:
```dart
test('Job.fromJson should parse backend response', () {
  final json = {
    'id': '123',
    'title': 'Software Engineer',
    'company': 'TechCorp',
    'job_source': 'user_created',
    'status': 'active',
    'application_status': 'not_applied',
  };

  final job = Job.fromJson(json);

  expect(job.id, '123');
  expect(job.title, 'Software Engineer');
  expect(job.jobSource, JobSource.userCreated);
});
```

---

## 12. Architecture Decision Records (ADRs)

### ADR-F001: Hybrid State Management (Code Gen + StateNotifier)

**Decision**: Use Riverpod code generation for simple CRUD, StateNotifier for complex flows

**Rationale**:
- Code generation reduces boilerplate for standard patterns
- StateNotifier provides explicit control for multi-stage processes
- Best of both worlds approach

**Trade-offs**:
- ✅ Flexibility to choose the right tool
- ❌ Two patterns to learn and maintain
- ❌ Less consistency across codebase

---

### ADR-F002: Freezed for Complex Models Only

**Decision**: Use Freezed for entities with complex behavior (Job, Generation), manual classes for simple DTOs

**Rationale**:
- Freezed provides immutability, copy-with, equality for free
- Manual classes are simpler for basic data transfer objects
- Avoid over-engineering simple models

**Trade-offs**:
- ✅ Less boilerplate for simple models
- ✅ Powerful features where needed
- ❌ Mixed patterns across codebase

---

### ADR-F003: Flat Screen Structure

**Decision**: Single `screens/` folder instead of feature-based organization

**Rationale**:
- Simpler for current app size (9 screens)
- Easier file discovery
- Less deep nesting

**Future Consideration**: May need refactor to feature folders if app grows beyond 20 screens

**Trade-offs**:
- ✅ Simplicity now
- ❌ Scalability later

---

### ADR-F004: Widget Composition over Separate Screens

**Decision**: Integrate complex features (generation) as widgets within related screens

**Example**: `JobGenerationTab` inside `JobDetailScreen` instead of separate `GenerationScreen`

**Rationale**:
- Better context (job details visible during generation)
- Less navigation complexity
- Unified user experience
- Shared state between tabs

**Trade-offs**:
- ✅ Better UX
- ✅ Less navigation code
- ❌ Larger screen files
- ❌ Less deep linking capability

---

### ADR-F005: Optimistic Updates with Rollback

**Decision**: Update UI immediately, rollback on error

**Rationale**:
- Better perceived performance
- Immediate user feedback
- Most operations succeed, so rollback is rare

**Trade-offs**:
- ✅ Responsive UI
- ✅ Better UX
- ❌ Slightly more complex code
- ❌ Potential for state inconsistency during network failures

---

### ADR-F006: GoRouter for Navigation

**Decision**: Use GoRouter instead of Navigator 2.0 directly

**Rationale**:
- Declarative routing
- Deep linking support
- Type-safe routes
- Auth guards built-in

**Benefits**:
- ✅ Cleaner code
- ✅ Better testability
- ✅ Deep linking ready

---

### ADR-F007: Dio over http Package

**Decision**: Use Dio for HTTP client

**Rationale**:
- Built-in interceptors (auth, logging, error handling)
- Request/response transformation
- Better error handling
- Auto-retry support

**Key Feature**: Automatic token refresh with transparent retry

**Benefits**:
- ✅ Less boilerplate
- ✅ Powerful interceptor system
- ✅ Better developer experience

---

## 13. Quality Attributes

### Maintainability
- Clear layer separation
- Consistent naming conventions
- Comprehensive documentation
- Type-safe code generation

### Testability
- Dependency injection via Riverpod
- Mockable API clients
- Isolated business logic
- Widget tests for UI

### Reliability
- Error handling at every layer
- Automatic token refresh
- Optimistic updates with rollback
- Offline-friendly architecture (planned)

### Usability
- Responsive UI
- Loading indicators
- Clear error messages
- Intuitive navigation

### Performance
- Lazy loading
- Optimistic updates
- Fine-grained reactivity
- Efficient state management

### Security
- Encrypted token storage
- HTTPS only
- No sensitive data in logs
- Auto-logout on token expiry

---

## 14. Future Enhancements

### Planned Features
- **Offline Support**: SQLite local cache with sync
- **Push Notifications**: Job updates, generation completion
- **Biometric Auth**: Fingerprint/Face ID login
- **Dark Mode**: Theme switching
- **Localization**: Multi-language support
- **Analytics**: User behavior tracking
- **Crash Reporting**: Error monitoring (Firebase Crashlytics)

### Technical Debt
- Refactor to feature-based folders (if app grows)
- Add integration tests for critical flows
- Improve error recovery mechanisms
- Add retry logic for failed operations
- Implement proper logging framework

---

## 15. Related Documentation

**Backend Documentation**:
- `../BACKEND_ARCHITECTURE_OVERVIEW.md` - Backend architecture overview
- `../api-services/01-authentication-api.md` - Auth API specification
- `../api-services/02-profile-api.md` - Profile API specification
- `../api-services/03-job-api.md` - Job API specification
- `../api-services/04a-sample-upload-api.md` - Sample upload API
- `../api-services/04b-ai-generation-api.md` - AI generation API
- `../api-services/05-document-export-api.md` - Document export API

**Mobile Documentation**:
- `./mobile-new/README.md` - Mobile features index
- `./mobile-new/00-api-configuration.md` - API client setup
- `./mobile-new/01-authentication-feature.md` - Auth feature details
- `./mobile-new/02-profile-management-feature.md` - Profile feature details
- `./mobile-new/03-job-browsing-feature.md` - Job feature details
- `./mobile-new/04-generation-feature.md` - AI generation feature details
- `./mobile-new/05-document-feature.md` - Document export feature details

---

**Document Maintenance**:
- This document reflects the **actual current implementation** as of December 2025
- Update this document when making architectural changes
- Keep in sync with backend API specifications
- Review quarterly for accuracy
