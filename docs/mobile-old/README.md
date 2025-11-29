# JobWise Mobile App - Feature Documentation

**Version**: 1.0
**Platform**: Flutter (iOS & Android)
**State Management**: Riverpod
**Last Updated**: November 2025

---

## Overview

This directory contains comprehensive design documentation for all mobile app features, organized by backend API service alignment.

**Total Features**: 5 core features matching 5 backend APIs
**Total Screens**: 13 screens across 5 feature areas
**Architecture**: Clean Architecture with Riverpod state management

---

## Documentation Structure

Each feature document is aligned with its corresponding backend API service and includes:

1. **Feature Overview** - User stories and requirements
2. **Backend API Integration** - Endpoint mapping and request/response handling
3. **Data Models** - Freezed/manual models with JSON serialization
4. **State Management** - Riverpod providers and StateNotifiers
5. **Service Layer** - API clients and business logic
6. **UI Screens** - Screen designs and navigation
7. **Security & Testing** - Implementation details

---

## Feature Documents (Organized by Backend API)

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
- Automatic token refresh on 401
- Secure token storage (flutter_secure_storage)
- Password change and reset flows
- Email availability checking

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

---

### 2. [Profile Management Feature](02-profile-management-feature.md)
**Backend API**: [Profile API](../api-services/02-profile-api.md)
**Base Path**: `/api/v1/profiles`
**Status**: ✅ Fully Implemented

**Screens** (3):
- ProfileViewScreen
- ProfileEditScreen (multi-step form)
- SettingsScreen

**Key Features**:
- Master resume profile CRUD
- Multi-step form (Personal Info → Experiences → Education → Skills → Projects)
- Bulk operations for experiences, education, projects
- Skills management (technical, soft, languages, certifications)
- Profile completeness analytics
- Custom fields support

**API Endpoints Used**: 24 endpoints (profile CRUD, bulk operations, skills management)

---

### 3. [Job Management Feature](03-job-management-feature.md)
**Backend API**: [Job API](../api-services/03-job-api.md)
**Base Path**: `/api/v1/jobs`
**Status**: ✅ Fully Implemented

**Screens** (4):
- JobBrowseScreen (API job search - future)
- JobListScreen (saved jobs)
- JobDetailScreen
- JobPasteScreen (text input)

**Key Features**:
- Create job from pasted text (AI parsing)
- Create job from structured input
- List saved jobs with filters
- Update application status tracking
- Delete jobs
- Job keyword highlighting

**API Endpoints Used**: 5 endpoints
- POST / (create from text or structured)
- GET / (list with filters)
- GET /{id} (details)
- PUT /{id} (update)
- DELETE /{id}

---

### 4. [Generation Feature](04-generation-feature.md)
**Backend API**: [V3 Generation API](../api-services/04-v3-generation-api.md)
**Base Path**: `/api/v1`
**Status**: ✅ Fully Implemented

**Screens** (4):
- GenerationOptionsScreen
- GenerationProgressScreen
- GenerationResultScreen
- GenerationHistoryScreen

**Key Features**:
- Sample document upload (.txt files)
- AI-powered profile enhancement
- Job-specific content ranking
- Resume generation (pure logic, <1s)
- Cover letter generation (LLM-powered, ~3-5s)
- Real-time generation status tracking
- ATS score display
- Generation history with filtering

**API Endpoints Used**: 10 endpoints
- POST /samples/upload
- POST /profile/enhance
- POST /rankings/create
- POST /generations/resume
- POST /generations/cover-letter
- GET /samples
- GET /samples/{id}
- DELETE /samples/{id}
- GET /rankings/job/{job_id}
- GET /generations/history

---

### 5. [Document Export Feature](05-document-export-feature.md) 🔄 Planned
**Backend API**: [Document Export API](../api-services/05-document-export-api.md)
**Base Path**: `/api/v1/exports`
**Status**: 🔄 Design Complete - Implementation Pending

**Screens** (3 planned):
- TemplateSelectionScreen
- ExportOptionsScreen
- ExportedFilesScreen

**Key Features**:
- PDF export with 4 professional templates
- DOCX export for editable documents
- Template preview before export
- Batch export (resume + cover letter packages)
- File download and management
- Template customization (fonts, colors, spacing)
- Storage tracking

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

---

## App Architecture

### State Management: Riverpod

**Provider Hierarchy**:
```
AuthProvider
  ├─→ ProfileProvider
  │     ├─→ ExperiencesProvider
  │     ├─→ EducationProvider
  │     ├─→ ProjectsProvider
  │     └─→ SkillsProvider
  ├─→ JobsProvider
  ├─→ GenerationsProvider
  │     ├─→ SamplesProvider
  │     ├─→ RankingsProvider
  │     └─→ GenerationHistoryProvider
  └─→ ExportsProvider (planned)
        ├─→ TemplatesProvider
        └─→ ExportedFilesProvider
```

### Clean Architecture Layers

```
UI Layer (Screens & Widgets)
    ↓
State Layer (Riverpod Providers)
    ↓
Service Layer (API Clients)
    ↓
Models Layer (Freezed/Manual Models)
    ↓
Network Layer (Dio HTTP Client)
```

---

## Screen Navigation Map

```
AppShell (Go Router)
├── Authentication Flow
│   ├── LoginScreen
│   └── RegisterScreen
│
├── Main Navigation (Bottom Nav)
│   ├── Home Tab
│   │   ├── HomeScreen
│   │   └── GenerationHistoryScreen
│   │
│   ├── Profile Tab
│   │   ├── ProfileViewScreen
│   │   ├── ProfileEditScreen (multi-step)
│   │   └── SettingsScreen
│   │
│   ├── Jobs Tab
│   │   ├── JobListScreen
│   │   ├── JobDetailScreen
│   │   ├── JobPasteScreen
│   │   └── JobBrowseScreen (future)
│   │
│   └── Generation Tab
│       ├── GenerationOptionsScreen
│       ├── GenerationProgressScreen
│       ├── GenerationResultScreen
│       └── (Templates/Export when implemented)
│
└── Debug Screen (dev mode only)
```

**Total Screens**: 13 implemented + 3 planned = 16 screens

---

## Data Models Summary

### Freezed Models (Immutable)
Used for Job-related entities:
- `Job`
- `JobFilter`
- `SavedJob`

### Manual Models
Used for Auth and Profile:
- `User`, `AuthResponse`
- `Profile`, `PersonalInfo`, `Experience`, `Education`, `Project`, `Skills`

### Future: Migrate to Freezed
Consider migrating Profile models to Freezed for consistency.

---

## API Client Architecture

### BaseHttpClient
**File**: `lib/services/api/base_http_client.dart`

**Features**:
- Dio configuration with base URL
- Request interceptor (add JWT token)
- Response interceptor (logging)
- Error interceptor (auto-refresh on 401)
- Timeout configuration

### Feature-Specific API Clients

| Client | Base Path | File |
|--------|-----------|------|
| `AuthApiClient` | /api/v1/auth | `lib/services/api/auth_api_client.dart` |
| `ProfilesApiClient` | /api/v1/profiles | `lib/services/api/profiles_api_client.dart` |
| `JobsApiClient` | /api/v1/jobs | `lib/services/api/jobs_api_client.dart` |
| `GenerationsApiClient` | /api/v1 | `lib/services/api/generations_api_client.dart` |
| `ExportsApiClient` | /api/v1/exports | `lib/services/api/exports_api_client.dart` (planned) |

---

## Shared UI Components

### Reusable Widgets
**Location**: `lib/widgets/`

**Core Components**:
- `loading_overlay.dart` - Fullscreen loading indicator
- `error_display.dart` - Error message display
- `empty_state.dart` - Empty list placeholder
- `confirmation_dialog.dart` - Action confirmation
- `custom_button.dart` - Styled button
- `custom_text_field.dart` - Styled input field

**Feature-Specific Components**:
- `profile_card.dart` - Profile summary card
- `profile_completeness_indicator.dart` - Progress bar
- `experience_card.dart` - Experience list item
- `job_card.dart` - Job listing card
- `generation_card.dart` - Generation status card
- `ats_score_badge.dart` - ATS score display
- `keyword_chip.dart` - Keyword tag
- `match_score_widget.dart` - Visual match percentage

---

## Backend Connectivity

### Development Environment

**Android Emulator**:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

**iOS Simulator**:
```dart
static const String baseUrl = 'http://localhost:8000';
```

**Physical Device**:
```dart
static const String baseUrl = 'http://192.168.1.10:8000'; // Your computer's local IP
```

### Backend Server Setup

**Start Backend**:
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Health**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

**API Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

  # PDF (for future export feature)
  flutter_pdfview: ^1.3.2
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
# Install dependencies
cd mobile_app
flutter pub get

# Generate code (Freezed, JSON serialization)
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate)
flutter pub run build_runner watch --delete-conflicting-outputs
```

### Run
```bash
# Run on default device
flutter run

# Run on specific platform
flutter run -d chrome       # Web
flutter run -d android      # Android
flutter run -d ios          # iOS
```

### Testing
```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/services/auth_api_client_test.dart
```

---

## Implementation Status

### Completed (✅)
- Authentication Feature (2 screens)
- Profile Management Feature (3 screens)
- Job Management Feature (4 screens)
- Generation Feature (4 screens)
- Debug Screen (1 screen)

**Total**: 13 screens implemented

### Planned (🔄)
- Document Export Feature (3 screens)
- PDF viewer integration
- Template customization UI
- Batch export workflow

---

## Testing Strategy

### Unit Tests
**Coverage**: Model serialization, state logic, API clients (mocked)

**Example**:
```dart
test('AuthApiClient login returns AuthResponse', () async {
  // Mock Dio response
  final mockDio = MockDio();
  final client = AuthApiClient(mockDio);

  // Test login
  final response = await client.login('test@example.com', 'password');

  // Assertions
  expect(response.accessToken, isNotNull);
  expect(response.user.email, 'test@example.com');
});
```

### Widget Tests
**Coverage**: UI components, form validation, user interactions

**Example**:
```dart
testWidgets('LoginScreen shows error on invalid credentials', (tester) async {
  await tester.pumpWidget(MyApp());

  // Enter invalid credentials
  await tester.enterText(find.byKey(Key('email')), 'invalid@example.com');
  await tester.enterText(find.byKey(Key('password')), 'wrongpass');
  await tester.tap(find.byKey(Key('login_button')));
  await tester.pump();

  // Expect error message
  expect(find.text('Invalid email or password'), findsOneWidget);
});
```

### Integration Tests
**Coverage**: Full user flows with real backend

**Example**:
```dart
testWidgets('Complete registration and profile creation flow', (tester) async {
  // 1. Register user
  await tester.tap(find.text('Register'));
  // ... fill form and submit

  // 2. Create profile
  await tester.tap(find.text('Create Profile'));
  // ... fill multi-step form

  // 3. Verify profile created
  expect(find.text('Profile created successfully'), findsOneWidget);
});
```

---

## Next Steps

### Phase 1: Document Export Feature (Next Sprint)
1. Implement `ExportsApiClient`
2. Create export data models
3. Build `TemplateSelectionScreen`
4. Implement PDF preview
5. Add download and share functionality

### Phase 2: Enhancements
1. Offline mode with local caching
2. Profile version history
3. Batch generation for multiple jobs
4. Analytics dashboard
5. Push notifications for generation completion

### Phase 3: Polish
1. Accessibility improvements (screen readers)
2. Internationalization (i18n)
3. Dark mode
4. Onboarding tutorial
5. Performance optimization

---

**Documentation Status**: Complete
**Features Documented**: 5/5 (Auth, Profile, Job, Generation, Export)
**Implementation Status**: 4/5 features complete (Export pending)
**Total Screens**: 13 implemented + 3 planned

---

**Last Updated**: November 2025
**Maintained By**: Mobile Development Team
**Related Docs**: [Backend API Documentation](../api-services/README.md)
