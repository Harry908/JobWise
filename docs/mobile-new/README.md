# JobWise Mobile App - Feature Documentation

**At a Glance (For AI Agents)**
- **Directory Role**: Canonical reference for how the Flutter app talks to the JobWise backend across auth, profile, jobs, AI generation, samples, and exports.
- **Key Index Files**: `00-api-configuration.md` (client config), this `README.md` (map), and feature docs `01`–`05`.
- **Backend Contract Index**: Each feature doc links to a sibling in `../api-services/` with the same numeric prefix (01 auth, 02 profile, 03 jobs, 04x generation, 05 exports).
- **Critical Invariants**: JWT auth required for all `/api/v1/**` except `/auth/*`; jobs use `application_status` as the only status; exports are S3-backed only (no local storage assumptions).

**Related Docs (Navigation Hints)**
- Backend overview: `../JobWise-Services-APIs-Specification.md`, `../BACKEND_ARCHITECTURE_OVERVIEW.md`.
- Backend APIs by number: `../api-services/01-authentication-api.md` through `../api-services/05-document-export-api.md`.
- Mobile feature details: `01-authentication-feature.md`, `02-profile-management-feature.md`, `03-job-browsing-feature.md`, `04a-sample-upload-feature.md`, `04b-ai-generation-feature.md`, `04-generation-feature.md`, `05-document-feature.md`.

**Key Field / Flow Semantics**
- Auth/session: `access_token` / `refresh_token` drive all authenticated Dio requests via `BaseHttpClient`; logout and 401s must clear or refresh these.
- Profile-centric: `Profile.id` is used as the anchor for experiences, education, projects, skills, and AI enhancements.
- Job-centric: `job_id` links job parsing, ranking, and document generation flows; `application_status` drives all job pipeline UI.
- Generation-centric: `generation_id` connects AI outputs to exports and history; `document_type` differentiates resumes vs cover letters.
- Export-centric: `export_id` and `generation_id` form the bridge between text content and S3-backed files; mobile treats `download_url` as opaque.

**Version**: 1.0
**Platform**: Flutter (iOS & Android)
**State Management**: Riverpod
**Last Updated**: November 2025

---

## Overview

This directory contains comprehensive technical documentation for all mobile app features in the JobWise application. Each feature is aligned with its corresponding backend API service and includes complete implementation details for data models, state management, service layer, and UI components.

**Documentation Type**: Technical Implementation Guides
**Audience**: Mobile Developers, Backend Developers, QA Engineers, AI Coding Agents
**Total Features**: 5 core features + 1 configuration guide
**Total Screens**: 16 screens (13 implemented + 3 planned)

---

## Documentation Structure

Each feature document follows a consistent structure:

1. **Overview & User Stories** - Feature purpose and user requirements
2. **Screens** - UI design and user flows for each screen
3. **Backend API Integration** - Complete endpoint documentation with request/response examples
4. **Data Models** - Dart classes with JSON serialization
5. **State Management** - Riverpod StateNotifier implementations
6. **Service Layer** - API client implementations
7. **UI Components** - Reusable widgets
8. **Testing** - Unit and widget test examples
9. **Performance Considerations** - Optimization strategies

---

## Feature Documents

### 0. [API Configuration](00-api-configuration.md)
**Status**: ✅ Fully Implemented

**Purpose**: Base HTTP client setup and authentication

**Key Components**:
- BaseHttpClient with Dio configuration
- JWT token management and auto-refresh
- Request/response interceptors
- Error handling
- Secure token storage

**Used By**: All feature API clients

---

### 1. [Authentication Feature](01-authentication-feature.md)
**Backend API**: [Authentication API](../api-services/01-authentication-api.md)
**Base Path**: `/api/v1/auth`
**Status**: ✅ Fully Implemented

**Screens** (2):
- LoginScreen
- RegisterScreen

**Key Features**:
- User registration with email validation
- Login with JWT token management
- Automatic token refresh on 401 errors
- Password strength validation
- Email availability checking
- Secure token storage (flutter_secure_storage)

**API Endpoints Used**: 9 endpoints
- POST /register
- POST /login
- POST /refresh
- GET /me
- POST /logout
- POST /change-password
- POST /forgot-password
- POST /reset-password
- GET /check-email

**Data Models**:
- User
- AuthResponse
- AuthState

**State Management**:
- AuthNotifier (StateNotifier)
- AuthState (authentication status, user data)

---

### 2. [Profile Management Feature](02-profile-management-feature.md)
**Backend API**: [Profile API](../api-services/02-profile-api.md)
**Base Path**: `/api/v1/profiles`
**Status**: ✅ Fully Implemented

**Screens** (3):
- ProfileViewScreen (profile display with completeness indicator)
- ProfileEditScreen (multi-step form with 5 steps)
- SettingsScreen (account settings and preferences)

**Key Features**:
- Master resume profile CRUD operations
- Multi-step profile editing (Personal Info → Experiences → Education → Skills → Projects)
- Bulk operations for experiences, education, projects
- Skills management (technical, soft, languages, certifications)
- Profile completeness analytics
- Custom fields support

**API Endpoints Used**: 24 endpoints
- Profile CRUD (6 endpoints)
- Experiences bulk operations (4 endpoints)
- Education bulk operations (3 endpoints)
- Projects bulk operations (3 endpoints)
- Skills management (6 endpoints)
- Custom fields (2 endpoints)

**Data Models**:
- Profile
- PersonalInfo
- Experience
- Education
- Project
- Skills (with Language and Certification)
- ProfileState

**State Management**:
- ProfileNotifier (StateNotifier)
- Manages profile, experiences, education, projects, skills

**UI Components**:
- ProfileCompletenessIndicator (circular progress)
- ExperienceCard (expandable)
- EducationCard
- ProjectCard
- SkillsChipGroup

---

### 3. [Job Management Feature](03-job-browsing-feature.md)
**Backend API**: [Job API](../api-services/03-job-api.md)
**Base Path**: `/api/v1/jobs`
**Status**: ✅ Fully Implemented

**Screens** (4):
- JobBrowseScreen (API job search - future)
- JobListScreen (saved jobs with filters)
- JobDetailScreen (job details with keyword highlighting)
- JobPasteScreen (create job from pasted text)

**Key Features**:
- Create job from pasted text with AI parsing
- Create job from URL (scraping - future)
- Create job from structured input
- List saved jobs with filtering (status, source)
- Update application status tracking
- Delete jobs
- Keyword highlighting in job descriptions

**API Endpoints Used**: 5 endpoints
- POST / (create from text, URL, or structured data)
- GET / (list with filters)
- GET /{id} (job details)
- PUT /{id} (update status/keywords)
- DELETE /{id}

**Data Models** (Freezed):
- Job
- JobFilter
- SavedJob
- JobsState

**State Management**:
- JobsNotifier (StateNotifier)
- Manages job list, filters, selected job

**UI Components**:
- JobCard (with company logo, status badge)
- ApplicationStatusBadge (color-coded)
- KeywordHighlighter (highlights job keywords)

---

### 4. Generation Feature (Split into 2 groups)

#### 4a. [Sample Upload Feature](04a-sample-upload-feature.md)
**Backend API**: [Sample Upload API](../api-services/04a-sample-upload-api.md)
**Base Path**: `/api/v1/samples`
**Status**: ✅ Fully Implemented

**Screens** (2):
- SampleUploadScreen
- SampleDetailScreen

**Key Features**:
- Upload sample resumes and cover letters (.txt files)
- View and manage uploaded samples
- Active sample tracking per document type
- Fast CRUD operations (no LLM)

**API Endpoints Used**: 4 endpoints

**State Management**:
- SamplesNotifier (StateNotifier)
- SamplesState (samples list, upload status)

---

#### 4b. [AI Generation Feature](04b-ai-generation-feature.md)
**Backend API**: [AI Generation API](../api-services/04b-ai-generation-api.md)
**Base Path**: `/api/v1`
**Status**: ✅ Fully Implemented

**Screens** (4):
- GenerationOptionsScreen (configure generation settings)
- GenerationProgressScreen (real-time progress tracking)
- GenerationResultScreen (view generated document with ATS score)
- GenerationHistoryScreen (list all generations)

**Key Features**:
- AI-powered profile enhancement using writing style
- Job-specific content ranking (LLM-powered)
- Resume generation (pure logic, <1 second)
- Cover letter generation (LLM-powered, 3-5 seconds)
- Real-time generation progress tracking
- ATS score display and analysis
- Generation history with filtering

**API Endpoints Used**: 6 endpoints

**LLM Integration**:
- Groq API with llama-3.3-70b-versatile (cover letters, enhancements)
- Groq API with llama-3.1-8b-instant (ranking, analysis)

**State Management**:
- GenerationsNotifier (StateNotifier)
- Manages generations, rankings, progress

---

#### [Generation Feature](04-generation-feature.md) (Combined Reference)
**Note**: This is the combined documentation. Use 04a and 04b for focused agent work.

---

### 5. [Document Export Feature](05-document-feature.md)
**Backend API**: [Document Export API](../api-services/05-document-export-api.md)
**Base Path**: `/api/v1/exports`
**Status**: 🔄 Design Complete - Implementation Pending

**Screens** (3 planned):
- TemplateSelectionScreen (choose from 4 templates)
- ExportOptionsScreen (customize export settings)
- ExportedFilesScreen (manage exported files)

**Key Features**:
- PDF export with 4 professional templates
- DOCX export for editable documents
- Template preview before export
- Batch export (resume + cover letter packages)
- File download and management
- Template customization (fonts, colors, spacing, margins)
- Storage tracking and auto-cleanup

**Templates**:
1. **Modern** - 85% ATS - Tech/Startups
2. **Classic** - 95% ATS - Corporate/Finance
3. **Creative** - 75% ATS - Design/Marketing
4. **ATS-Optimized** - 98% ATS - Enterprise/Government

**API Endpoints Planned**: 9 endpoints
- POST /pdf
- POST /docx
- POST /batch
- GET /templates
- GET /templates/{id}
- POST /preview
- GET /files
- GET /files/{id}/download
- DELETE /files/{id}

**Data Models**:
- ExportedFile
- Template
- TemplateCustomization
- ExportOptions
- ExportsState

**State Management**:
- ExportsNotifier (StateNotifier)
- Manages templates, exported files, export progress

**UI Components**:
- TemplateCard (with preview and ATS score)
- ExportOptionsForm (customization controls)
- ExportedFileCard (with open/share/delete actions)
- StorageUsageIndicator

---

## App Architecture

### State Management: Riverpod

**Provider Hierarchy**:
```
AppLevel Providers
├── secureStorageProvider
├── tokenStorageProvider
├── baseHttpClientProvider
└── dioProvider

Feature Providers
├── AuthProvider
│   └── authNotifierProvider
│
├── ProfileProvider
│   └── profileNotifierProvider
│       ├── manages Profile
│       ├── manages Experiences
│       ├── manages Education
│       ├── manages Projects
│       └── manages Skills
│
├── JobsProvider
│   └── jobsNotifierProvider
│       ├── manages Job list
│       ├── manages Filters
│       └── manages Selected job
│
├── GenerationsProvider
│   └── generationsNotifierProvider
│       ├── manages Samples
│       ├── manages Rankings
│       ├── manages Generations
│       └── manages Progress
│
└── ExportsProvider (planned)
    └── exportsNotifierProvider
        ├── manages Templates
        ├── manages Exported files
        └── manages Export progress
```

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│         UI Layer (Screens & Widgets)    │
│  - Screens consume state via Riverpod  │
│  - Widgets are stateless/pure           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    State Layer (Riverpod Providers)     │
│  - StateNotifiers manage feature state  │
│  - Business logic orchestration         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Service Layer (API Clients)        │
│  - HTTP requests via Dio                │
│  - Error handling and transformation    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Models Layer (Data Classes)       │
│  - Freezed models (Job, JobFilter)      │
│  - Manual models (Profile, User)        │
│  - JSON serialization                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Network Layer (Dio HTTP Client)    │
│  - BaseHttpClient with interceptors     │
│  - JWT token injection                  │
│  - Auto token refresh on 401            │
└─────────────────────────────────────────┘
```

---

## Screen Navigation Map

```
AppShell (GoRouter with auth redirect)
│
├── Authentication Flow (Unauthenticated)
│   ├── /login → LoginScreen
│   └── /register → RegisterScreen
│
└── Main App (Authenticated)
    │
    ├── Bottom Navigation Bar
    │   │
    │   ├── Home Tab
    │   │   ├── /home → HomeScreen
    │   │   └── /history → GenerationHistoryScreen
    │   │
    │   ├── Profile Tab
    │   │   ├── /profile → ProfileViewScreen
    │   │   ├── /profile/edit → ProfileEditScreen (multi-step)
    │   │   └── /settings → SettingsScreen
    │   │
    │   ├── Jobs Tab
    │   │   ├── /jobs → JobListScreen
    │   │   ├── /jobs/:id → JobDetailScreen
    │   │   ├── /jobs/paste → JobPasteScreen
    │   │   └── /jobs/browse → JobBrowseScreen (future)
    │   │
    │   └── Generation Tab
    │       ├── /generate → GenerationOptionsScreen
    │       ├── /generate/progress → GenerationProgressScreen
    │       └── /generate/result/:id → GenerationResultScreen
    │
    └── Export Flow (accessed from GenerationResultScreen)
        ├── /export/templates → TemplateSelectionScreen
        ├── /export/options → ExportOptionsScreen
        └── /export/files → ExportedFilesScreen
```

**Total Screens**: 16 screens
- **Implemented**: 13 screens (Auth: 2, Profile: 3, Jobs: 4, Generation: 4)
- **Planned**: 3 screens (Export: 3)

---

## Data Models Summary

### Freezed Models (Immutable with Code Generation)

Used for Job-related entities:
- `Job` - Complete job posting data
- `JobFilter` - Job list filtering options
- `SavedJob` - Simplified job for list view

**Benefits**:
- Immutable by default
- copyWith() method auto-generated
- JSON serialization auto-generated
- Pattern matching support
- Compile-time safety

**Code Generation**:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Manual Models

Used for Auth and Profile entities:
- `User`, `AuthResponse`
- `Profile`, `PersonalInfo`, `Experience`, `Education`, `Project`, `Skills`
- `Sample`, `Generation`, `Ranking`
- `ExportedFile`, `Template`

**Recommendation**: Consider migrating all models to Freezed for consistency.

---

## API Client Architecture

### BaseHttpClient

**File**: `lib/services/api/base_http_client.dart`

**Features**:
- Dio configuration with base URL
- Request interceptor (add JWT token to all requests)
- Response interceptor (logging in debug mode)
- Error interceptor (auto-refresh tokens on 401)
- Timeout configuration (30s connect, 30s receive)

**Base URL Configuration**:
```dart
// Android Emulator
static const String baseUrl = 'http://10.0.2.2:8000';

// iOS Simulator
static const String baseUrl = 'http://localhost:8000';

// Physical Device
static const String baseUrl = 'http://192.168.1.10:8000'; // Your PC's IP

// Production
static const String baseUrl = 'https://api.jobwise.app';
```

### Feature-Specific API Clients

| Client | Base Path | File | Endpoints |
|--------|-----------|------|-----------|
| `AuthApiClient` | /api/v1/auth | `lib/services/api/auth_api_client.dart` | 9 |
| `ProfilesApiClient` | /api/v1/profiles | `lib/services/api/profiles_api_client.dart` | 24 |
| `JobsApiClient` | /api/v1/jobs | `lib/services/api/jobs_api_client.dart` | 5 |
| `GenerationsApiClient` | /api/v1 | `lib/services/api/generations_api_client.dart` | 10 |
| `ExportsApiClient` | /api/v1/exports | `lib/services/api/exports_api_client.dart` | 9 (planned) |

**Total API Endpoints**: 57 endpoints

---

## Shared UI Components

### Location: `lib/widgets/`

**Core Components**:
- `loading_overlay.dart` - Fullscreen loading indicator
- `error_display.dart` - Error message display with retry
- `empty_state.dart` - Empty list placeholder with action
- `confirmation_dialog.dart` - Action confirmation
- `custom_button.dart` - Styled button (primary, secondary)
- `custom_text_field.dart` - Styled input field with validation

**Feature-Specific Components**:

**Profile**:
- `profile_card.dart` - Profile summary card
- `profile_completeness_indicator.dart` - Circular progress indicator
- `experience_card.dart` - Expandable experience item
- `education_card.dart` - Education entry card
- `project_card.dart` - Project item with links
- `skills_chip_group.dart` - Skills grouped by type

**Jobs**:
- `job_card.dart` - Job listing card
- `application_status_badge.dart` - Color-coded status
- `keyword_chip.dart` - Keyword tag
- `keyword_highlighter.dart` - Highlights keywords in text

**Generation**:
- `generation_card.dart` - Generation history item
- `ats_score_badge.dart` - ATS score display with color
- `sample_upload_button.dart` - File picker for samples
- `progress_indicator.dart` - Stage-based progress

**Export**:
- `template_card.dart` - Template preview with ATS score
- `exported_file_card.dart` - File item with actions
- `storage_usage_indicator.dart` - Storage quota display

---

## Backend Connectivity

### Development Environment

**Start Backend Server**:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend Health**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

**API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Mobile App Configuration

**Android Emulator**:
```dart
// lib/config/environment.dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

**iOS Simulator**:
```dart
static const String baseUrl = 'http://localhost:8000';
```

**Network Security Config** (Android):
```xml
<!-- android/app/src/main/res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
</network-security-config>
```

---

## Dependencies

### Core Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.4.9
  riverpod_annotation: ^2.3.0

  # HTTP & Networking
  dio: ^5.4.0

  # Secure Storage
  flutter_secure_storage: ^9.0.0

  # Code Generation
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1

  # Navigation
  go_router: ^12.1.1

  # UI Components
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0

  # File Handling
  file_picker: ^6.1.1
  path_provider: ^2.1.1

  # File Operations (Export feature)
  open_file: ^3.3.2
  share_plus: ^7.2.1

  # Utilities
  intl: ^0.18.1
  uuid: ^4.2.1
```

### Dev Dependencies

```yaml
dev_dependencies:
  # Code Generators
  build_runner: ^2.4.6
  freezed: ^2.4.6
  json_serializable: ^6.7.1
  riverpod_generator: ^2.3.0

  # Testing
  flutter_test:
    sdk: flutter
  mockito: ^5.4.4

  # Linting
  flutter_lints: ^3.0.1
```

---

## Quick Start Commands

### Setup

```bash
# Navigate to mobile app directory
cd mobile_app

# Install dependencies
flutter pub get

# Generate code (Freezed, JSON serialization)
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate on file changes)
flutter pub run build_runner watch --delete-conflicting-outputs
```

### Run

```bash
# Run on default device
flutter run

# Run on specific platform
flutter run -d chrome       # Web
flutter run -d android      # Android
flutter run -d ios          # iOS (macOS only)

# Run with specific flavor
flutter run --flavor dev
flutter run --flavor prod
```

### Testing

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Generate HTML coverage report
genhtml coverage/lcov.info -o coverage/html

# Run specific test file
flutter test test/services/auth_api_client_test.dart

# Run widget tests only
flutter test test/widgets/
```

### Code Quality

```bash
# Analyze code
flutter analyze

# Format code
flutter format lib/ test/

# Check for unused dependencies
flutter pub deps
```

---

## Implementation Status

### Completed Features (✅)

1. **Authentication Feature** (2 screens)
   - Login and registration
   - JWT token management
   - Password validation

2. **Profile Management Feature** (3 screens)
   - Profile CRUD with multi-step form
   - Bulk operations
   - Completeness analytics

3. **Job Management Feature** (4 screens)
   - Create jobs from text
   - List and filter jobs
   - Application status tracking

4. **Generation Feature** (4 screens)
   - Sample upload
   - AI-powered generation
   - Real-time progress
   - Generation history

**Total Implemented**: 13 screens, 48 API endpoints

### Planned Features (🔄)

1. **Document Export Feature** (3 screens)
   - Template selection
   - PDF/DOCX export
   - File management

**Total Planned**: 3 screens, 9 API endpoints

---

## Testing Strategy

### Unit Tests

**Coverage**: API clients, state management, data models

**Example**:
```dart
test('AuthApiClient login returns AuthResponse', () async {
  final mockDio = MockDio();
  final client = AuthApiClient(mockDio);

  when(mockDio.post('/api/v1/auth/login', data: anyNamed('data')))
      .thenAnswer((_) async => Response(
            data: mockAuthResponse,
            statusCode: 200,
            requestOptions: RequestOptions(path: '/api/v1/auth/login'),
          ));

  final response = await client.login(
    email: 'test@example.com',
    password: 'password123',
  );

  expect(response.accessToken, isNotNull);
  expect(response.user.email, 'test@example.com');
});
```

### Widget Tests

**Coverage**: UI components, user interactions, form validation

**Example**:
```dart
testWidgets('LoginScreen shows error on invalid credentials', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      child: MaterialApp(home: LoginScreen()),
    ),
  );

  await tester.enterText(find.byKey(Key('email_field')), 'invalid@example.com');
  await tester.enterText(find.byKey(Key('password_field')), 'wrongpass');
  await tester.tap(find.byKey(Key('login_button')));
  await tester.pump();

  expect(find.text('Invalid email or password'), findsOneWidget);
});
```

### Integration Tests

**Coverage**: Full user flows with real backend

**Example**:
```dart
testWidgets('Complete generation flow', (tester) async {
  // 1. Login
  await tester.tap(find.text('Login'));
  // ... fill form and submit

  // 2. Create job
  await tester.tap(find.text('Add Job'));
  // ... paste job text

  // 3. Generate resume
  await tester.tap(find.text('Generate Resume'));
  await tester.pumpAndSettle();

  // 4. Verify result
  expect(find.byType(GenerationResultScreen), findsOneWidget);
  expect(find.byType(ATSScoreBadge), findsOneWidget);
});
```

---

## Performance Considerations

### API Response Times

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Login/Register | <500ms | JWT generation |
| Profile Fetch | <300ms | Single query |
| Job List | <500ms | Pagination |
| AI Job Parsing | 2-5s | LLM processing |
| Content Ranking | 1-2s | LLM analysis |
| Resume Generation | <1s | Pure logic, no LLM |
| Cover Letter Generation | 3-5s | LLM generation |
| PDF Export | 2-5s | Template rendering |

### Optimization Strategies

1. **Caching**:
   - Cache profile data for 5 minutes
   - Cache job list for 1 minute
   - Cache rankings per job (reuse for multiple generations)

2. **Pagination**:
   - Load jobs in batches of 20-50
   - Infinite scroll for history screens

3. **Optimistic Updates**:
   - Update UI immediately for status changes
   - Rollback on API error

4. **Progress Feedback**:
   - Real-time progress for slow operations (LLM calls)
   - Loading overlays for quick operations

5. **Image Optimization**:
   - Use CachedNetworkImage for template previews
   - Lazy load images in lists

---

## Security Best Practices

1. **Token Storage**:
   - Use flutter_secure_storage (iOS Keychain, Android Keystore)
   - Never store tokens in SharedPreferences
   - Clear tokens on logout

2. **Network Security**:
   - Use HTTPS in production
   - Implement certificate pinning
   - Validate SSL certificates

3. **Input Validation**:
   - Client-side validation for user experience
   - Never trust client-side validation alone
   - Server performs authoritative validation

4. **Sensitive Data**:
   - Never log tokens or passwords
   - Sanitize error messages
   - Don't expose stack traces to users

---

## Troubleshooting

### Common Issues

**1. Connection Refused (Android Emulator)**
```
Problem: Cannot connect to localhost:8000
Solution: Use 10.0.2.2 instead of localhost
```

**2. Token Expired**
```
Problem: 401 Unauthorized errors
Solution: Check token refresh interceptor is working
```

**3. Code Generation Fails**
```
Problem: build_runner errors
Solution: flutter pub run build_runner clean
         flutter pub run build_runner build --delete-conflicting-outputs
```

**4. State Not Updating**
```
Problem: UI doesn't reflect state changes
Solution: Ensure StateNotifier uses state = state.copyWith(...)
```

---

## Next Steps

### Phase 1: Complete Export Feature (Sprint 6)

1. Implement ExportsApiClient
2. Create export data models
3. Build TemplateSelectionScreen
4. Implement PDF preview
5. Add download and share functionality
6. Write tests

### Phase 2: Enhancements

1. **Offline Mode**: Local caching with SQLite
2. **Profile Versioning**: Track profile history
3. **Batch Generation**: Generate for multiple jobs
4. **Analytics Dashboard**: Track application success
5. **Push Notifications**: Generation completion

### Phase 3: Polish

1. **Accessibility**: Screen reader support
2. **Internationalization**: Multi-language support
3. **Dark Mode**: Theme switching
4. **Onboarding**: Tutorial for new users
5. **Performance**: Optimize image loading and API calls

---

## Related Documentation

- [Backend API Documentation](../api-services/README.md)
- [UNIFIED-BACKEND-ARCHITECTURE.md](../UNIFIED-BACKEND-ARCHITECTURE.md)
- [CLAUDE.md](../../CLAUDE.md) - Project overview for AI assistants

---

**Documentation Status**: Complete
**Features Documented**: 6 (Configuration + 5 features)
**Implementation Status**: 4 features complete, 1 feature planned
**Total Screens**: 16 (13 implemented, 3 planned)
**Total API Endpoints**: 57 endpoints (48 implemented, 9 planned)

---

**Last Updated**: November 2025
**Maintained By**: Mobile Development Team
**Questions?**: Refer to CLAUDE.md for development guidance
