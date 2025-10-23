# JobWise Mobile App - Feature Design Documents

**Version**: 1.0  
**Purpose**: Quick reference index for all mobile feature design documents  
**Last Updated**: October 22, 2025

---

## Document Structure

All feature design documents are located in `.context/mobile/` and follow a consistent structure:

1. **Feature Overview** - Purpose and user stories
2. **API Integration** - Backend endpoints and connection details
3. **Data Models** - Freezed models with JSON serialization
4. **State Management** - Riverpod providers and state classes
5. **Service Layer** - API clients and business logic
6. **UI Components** - Screens and widgets
7. **Security/Testing** - Implementation details

---

## Available Design Documents

### 0. API Configuration
**File**: `00-api-configuration.md`  
**Status**: ✅ Complete

**Contents**:
- Backend connection URLs (Android emulator: `10.0.2.2:8000`, iOS: `localhost:8000`)
- CORS configuration
- All API endpoints summary (37+ endpoints across 5 services)
- Dio HTTP client setup with interceptors
- Environment-specific configuration
- Common connection issues and solutions

**Key Takeaway**: Use `http://10.0.2.2:8000/api/v1` for Android emulator development.

---

### 1. Authentication Feature
**File**: `01-authentication-feature.md`  
**Status**: ✅ Complete  
**API Base Path**: `/api/v1/auth`

**Key Features**:
- User registration and login
- JWT token management with auto-refresh
- Secure token storage (flutter_secure_storage)
- Password validation (8+ chars, uppercase, lowercase, number)
- Automatic 401 handling with token refresh

**Models**: `User`, `AuthResponse`, `LoginRequest`, `RegisterRequest`

**State**: `AuthState` with `AuthNotifier`

**Services**: `AuthApiClient`, `StorageService`, `BaseHttpClient`

**Screens**: `LoginScreen`, `RegisterScreen`

**Key Dependencies**:
```yaml
flutter_riverpod: ^2.4.9
dio: ^5.4.0
flutter_secure_storage: ^9.0.0
freezed_annotation: ^2.4.1
```

---

### 2. Profile Feature
**File**: `02-profile-feature.md`  
**Status**: ✅ Complete  
**API Base Path**: `/api/v1/profiles`

**Key Features**:
- Master resume profile management
- Bulk operations for experiences, education, projects
- Multi-step form (Personal Info → Experience → Education/Skills → Projects)
- Profile completeness analytics
- Version control support

**Models**: 
- `Profile`, `PersonalInfo`, `Experience`, `Education`
- `Skills`, `Language`, `Certification`, `Project`

**State**: `ProfileState` with `ProfileNotifier`

**Services**: `ProfilesApiClient` with bulk operation methods

**Screens**: `ProfileEditScreen` (multi-step stepper)

**Key Endpoints**:
- `POST /profiles` - Create with all components
- `GET /profiles/me` - Get current user's profile
- `POST /profiles/{id}/experiences` - Add multiple experiences
- `PUT /profiles/{id}/experiences` - Update multiple experiences

---

### 3. Job Feature
**File**: `03-job-feature.md` (To be created)  
**API Base Path**: `/api/v1/jobs`

**Key Features**:
- Job description management (paste text or manual entry)
- Text parsing with LLM extraction
- Job filtering (status, source)
- Save jobs for resume generation

**Models**: `Job`, `SavedJob` (with notes)

**Endpoints**:
- `POST /jobs` - Create from raw text or structured data
- `GET /jobs` - List with filters (status, source)
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Hard delete

---

### 4. Generation Feature
**File**: `04-generation-feature.md` (To be created)  
**API Base Path**: `/api/v1/generations`

**Key Features**:
- AI resume and cover letter generation
- 5-stage pipeline with progress tracking
- Real-time polling for status updates
- ATS score and keyword coverage analytics

**Models**: `Generation`, `GenerationProgress`, `GenerationResult`

**State**: Polling stream with status updates

**Key Flow**:
1. Start generation → Get generation_id
2. Poll `/generations/{id}` every 2 seconds
3. Show progress (Stage 1/5, 20%, "Job Analysis...")
4. On completion, get result with document_id and PDF URL

**Endpoints**:
- `POST /generations/resume` - Start resume generation
- `GET /generations/{id}` - Poll for status
- `GET /generations/{id}/result` - Get final result

---

### 5. Document Feature
**File**: `05-document-feature.md` (To be created)  
**API Base Path**: `/api/v1/documents`

**Key Features**:
- View generated documents
- Download PDF files
- Share documents
- Document history and versioning

**Models**: `Document`, `DocumentContent`, `DocumentMetadata`, `PDFInfo`

**Key Flow**:
1. List documents with metadata
2. View document content (text, HTML, markdown)
3. Download PDF → Save to device
4. Share PDF via system share sheet

**Endpoints**:
- `GET /documents` - List documents with filters
- `GET /documents/{id}` - Get document with content
- `GET /documents/{id}/download` - Download PDF binary
- `DELETE /documents/{id}` - Delete document

---

## Implementation Priority

### Sprint 1 (Core Features)
1. ✅ Authentication (login, register, token management)
2. ✅ Profile (create, edit master resume)
3. 🔄 Job (save job descriptions)

### Sprint 2 (AI Features)
4. ⏳ Generation (AI resume generation)
5. ⏳ Document (view and download PDFs)

### Sprint 3 (Enhancements)
- Offline support with local caching
- Profile analytics dashboard
- Batch resume generation
- Document templates selection

---

## Shared Components

### Reusable Widgets
Located in `lib/widgets/`:

- `loading_overlay.dart` - Fullscreen loading indicator
- `error_display.dart` - Error message display
- `profile_card.dart` - Profile summary card
- `job_card.dart` - Job listing card
- `generation_card.dart` - Generation status card
- `document_card.dart` - Document listing card
- `profile_completeness_indicator.dart` - Progress bar for profile
- `match_score_widget.dart` - Visual match percentage
- `ats_score_badge.dart` - ATS score display
- `pdf_viewer_widget.dart` - Inline PDF viewer

### Utilities
Located in `lib/utils/`:

- `validators.dart` - Form validation helpers
- `formatters.dart` - Date, currency formatting
- `date_utils.dart` - Date parsing and formatting

---

## State Management Architecture

### Provider Hierarchy
```dart
// Top-level providers
authProvider → Manages user authentication state
  ↓
profileProvider → Manages user profile (depends on auth)
  ↓
jobsProvider → Manages saved jobs (depends on auth)
  ↓
generationsProvider → Manages generation requests (depends on profile + jobs)
  ↓
documentsProvider → Manages generated documents (depends on generations)
```

### State Pattern
All feature states follow this pattern:
```dart
@freezed
class FeatureState with _$FeatureState {
  const factory FeatureState({
    DataModel? data,
    @Default(false) bool isLoading,
    @Default(false) bool isSaving,
    String? errorMessage,
  }) = _FeatureState;
}
```

---

## API Client Architecture

### BaseHttpClient (Shared)
- Dio configuration with base URL
- Request interceptor (add JWT token)
- Response interceptor (logging)
- Error interceptor (auto-refresh on 401)

### Feature-Specific Clients
- `AuthApiClient` → `/api/v1/auth`
- `ProfilesApiClient` → `/api/v1/profiles`
- `JobsApiClient` → `/api/v1/jobs`
- `GenerationsApiClient` → `/api/v1/generations`
- `DocumentsApiClient` → `/api/v1/documents`

---

## Testing Strategy

### Unit Tests
- Model serialization/deserialization
- State notifier logic
- API client methods (mocked)

### Widget Tests
- Form validation
- UI component rendering
- User interactions

### Integration Tests
- Full user flows (register → create profile → save job → generate resume)
- API integration with test backend
- Offline behavior

---

## Next Steps for Implementation

1. **Setup Project Dependencies** (pubspec.yaml)
   - Add all required packages
   - Run code generation (`flutter pub run build_runner build`)

2. **Create Base Infrastructure**
   - Implement `BaseHttpClient` with interceptors
   - Implement `StorageService` for token storage
   - Setup app configuration

3. **Implement Authentication** (Sprint 1)
   - Create models, providers, services
   - Build login and register screens
   - Test token management

4. **Implement Profile** (Sprint 1)
   - Create profile models (nested structures)
   - Build multi-step form UI
   - Test bulk operations

5. **Implement Job** (Sprint 1)
   - Create job models
   - Build job list and detail screens
   - Implement text parsing integration

6. **Implement Generation** (Sprint 2)
   - Create generation models
   - Build progress tracking UI
   - Implement polling mechanism

7. **Implement Document** (Sprint 2)
   - Create document models
   - Build PDF viewer
   - Implement download and share

---

## Quick Reference Commands

### Backend Server
```powershell
# Start backend server
cd backend
.\start-server.bat

# Server will run on http://0.0.0.0:8000
# API available at http://localhost:8000/api/v1
```

### Flutter App
```powershell
# Run on Android emulator
cd mobile_app
flutter run

# Code generation
flutter pub run build_runner build --delete-conflicting-outputs

# Run tests
flutter test
```

### Health Check
```powershell
# Test backend connectivity
curl http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"..."}
```

---

## Dependencies Summary

### Core Dependencies
```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.9
  
  # HTTP & Networking
  dio: ^5.4.0
  
  # Secure Storage
  flutter_secure_storage: ^9.0.0
  
  # Code Generation
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1
  
  # UI Components
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.0
  
  # PDF Handling
  flutter_pdfview: ^1.3.2
  open_file: ^3.3.2
  path_provider: ^2.1.1
  
  # File Sharing
  share_plus: ^7.2.1
  
  # Date/Time
  intl: ^0.18.1

dev_dependencies:
  # Code Generators
  build_runner: ^2.4.6
  freezed: ^2.4.6
  json_serializable: ^6.7.1
  
  # Testing
  flutter_test:
    sdk: flutter
  mockito: ^5.4.4
  flutter_lints: ^3.0.1
```

---

**Document Status**: Index Complete  
**Feature Docs**: 3/6 Complete (Authentication, Profile, API Config)  
**Next**: Complete Job, Generation, Document feature design docs
