# Job Browsing Feature - Mobile Design Document

**Version**: 1.0
**Feature**: Job Description Management & Browsing
**API Service**: Job API
**Status**: ❌ **Not Implemented** (Fully specified, ready for implementation)
**Last Updated**: November 2, 2025

---

## Implementation Status

### ❌ Not Implemented
- Job paste screen (paste raw text → backend parsing → save)
- Job browse screen (search mock jobs → select → save)
- Saved jobs list screen (view user's saved jobs)
- Job detail screen (full job information display)
- Job edit screen (edit saved job descriptions)
- Job API client (all endpoints)
- Job state management (Riverpod provider)
- Mock job filtering and search
- Job-to-Resume generation flow

### ✅ API Ready (Backend Specified)
- POST /jobs - Create job from raw text or structured data
- GET /jobs/browse - Browse mock job listings
- GET /jobs - List user's saved jobs
- GET /jobs/{id} - Get job details
- PUT /jobs/{id} - Update job
- DELETE /jobs/{id} - Delete job

---

## Feature Overview

### Purpose
Enable users to manage job descriptions for AI-tailored resume generation. Users can paste job text, browse mock job listings, or manually create jobs. All job data is optimized for LLM processing to generate tailored resumes.

### Key Features
1. **Paste Job Description** - Paste raw text → auto-parse → review → save
2. **Browse Mock Jobs** - Search mock job listings → select → save to my jobs
3. **Manage Saved Jobs** - View, edit, delete, archive saved job descriptions
4. **LLM-Optimized Storage** - Job data structured for easy AI prompt injection
5. **Job-to-Resume Flow** - Select saved job → generate tailored resume

### Core User Flows

#### Flow 1: Paste Job Description
```
User Journey:
1. User copies job description from job board (Indeed, LinkedIn, etc.)
2. User opens "Add Job" screen → selects "Paste Description"
3. User pastes text into text area
4. User taps "Parse & Save"
5. Loading indicator shown (backend parsing)
6. Backend returns parsed job (title, company, requirements, keywords)
7. User reviews parsed data in form
8. User edits any fields if needed
9. User taps "Save Job"
10. Job saved to database → navigate to job detail screen

Data Flow:
Mobile → POST /jobs {source: "user_created", raw_text: "..."} → Backend parses → Returns structured job → Mobile saves to state
```

#### Flow 2: Browse & Save Mock Jobs
```
User Journey:
1. User opens "Browse Jobs" screen
2. User enters search query (e.g., "Python Developer")
3. User applies filters (location, remote, etc.)
4. User sees list of mock jobs
5. User taps on job card → job detail modal shown
6. User reviews job description, requirements, benefits
7. User taps "Save Job"
8. Job saved to user's jobs (POST /jobs with mock job data)
9. Success message shown → job appears in "My Jobs" list

Data Flow:
Mobile → GET /jobs/browse?query=Python&remote=true → Backend returns mock jobs → User selects job → Mobile → POST /jobs {...job data, source: "user_created"} → Job saved with user_id
```

#### Flow 3: Manage Saved Jobs
```
User Journey:
1. User opens "My Jobs" screen
2. User sees list of saved jobs (cards with title, company, date)
3. User can:
   - Tap job → view full details
   - Swipe left → Archive or Delete
   - Tap "Generate Resume" → navigate to generation flow
   - Tap Edit → edit job fields
   - Pull to refresh → reload jobs from server

Data Flow:
Mobile → GET /jobs?status=active → Backend returns user's jobs → Display in list
```

---

## API Integration

### Backend Connection
```
Base URL: http://10.0.2.2:8000/api/v1
Authentication: JWT Bearer token in Authorization header
```

### Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/jobs` | POST | Create job (paste or structured) | `{source, raw_text}` or `{source, title, company, ...}` | Job object (201) |
| `/jobs/browse` | GET | Browse mock jobs | Query params: `query`, `location`, `remote`, `limit`, `offset` | Jobs array (200) |
| `/jobs` | GET | List user's saved jobs | Query params: `status`, `source`, `limit`, `offset` | Jobs array (200) |
| `/jobs/{id}` | GET | Get job details | - | Job object (200) |
| `/jobs/{id}` | PUT | Update job | Job object (partial) | Updated job (200) |
| `/jobs/{id}` | DELETE | Delete job | - | No content (204) |

### Error Codes

| Code | Meaning | User Action |
|------|---------|-------------|
| 400 | Validation error (missing fields, invalid data) | Show field-specific errors |
| 401 | Unauthorized (invalid/expired token) | Redirect to login |
| 403 | Forbidden (not job owner) | Show error message |
| 404 | Job not found | Show "Job not found" message |
| 422 | Unprocessable entity (parsing failed) | Show parsing error, allow manual entry |
| 500 | Server error | Show generic error, allow retry |

---

## Data Models

### Job Model

```dart
// lib/models/job.dart

import 'package:freezed_annotation/freezed_annotation.dart';

part 'job.freezed.dart';
part 'job.g.dart';

@freezed
class Job with _$Job {
  const factory Job({
    required String id,
    String? userId,
    required JobSource source,
    required String title,
    required String company,
    String? location,
    required String description,
    String? rawText,
    @Default([]) List<String> parsedKeywords,
    @Default([]) List<String> requirements,
    @Default([]) List<String> benefits,
    String? salaryRange,
    @Default(false) bool remote,
    @Default(JobStatus.active) JobStatus status,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Job;

  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
}

enum JobSource {
  @JsonValue('user_created')
  userCreated,
  @JsonValue('mock')
  mock,
  @JsonValue('indeed')
  indeed,
  @JsonValue('linkedin')
  linkedin,
  @JsonValue('imported')
  imported,
}

enum JobStatus {
  @JsonValue('active')
  active,
  @JsonValue('archived')
  archived,
  @JsonValue('draft')
  draft,
}

// For browsing mock jobs (no user_id yet)
@freezed
class BrowseJob with _$BrowseJob {
  const factory BrowseJob({
    required JobSource source,
    required String title,
    required String company,
    String? location,
    required String description,
    @Default([]) List<String> parsedKeywords,
    @Default([]) List<String> requirements,
    @Default([]) List<String> benefits,
    String? salaryRange,
    @Default(false) bool remote,
  }) = _BrowseJob;

  factory BrowseJob.fromJson(Map<String, dynamic> json) => _$BrowseJobFromJson(json);
}

// API response models
@freezed
class JobListResponse with _$JobListResponse {
  const factory JobListResponse({
    required List<Job> jobs,
    required PaginationMeta pagination,
  }) = _JobListResponse;

  factory JobListResponse.fromJson(Map<String, dynamic> json) => _$JobListResponseFromJson(json);
}

@freezed
class BrowseJobListResponse with _$BrowseJobListResponse {
  const factory BrowseJobListResponse({
    required List<BrowseJob> jobs,
    required PaginationMeta pagination,
  }) = _BrowseJobListResponse;

  factory BrowseJobListResponse.fromJson(Map<String, dynamic> json) => _$BrowseJobListResponseFromJson(json);
}

@freezed
class PaginationMeta with _$PaginationMeta {
  const factory PaginationMeta({
    required int total,
    required int limit,
    required int offset,
    @Default(false) bool hasNext,
    @Default(false) bool hasPrevious,
  }) = _PaginationMeta;

  factory PaginationMeta.fromJson(Map<String, dynamic> json) => _$PaginationMetaFromJson(json);
}
```

### LLM-Optimized Structure

The Job model is specifically designed for LLM prompt injection:

**Key Fields for AI Processing:**
1. **`description`**: Full raw job description (LLM context)
2. **`parsedKeywords`**: Technical skills array for matching against profile
3. **`requirements`**: Bulleted list of qualifications (direct prompt injection)
4. **`benefits`**: Company perks (optional, for cover letter)
5. **`rawText`**: Original pasted text (fallback/re-parsing)

**Example LLM Prompt Construction:**
```dart
String buildResumePrompt(Profile profile, Job job) {
  return '''
Generate a tailored resume for this candidate:

CANDIDATE PROFILE:
${profile.professionalSummary}

Skills: ${profile.skills.technical.join(', ')}
Experience: ${_formatExperiences(profile.experiences)}

TARGET JOB:
Title: ${job.title} at ${job.company}
Location: ${job.location ?? 'Not specified'}

Key Technologies: ${job.parsedKeywords.join(', ')}

Job Requirements:
${job.requirements.map((r) => '- $r').join('\n')}

Job Description:
${job.description}

Please highlight relevant experience and skills that match the job requirements.
Focus on technologies: ${job.parsedKeywords.join(', ')}
''';
}
```

---

## State Management

### Job Provider

```dart
// lib/providers/job_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/job.dart';
import '../services/api/jobs_api_client.dart';

part 'job_provider.freezed.dart';

@freezed
class JobState with _$JobState {
  const factory JobState({
    @Default([]) List<Job> savedJobs,
    @Default([]) List<BrowseJob> browseJobs,
    @Default(false) bool isLoading,
    @Default(false) bool isSaving,
    @Default(false) bool isBrowsing,
    String? errorMessage,
    PaginationMeta? savedJobsPagination,
    PaginationMeta? browseJobsPagination,
  }) = _JobState;
}

class JobNotifier extends StateNotifier<JobState> {
  final JobsApiClient _jobsApi;

  JobNotifier(this._jobsApi) : super(const JobState()) {
    _loadSavedJobs();
  }

  // Load user's saved jobs
  Future<void> _loadSavedJobs() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final response = await _jobsApi.getJobs(status: JobStatus.active);
      state = state.copyWith(
        savedJobs: response.jobs,
        savedJobsPagination: response.pagination,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Failed to load jobs',
      );
    }
  }

  // Create job from raw text (paste)
  Future<Job?> createFromText(String rawText) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final job = await _jobsApi.createFromText(rawText);
      state = state.copyWith(
        savedJobs: [job, ...state.savedJobs],
        isSaving: false,
      );
      return job;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: _extractErrorMessage(e),
      );
      rethrow;
    }
  }

  // Create job from structured data (form or browse)
  Future<Job?> createFromData(Map<String, dynamic> jobData) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final job = await _jobsApi.createFromData(jobData);
      state = state.copyWith(
        savedJobs: [job, ...state.savedJobs],
        isSaving: false,
      );
      return job;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: _extractErrorMessage(e),
      );
      rethrow;
    }
  }

  // Browse mock jobs
  Future<void> browseMockJobs({
    String? query,
    String? location,
    bool? remote,
    int limit = 20,
    int offset = 0,
  }) async {
    state = state.copyWith(isBrowsing: true, errorMessage: null);
    try {
      final response = await _jobsApi.browseJobs(
        query: query,
        location: location,
        remote: remote,
        limit: limit,
        offset: offset,
      );
      state = state.copyWith(
        browseJobs: response.jobs,
        browseJobsPagination: response.pagination,
        isBrowsing: false,
      );
    } catch (e) {
      state = state.copyWith(
        isBrowsing: false,
        errorMessage: 'Failed to browse jobs',
      );
    }
  }

  // Save browse job to user's jobs
  Future<Job?> saveBrowseJob(BrowseJob browseJob) async {
    final jobData = {
      'source': 'user_created',
      'title': browseJob.title,
      'company': browseJob.company,
      'location': browseJob.location,
      'description': browseJob.description,
      'requirements': browseJob.requirements,
      'benefits': browseJob.benefits,
      'parsed_keywords': browseJob.parsedKeywords,
      'salary_range': browseJob.salaryRange,
      'remote': browseJob.remote,
      'status': 'active',
    };
    return await createFromData(jobData);
  }

  // Update job
  Future<Job?> updateJob(String jobId, Map<String, dynamic> updates) async {
    state = state.copyWith(isSaving: true, errorMessage: null);
    try {
      final updatedJob = await _jobsApi.updateJob(jobId, updates);
      final updatedList = state.savedJobs.map((job) {
        return job.id == jobId ? updatedJob : job;
      }).toList();
      state = state.copyWith(
        savedJobs: updatedList,
        isSaving: false,
      );
      return updatedJob;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'Failed to update job',
      );
      rethrow;
    }
  }

  // Delete job
  Future<void> deleteJob(String jobId) async {
    try {
      await _jobsApi.deleteJob(jobId);
      final updatedList = state.savedJobs.where((job) => job.id != jobId).toList();
      state = state.copyWith(savedJobs: updatedList);
    } catch (e) {
      state = state.copyWith(errorMessage: 'Failed to delete job');
      rethrow;
    }
  }

  // Archive job
  Future<void> archiveJob(String jobId) async {
    await updateJob(jobId, {'status': 'archived'});
  }

  // Refresh saved jobs
  Future<void> refreshSavedJobs() async {
    await _loadSavedJobs();
  }

  String _extractErrorMessage(dynamic error) {
    // Extract user-friendly error message from DioException
    return 'An error occurred. Please try again.';
  }
}

final jobProvider = StateNotifierProvider<JobNotifier, JobState>((ref) {
  return JobNotifier(ref.watch(jobsApiClientProvider));
});
```

---

## Service Layer

### Jobs API Client

```dart
// lib/services/api/jobs_api_client.dart

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/job.dart';
import 'base_http_client.dart';

class JobsApiClient {
  final BaseHttpClient _client;

  JobsApiClient(this._client);

  // Create job from raw text
  Future<Job> createFromText(String rawText) async {
    final response = await _client.post('/jobs', data: {
      'source': 'user_created',
      'raw_text': rawText,
    });
    return Job.fromJson(response.data);
  }

  // Create job from structured data
  Future<Job> createFromData(Map<String, dynamic> data) async {
    final response = await _client.post('/jobs', data: data);
    return Job.fromJson(response.data);
  }

  // Browse mock jobs
  Future<BrowseJobListResponse> browseJobs({
    String? query,
    String? location,
    bool? remote,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/jobs/browse', queryParameters: {
      if (query != null) 'query': query,
      if (location != null) 'location': location,
      if (remote != null) 'remote': remote,
      'limit': limit,
      'offset': offset,
    });
    return BrowseJobListResponse.fromJson(response.data);
  }

  // Get user's saved jobs
  Future<JobListResponse> getJobs({
    JobStatus? status,
    JobSource? source,
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _client.get('/jobs', queryParameters: {
      if (status != null) 'status': status.name,
      if (source != null) 'source': _sourceToString(source),
      'limit': limit,
      'offset': offset,
    });
    return JobListResponse.fromJson(response.data);
  }

  // Get job by ID
  Future<Job> getJob(String id) async {
    final response = await _client.get('/jobs/$id');
    return Job.fromJson(response.data);
  }

  // Update job
  Future<Job> updateJob(String id, Map<String, dynamic> updates) async {
    final response = await _client.put('/jobs/$id', data: updates);
    return Job.fromJson(response.data);
  }

  // Delete job
  Future<void> deleteJob(String id) async {
    await _client.delete('/jobs/$id');
  }

  String _sourceToString(JobSource source) {
    return source.toString().split('.').last;
  }
}

final jobsApiClientProvider = Provider<JobsApiClient>((ref) {
  return JobsApiClient(ref.watch(baseHttpClientProvider));
});
```

---

## UI Components & Screens

### Screen 1: Job Paste Screen

**Route**: `/jobs/paste`

**Purpose**: Allow user to paste raw job description text for parsing

**Layout**:
```
AppBar: "Paste Job Description"

Body:
  - Instructions card: "Copy and paste a job description from any job board"
  - Large TextField (multiline, min 10 lines):
      - Label: "Job Description"
      - Hint: "Paste the full job description here..."
      - Max length: 10,000 chars
      - Counter shown
  - Parse & Save Button (primary, full width)
  - Loading indicator during parsing

Bottom Sheet (after parsing):
  - "Review Parsed Job" title
  - Show parsed fields in read-only cards:
      - Title
      - Company
      - Location
      - Keywords (chips)
      - Requirements (bullets)
      - Benefits (bullets)
  - Edit button → navigate to edit form
  - Save button (confirm and save)
```

**User Interactions**:
- Paste text → "Parse & Save" enabled
- Tap "Parse & Save" → Loading → Show review bottom sheet
- Tap "Edit" → Navigate to job form with pre-filled data
- Tap "Save" → Save to database → Navigate to job detail

**Validation**:
- Minimum 50 characters required
- Show error if parsing fails (422 error)
- Allow manual entry as fallback

**Error Handling**:
- 422 (parsing failed) → Show "Unable to parse automatically. Please enter manually" → Navigate to form
- 400 (validation error) → Show specific field errors
- 500 (server error) → Show "Error saving job. Please try again"

---

### Screen 2: Job Browse Screen

**Route**: `/jobs/browse`

**Purpose**: Browse mock job listings and save to user's jobs

**Layout**:
```
AppBar: "Browse Jobs"
  - Actions: Filter icon

Body:
  - Search bar:
      - TextField: "Search jobs (e.g., Python Developer)"
      - Search icon button
  - Filter chips (horizontal scroll):
      - "Remote Only" toggle chip
      - "Location" chip → location picker dialog
      - "Clear Filters" chip
  - Job cards list (ListView):
      Each card:
        - Company logo placeholder (circle avatar)
        - Title (bold, 18sp)
        - Company name (14sp, gray)
        - Location (12sp, gray, location icon)
        - Remote badge (if remote)
        - Keywords chips (3 max, "+2 more")
        - Salary range (if available)
        - "View Details" button
  - Pagination: Load more button / infinite scroll
  - Empty state: "No jobs found. Try different keywords."
  - Loading state: Shimmer cards

Job Detail Bottom Sheet (modal):
  - Job title & company (header)
  - Location, remote badge, salary
  - "Description" section (collapsible)
  - "Requirements" section (bullet list)
  - "Benefits" section (bullet list)
  - "Keywords" section (chips)
  - Action buttons:
      - "Save Job" (primary)
      - "Close" (secondary)
```

**User Interactions**:
- Type search query → Tap search → Fetch results
- Tap filter chip → Show filter dialog → Apply filters
- Tap job card → Show detail bottom sheet
- Tap "Save Job" → POST to /jobs → Show success → Dismiss modal
- Pull to refresh → Reload results
- Scroll to bottom → Load next page (pagination)

**State Management**:
- Manage search query, filters, pagination state
- Show loading indicator during fetch
- Cache results for quick back navigation

---

### Screen 3: Saved Jobs List Screen

**Route**: `/jobs` (main tab)

**Purpose**: Display user's saved jobs with management options

**Layout**:
```
AppBar: "My Jobs"
  - Actions:
      - Add icon (+ button) → Menu: "Paste Description" / "Browse Jobs"
      - Filter icon → Status filter (Active / Archived)

Body:
  - Tab bar (optional):
      - "Active" tab
      - "Archived" tab
  - Job cards list:
      Each card:
        - Title (bold)
        - Company name
        - Location + remote badge
        - Date saved (relative, e.g., "2 days ago")
        - Keywords chips (3 max)
        - Trailing: More icon (menu)
  - Swipe actions:
      - Swipe left: Archive / Delete
  - Empty state: "No saved jobs. Tap + to add one."
  - Pull to refresh

Context Menu (tap more icon):
  - View Details
  - Edit Job
  - Generate Resume
  - Archive / Unarchive
  - Delete
```

**User Interactions**:
- Tap job card → Navigate to job detail screen
- Tap + button → Show menu: Paste / Browse
- Swipe left on card → Show actions (Archive/Delete)
- Pull to refresh → Reload jobs
- Tap "Generate Resume" → Navigate to generation screen with job pre-selected

**Data Loading**:
- Load on screen init: GET /jobs?status=active
- Auto-refresh when returning from other screens
- Show cached data immediately, refresh in background

---

### Screen 4: Job Detail Screen

**Route**: `/jobs/:id`

**Purpose**: Display full job information with actions

**Layout**:
```
AppBar: Job title
  - Actions: Edit icon, More menu (Archive/Delete)

Body (ScrollView):
  - Header card:
      - Company name (large, bold)
      - Title (subtitle)
      - Location, remote badge, salary
  - "Description" section:
      - Full description text
      - Markdown rendering (if applicable)
  - "Requirements" section:
      - Bullet list (checkmark icons)
      - Highlight keywords that match user's profile (future)
  - "Benefits" section:
      - Bullet list with icons
  - "Keywords" section:
      - Chips (all keywords shown)
  - Metadata:
      - Source (badge)
      - Date saved
      - Last updated

Floating Action Button:
  - "Generate Resume" → Navigate to generation flow
```

**User Interactions**:
- Tap Edit icon → Navigate to edit screen
- Tap More menu → Archive / Delete with confirmation
- Tap "Generate Resume" → Navigate to generation with job pre-filled
- Share job (future)

---

### Screen 5: Job Edit Screen

**Route**: `/jobs/:id/edit`

**Purpose**: Edit saved job details

**Layout**:
```
AppBar: "Edit Job"
  - Actions: Save icon

Body (Form with ScrollView):
  - Title TextField (required)
  - Company TextField (required)
  - Location TextField
  - Remote Switch
  - Description TextArea (multiline, required)
  - Requirements Section:
      - List builder (add/remove bullets)
      - Add button → Dialog with TextField
  - Benefits Section:
      - List builder (add/remove bullets)
      - Add button → Dialog with TextField
  - Keywords Section:
      - Tag input (chips)
  - Salary Range TextField
  - Status Dropdown (Active / Archived)
  - Save Button (primary, full width)
```

**User Interactions**:
- Edit any field → Enable save button
- Tap "Add" under Requirements → Show dialog → Add bullet
- Tap X on requirement bullet → Remove
- Tap Save → Validate → PUT /jobs/:id → Navigate back

**Validation**:
- Title, company, description required
- Min 10 chars for description
- Show field-level errors

---

## Implementation Checklist

### Data Models (lib/models/)
- [ ] Create `job.dart` with Job, BrowseJob, JobListResponse models
- [ ] Add freezed annotations and generate code (`flutter pub run build_runner build`)
- [ ] Create JobSource and JobStatus enums
- [ ] Implement fromJson/toJson for all models
- [ ] Add PaginationMeta model

### API Client (lib/services/api/)
- [ ] Create `jobs_api_client.dart`
- [ ] Implement `createFromText(String)` method
- [ ] Implement `createFromData(Map)` method
- [ ] Implement `browseJobs(...)` method
- [ ] Implement `getJobs(...)` method
- [ ] Implement `getJob(id)` method
- [ ] Implement `updateJob(id, data)` method
- [ ] Implement `deleteJob(id)` method
- [ ] Add error handling with DioException

### State Management (lib/providers/)
- [ ] Create `job_provider.dart` with JobNotifier and JobState
- [ ] Implement `createFromText()` method
- [ ] Implement `createFromData()` method
- [ ] Implement `browseMockJobs()` method
- [ ] Implement `saveBrowseJob()` method
- [ ] Implement `updateJob()` method
- [ ] Implement `deleteJob()` method
- [ ] Implement `archiveJob()` method
- [ ] Add pagination support
- [ ] Add error handling and state updates

### Screens (lib/screens/)
- [ ] Create `job_paste_screen.dart` with paste UI
- [ ] Create `job_browse_screen.dart` with search and filters
- [ ] Create `saved_jobs_list_screen.dart` with tabs and swipe actions
- [ ] Create `job_detail_screen.dart` with full job display
- [ ] Create `job_edit_screen.dart` with form and validation

### Widgets (lib/widgets/jobs/)
- [ ] Create `job_card.dart` (reusable job card)
- [ ] Create `job_detail_bottom_sheet.dart` (modal for browse)
- [ ] Create `keyword_chips.dart` (keyword display)
- [ ] Create `requirement_list.dart` (bullet list)
- [ ] Create `benefit_list.dart` (bullet list with icons)
- [ ] Create `job_empty_state.dart` (no jobs UI)

### Navigation (lib/router/)
- [ ] Add `/jobs` route (saved jobs list)
- [ ] Add `/jobs/paste` route (paste screen)
- [ ] Add `/jobs/browse` route (browse screen)
- [ ] Add `/jobs/:id` route (job detail)
- [ ] Add `/jobs/:id/edit` route (edit screen)

### Testing
- [ ] Unit tests for Job model serialization
- [ ] Unit tests for JobsApiClient methods
- [ ] Unit tests for JobNotifier state management
- [ ] Widget tests for all screens
- [ ] Integration tests for paste → parse → save flow
- [ ] Integration tests for browse → select → save flow

---

## Error Handling Strategy

### Network Errors
```dart
try {
  final job = await ref.read(jobProvider.notifier).createFromText(text);
  // Success
} on DioException catch (e) {
  final statusCode = e.response?.statusCode;
  if (statusCode == 400) {
    // Validation error
    showSnackBar('Please check the job description and try again.');
  } else if (statusCode == 422) {
    // Parsing failed
    showDialog(
      title: 'Parsing Failed',
      message: 'Unable to automatically parse job description. Would you like to enter details manually?',
      actions: [
        TextButton('Cancel'),
        TextButton('Enter Manually', onPressed: () => navigateToJobForm()),
      ],
    );
  } else if (statusCode == 401) {
    // Unauthorized
    navigateToLogin();
  } else {
    // Generic error
    showSnackBar('Failed to save job. Please try again.');
  }
}
```

### Parsing Failures
- 422 error → Offer manual entry as fallback
- Show parsed fields even if incomplete (partial success)
- Allow user to edit parsed fields before saving

### Empty States
- No saved jobs → Show prompt to add first job
- No browse results → "No jobs found. Try different keywords."
- Network error → "Unable to load jobs. Pull to refresh."

---

## Testing Strategy

### Unit Tests
- Test Job model fromJson/toJson
- Test JobsApiClient HTTP methods
- Test JobNotifier state transitions
- Test error handling logic

### Widget Tests
- Test job paste screen UI
- Test browse screen search and filters
- Test job card rendering
- Test swipe actions
- Test bottom sheet modal

### Integration Tests
- Test paste → parse → save full flow
- Test browse → save full flow
- Test edit → update flow
- Test delete flow
- Test pagination

---

## Future Enhancements

### Phase 2 Features
- [ ] Real-time job API integration (Indeed, LinkedIn)
- [ ] Job matching score (profile vs job)
- [ ] Bookmark/favorite jobs without saving
- [ ] Job application tracking
- [ ] Cover letter generation (separate feature)

### Phase 3 Features
- [ ] Job alert notifications
- [ ] Shared jobs (team/workspace feature)
- [ ] Job comparison view (side-by-side)
- [ ] Export job data (JSON/PDF)

---

**Document Status**: ✅ Ready for Implementation
**Backend Dependency**: Job API (Sprint 3 - not yet implemented)
**Mobile Complexity**: Medium (5 screens, state management, API integration)
**Estimated Implementation**: 2-3 weeks (with backend)
