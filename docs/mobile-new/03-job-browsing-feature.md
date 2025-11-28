# Job Management Feature

**Backend API**: [Job API](../api-services/03-job-api.md)
**Base Path**: `/api/v1/jobs`
**Status**: ✅ Fully Implemented
**Last Updated**: November 2025

---

## Overview

The Job Management feature allows users to save job postings from various sources, track application status, and manage their job search pipeline.

### User Stories

**As a user**, I want to:
- Save job postings from text (copy-paste from job boards)
- Save jobs from URLs (automatic scraping - future)
- View all my saved jobs in a filterable list
- Track application status for each job (Not Applied, Applied, Interview, Offer, Rejected)
- View job details with keyword highlighting
- Delete jobs I'm no longer interested in
- Filter jobs by status and source

---

## Screens

### 1. JobBrowseScreen (Future - API Integration)

**Route**: `/jobs/browse`
**File**: `lib/screens/jobs/job_browse_screen.dart`
**Status**: 🔄 Planned for future sprint

**UI Components** (Future):
- Search bar with filters (location, salary, remote, etc.)
- Job listing cards from external APIs
- "Save Job" button on each card
- Pagination controls

**Planned Integrations**:
- LinkedIn Jobs API
- Indeed API
- RemoteOK API
- GitHub Jobs

### 2. JobListScreen (Saved Jobs)

**Route**: `/jobs`
**File**: `lib/screens/jobs/job_list_screen.dart`

**UI Components**:
- Filter chips (status, source)
- Job cards with:
  - Company name and logo placeholder
  - Job title
  - Location
  - Employment type (Full-time, Part-time, Contract)
  - Application status badge
  - Posted date
- "Add Job" FAB (Floating Action Button)
- Pull-to-refresh
- Empty state ("No saved jobs yet")

**Filters**:
```dart
enum JobStatus {
  notApplied('Not Applied'),
  applied('Applied'),
  interview('Interview'),
  offer('Offer'),
  rejected('Rejected');
}

enum JobSource {
  userCreated('Pasted'),
  scraped('Scraped'),
  api('Job Board'),
  imported('Imported');
}
```

**User Flow**:
```
1. Screen loads → fetch jobs
2. Show loading spinner
3. Display job cards
4. Tap filter chip → filter list
5. Tap job card → navigate to JobDetailScreen
6. Pull down → refresh list
7. Tap FAB → navigate to JobPasteScreen
```

### 3. JobDetailScreen

**Route**: `/jobs/:id`
**File**: `lib/screens/jobs/job_detail_screen.dart`

**UI Components**:
- Job header:
  - Company name
  - Job title
  - Location
  - Employment type
  - Posted date
- Application status dropdown (update status)
- Job description with keyword highlighting
- Requirements section
- Qualifications section
- "Generate Resume" button (navigates to generation flow)
- "Generate Cover Letter" button
- "Delete Job" button (in overflow menu)

**Keyword Highlighting**:
```dart
// Highlights keywords from job_keywords field
class KeywordHighlighter extends StatelessWidget {
  final String text;
  final List<String> keywords;

  Widget build(BuildContext context) {
    return RichText(
      text: TextSpan(
        children: _buildTextSpans(text, keywords),
      ),
    );
  }

  List<TextSpan> _buildTextSpans(String text, List<String> keywords) {
    // Split text and highlight keywords
    // Return list of TextSpans with highlighted keywords
  }
}
```

**User Flow**:
```
1. Receive job ID from route
2. Fetch job details
3. Display job information
4. User updates status → send PUT request
5. User taps "Generate Resume" → navigate to GenerationOptionsScreen
6. User deletes job → confirm → send DELETE request → navigate back
```

### 4. JobPasteScreen (Text Input)

**Route**: `/jobs/paste`
**File**: `lib/screens/jobs/job_paste_screen.dart`

**UI Components**:
- Large multi-line text field
- Character counter (optional)
- "Paste from Clipboard" button
- "Create Job" button
- Loading overlay during AI parsing

**Form Validation**:
- Minimum 50 characters required

**User Flow**:
```
1. User navigates to paste screen
2. User pastes job posting text or types manually
3. Optional: Tap "Paste from Clipboard" → auto-fill text field
4. Tap "Create Job" button
5. Show loading overlay
6. API parses text with AI
7. On success:
   - Navigate to JobDetailScreen with new job
8. On error:
   - Show error message
   - Keep text in field for retry
```

---

## Backend API Integration

### API Endpoints (5 total)

#### 1. POST /api/v1/jobs - Create Job

**From Raw Text** (AI Parsing):
```dart
final job = await jobsApiClient.createJobFromText(
  rawText: '''
  Senior Software Engineer - TechCorp
  Location: Seattle, WA
  Type: Full-time

  We are looking for an experienced software engineer...
  Requirements:
  - 5+ years Python experience
  - FastAPI knowledge
  - AWS experience
  ''',
);
```

Request:
```json
{
  "raw_text": "Senior Software Engineer - TechCorp\nLocation: Seattle, WA..."
}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 1,
  "source": "user_created",
  "company_name": "TechCorp",
  "job_title": "Senior Software Engineer",
  "location": "Seattle, WA",
  "employment_type": "Full-time",
  "description": "We are looking for an experienced software engineer...",
  "requirements": "5+ years Python experience, FastAPI knowledge, AWS experience",
  "qualifications": null,
  "job_url": null,
  "raw_text": "Senior Software Engineer - TechCorp...",
  "job_keywords": ["Python", "FastAPI", "AWS", "software engineer"],
  "application_status": "not_applied",
  "posted_date": null,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**From URL** (Scraping - Future):
```dart
final job = await jobsApiClient.createJobFromUrl(
  url: 'https://jobs.example.com/posting/12345',
);
```

Request:
```json
{
  "job_url": "https://jobs.example.com/posting/12345"
}
```

**From Structured Data**:
```dart
final job = await jobsApiClient.createJob(
  companyName: 'TechCorp',
  jobTitle: 'Senior Software Engineer',
  location: 'Seattle, WA',
  employmentType: 'Full-time',
  description: 'We are looking for...',
  requirements: '5+ years Python...',
);
```

Request:
```json
{
  "company_name": "TechCorp",
  "job_title": "Senior Software Engineer",
  "location": "Seattle, WA",
  "employment_type": "Full-time",
  "description": "We are looking for...",
  "requirements": "5+ years Python...",
  "qualifications": "Bachelor's degree in CS",
  "job_url": "https://careers.techcorp.com/job/12345"
}
```

#### 2. GET /api/v1/jobs - List Jobs

**Without Filters**:
```dart
final jobs = await jobsApiClient.getJobs();
```

**With Filters**:
```dart
final jobs = await jobsApiClient.getJobs(
  status: 'applied',
  source: 'user_created',
  limit: 20,
  offset: 0,
);
```

Request:
```
GET /api/v1/jobs?status=applied&source=user_created&limit=20&offset=0
```

Response:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "company_name": "TechCorp",
      "job_title": "Senior Software Engineer",
      "location": "Seattle, WA",
      "employment_type": "Full-time",
      "application_status": "applied",
      "created_at": "2025-11-15T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### 3. GET /api/v1/jobs/{id} - Get Job Details

```dart
final job = await jobsApiClient.getJob(jobId);
```

Response: Full job object (same as create response)

#### 4. PUT /api/v1/jobs/{id} - Update Job

**Update Status**:
```dart
await jobsApiClient.updateJobStatus(
  jobId: jobId,
  status: 'interview',
);
```

Request:
```json
{
  "application_status": "interview"
}
```

**Update Keywords**:
```dart
await jobsApiClient.updateJob(
  jobId: jobId,
  jobKeywords: ['Python', 'FastAPI', 'AWS', 'Docker'],
);
```

Response: Updated job object

#### 5. DELETE /api/v1/jobs/{id} - Delete Job

```dart
await jobsApiClient.deleteJob(jobId);
```

Response: `204 No Content`

---

## Data Models

### Job (Freezed Model)

**File**: `lib/models/job.dart`

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'job.freezed.dart';
part 'job.g.dart';

@freezed
class Job with _$Job {
  const factory Job({
    required String id,
    required int userId,
    required String source,
    required String companyName,
    required String jobTitle,
    String? location,
    String? employmentType,
    String? description,
    String? requirements,
    String? qualifications,
    String? jobUrl,
    String? rawText,
    @Default([]) List<String> jobKeywords,
    @Default('not_applied') String applicationStatus,
    DateTime? postedDate,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Job;

  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
}
```

### JobFilter (Freezed Model)

**File**: `lib/models/job_filter.dart`

```dart
@freezed
class JobFilter with _$JobFilter {
  const factory JobFilter({
    String? status,
    String? source,
    int? limit,
    int? offset,
  }) = _JobFilter;

  factory JobFilter.fromJson(Map<String, dynamic> json) =>
      _$JobFilterFromJson(json);
}
```

### SavedJob (Simplified for List View)

**File**: `lib/models/saved_job.dart`

```dart
@freezed
class SavedJob with _$SavedJob {
  const factory SavedJob({
    required String id,
    required String companyName,
    required String jobTitle,
    String? location,
    String? employmentType,
    required String applicationStatus,
    required DateTime createdAt,
  }) = _SavedJob;

  factory SavedJob.fromJson(Map<String, dynamic> json) =>
      _$SavedJobFromJson(json);
}
```

---

## State Management

### JobsState

**File**: `lib/providers/jobs/jobs_state.dart`

```dart
class JobsState {
  final List<SavedJob> jobs;
  final Job? selectedJob;
  final JobFilter filter;
  final bool isLoading;
  final String? errorMessage;
  final int total;

  JobsState({
    this.jobs = const [],
    this.selectedJob,
    this.filter = const JobFilter(),
    this.isLoading = false,
    this.errorMessage,
    this.total = 0,
  });

  factory JobsState.initial() {
    return JobsState();
  }

  JobsState copyWith({
    List<SavedJob>? jobs,
    Job? selectedJob,
    JobFilter? filter,
    bool? isLoading,
    String? errorMessage,
    int? total,
  }) {
    return JobsState(
      jobs: jobs ?? this.jobs,
      selectedJob: selectedJob ?? this.selectedJob,
      filter: filter ?? this.filter,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      total: total ?? this.total,
    );
  }
}
```

### JobsNotifier

**File**: `lib/providers/jobs/jobs_notifier.dart`

```dart
class JobsNotifier extends StateNotifier<JobsState> {
  final JobsApiClient _apiClient;

  JobsNotifier(this._apiClient) : super(JobsState.initial()) {
    fetchJobs();
  }

  Future<void> fetchJobs({JobFilter? filter}) async {
    state = state.copyWith(isLoading: true);

    try {
      final response = await _apiClient.getJobs(
        status: filter?.status,
        source: filter?.source,
        limit: filter?.limit ?? 50,
        offset: filter?.offset ?? 0,
      );

      final jobs = (response['items'] as List)
          .map((json) => SavedJob.fromJson(json))
          .toList();

      state = state.copyWith(
        jobs: jobs,
        total: response['total'],
        filter: filter ?? state.filter,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> fetchJobDetails(String jobId) async {
    state = state.copyWith(isLoading: true);

    try {
      final job = await _apiClient.getJob(jobId);
      state = state.copyWith(
        selectedJob: job,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<Job> createJobFromText(String rawText) async {
    try {
      final job = await _apiClient.createJobFromText(rawText: rawText);

      // Refresh job list
      await fetchJobs(filter: state.filter);

      return job;
    } catch (e) {
      rethrow;
    }
  }

  Future<void> updateJobStatus(String jobId, String status) async {
    try {
      await _apiClient.updateJob(
        jobId: jobId,
        applicationStatus: status,
      );

      // Update selected job
      if (state.selectedJob?.id == jobId) {
        state = state.copyWith(
          selectedJob: state.selectedJob?.copyWith(applicationStatus: status),
        );
      }

      // Refresh job list
      await fetchJobs(filter: state.filter);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> deleteJob(String jobId) async {
    try {
      await _apiClient.deleteJob(jobId);

      // Remove from list
      state = state.copyWith(
        jobs: state.jobs.where((j) => j.id != jobId).toList(),
        total: state.total - 1,
      );
    } catch (e) {
      rethrow;
    }
  }

  void applyFilter(JobFilter filter) {
    fetchJobs(filter: filter);
  }

  void clearFilter() {
    fetchJobs(filter: const JobFilter());
  }
}

// Provider
final jobsNotifierProvider = StateNotifierProvider<JobsNotifier, JobsState>(
  (ref) {
    final apiClient = ref.watch(jobsApiClientProvider);
    return JobsNotifier(apiClient);
  },
);
```

---

## Service Layer

### JobsApiClient

**File**: `lib/services/api/jobs_api_client.dart`

```dart
class JobsApiClient {
  final Dio _dio;

  JobsApiClient(this._dio);

  Future<Job> createJobFromText({required String rawText}) async {
    try {
      final response = await _dio.post(
        '/api/v1/jobs',
        data: {'raw_text': rawText},
      );
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Job> createJobFromUrl({required String url}) async {
    try {
      final response = await _dio.post(
        '/api/v1/jobs',
        data: {'job_url': url},
      );
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Job> createJob({
    required String companyName,
    required String jobTitle,
    String? location,
    String? employmentType,
    String? description,
    String? requirements,
    String? qualifications,
    String? jobUrl,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/jobs',
        data: {
          'company_name': companyName,
          'job_title': jobTitle,
          'location': location,
          'employment_type': employmentType,
          'description': description,
          'requirements': requirements,
          'qualifications': qualifications,
          'job_url': jobUrl,
        },
      );
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getJobs({
    String? status,
    String? source,
    int? limit,
    int? offset,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status;
      if (source != null) queryParams['source'] = source;
      if (limit != null) queryParams['limit'] = limit;
      if (offset != null) queryParams['offset'] = offset;

      final response = await _dio.get(
        '/api/v1/jobs',
        queryParameters: queryParams,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Job> getJob(String jobId) async {
    try {
      final response = await _dio.get('/api/v1/jobs/$jobId');
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Job> updateJob({
    required String jobId,
    String? applicationStatus,
    List<String>? jobKeywords,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (applicationStatus != null) data['application_status'] = applicationStatus;
      if (jobKeywords != null) data['job_keywords'] = jobKeywords;

      final response = await _dio.put(
        '/api/v1/jobs/$jobId',
        data: data,
      );
      return Job.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteJob(String jobId) async {
    try {
      await _dio.delete('/api/v1/jobs/$jobId');
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
final jobsApiClientProvider = Provider<JobsApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return JobsApiClient(dio);
});
```

---

## UI Components

### Job Card

**File**: `lib/widgets/job_card.dart`

```dart
class JobCard extends StatelessWidget {
  final SavedJob job;
  final VoidCallback onTap;

  const JobCard({required this.job, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          child: Text(job.companyName[0].toUpperCase()),
        ),
        title: Text(job.jobTitle),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(job.companyName),
            if (job.location != null) Text(job.location!),
            if (job.employmentType != null)
              Chip(
                label: Text(job.employmentType!),
                padding: EdgeInsets.zero,
              ),
          ],
        ),
        trailing: ApplicationStatusBadge(status: job.applicationStatus),
        onTap: onTap,
      ),
    );
  }
}
```

### Application Status Badge

```dart
class ApplicationStatusBadge extends StatelessWidget {
  final String status;

  const ApplicationStatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getColor(status),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        _getLabel(status),
        style: TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }

  Color _getColor(String status) {
    switch (status) {
      case 'not_applied': return Colors.grey;
      case 'applied': return Colors.blue;
      case 'interview': return Colors.orange;
      case 'offer': return Colors.green;
      case 'rejected': return Colors.red;
      default: return Colors.grey;
    }
  }

  String _getLabel(String status) {
    return status.split('_').map((w) => w[0].toUpperCase() + w.substring(1)).join(' ');
  }
}
```

---

## Testing

### Unit Tests

```dart
test('JobsNotifier creates job from text', () async {
  final mockClient = MockJobsApiClient();
  final notifier = JobsNotifier(mockClient);

  when(mockClient.createJobFromText(rawText: any))
      .thenAnswer((_) async => testJob);

  await notifier.createJobFromText('Senior Engineer at TechCorp...');

  expect(notifier.state.jobs, isNotEmpty);
});

test('JobsNotifier filters jobs by status', () async {
  final mockClient = MockJobsApiClient();
  final notifier = JobsNotifier(mockClient);

  when(mockClient.getJobs(status: 'applied'))
      .thenAnswer((_) async => {'items': [testJob], 'total': 1});

  await notifier.applyFilter(JobFilter(status: 'applied'));

  expect(notifier.state.filter.status, 'applied');
  expect(notifier.state.jobs.length, 1);
});
```

---

## Performance Considerations

1. **Pagination**: Load jobs in batches of 20-50
2. **Caching**: Cache job list to avoid unnecessary API calls
3. **Optimistic Updates**: Update status immediately in UI
4. **Text Parsing**: Show loading overlay during AI parsing (2-5s)

---

**Status**: ✅ Fully Implemented
**Screens**: 4 (Browse, List, Detail, Paste)
**API Endpoints**: 5 endpoints
**Dependencies**: freezed, json_serializable, dio
**Last Updated**: November 2025
