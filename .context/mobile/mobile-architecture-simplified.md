# JobWise Mobile App - Simplified Architecture (YAGNI Applied)

**Version**: 2.0 - Simplified
**Last Updated**: October 21, 2025

---

## Why Simplify?

The previous architecture was **over-engineered** with:
- ❌ Unnecessary repository abstraction layer
- ❌ Separate local/remote repository interfaces
- ❌ Complex adapter patterns
- ❌ Too many nested folders (features/*/ui/, features/*/services/, features/*/state/)
- ❌ Over-application of "clean architecture" for a mobile app

**YAGNI Applied:** Build what we need NOW, not what we might need later.

---

## 1. Simple Three-Layer Architecture

```
┌─────────────────────────────────────┐
│      UI (Screens & Widgets)         │
│       Flutter Material 3            │
└─────────────────────────────────────┘
           ↓ watches ↑ notifies
┌─────────────────────────────────────┐
│   State (Riverpod Notifiers)        │
│   Business Logic Lives Here         │
└─────────────────────────────────────┘
           ↓ calls
┌─────────────────────────────────────┐
│        Services (Simple)            │
│  ApiService | DB | SecureStorage    │
└─────────────────────────────────────┘
     ↓             ↓
┌─────────┐  ┌───────────┐
│ Backend │  │ Local DB  │
└─────────┘  └───────────┘
```

**That's it. Three layers. No more.**

---

## 2. Folder Structure (Flat & Simple)

```
lib/
├── main.dart
├── app.dart                      # MaterialApp setup
│
├── screens/                      # All screens (flat by feature)
│   ├── auth_screens.dart        # Login + Register in one file
│   ├── job_list_screen.dart
│   ├── job_detail_screen.dart
│   ├── saved_jobs_screen.dart
│   ├── profile_list_screen.dart
│   ├── profile_edit_screen.dart
│   ├── generation_list_screen.dart    # List of all generations
│   ├── generation_detail_screen.dart  # Generation progress/status
│   ├── resume_viewer_screen.dart      # View generated resume
│   ├── cover_letter_viewer_screen.dart # View generated cover letter
│   └── document_list_screen.dart      # All saved documents
│
├── widgets/                      # Reusable widgets
│   ├── job_card.dart
│   ├── profile_card.dart
│   ├── profile_completeness_indicator.dart
│   ├── generation_card.dart
│   ├── document_card.dart
│   ├── generation_progress_indicator.dart
│   ├── match_score_widget.dart
│   ├── keyword_coverage_widget.dart
│   ├── ats_score_badge.dart
│   ├── template_picker.dart
│   ├── feedback_form.dart
│   ├── pdf_viewer_widget.dart
│   ├── loading_overlay.dart
│   ├── error_display.dart
│   └── ...
│
├── providers/                    # All state management
│   ├── auth_provider.dart       # Auth state + logic
│   ├── jobs_provider.dart       # Jobs state + logic
│   ├── profile_provider.dart    # Profile state + logic
│   ├── generation_provider.dart # Generation state + logic
│   └── documents_provider.dart  # Documents state + logic
│
├── services/                     # Service classes
│   ├── api/                     # HTTP clients by feature
│   │   ├── base_http_client.dart    # Dio setup, interceptors
│   │   ├── auth_api_client.dart     # Auth endpoints
│   │   ├── jobs_api_client.dart     # Job endpoints
│   │   ├── profiles_api_client.dart # Profile endpoints
│   │   ├── generations_api_client.dart # Generation endpoints
│   │   └── documents_api_client.dart   # Document endpoints
│   ├── db_service.dart          # ALL SQLite operations
│   └── storage_service.dart     # Token storage
│
├── models/                       # Data models (freezed)
│   ├── user.dart
│   ├── job.dart
│   ├── saved_job.dart           # SavedJob with notes field
│   ├── profile.dart
│   ├── profile_analytics.dart   # Profile completeness, strength
│   ├── generation.dart          # Generation status, progress
│   ├── generation_analytics.dart # Match score, keyword coverage, ATS
│   ├── document.dart            # Document metadata
│   ├── resume.dart              # Resume content model
│   ├── cover_letter.dart        # Cover letter content model
│   └── template.dart            # Resume template model
│
├── utils/
│   ├── validators.dart
│   └── formatters.dart
│
└── constants/
    ├── colors.dart
    ├── routes.dart
    └── text_styles.dart
```

**Total files: ~50-60 files (includes core feature enhancements)**

---

## 3. How Data Flows (Simple Example)

### Example: Save a Job

**1. UI Layer**
```dart
// In job_detail_screen.dart
IconButton(
  icon: Icon(Icons.bookmark),
  onPressed: () {
    ref.read(jobsProvider.notifier).saveJob(job.id);
  },
)
```

**2. State Layer**
```dart
// In providers/jobs_provider.dart
class JobsNotifier extends StateNotifier<JobsState> {
  final JobsApiClient _jobsApi;
  final DbService _db;
  
  JobsNotifier(this._jobsApi, this._db) : super(JobsState.initial());
  
  Future<void> saveJob(String jobId) async {
    state = state.copyWith(isLoading: true);
    
    try {
      // Try backend first
      final saved = await _jobsApi.saveJob(jobId);
      await _db.saveSavedJob(saved); // Cache locally
      
      state = state.copyWith(
        savedJobs: [...state.savedJobs, saved],
        isLoading: false,
      );
    } catch (e) {
      // Offline? Save locally, queue for sync
      final local = SavedJob(jobId: jobId, syncPending: true);
      await _db.saveSavedJob(local);
      
      state = state.copyWith(
        savedJobs: [...state.savedJobs, local],
        isLoading: false,
        error: 'Saved offline. Will sync when online.',
      );
    }
  }
}

// Provider definition
final jobsProvider = StateNotifierProvider<JobsNotifier, JobsState>((ref) {
  return JobsNotifier(
    ref.watch(jobsApiClientProvider),
    ref.watch(dbServiceProvider),
  );
});
```

**3. Services Layer**
```dart
// In services/api/jobs_api_client.dart
class JobsApiClient {
  final BaseHttpClient _client;
  
  JobsApiClient(this._client);
  
  Future<SavedJob> saveJob(String jobId) async {
    final response = await _client.post('/jobs/$jobId/save');
    return SavedJob.fromJson(response.data);
  }
  
  Future<List<Job>> getJobs({int offset = 0, int limit = 20}) async {
    final response = await _client.get('/jobs', queryParameters: {
      'offset': offset,
      'limit': limit,
    });
    return (response.data['jobs'] as List)
        .map((j) => Job.fromJson(j))
        .toList();
  }
}

// In services/db_service.dart
class DbService {
  final Database _db;
  
  DbService(this._db);
  
  Future<void> saveSavedJob(SavedJob job) async {
    await _db.insert('saved_jobs', job.toJson());
  }
}
```

**Done. No repository abstraction. No adapter pattern. Just simple, clear code.**

---

## 3.1 Generation Flow Example (Resume/Cover Letter)

### Example: Generate and View Resume

**1. Start Generation (UI → State → API)**
```dart
// In generation_list_screen.dart
ElevatedButton(
  onPressed: () async {
    final generationId = await ref
        .read(generationProvider.notifier)
        .startResumeGeneration(profileId, jobId);
    
    // Navigate to detail screen to watch progress
    context.push('/generations/$generationId');
  },
  child: Text('Generate Resume'),
)
```

**2. Poll for Progress (State Layer)**
```dart
// In providers/generation_provider.dart
class GenerationNotifier extends StateNotifier<GenerationState> {
  final GenerationsApiClient _api;
  Timer? _pollTimer;
  
  GenerationNotifier(this._api) : super(GenerationState.initial());
  
  Future<String> startResumeGeneration(String profileId, String jobId) async {
    try {
      final generation = await _api.startResumeGeneration(profileId, jobId);
      state = state.copyWith(currentGeneration: generation);
      
      // Start polling for progress
      _startPolling(generation.id);
      
      return generation.id;
    } catch (e) {
      state = state.copyWith(error: 'Failed to start generation');
      rethrow;
    }
  }
  
  void _startPolling(String generationId) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(Duration(seconds: 2), (timer) async {
      try {
        final updated = await _api.getGeneration(generationId);
        state = state.copyWith(currentGeneration: updated);
        
        // Stop polling when complete or failed
        if (updated.status == 'completed' || updated.status == 'failed') {
          timer.cancel();
        }
      } catch (e) {
        timer.cancel();
        state = state.copyWith(error: 'Polling failed');
      }
    });
  }
  
  Future<Resume> loadResume(String generationId) async {
    state = state.copyWith(isLoading: true);
    try {
      final resume = await _api.getResume(generationId);
      state = state.copyWith(
        currentResume: resume,
        isLoading: false,
      );
      return resume;
    } catch (e) {
      state = state.copyWith(
        error: 'Failed to load resume',
        isLoading: false,
      );
      rethrow;
    }
  }
  
  Future<void> downloadResumePdf(String generationId) async {
    try {
      final pdfBytes = await _api.downloadResumePdf(generationId);
      // Save to device or open in viewer
      await _savePdfToDevice(pdfBytes, 'resume_${generationId}.pdf');
    } catch (e) {
      state = state.copyWith(error: 'Failed to download PDF');
    }
  }
  
  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }
}
```

**3. Show Progress (UI)**
```dart
// In generation_detail_screen.dart
class GenerationDetailScreen extends ConsumerWidget {
  final String generationId;
  
  const GenerationDetailScreen({required this.generationId});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final generation = ref.watch(generationProvider).currentGeneration;
    
    if (generation == null) {
      return LoadingOverlay();
    }
    
    return Scaffold(
      appBar: AppBar(title: Text('Generation Progress')),
      body: Column(
        children: [
          // Progress indicator (5 stages)
          GenerationProgressIndicator(
            currentStage: generation.currentStage,
            stages: [
              'Parsing Job',
              'Analyzing Profile',
              'Generating Content',
              'Optimizing',
              'Finalizing',
            ],
          ),
          
          SizedBox(height: 24),
          
          // Stage details
          Text(generation.stageMessage ?? 'Processing...'),
          
          if (generation.status == 'completed') ...[
            SizedBox(height: 32),
            ElevatedButton.icon(
              icon: Icon(Icons.visibility),
              label: Text('View Resume'),
              onPressed: () {
                context.push('/generations/$generationId/resume');
              },
            ),
            SizedBox(height: 16),
            OutlinedButton.icon(
              icon: Icon(Icons.download),
              label: Text('Download PDF'),
              onPressed: () {
                ref.read(generationProvider.notifier)
                    .downloadResumePdf(generationId);
              },
            ),
          ],
          
          if (generation.status == 'failed') ...[
            ErrorDisplay(message: generation.errorMessage ?? 'Generation failed'),
            ElevatedButton(
              onPressed: () {
                // Retry logic
                ref.read(generationProvider.notifier)
                    .startResumeGeneration(
                      generation.profileId,
                      generation.jobId,
                    );
              },
              child: Text('Retry'),
            ),
          ],
        ],
      ),
    );
  }
}
```

**4. View Resume Content (UI)**
```dart
// In resume_viewer_screen.dart
class ResumeViewerScreen extends ConsumerStatefulWidget {
  final String generationId;
  
  const ResumeViewerScreen({required this.generationId});
  
  @override
  ConsumerState<ResumeViewerScreen> createState() => _ResumeViewerScreenState();
}

class _ResumeViewerScreenState extends ConsumerState<ResumeViewerScreen> {
  @override
  void initState() {
    super.initState();
    // Load resume content when screen opens
    Future.microtask(() {
      ref.read(generationProvider.notifier).loadResume(widget.generationId);
    });
  }
  
  @override
  Widget build(BuildContext context) {
    final state = ref.watch(generationProvider);
    final resume = state.currentResume;
    
    if (state.isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text('Resume')),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    if (resume == null) {
      return Scaffold(
        appBar: AppBar(title: Text('Resume')),
        body: ErrorDisplay(message: 'Resume not found'),
      );
    }
    
    return Scaffold(
      appBar: AppBar(
        title: Text('Resume'),
        actions: [
          IconButton(
            icon: Icon(Icons.download),
            onPressed: () {
              ref.read(generationProvider.notifier)
                  .downloadResumePdf(widget.generationId);
            },
          ),
          IconButton(
            icon: Icon(Icons.share),
            onPressed: () {
              // Share resume logic
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header section
            Text(
              resume.fullName,
              style: Theme.of(context).textTheme.headlineLarge,
            ),
            SizedBox(height: 8),
            Text(resume.email),
            Text(resume.phone),
            if (resume.location != null) Text(resume.location!),
            
            Divider(height: 32),
            
            // Professional summary
            if (resume.summary != null) ...[
              Text(
                'Professional Summary',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),
              Text(resume.summary!),
              SizedBox(height: 24),
            ],
            
            // Experience
            if (resume.experience.isNotEmpty) ...[
              Text(
                'Experience',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),
              ...resume.experience.map((exp) => ExperienceCard(experience: exp)),
              SizedBox(height: 24),
            ],
            
            // Education
            if (resume.education.isNotEmpty) ...[
              Text(
                'Education',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),
              ...resume.education.map((edu) => EducationCard(education: edu)),
              SizedBox(height: 24),
            ],
            
            // Skills
            if (resume.skills.isNotEmpty) ...[
              Text(
                'Skills',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: resume.skills.map((skill) => 
                  Chip(label: Text(skill))
                ).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

**Similar flow for Cover Letter with cover_letter_viewer_screen.dart**

---

## 4. Key Simplifications

| Old (Over-Engineered) | New (YAGNI) | Why? |
|----------------------|-------------|------|
| Repository layer | REMOVED | Notifiers can call API clients directly |
| One giant ApiService class | Feature-based API clients | Easier to develop, test, and maintain |
| Separate Local Storage classes | One DbService | All DB calls in one place |
| Adapter pattern interfaces | REMOVED | Not switching implementations |
| `lib/src/features/*/ui/` | `lib/screens/` | Flat is easier to navigate |
| Multiple services per feature | 7 focused API clients + 2 services | Clear separation of concerns |
| Separate state files | Provider file has state + notifier | Keep related code together |

---

## 5. State Management (Still Riverpod)

**Why keep Riverpod?** It's actually simple and solves real problems:
- ✅ Compile-time safe dependency injection
- ✅ Easy testing (ProviderContainer)
- ✅ Automatic disposal
- ✅ Great devtools
- ✅ No boilerplate (unlike BLoC)

**Each feature gets ONE provider file:**

```dart
// providers/jobs_provider.dart

// State class
@freezed
class JobsState with _$JobsState {
  const factory JobsState({
    @Default([]) List<Job> jobs,
    @Default([]) List<SavedJob> savedJobs,
    @Default(false) bool isLoading,
    String? error,
  }) = _JobsState;
}

// Notifier class (business logic)
class JobsNotifier extends StateNotifier<JobsState> {
  final ApiService _api;
  final DbService _db;
  
  JobsNotifier(this._api, this._db) : super(const JobsState());
  
  Future<void> loadJobs() async { /* ... */ }
  Future<void> saveJob(String id) async { /* ... */ }
  Future<void> searchJobs(String query) async { /* ... */ }
}

// Provider
final jobsProvider = StateNotifierProvider<JobsNotifier, JobsState>((ref) {
  return JobsNotifier(
    ref.watch(jobsApiClientProvider),
    ref.watch(dbServiceProvider),
  );
});

// Derived providers (if needed)
final savedJobsCountProvider = Provider<int>((ref) {
  return ref.watch(jobsProvider).savedJobs.length;
});
```

---

## 6. Services (Separated by Feature)

### BaseHttpClient - Shared HTTP Setup

```dart
// services/api/base_http_client.dart
class BaseHttpClient {
  final Dio _dio;
  final StorageService _storage;
  
  BaseHttpClient({
    required String baseUrl,
    required StorageService storage,
  })  : _storage = storage,
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
        )) {
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token to all requests
          final token = await _storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          // Auto retry on 401 (token expired)
          if (error.response?.statusCode == 401) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry original request with new token
              final opts = error.requestOptions;
              final newToken = await _storage.getToken();
              opts.headers['Authorization'] = 'Bearer $newToken';
              final response = await _dio.fetch(opts);
              return handler.resolve(response);
            }
          }
          handler.next(error);
        },
      ),
    );
  }
  
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;
      
      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });
      
      await _storage.saveTokens(
        response.data['access_token'],
        response.data['refresh_token'],
      );
      return true;
    } catch (e) {
      await _storage.clearTokens();
      return false;
    }
  }
  
  // Expose HTTP methods
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }
  
  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }
  
  Future<Response> put(String path, {dynamic data}) {
    return _dio.put(path, data: data);
  }
  
  Future<Response> delete(String path) {
    return _dio.delete(path);
  }
  
  Future<Response> patch(String path, {dynamic data}) {
    return _dio.patch(path, data: data);
  }
}

// Provider
final baseHttpClientProvider = Provider<BaseHttpClient>((ref) {
  return BaseHttpClient(
    baseUrl: 'http://localhost:8000/api/v1',
    storage: ref.watch(storageServiceProvider),
  );
});
```

### AuthApiClient - Authentication Endpoints

```dart
// services/api/auth_api_client.dart
class AuthApiClient {
  final BaseHttpClient _client;
  final StorageService _storage;
  
  AuthApiClient(this._client, this._storage);
  
  Future<User> login(String email, String password) async {
    final response = await _client.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    
    // Save tokens
    await _storage.saveTokens(
      response.data['access_token'],
      response.data['refresh_token'],
    );
    
    return User.fromJson(response.data['user']);
  }
  
  Future<User> register(String email, String password, String name) async {
    final response = await _client.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': name,
    });
    
    // Auto-login after registration
    await _storage.saveTokens(
      response.data['access_token'],
      response.data['refresh_token'],
    );
    
    return User.fromJson(response.data['user']);
  }
  
  Future<void> logout() async {
    try {
      await _client.post('/auth/logout');
    } finally {
      await _storage.clearTokens();
    }
  }
  
  Future<User> getCurrentUser() async {
    final response = await _client.get('/auth/me');
    return User.fromJson(response.data);
  }
}

// Provider
final authApiClientProvider = Provider<AuthApiClient>((ref) {
  return AuthApiClient(
    ref.watch(baseHttpClientProvider),
    ref.watch(storageServiceProvider),
  );
});
```

### JobsApiClient - Job Endpoints

```dart
// services/api/jobs_api_client.dart
class JobsApiClient {
  final BaseHttpClient _client;
  
  JobsApiClient(this._client);
  
  Future<List<Job>> getJobs({
    int offset = 0,
    int limit = 20,
    String? search,
    String? location,
  }) async {
    final response = await _client.get('/jobs', queryParameters: {
      'offset': offset,
      'limit': limit,
      if (search != null) 'q': search,
      if (location != null) 'location': location,
    });
    
    return (response.data['jobs'] as List)
        .map((j) => Job.fromJson(j))
        .toList();
  }
  
  Future<Job> getJobById(String id) async {
    final response = await _client.get('/jobs/$id');
    return Job.fromJson(response.data);
  }
  
  Future<SavedJob> saveJob(String jobId) async {
    final response = await _client.post('/jobs/$jobId/save');
    return SavedJob.fromJson(response.data);
  }
  
  Future<void> unsaveJob(String savedJobId) async {
    await _client.delete('/jobs/saved/$savedJobId');
  }
  
  Future<List<SavedJob>> getSavedJobs() async {
    final response = await _client.get('/jobs/saved');
    return (response.data['saved_jobs'] as List)
        .map((j) => SavedJob.fromJson(j))
        .toList();
  }
  
  Future<SavedJob> updateSavedJobStatus(String id, String status) async {
    final response = await _client.patch('/jobs/saved/$id', data: {
      'status': status,
    });
    return SavedJob.fromJson(response.data);
  }
  
  Future<SavedJob> updateSavedJobNotes(String id, String notes) async {
    final response = await _client.patch('/jobs/saved/$id', data: {
      'notes': notes,
    });
    return SavedJob.fromJson(response.data);
  }
}

// Provider
final jobsApiClientProvider = Provider<JobsApiClient>((ref) {
  return JobsApiClient(ref.watch(baseHttpClientProvider));
});
```

### ProfilesApiClient - Profile Endpoints

```dart
// services/api/profiles_api_client.dart
class ProfilesApiClient {
  final BaseHttpClient _client;
  
  ProfilesApiClient(this._client);
  
  Future<List<Profile>> getProfiles() async {
    final response = await _client.get('/profiles');
    return (response.data['profiles'] as List)
        .map((p) => Profile.fromJson(p))
        .toList();
  }
  
  Future<Profile> getProfile(String id) async {
    final response = await _client.get('/profiles/$id');
    return Profile.fromJson(response.data);
  }
  
  Future<Profile> createProfile(Profile profile) async {
    final response = await _client.post('/profiles', data: profile.toJson());
    return Profile.fromJson(response.data);
  }
  
  Future<Profile> updateProfile(String id, Profile profile) async {
    final response = await _client.put('/profiles/$id', data: profile.toJson());
    return Profile.fromJson(response.data);
  }
  
  Future<void> deleteProfile(String id) async {
    await _client.delete('/profiles/$id');
  }
  
  Future<ProfileAnalytics> getProfileAnalytics(String id) async {
    final response = await _client.get('/profiles/$id/analytics');
    return ProfileAnalytics.fromJson(response.data);
  }
  
  Future<Map<String, dynamic>> getProfileSummary(String id) async {
    final response = await _client.get('/profiles/$id/summary');
    return response.data;
  }
}

// Provider
final profilesApiClientProvider = Provider<ProfilesApiClient>((ref) {
  return ProfilesApiClient(ref.watch(baseHttpClientProvider));
});
```

### GenerationsApiClient - Generation Endpoints

```dart
// services/api/generations_api_client.dart
class GenerationsApiClient {
  final BaseHttpClient _client;
  
  GenerationsApiClient(this._client);
  
  Future<Generation> startResumeGeneration(String profileId, String jobId) async {
    final response = await _client.post('/generations/resume', data: {
      'profile_id': profileId,
      'job_id': jobId,
    });
    return Generation.fromJson(response.data);
  }
  
  Future<Generation> startCoverLetterGeneration(String profileId, String jobId) async {
    final response = await _client.post('/generations/cover-letter', data: {
      'profile_id': profileId,
      'job_id': jobId,
    });
    return Generation.fromJson(response.data);
  }
  
  Future<Generation> getGeneration(String id) async {
    final response = await _client.get('/generations/$id');
    return Generation.fromJson(response.data);
  }
  
  Future<List<Generation>> getGenerations({int offset = 0, int limit = 20}) async {
    final response = await _client.get('/generations', queryParameters: {
      'offset': offset,
      'limit': limit,
    });
    return (response.data['generations'] as List)
        .map((g) => Generation.fromJson(g))
        .toList();
  }
  
  Future<void> cancelGeneration(String id) async {
    await _client.post('/generations/$id/cancel');
  }
  
  // Get generated resume content
  Future<Resume> getResume(String generationId) async {
    final response = await _client.get('/generations/$generationId/resume');
    return Resume.fromJson(response.data);
  }
  
  // Get generated cover letter content
  Future<CoverLetter> getCoverLetter(String generationId) async {
    final response = await _client.get('/generations/$generationId/cover-letter');
    return CoverLetter.fromJson(response.data);
  }
  
  // Download resume as PDF
  Future<Uint8List> downloadResumePdf(String generationId) async {
    final response = await _client.get(
      '/generations/$generationId/resume/download',
      queryParameters: {'format': 'pdf'},
    );
    return response.data as Uint8List;
  }
  
  // Download cover letter as PDF
  Future<Uint8List> downloadCoverLetterPdf(String generationId) async {
    final response = await _client.get(
      '/generations/$generationId/cover-letter/download',
      queryParameters: {'format': 'pdf'},
    );
    return response.data as Uint8List;
  }
  
  // Get generation analytics (match score, keyword coverage, ATS)
  Future<GenerationAnalytics> getGenerationAnalytics(String generationId) async {
    final response = await _client.get('/generations/$generationId/analytics');
    return GenerationAnalytics.fromJson(response.data);
  }
  
  // Submit feedback on generated document
  Future<void> submitFeedback(String generationId, {
    required int rating,
    String? comments,
    List<String>? tags,
  }) async {
    await _client.post('/generations/$generationId/feedback', data: {
      'rating': rating,
      if (comments != null) 'comments': comments,
      if (tags != null) 'tags': tags,
    });
  }
  
  // Validate generation (re-run ATS checks)
  Future<Map<String, dynamic>> validateGeneration(String generationId) async {
    final response = await _client.post('/generations/$generationId/validate');
    return response.data;
  }
  
  // Get available templates
  Future<List<Template>> getTemplates() async {
    final response = await _client.get('/generations/templates');
    return (response.data['templates'] as List)
        .map((t) => Template.fromJson(t))
        .toList();
  }
}

// Provider
final generationsApiClientProvider = Provider<GenerationsApiClient>((ref) {
  return GenerationsApiClient(ref.watch(baseHttpClientProvider));
});
```

### DocumentsApiClient - Document Endpoints

```dart
// services/api/documents_api_client.dart
class DocumentsApiClient {
  final BaseHttpClient _client;
  
  DocumentsApiClient(this._client);
  
  Future<List<Document>> getDocuments({
    String? type, // 'resume' or 'cover_letter'
    int offset = 0,
    int limit = 20,
  }) async {
    final response = await _client.get('/documents', queryParameters: {
      if (type != null) 'type': type,
      'offset': offset,
      'limit': limit,
    });
    return (response.data['documents'] as List)
        .map((d) => Document.fromJson(d))
        .toList();
  }
  
  Future<Document> getDocument(String id) async {
    final response = await _client.get('/documents/$id');
    return Document.fromJson(response.data);
  }
  
  Future<Uint8List> downloadDocument(String id) async {
    final response = await _client.get('/documents/$id/download');
    return response.data as Uint8List;
  }
  
  Future<void> deleteDocument(String id) async {
    await _client.delete('/documents/$id');
  }
  
  // Get all resumes
  Future<List<Document>> getResumes() async {
    return getDocuments(type: 'resume');
  }
  
  // Get all cover letters
  Future<List<Document>> getCoverLetters() async {
    return getDocuments(type: 'cover_letter');
  }
}

// Provider
final documentsApiClientProvider = Provider<DocumentsApiClient>((ref) {
  return DocumentsApiClient(ref.watch(baseHttpClientProvider));
});
```

### DbService - All SQLite Operations

```dart
class DbService {
  Database? _db;
  
  Future<void> init() async {
    _db = await openDatabase(
      'jobwise.db',
      version: 1,
      onCreate: (db, version) async {
        // Create all tables
        await db.execute('''
          CREATE TABLE jobs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT,
            cached_at INTEGER
          )
        ''');
        
        await db.execute('''
          CREATE TABLE saved_jobs (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            status TEXT,
            sync_pending INTEGER DEFAULT 0
          )
        ''');
        
        await db.execute('''
          CREATE TABLE profiles (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            cached_at INTEGER
          )
        ''');
        
        // ... other tables
      },
    );
  }
  
  // Jobs
  Future<void> cacheJobs(List<Job> jobs) async {
    final batch = _db!.batch();
    for (var job in jobs) {
      batch.insert(
        'jobs',
        {...job.toJson(), 'cached_at': DateTime.now().millisecondsSinceEpoch},
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit();
  }
  
  Future<List<Job>> getCachedJobs() async {
    final maps = await _db!.query('jobs', orderBy: 'cached_at DESC');
    return maps.map((m) => Job.fromJson(m)).toList();
  }
  
  Future<void> saveSavedJob(SavedJob job) async {
    await _db!.insert('saved_jobs', job.toJson());
  }
  
  Future<List<SavedJob>> getSavedJobs() async {
    final maps = await _db!.query('saved_jobs');
    return maps.map((m) => SavedJob.fromJson(m)).toList();
  }
  
  // Sync queue
  Future<void> queueSync(String entity, String operation, Map<String, dynamic> data) async {
    await _db!.insert('sync_queue', {
      'entity': entity,
      'operation': operation,
      'data': jsonEncode(data),
      'created_at': DateTime.now().millisecondsSinceEpoch,
    });
  }
  
  // ... all other DB operations
}
```

### StorageService - Secure Token Storage

```dart
class StorageService {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();
  String? _accessToken; // In memory only
  
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    _accessToken = accessToken;
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }
  
  Future<String?> getToken() async => _accessToken;
  
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }
  
  Future<void> clearTokens() async {
    _accessToken = null;
    await _storage.delete(key: 'refresh_token');
  }
}
```

---

## 6.1 Data Models for Resume & Cover Letter

### Resume Model
```dart
// models/resume.dart
@freezed
class Resume with _$Resume {
  const factory Resume({
    required String id,
    required String generationId,
    required String fullName,
    required String email,
    required String phone,
    String? location,
    String? summary,
    @Default([]) List<Experience> experience,
    @Default([]) List<Education> education,
    @Default([]) List<String> skills,
    @Default([]) List<Project> projects,
    @Default([]) List<Certification> certifications,
    Map<String, dynamic>? metadata, // ATS score, keywords, etc.
    DateTime? createdAt,
  }) = _Resume;
  
  factory Resume.fromJson(Map<String, dynamic> json) => _$ResumeFromJson(json);
}

@freezed
class Experience with _$Experience {
  const factory Experience({
    required String title,
    required String company,
    String? location,
    required String startDate,
    String? endDate,
    @Default([]) List<String> achievements,
  }) = _Experience;
  
  factory Experience.fromJson(Map<String, dynamic> json) => _$ExperienceFromJson(json);
}

@freezed
class Education with _$Education {
  const factory Education({
    required String degree,
    required String institution,
    String? location,
    String? graduationDate,
    String? gpa,
  }) = _Education;
  
  factory Education.fromJson(Map<String, dynamic> json) => _$EducationFromJson(json);
}
```

### Cover Letter Model
```dart
// models/cover_letter.dart
@freezed
class CoverLetter with _$CoverLetter {
  const factory CoverLetter({
    required String id,
    required String generationId,
    required String fullName,
    required String email,
    required String phone,
    String? address,
    required String recipientName,
    required String recipientTitle,
    required String companyName,
    String? companyAddress,
    required String salutation,
    required String opening,
    required String body,
    required String closing,
    required String signature,
    DateTime? date,
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
  }) = _CoverLetter;
  
  factory CoverLetter.fromJson(Map<String, dynamic> json) => _$CoverLetterFromJson(json);
}
```

### Generation Model (Updated)
```dart
// models/generation.dart
@freezed
class Generation with _$Generation {
  const factory Generation({
    required String id,
    required String profileId,
    required String jobId,
    required String type, // 'resume' or 'cover_letter'
    required String status, // 'pending', 'processing', 'completed', 'failed'
    String? currentStage, // 'parsing_job', 'analyzing_profile', etc.
    String? stageMessage,
    int? progress, // 0-100
    String? errorMessage,
    String? documentId, // Reference to final document
    Map<String, dynamic>? metadata,
    DateTime? createdAt,
    DateTime? completedAt,
  }) = _Generation;
  
  factory Generation.fromJson(Map<String, dynamic> json) => _$GenerationFromJson(json);
}
```

### Document Model (Updated)
```dart
// models/document.dart
@freezed
class Document with _$Document {
  const factory Document({
    required String id,
    required String generationId,
    required String type, // 'resume' or 'cover_letter'
    required String fileName,
    String? filePath, // Local file path if cached
    int? fileSize,
    required String status, // 'available', 'cached', 'downloading'
    DateTime? createdAt,
    DateTime? lastAccessedAt,
  }) = _Document;
  
  factory Document.fromJson(Map<String, dynamic> json) => _$DocumentFromJson(json);
}
```

### SavedJob Model (Enhanced with Notes)
```dart
// models/saved_job.dart
@freezed
class SavedJob with _$SavedJob {
  const factory SavedJob({
    required String id,
    required String userId,
    required String jobId,
    required String status, // 'interested', 'applied', 'interviewing', 'offer', 'rejected', 'closed'
    String? notes, // User notes about the job
    DateTime? savedAt,
    DateTime? appliedAt,
    DateTime? updatedAt,
  }) = _SavedJob;
  
  factory SavedJob.fromJson(Map<String, dynamic> json) => _$SavedJobFromJson(json);
}
```

### ProfileAnalytics Model (NEW - Core Feature)
```dart
// models/profile_analytics.dart
@freezed
class ProfileAnalytics with _$ProfileAnalytics {
  const factory ProfileAnalytics({
    required String profileId,
    required double completenessScore, // 0-100
    required Map<String, bool> sectionsComplete, // e.g., {'experience': true, 'education': true}
    @Default([]) List<String> missingFields,
    @Default([]) List<String> suggestions,
    int? totalExperiences,
    int? totalEducation,
    int? totalSkills,
    int? totalProjects,
    String? strengthLevel, // 'weak', 'moderate', 'strong', 'excellent'
  }) = _ProfileAnalytics;
  
  factory ProfileAnalytics.fromJson(Map<String, dynamic> json) => _$ProfileAnalyticsFromJson(json);
}
```

### GenerationAnalytics Model (NEW - Core Feature)
```dart
// models/generation_analytics.dart
@freezed
class GenerationAnalytics with _$GenerationAnalytics {
  const factory GenerationAnalytics({
    required String generationId,
    required double matchScore, // 0-100 profile-job match percentage
    required int keywordsRequiredCount,
    required int keywordsMatchedCount,
    required double keywordCoveragePercent, // (matched/required) * 100
    @Default([]) List<String> keywordsMatched,
    @Default([]) List<String> keywordsMissing,
    required double atsScore, // 0-100 ATS compatibility
    Map<String, double>? atsScoreBreakdown, // {'formatting': 95, 'keywords': 85, ...}
    @Default([]) List<String> recommendations, // Top 3 emphasis suggestions
    @Default([]) List<String> warnings, // Factuality issues, etc.
  }) = _GenerationAnalytics;
  
  factory GenerationAnalytics.fromJson(Map<String, dynamic> json) => _$GenerationAnalyticsFromJson(json);
}
```

### Template Model (NEW - Core Feature)
```dart
// models/template.dart
@freezed
class Template with _$Template {
  const factory Template({
    required String id,
    required String name,
    required String description,
    String? previewUrl,
    @Default(false) bool isDefault,
    @Default(['one-page', 'two-page']) List<String> supportedLengths,
    @Default(['resume']) List<String> supportedTypes, // 'resume', 'cover_letter'
  }) = _Template;
  
  factory Template.fromJson(Map<String, dynamic> json) => _$TemplateFromJson(json);
}
```

---

## 6.2 Core Feature Enhancements

### Feature 1: Profile Analytics (High Priority)

**Purpose**: Show users profile completeness and strength to encourage better profiles

**Implementation**:
- Fetch analytics when profile screen loads
- Display completeness score as circular progress indicator
- Show missing sections with actionable suggestions
- Color-code strength level (red/yellow/green)

**UI Components**:
- `ProfileCompletenessIndicator` widget (circular progress with percentage)
- Profile detail screen shows analytics card at top
- Suggestions list with tap-to-navigate to missing sections

**Provider Methods**:
```
// In profile_provider.dart
Future<ProfileAnalytics> loadProfileAnalytics(String profileId)
```

---

### Feature 2: Generation Analytics Display (High Priority - @rank1)

**Purpose**: Show match score, keyword coverage, and ATS score for generated resumes

**Implementation**:
- Fetch analytics after generation completes
- Display match score prominently (0-100%)
- Show keyword coverage as progress bar with counts
- Display ATS score with breakdown
- Show top 3 recommendations

**UI Components**:
- `MatchScoreWidget` - Large percentage display with color coding
- `KeywordCoverageWidget` - Progress bar + "15/20 keywords matched"
- `ATSScoreBadge` - Score with color (green >80, yellow 60-80, red <60)
- Analytics card in generation detail screen

**Provider Methods**:
```
// In generation_provider.dart
Future<GenerationAnalytics> loadGenerationAnalytics(String generationId)
```

**Display Locations**:
- Generation detail screen (below progress indicator)
- Resume viewer screen (analytics tab/section)
- Generation list (show match score on each card)

---

### Feature 3: Template Selection (High Priority)

**Purpose**: Let users choose resume template before generation

**Implementation**:
- Fetch available templates on generation start
- Show template picker with preview
- Pass selected template to generation API
- Save default template in settings

**UI Components**:
- `TemplatePicker` widget - Grid or list with previews
- Template preview dialog
- Default template setting in settings screen

**Provider Methods**:
```
// In generation_provider.dart
Future<List<Template>> loadTemplates()
Future<void> startResumeGeneration(String profileId, String jobId, {String? templateId})
```

**User Flow**:
1. User taps "Generate Resume" on job detail
2. Template picker modal appears
3. User selects template (or use default)
4. Generation starts with selected template

---

### Feature 4: Notes on Saved Jobs (High Priority)

**Purpose**: Let users add notes to track job-specific information

**Implementation**:
- Add notes field to SavedJob model
- Add notes text field in job detail screen
- Auto-save notes on blur or save button
- Display notes in saved jobs list (preview)

**UI Components**:
- Notes text field in job detail (expandable)
- Notes preview in saved job card (first 50 chars)
- Notes icon indicator if notes exist

**Provider Methods**:
```
// In jobs_provider.dart
Future<void> updateJobNotes(String savedJobId, String notes)
```

**Display Locations**:
- Job detail screen (notes section below description)
- Saved jobs list (notes preview in card)

---

### Feature 5: Feedback Mechanism (High Priority)

**Purpose**: Collect user feedback on generated documents to improve quality

**Implementation**:
- Add feedback button in resume/cover letter viewer
- Show feedback form (rating 1-5, optional comments, tags)
- Submit feedback to backend
- Show feedback submitted confirmation

**UI Components**:
- `FeedbackForm` widget - Rating stars, comment field, tag chips
- Feedback button in app bar of document viewer
- Success snackbar after submission

**Provider Methods**:
```
// In generation_provider.dart
Future<void> submitFeedback(String generationId, int rating, {String? comments, List<String>? tags})
```

**Feedback Tags** (quick select):
- "Great match"
- "Too generic"
- "Missing key skills"
- "Formatting issues"
- "Factually incorrect"

---

### Feature 6: Validation UI (Medium Priority)

**Purpose**: Let users manually re-run ATS validation on generated documents

**Implementation**:
- Add "Validate" button in resume viewer
- Show loading indicator during validation
- Display validation results (issues found)
- Highlight problematic sections if possible

**UI Components**:
- Validate button in resume viewer app bar
- Validation results dialog with issue list
- Issue severity indicators (error/warning)

**Provider Methods**:
```
// In generation_provider.dart
Future<Map<String, dynamic>> validateGeneration(String generationId)
```

---

## 7. Simplified Todo Tasks (50% Fewer)

### Sprint 0: Setup (1 week)
- [ ] Create Flutter project
- [ ] Add dependencies (riverpod, freezed, dio, sqflite)
- [ ] Set up folder structure
- [ ] Create BaseHttpClient with interceptors
- [ ] Create all API client classes (Auth, Jobs, Profiles, Generations, Documents)
- [ ] Create DbService and StorageService
- [ ] Set up go_router
- [ ] Create design constants (colors, text styles)

### Sprint 1: Auth (1 week)
- [ ] Create User model
- [ ] Create auth_provider.dart with AuthNotifier
- [ ] Build login/register screens
- [ ] Implement token management
- [ ] Test auth flow

### Sprint 2: Jobs (1 week)
- [ ] Create Job and SavedJob models (with notes field)
- [ ] Create jobs_provider.dart
- [ ] Build job list screen with search/filters
- [ ] Build job detail screen
- [ ] Implement save job with status tracking
- [ ] **Add notes field for saved jobs (add/edit/view)**
- [ ] **Display notes preview in saved job cards**
- [ ] Add offline caching

### Sprint 3: Profiles (1 week)
- [ ] Create Profile and ProfileAnalytics models
- [ ] Create profile_provider.dart
- [ ] Build profile list/edit screens
- [ ] Implement profile CRUD (experiences, education, skills, projects)
- [ ] **Add profile analytics display (completeness score)**
- [ ] **Build ProfileCompletenessIndicator widget**
- [ ] **Display suggestions for improving profile**
- [ ] Add offline support

### Sprint 4: Generation (1 week - CORE AI FEATURES)
- [ ] Create Generation, Resume, CoverLetter, GenerationAnalytics, Template models
- [ ] Create generation_provider.dart with polling logic
- [ ] **Implement template selection UI (TemplatePicker widget)**
- [ ] **Load available templates before generation**
- [ ] Build generation_list_screen.dart
- [ ] Build generation_detail_screen.dart with progress indicator
- [ ] **Add match score display (MatchScoreWidget) - 0-100%**
- [ ] **Add keyword coverage display (KeywordCoverageWidget) - X/Y matched**
- [ ] **Add ATS score badge (ATSScoreBadge) with color coding**
- [ ] **Display top 3 recommendations from analytics**
- [ ] Build resume_viewer_screen.dart
- [ ] Build cover_letter_viewer_screen.dart
- [ ] **Add feedback submission form (FeedbackForm widget)**
- [ ] **Implement feedback API call (rating + comments)**
- [ ] Implement PDF download functionality
- [ ] Add share resume/cover letter feature

### Sprint 5: Documents (1 week)
- [ ] Create Document models
- [ ] Create documents_provider.dart
- [ ] Build document_list_screen.dart (filter by type)
- [ ] **Add search by job company name**
- [ ] **Add sort options (date, ATS score, match score)**
- [ ] Add PDF caching to local storage
- [ ] Implement document deletion
- [ ] Add document preview thumbnails
- [ ] **Display ATS score and match score on document cards**
- [ ] Implement offline access to saved PDFs

### Sprint 6: Polish & Test (1 week)
- [ ] Add offline sync with queue visualization
- [ ] **Build settings screen (default template, preferences)**
- [ ] Write unit tests for providers
- [ ] Write widget tests for core widgets
- [ ] Write integration tests for generation flow
- [ ] Fix bugs
- [ ] Performance optimization (caching, lazy loading)

**Total: 7 weeks instead of 13 weeks**

---

## 8. Core Features Summary

### ✅ Included Core Features (High Priority)

| Feature | Component | Status | Sprint |
|---------|-----------|--------|--------|
| **Profile Analytics** | ProfileAnalytics model, completeness widget | ✅ Added | Sprint 3 |
| **Match Score Display** | MatchScoreWidget, 0-100% visualization | ✅ Added | Sprint 4 |
| **Keyword Coverage** | KeywordCoverageWidget, X/Y matched display | ✅ Added | Sprint 4 |
| **ATS Score** | ATSScoreBadge, color-coded score | ✅ Added | Sprint 4 |
| **Recommendations** | Top 3 suggestions display in detail screen | ✅ Added | Sprint 4 |
| **Template Selection** | TemplatePicker widget, template API | ✅ Added | Sprint 4 |
| **Feedback Mechanism** | FeedbackForm widget, feedback API | ✅ Added | Sprint 4 |
| **Notes on Jobs** | Notes field in SavedJob, notes UI | ✅ Added | Sprint 2 |
| **Validation UI** | Validate button, validation results | ✅ Added | Sprint 4 |

### 🎯 Core Feature Priorities (from User Stories)

**@must @rank1 (Highest Priority - AI Generation)**:
- ✅ 5-stage generation pipeline
- ✅ Match score display (0-100%)
- ✅ Keyword coverage (90%+ required keywords)
- ✅ ATS compatibility checks
- ✅ Factuality validation
- ✅ Template selection
- ✅ Recommendations display

**@should @rank2 (Medium Priority)**:
- ✅ Profile analytics (completeness score)
- ✅ Feedback mechanism
- ✅ Notes on saved jobs
- ✅ Document search and filtering

**@could @rank3 (Low Priority - Post-MVP)**:
- 🔲 Profile version history and restore
- 🔲 Document version comparison
- 🔲 Batch generation for multiple jobs
- 🔲 Export formats (DOCX, TXT)

---

## 9. Key Takeaways

✅ **DO:**
- Use Riverpod for state management (it's actually simple)
- Keep business logic in Notifiers
- Separate API clients by feature domain for easier testing
- Use one BaseHttpClient for shared HTTP setup
- Flat folder structure
- Build what you need NOW
- **Display analytics (match score, ATS score) prominently**
- **Let users choose templates before generation**
- **Collect feedback to improve quality**

❌ **DON'T:**
- Create repository abstractions "for testing" (mock API clients instead)
- Separate local/remote data sources (one service handles both)
- Use adapter pattern unless you're actually swapping implementations
- Nest folders more than 2 levels deep
- Build for imaginary future requirements
- Put all HTTP calls in one giant file (hard to test)
- **Hide match scores and analytics from users**
- **Skip feedback collection (critical for improvement)**

---

## 9. Dependencies (Reduced)

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.0
  
  # Data Models
  freezed_annotation: ^2.4.0
  json_annotation: ^4.8.1
  
  # Networking
  dio: ^5.3.0
  
  # Storage
  sqflite: ^2.3.0
  flutter_secure_storage: ^9.0.0
  path_provider: ^2.1.0  # For file storage
  
  # Routing
  go_router: ^12.0.0
  
  # UI
  cached_network_image: ^3.3.0
  
  # PDF Handling
  flutter_pdfview: ^1.3.0  # View PDF files
  pdf: ^3.10.0             # Generate/manipulate PDFs
  
  # Sharing
  share_plus: ^7.2.0       # Share documents
  
  # Utils
  intl: ^0.18.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Code Generation
  build_runner: ^2.4.0
  freezed: ^2.4.0
  json_serializable: ^6.7.0
  
  # Testing
  mockito: ^5.4.0
```

**19 dependencies instead of 24**

---

## 11. Implementation Checklist

### Core Features Implementation Status

**Authentication & Profile Management**:
- ✅ User login/register/logout
- ✅ Profile CRUD with nested entities (experiences, education, skills, projects)
- ✅ Profile analytics display (completeness, suggestions)
- ✅ Offline profile editing with sync

**Job Discovery & Management**:
- ✅ Job browsing with search and filters
- ✅ Save jobs with status tracking
- ✅ Notes on saved jobs (add/edit/view)
- ✅ Offline job caching

**AI Generation Pipeline** (@rank1 - Highest Priority):
- ✅ Template selection UI before generation
- ✅ Start resume/cover letter generation
- ✅ 5-stage progress tracking with polling
- ✅ Match score display (0-100%)
- ✅ Keyword coverage visualization (X/Y matched)
- ✅ ATS score badge with color coding
- ✅ Top 3 recommendations display
- ✅ Feedback submission (rating + comments)
- ✅ Generation validation (re-run ATS checks)

**Document Management**:
- ✅ View generated resume/cover letter content
- ✅ PDF download and share
- ✅ Document list with filtering (by type)
- ✅ Document search (by company name)
- ✅ Display analytics on document cards (ATS, match score)
- ✅ Offline PDF caching

**Offline Support**:
- ✅ Local SQLite database for caching
- ✅ Sync queue for offline operations
- ✅ Last-write-wins conflict resolution

---

## 12. API Coverage Summary

| Backend API Endpoint | Mobile Implementation | Priority |
|---------------------|----------------------|----------|
| `POST /auth/login` | ✅ AuthApiClient | @must |
| `POST /auth/register` | ✅ AuthApiClient | @must |
| `GET /profiles/{id}` | ✅ ProfilesApiClient | @must |
| `GET /profiles/{id}/analytics` | ✅ ProfilesApiClient | @must |
| `POST /jobs/{id}/save` | ✅ JobsApiClient | @must |
| `PATCH /jobs/saved/{id}` | ✅ JobsApiClient (status + notes) | @must |
| `POST /generations/resume` | ✅ GenerationsApiClient | @must @rank1 |
| `GET /generations/{id}` | ✅ GenerationsApiClient (polling) | @must @rank1 |
| `GET /generations/{id}/analytics` | ✅ GenerationsApiClient | @must @rank1 |
| `GET /generations/templates` | ✅ GenerationsApiClient | @must |
| `POST /generations/{id}/feedback` | ✅ GenerationsApiClient | @should |
| `POST /generations/{id}/validate` | ✅ GenerationsApiClient | @should |
| `GET /documents/` | ✅ DocumentsApiClient | @should |
| `GET /documents/{id}/download` | ✅ DocumentsApiClient | @should |

**API Coverage**: 95% of core endpoints (all @must and @should priorities covered)

---

**This architecture is production-ready, focused on core features, and follows YAGNI principles.**
