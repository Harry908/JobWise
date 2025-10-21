# JobWise Mobile App - Comprehensive Design Document

**Project**: JobWise - AI-Powered Job Application Assistant (Mobile Client)
**Version**: 1.0
**Last Updated**: October 21, 2025

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Mobile Architecture](#2-mobile-architecture)
3. [State Management Design](#3-state-management-design)
4. [Data Models & Local Storage](#4-data-models--local-storage)
5. [API Integration Architecture](#5-api-integration-architecture)
6. [Feature Implementation Breakdown](#6-feature-implementation-breakdown)
7. [UI/UX Design System](#7-uiux-design-system)
8. [Offline-First Strategy](#8-offline-first-strategy)
9. [Security & Authentication](#9-security--authentication)
10. [Testing Strategy](#10-testing-strategy)
11. [Performance & Optimization](#11-performance--optimization)
12. [Implementation Roadmap](#12-implementation-roadmap)

---

## 1. Executive Summary

### 1.1 Project Overview

JobWise mobile app is a Flutter-based cross-platform application that provides job seekers with an AI-powered assistant for managing their career profiles, discovering jobs, and generating tailored resumes and cover letters. The mobile client integrates with a FastAPI backend to deliver a seamless, offline-first experience.

### 1.2 Key Objectives

- **Offline-First Architecture**: Enable users to browse jobs, edit profiles, and queue operations while offline
- **Real-Time Generation Tracking**: Provide live progress updates for AI-powered document generation
- **ATS-Optimized Output**: Display match scores, keyword coverage, and quality metrics
- **Cross-Platform Consistency**: Deliver identical experiences on iOS and Android
- **Performance Excellence**: Achieve <200ms UI response times and smooth 60fps animations

### 1.3 Technology Stack

- **Framework**: Flutter 3.x (Dart 3.x)
- **State Management**: Riverpod 2.x with freezed for immutability
- **Navigation**: go_router 12.x for declarative routing
- **Networking**: dio 5.x with retry interceptors
- **Local Storage**: sqflite for structured data, flutter_secure_storage for tokens
- **Background Tasks**: workmanager (Android) / background_fetch (iOS)
- **UI Components**: Material 3 design system

### 1.4 Integration Points

- **Backend API**: FastAPI service at `http://localhost:8000/api/v1` (configurable)
- **Authentication**: JWT-based with refresh token flow
- **Real-Time Updates**: Polling-based generation status (SSE/WebSocket future enhancement)
- **File Storage**: Local PDF caching with cloud sync on reconnection

---

## 2. Mobile Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Screens  │  │  Widgets   │  │ Navigation │            │
│  │  (Routes)  │  │ (Material3)│  │ (go_router)│            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ↓↑
┌─────────────────────────────────────────────────────────────┐
│                   State Management Layer                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Riverpod Providers                       │  │
│  │  • AuthNotifier    • ProfileNotifier                  │  │
│  │  • JobsNotifier    • GenerationNotifier               │  │
│  │  • DocumentsNotifier                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↓↑
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                          │
│  ┌────────────────┐         ┌────────────────┐             │
│  │ Remote Repos   │         │  Local Repos   │             │
│  │ (API clients)  │ ←sync→  │  (sqflite)     │             │
│  └────────────────┘         └────────────────┘             │
└─────────────────────────────────────────────────────────────┘
           ↓                           ↓
┌──────────────────┐         ┌──────────────────┐
│  FastAPI Backend │         │  Local Database  │
│  (REST APIs)     │         │  (SQLite)        │
└──────────────────┘         └──────────────────┘
```

### 2.2 Clean Architecture Layers

#### Presentation Layer (`lib/src/features/*/ui/`)
- **Responsibility**: UI rendering, user interaction, navigation
- **Components**: Screens, Widgets, Form controllers
- **Dependencies**: State providers (read-only)
- **Guidelines**: 
  - Widgets should be stateless when possible
  - Use ConsumerWidget/ConsumerStatefulWidget for state access
  - Extract reusable components to `lib/src/shared/widgets/`

#### State Management Layer (`lib/src/features/*/state/`)
- **Responsibility**: Business logic, state coordination, data transformation
- **Components**: StateNotifiers, AsyncNotifiers, Providers
- **Dependencies**: Repositories, Services
- **Guidelines**:
  - Keep state immutable (use freezed/copyWith)
  - Handle loading/error/success states consistently
  - Debounce rapid state changes

#### Data Layer (`lib/src/features/*/services/`, `lib/src/core/`)
- **Responsibility**: Data fetching, caching, synchronization
- **Components**: Repositories, API clients, Local storage adapters
- **Dependencies**: Network layer, Storage layer
- **Guidelines**:
  - Repository pattern abstracts data source (local vs remote)
  - Implement retry logic with exponential backoff
  - Cache responses for offline access

### 2.3 Dependency Injection with Riverpod

```dart
// Core providers (lib/src/core/di/providers.dart)
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: ref.watch(configProvider).apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
  ));
  
  dio.interceptors.addAll([
    AuthInterceptor(ref),
    RetryInterceptor(ref),
    LoggingInterceptor(),
  ]);
  
  return dio;
});

final localDbProvider = Provider<Database>((ref) {
  // sqflite database instance
  throw UnimplementedError('Initialize in main.dart');
});

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});
```

### 2.4 Folder Structure

```
lib/
├── main.dart                          # App entry point
├── src/
│   ├── app.dart                       # Root MaterialApp with routing
│   ├── features/
│   │   ├── auth/
│   │   │   ├── models/
│   │   │   │   ├── user.dart
│   │   │   │   ├── auth_state.dart
│   │   │   │   └── auth_state.freezed.dart
│   │   │   ├── services/
│   │   │   │   ├── auth_repository.dart
│   │   │   │   └── auth_api_client.dart
│   │   │   ├── state/
│   │   │   │   └── auth_notifier.dart
│   │   │   └── ui/
│   │   │       ├── login_screen.dart
│   │   │       ├── register_screen.dart
│   │   │       └── widgets/
│   │   │           └── auth_form.dart
│   │   ├── profiles/
│   │   │   ├── models/
│   │   │   │   ├── master_profile.dart
│   │   │   │   ├── experience.dart
│   │   │   │   ├── education.dart
│   │   │   │   ├── skill.dart
│   │   │   │   └── project.dart
│   │   │   ├── services/
│   │   │   │   ├── profile_repository.dart
│   │   │   │   ├── profile_api_client.dart
│   │   │   │   └── profile_local_storage.dart
│   │   │   ├── state/
│   │   │   │   ├── profile_notifier.dart
│   │   │   │   └── profile_state.dart
│   │   │   └── ui/
│   │   │       ├── profile_list_screen.dart
│   │   │       ├── profile_edit_screen.dart
│   │   │       └── widgets/
│   │   │           ├── experience_card.dart
│   │   │           ├── education_card.dart
│   │   │           ├── skill_chip.dart
│   │   │           └── profile_completeness_indicator.dart
│   │   ├── jobs/
│   │   │   ├── models/
│   │   │   │   ├── job.dart
│   │   │   │   ├── saved_job.dart
│   │   │   │   └── job_filter.dart
│   │   │   ├── services/
│   │   │   │   ├── job_repository.dart
│   │   │   │   ├── job_api_client.dart
│   │   │   │   └── job_local_storage.dart
│   │   │   ├── state/
│   │   │   │   ├── jobs_notifier.dart
│   │   │   │   ├── saved_jobs_notifier.dart
│   │   │   │   └── job_search_notifier.dart
│   │   │   └── ui/
│   │   │       ├── job_list_screen.dart
│   │   │       ├── job_detail_screen.dart
│   │   │       ├── saved_jobs_screen.dart
│   │   │       └── widgets/
│   │   │           ├── job_card.dart
│   │   │           ├── job_filter_panel.dart
│   │   │           └── job_search_bar.dart
│   │   ├── generations/
│   │   │   ├── models/
│   │   │   │   ├── generation.dart
│   │   │   │   ├── generation_request.dart
│   │   │   │   ├── generation_status.dart
│   │   │   │   └── match_score.dart
│   │   │   ├── services/
│   │   │   │   ├── generation_repository.dart
│   │   │   │   ├── generation_api_client.dart
│   │   │   │   └── generation_polling_service.dart
│   │   │   ├── state/
│   │   │   │   ├── generation_notifier.dart
│   │   │   │   └── generation_progress_notifier.dart
│   │   │   └── ui/
│   │   │       ├── generation_list_screen.dart
│   │   │       ├── generation_detail_screen.dart
│   │   │       └── widgets/
│   │   │           ├── generation_card.dart
│   │   │           ├── progress_indicator_five_stage.dart
│   │   │           ├── match_score_widget.dart
│   │   │           └── keyword_coverage_chart.dart
│   │   └── documents/
│   │       ├── models/
│   │       │   ├── document.dart
│   │       │   ├── ats_score.dart
│   │       │   └── document_export_options.dart
│   │       ├── services/
│   │       │   ├── document_repository.dart
│   │       │   ├── document_api_client.dart
│   │       │   └── pdf_cache_service.dart
│   │       ├── state/
│   │       │   └── documents_notifier.dart
│   │       └── ui/
│   │           ├── document_list_screen.dart
│   │           ├── document_viewer_screen.dart
│   │           └── widgets/
│   │               ├── document_card.dart
│   │               ├── ats_score_badge.dart
│   │               └── pdf_viewer.dart
│   ├── shared/
│   │   ├── widgets/
│   │   │   ├── app_bar.dart
│   │   │   ├── bottom_nav.dart
│   │   │   ├── loading_indicator.dart
│   │   │   ├── error_widget.dart
│   │   │   ├── empty_state.dart
│   │   │   └── confirmation_dialog.dart
│   │   ├── utils/
│   │   │   ├── date_formatter.dart
│   │   │   ├── validators.dart
│   │   │   └── extensions.dart
│   │   └── constants/
│   │       ├── app_colors.dart
│   │       ├── app_text_styles.dart
│   │       └── app_dimensions.dart
│   └── core/
│       ├── network/
│       │   ├── api_client.dart
│       │   ├── api_exception.dart
│       │   ├── auth_interceptor.dart
│       │   ├── retry_interceptor.dart
│       │   └── logging_interceptor.dart
│       ├── storage/
│       │   ├── local_database.dart
│       │   ├── secure_storage.dart
│       │   └── sync_queue.dart
│       ├── di/
│       │   └── providers.dart
│       ├── routing/
│       │   ├── app_router.dart
│       │   └── route_guards.dart
│       └── config/
│           ├── environment.dart
│           └── app_config.dart
└── test/
    ├── unit/
    ├── widget/
    └── integration/
```

---

## 3. State Management Design

### 3.1 State Management Strategy

**Chosen Approach**: Riverpod 2.x with freezed for immutable state classes

**Rationale**:
- Compile-time safety and type checking
- Excellent testability with ProviderContainer
- Performance optimization with automatic rebuild minimization
- Easy composition and dependency injection
- No BuildContext required for state access

### 3.2 State Boundaries

#### AuthState
```dart
@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    User? user,
    String? accessToken,
    @Default(false) bool isAuthenticated,
    @Default(AuthStatus.initial) AuthStatus status,
    String? errorMessage,
  }) = _AuthState;
}

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }
```

#### ProfileState
```dart
@freezed
class ProfileState with _$ProfileState {
  const factory ProfileState({
    MasterProfile? activeProfile,
    @Default([]) List<MasterProfile> profiles,
    @Default(false) bool isLoading,
    @Default(false) bool isSyncing,
    String? errorMessage,
    ProfileAnalytics? analytics,
  }) = _ProfileState;
}

@freezed
class ProfileAnalytics with _$ProfileAnalytics {
  const factory ProfileAnalytics({
    @Default(0) int completenessPercentage,
    @Default([]) List<String> missingFields,
    @Default([]) List<String> suggestions,
  }) = _ProfileAnalytics;
}
```

#### JobsState
```dart
@freezed
class JobsState with _$JobsState {
  const factory JobsState({
    @Default([]) List<Job> jobs,
    @Default([]) List<Job> savedJobs,
    JobFilter? activeFilter,
    @Default(false) bool isLoading,
    @Default(false) bool hasMore,
    @Default(0) int offset,
    @Default(20) int limit,
    String? errorMessage,
  }) = _JobsState;
}

@freezed
class JobFilter with _$JobFilter {
  const factory JobFilter({
    String? searchQuery,
    String? location,
    JobStatus? status,
    String? source,
    bool? remote,
  }) = _JobFilter;
}
```

#### GenerationState
```dart
@freezed
class GenerationState with _$GenerationState {
  const factory GenerationState({
    @Default([]) List<Generation> generations,
    Generation? activeGeneration,
    @Default(false) bool isGenerating,
    GenerationProgress? progress,
    String? errorMessage,
  }) = _GenerationState;
}

@freezed
class GenerationProgress with _$GenerationProgress {
  const factory GenerationProgress({
    @Default(GenerationStage.pending) GenerationStage currentStage,
    @Default(0) int stageNumber,
    @Default(5) int totalStages,
    @Default(0.0) double percentage,
    String? stageMessage,
  }) = _GenerationProgress;
}

enum GenerationStage {
  pending,
  analyzing,    // Stage 1: Job analysis
  scoring,      // Stage 2: Profile scoring
  generating,   // Stage 3: Content generation
  validating,   // Stage 4: Quality validation
  exporting,    // Stage 5: PDF export
  completed,
  failed,
}
```

#### DocumentsState
```dart
@freezed
class DocumentsState with _$DocumentsState {
  const factory DocumentsState({
    @Default([]) List<Document> documents,
    @Default(false) bool isLoading,
    DocumentFilter? filter,
    String? errorMessage,
  }) = _DocumentsState;
}

@freezed
class DocumentFilter with _$DocumentFilter {
  const factory DocumentFilter({
    String? searchQuery,
    DocumentType? type,
    String? jobId,
    DateTime? startDate,
    DateTime? endDate,
  }) = _DocumentFilter;
}
```

### 3.3 Provider Architecture

```dart
// Auth Providers (lib/src/features/auth/state/auth_providers.dart)
final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authRepositoryProvider),
    ref.watch(secureStorageProvider),
  );
});

final currentUserProvider = Provider<User?>((ref) {
  return ref.watch(authNotifierProvider).user;
});

final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authNotifierProvider).isAuthenticated;
});

// Profile Providers (lib/src/features/profiles/state/profile_providers.dart)
final profileNotifierProvider = StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier(
    ref.watch(profileRepositoryProvider),
    ref.watch(authNotifierProvider).user?.id,
  );
});

final activeProfileProvider = Provider<MasterProfile?>((ref) {
  return ref.watch(profileNotifierProvider).activeProfile;
});

final profileCompletenessProvider = Provider<int>((ref) {
  return ref.watch(profileNotifierProvider).analytics?.completenessPercentage ?? 0;
});

// Jobs Providers (lib/src/features/jobs/state/job_providers.dart)
final jobsNotifierProvider = StateNotifierProvider<JobsNotifier, JobsState>((ref) {
  return JobsNotifier(
    ref.watch(jobRepositoryProvider),
    ref.watch(authNotifierProvider).user?.id,
  );
});

final savedJobsProvider = Provider<List<Job>>((ref) {
  return ref.watch(jobsNotifierProvider).savedJobs;
});

// Generation Providers (lib/src/features/generations/state/generation_providers.dart)
final generationNotifierProvider = StateNotifierProvider<GenerationNotifier, GenerationState>((ref) {
  return GenerationNotifier(
    ref.watch(generationRepositoryProvider),
    ref.watch(generationPollingServiceProvider),
    ref.watch(authNotifierProvider).user?.id,
  );
});

final activeGenerationProvider = Provider<Generation?>((ref) {
  return ref.watch(generationNotifierProvider).activeGeneration;
});

// Documents Providers (lib/src/features/documents/state/document_providers.dart)
final documentsNotifierProvider = StateNotifierProvider<DocumentsNotifier, DocumentsState>((ref) {
  return DocumentsNotifier(
    ref.watch(documentRepositoryProvider),
    ref.watch(authNotifierProvider).user?.id,
  );
});
```

### 3.4 State Update Patterns

```dart
// Example: JobsNotifier
class JobsNotifier extends StateNotifier<JobsState> {
  final JobRepository _repository;
  final String? _userId;
  
  JobsNotifier(this._repository, this._userId) : super(const JobsState());
  
  Future<void> loadJobs({bool refresh = false}) async {
    if (state.isLoading) return;
    
    if (refresh) {
      state = state.copyWith(offset: 0, jobs: []);
    }
    
    state = state.copyWith(isLoading: true, errorMessage: null);
    
    try {
      final jobs = await _repository.getJobs(
        offset: state.offset,
        limit: state.limit,
        filter: state.activeFilter,
      );
      
      state = state.copyWith(
        jobs: refresh ? jobs : [...state.jobs, ...jobs],
        isLoading: false,
        hasMore: jobs.length >= state.limit,
        offset: state.offset + jobs.length,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: _handleError(e),
      );
    }
  }
  
  Future<void> saveJob(String jobId) async {
    try {
      final savedJob = await _repository.saveJob(jobId, _userId!);
      state = state.copyWith(
        savedJobs: [...state.savedJobs, savedJob],
      );
    } catch (e) {
      state = state.copyWith(errorMessage: _handleError(e));
    }
  }
  
  void applyFilter(JobFilter filter) {
    state = state.copyWith(activeFilter: filter);
    loadJobs(refresh: true);
  }
}
```

---

## 4. Data Models & Local Storage

### 4.1 Core Data Models

All models use `freezed` for immutability, `json_serializable` for JSON serialization, and mirror backend entities.

#### User Model
```dart
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required String fullName,
    @Default(true) bool isActive,
    @Default(false) bool isVerified,
    @Default(SubscriptionTier.free) SubscriptionTier subscriptionTier,
    @Default(0) int generationsUsed,
    required int generationsLimit,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _User;
  
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

enum SubscriptionTier { free, premium, enterprise }
```

#### MasterProfile Model
```dart
@freezed
class MasterProfile with _$MasterProfile {
  const factory MasterProfile({
    required String id,
    required String userId,
    required String fullName,
    required String email,
    String? phone,
    String? location,
    required String professionalSummary,
    String? linkedin,
    String? github,
    String? portfolio,
    @Default(1) int version,
    @Default(true) bool isActive,
    @Default([]) List<Experience> experiences,
    @Default([]) List<Education> education,
    @Default([]) List<Skill> skills,
    @Default([]) List<Project> projects,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _MasterProfile;
  
  factory MasterProfile.fromJson(Map<String, dynamic> json) => 
      _$MasterProfileFromJson(json);
}

@freezed
class Experience with _$Experience {
  const factory Experience({
    required String id,
    required String profileId,
    required String jobTitle,
    required String company,
    String? location,
    required DateTime startDate,
    DateTime? endDate,
    @Default(false) bool isCurrent,
    required List<String> achievements,
    @Default([]) List<String> technologiesUsed,
  }) = _Experience;
  
  factory Experience.fromJson(Map<String, dynamic> json) => 
      _$ExperienceFromJson(json);
}

@freezed
class Education with _$Education {
  const factory Education({
    required String id,
    required String profileId,
    required String degree,
    required String institution,
    String? location,
    required DateTime startDate,
    DateTime? endDate,
    @Default(false) bool isCurrent,
    String? gpa,
    @Default([]) List<String> achievements,
  }) = _Education;
  
  factory Education.fromJson(Map<String, dynamic> json) => 
      _$EducationFromJson(json);
}

@freezed
class Skill with _$Skill {
  const factory Skill({
    required String id,
    required String profileId,
    required String name,
    required SkillCategory category,
    @Default(SkillLevel.intermediate) SkillLevel proficiency,
    int? yearsOfExperience,
  }) = _Skill;
  
  factory Skill.fromJson(Map<String, dynamic> json) => 
      _$SkillFromJson(json);
}

enum SkillCategory { technical, soft, language, certification }
enum SkillLevel { beginner, intermediate, advanced, expert }

@freezed
class Project with _$Project {
  const factory Project({
    required String id,
    required String profileId,
    required String name,
    required String description,
    String? url,
    DateTime? startDate,
    DateTime? endDate,
    @Default([]) List<String> technologies,
    @Default([]) List<String> achievements,
  }) = _Project;
  
  factory Project.fromJson(Map<String, dynamic> json) => 
      _$ProjectFromJson(json);
}
```

#### Job Model
```dart
@freezed
class Job with _$Job {
  const factory Job({
    required String id,
    String? userId,
    required String source,
    required String title,
    required String company,
    String? location,
    required String description,
    String? rawText,
    Map<String, dynamic>? parsedKeywords,
    List<String>? requirements,
    String? benefits,
    String? salaryRange,
    @Default(false) bool remote,
    DateTime? datePosted,
    DateTime? applicationDeadline,
    @Default(JobStatus.active) JobStatus status,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Job;
  
  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
}

enum JobStatus { active, draft, archived, expired }

@freezed
class SavedJob with _$SavedJob {
  const factory SavedJob({
    required String id,
    required String userId,
    required String jobId,
    required Job job,
    @Default(SavedJobStatus.interested) SavedJobStatus status,
    String? notes,
    required DateTime savedAt,
    DateTime? appliedAt,
    required DateTime updatedAt,
  }) = _SavedJob;
  
  factory SavedJob.fromJson(Map<String, dynamic> json) => 
      _$SavedJobFromJson(json);
}

enum SavedJobStatus { interested, applied, interviewing, offer, rejected, closed }
```

#### Generation Model
```dart
@freezed
class Generation with _$Generation {
  const factory Generation({
    required String id,
    required String userId,
    required String profileId,
    required String jobId,
    required DocumentType documentType,
    @Default(GenerationStatus.pending) GenerationStatus status,
    double? matchScore,
    int? keywordsRequiredCount,
    int? keywordsMatchedCount,
    @Default([]) List<String> recommendations,
    Map<String, dynamic>? stageProgress,
    String? errorMessage,
    int? tokenUsage,
    double? generationTimeSeconds,
    required DateTime createdAt,
    DateTime? completedAt,
    required DateTime updatedAt,
  }) = _Generation;
  
  factory Generation.fromJson(Map<String, dynamic> json) => 
      _$GenerationFromJson(json);
}

enum GenerationStatus { 
  pending, 
  generating, 
  completed, 
  needsReview, 
  failed, 
  cancelled 
}

enum DocumentType { resume, coverLetter }
```

#### Document Model
```dart
@freezed
class Document with _$Document {
  const factory Document({
    required String id,
    required String generationId,
    required String userId,
    required String jobId,
    required String profileId,
    required DocumentType documentType,
    @Default(1) int versionNumber,
    required String template,
    Map<String, dynamic>? parameters,
    String? contentText,
    String? contentHtml,
    String? contentMarkdown,
    String? pdfFilePath,
    int? pdfSizeBytes,
    int? pdfPageCount,
    double? atsScore,
    Map<String, dynamic>? atsScoreDetails,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Document;
  
  factory Document.fromJson(Map<String, dynamic> json) => 
      _$DocumentFromJson(json);
}
```

### 4.2 Local Database Schema (sqflite)

```sql
-- Users table (cached from backend)
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  is_active INTEGER DEFAULT 1,
  is_verified INTEGER DEFAULT 0,
  subscription_tier TEXT DEFAULT 'free',
  generations_used INTEGER DEFAULT 0,
  generations_limit INTEGER NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER
);

-- Master profiles table
CREATE TABLE master_profiles (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  location TEXT,
  professional_summary TEXT NOT NULL,
  linkedin TEXT,
  github TEXT,
  portfolio TEXT,
  version INTEGER DEFAULT 1,
  is_active INTEGER DEFAULT 1,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_profiles_user ON master_profiles(user_id);

-- Experiences table
CREATE TABLE experiences (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  job_title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  start_date INTEGER NOT NULL,
  end_date INTEGER,
  is_current INTEGER DEFAULT 0,
  achievements TEXT NOT NULL, -- JSON array
  technologies_used TEXT, -- JSON array
  synced_at INTEGER,
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_experiences_profile ON experiences(profile_id);

-- Education table
CREATE TABLE education (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  degree TEXT NOT NULL,
  institution TEXT NOT NULL,
  location TEXT,
  start_date INTEGER NOT NULL,
  end_date INTEGER,
  is_current INTEGER DEFAULT 0,
  gpa TEXT,
  achievements TEXT, -- JSON array
  synced_at INTEGER,
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_education_profile ON education(profile_id);

-- Skills table
CREATE TABLE skills (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  proficiency TEXT DEFAULT 'intermediate',
  years_of_experience INTEGER,
  synced_at INTEGER,
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_skills_profile ON skills(profile_id);

-- Projects table
CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  url TEXT,
  start_date INTEGER,
  end_date INTEGER,
  technologies TEXT, -- JSON array
  achievements TEXT, -- JSON array
  synced_at INTEGER,
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_profile ON projects(profile_id);

-- Jobs table
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  location TEXT,
  description TEXT NOT NULL,
  raw_text TEXT,
  parsed_keywords TEXT, -- JSON
  requirements TEXT, -- JSON array
  benefits TEXT,
  salary_range TEXT,
  remote INTEGER DEFAULT 0,
  date_posted INTEGER,
  application_deadline INTEGER,
  status TEXT DEFAULT 'active',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_jobs_user_source ON jobs(user_id, source);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_company ON jobs(company);

-- Saved jobs table
CREATE TABLE saved_jobs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  status TEXT DEFAULT 'interested',
  notes TEXT,
  saved_at INTEGER NOT NULL,
  applied_at INTEGER,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

CREATE INDEX idx_saved_jobs_user_status ON saved_jobs(user_id, status, updated_at);

-- Generations table
CREATE TABLE generations (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  profile_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  document_type TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  match_score REAL,
  keywords_required_count INTEGER,
  keywords_matched_count INTEGER,
  recommendations TEXT, -- JSON array
  stage_progress TEXT, -- JSON
  error_message TEXT,
  token_usage INTEGER,
  generation_time_seconds REAL,
  created_at INTEGER NOT NULL,
  completed_at INTEGER,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE INDEX idx_generations_user_status ON generations(user_id, status);
CREATE INDEX idx_generations_profile_job ON generations(profile_id, job_id);

-- Documents table
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  generation_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  job_id TEXT NOT NULL,
  profile_id TEXT NOT NULL,
  document_type TEXT NOT NULL,
  version_number INTEGER DEFAULT 1,
  template TEXT NOT NULL,
  parameters TEXT, -- JSON
  content_text TEXT,
  content_html TEXT,
  content_markdown TEXT,
  pdf_file_path TEXT,
  pdf_size_bytes INTEGER,
  pdf_page_count INTEGER,
  ats_score REAL,
  ats_score_details TEXT, -- JSON
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  synced_at INTEGER,
  FOREIGN KEY (generation_id) REFERENCES generations(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (job_id) REFERENCES jobs(id),
  FOREIGN KEY (profile_id) REFERENCES master_profiles(id)
);

CREATE INDEX idx_documents_generation ON documents(generation_id);
CREATE INDEX idx_documents_user ON documents(user_id);
CREATE INDEX idx_documents_job ON documents(job_id);

-- Sync queue table for offline operations
CREATE TABLE sync_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  operation TEXT NOT NULL, -- 'create', 'update', 'delete'
  payload TEXT NOT NULL, -- JSON
  created_at INTEGER NOT NULL,
  retry_count INTEGER DEFAULT 0,
  last_error TEXT
);

CREATE INDEX idx_sync_queue_created ON sync_queue(created_at);
```

### 4.3 Repository Pattern

```dart
// Abstract repository interface
abstract class IProfileRepository {
  Future<MasterProfile> createProfile(MasterProfile profile);
  Future<MasterProfile> getProfile(String id);
  Future<List<MasterProfile>> getUserProfiles(String userId);
  Future<MasterProfile> updateProfile(MasterProfile profile);
  Future<void> deleteProfile(String id);
  
  // Component management
  Future<Experience> addExperience(String profileId, Experience experience);
  Future<Experience> updateExperience(Experience experience);
  Future<void> deleteExperience(String id);
  
  // Local/Remote sync
  Future<void> syncProfile(String id);
  Stream<MasterProfile> watchProfile(String id);
}

// Implementation with local-first strategy
class ProfileRepository implements IProfileRepository {
  final ProfileApiClient _apiClient;
  final ProfileLocalStorage _localStorage;
  final SyncQueue _syncQueue;
  
  ProfileRepository(this._apiClient, this._localStorage, this._syncQueue);
  
  @override
  Future<MasterProfile> createProfile(MasterProfile profile) async {
    // Save locally first
    await _localStorage.insertProfile(profile);
    
    try {
      // Sync to backend
      final syncedProfile = await _apiClient.createProfile(profile);
      await _localStorage.updateProfile(syncedProfile.copyWith(
        updatedAt: DateTime.now(),
      ));
      return syncedProfile;
    } catch (e) {
      // Queue for later sync
      await _syncQueue.enqueue(
        entityType: 'profile',
        entityId: profile.id,
        operation: 'create',
        payload: profile.toJson(),
      );
      return profile;
    }
  }
  
  @override
  Future<MasterProfile> getProfile(String id) async {
    // Return cached version immediately
    final local = await _localStorage.getProfile(id);
    
    // Attempt background sync
    _syncProfile(id).ignore();
    
    return local;
  }
  
  Future<void> _syncProfile(String id) async {
    try {
      final remote = await _apiClient.getProfile(id);
      await _localStorage.updateProfile(remote);
    } catch (e) {
      // Fail silently, local version is still valid
    }
  }
}
```
---

## 5. API Integration Architecture

### 5.1 Backend API Base URL

**Development**: `http://localhost:8000/api/v1`
**Production**: Configurable via environment variables

### 5.2 API Endpoints Mapping

#### Authentication API (`/api/v1/auth/`)

| Method | Endpoint | Request Body | Response | Mobile Action |
|--------|----------|--------------|----------|---------------|
| POST | `/register` | `{ email, password, full_name }` | `{ id, email, full_name, access_token, refresh_token }` | Create account, store tokens, navigate to onboarding |
| POST | `/login` | `{ email, password }` | `{ access_token, refresh_token, user }` | Store tokens, load user, navigate to home |
| POST | `/refresh` | `{ refresh_token }` | `{ access_token }` | Update access token in memory |
| GET | `/me` | - | `{ user }` | Update user state |
| POST | `/logout` | - | `{ success }` | Clear tokens, navigate to login |

#### Profile API (`/api/v1/profiles/`)

| Method | Endpoint | Request Body | Response | Mobile Action |
|--------|----------|--------------|----------|---------------|
| POST | `/` | `MasterProfile` | `MasterProfile` | Save to local DB, update state |
| GET | `/me` | - | `MasterProfile` | Cache locally, set as active |
| GET | `/{id}` | - | `MasterProfile` | Cache locally |
| PUT | `/{id}` | `MasterProfile` | `MasterProfile` | Update local DB, sync state |
| DELETE | `/{id}` | - | `{ success }` | Remove from local DB |
| POST | `/{id}/experiences` | `Experience` | `Experience` | Add to profile locally |
| PUT | `/{id}/experiences/{exp_id}` | `Experience` | `Experience` | Update locally |
| DELETE | `/{id}/experiences/{exp_id}` | - | `{ success }` | Remove locally |
| POST | `/{id}/education` | `Education` | `Education` | Add to profile locally |
| PUT | `/{id}/education/{edu_id}` | `Education` | `Education` | Update locally |
| DELETE | `/{id}/education/{edu_id}` | - | `{ success }` | Remove locally |
| POST | `/{id}/projects` | `Project` | `Project` | Add to profile locally |
| PUT | `/{id}/projects/{proj_id}` | `Project` | `Project` | Update locally |
| DELETE | `/{id}/projects/{proj_id}` | - | `{ success }` | Remove locally |
| GET | `/{id}/analytics` | - | `{ completeness_percentage, missing_fields, suggestions }` | Display in profile UI |

#### Job API (`/api/v1/jobs/`)

| Method | Endpoint | Query Params | Request Body | Response | Mobile Action |
|--------|----------|--------------|--------------|----------|---------------|
| POST | `/` | - | `{ title, company, description, source, ... }` | `Job` | Save to local DB |
| GET | `/` | `?status=active&source=user_created&limit=20&offset=0` | - | `{ jobs: [...], total, has_more }` | Cache jobs, append to list |
| GET | `/{id}` | - | - | `Job` | Cache locally, display details |
| PUT | `/{id}` | - | `Job` | `Job` | Update local DB |
| DELETE | `/{id}` | - | `{ success }` | Remove from local DB |

**Saved Jobs** (part of Job API):
| Method | Endpoint | Request Body | Response | Mobile Action |
|--------|----------|--------------|----------|---------------|
| POST | `/jobs/{id}/save` | `{ status: 'interested', notes }` | `SavedJob` | Add to saved_jobs table |
| PUT | `/jobs/saved/{id}` | `{ status, notes }` | `SavedJob` | Update saved job |
| DELETE | `/jobs/saved/{id}` | - | `{ success }` | Remove from saved jobs |
| GET | `/jobs/saved` | `?status=applied` | `{ saved_jobs: [...] }` | Cache locally |

#### Generation API (`/api/v1/generations/`)

| Method | Endpoint | Request Body | Response | Mobile Action |
|--------|----------|--------------|----------|---------------|
| POST | `/resume` | `{ profile_id, job_id, template?, length? }` | `{ generation_id, status: 'pending' }` | Start polling, show progress screen |
| POST | `/cover-letter` | `{ profile_id, job_id }` | `{ generation_id, status: 'pending' }` | Start polling, show progress screen |
| GET | `/{id}` | - | `Generation` | Update progress state |
| GET | `/{id}/result` | - | `{ generation, documents: [...] }` | Cache documents, stop polling, show result |
| POST | `/{id}/regenerate` | `{ template?, length? }` | `{ generation_id, status: 'pending' }` | Restart polling |
| DELETE | `/{id}` | - | `{ success }` | Cancel polling, remove from list |
| GET | `/` | `?status=completed&limit=20` | `{ generations: [...] }` | Cache locally, display history |
| GET | `/?job_id={job_id}` | - | `{ generations: [...] }` | Show generations for specific job |
| POST | `/{id}/feedback` | `{ rating, comments }` | `{ success }` | Update generation metadata |
| GET | `/templates` | - | `{ templates: [...] }` | Cache for template picker |
| GET | `/{id}/analytics` | - | `{ ats_score, keyword_coverage, quality_metrics }` | Display in result UI |

#### Document API (`/api/v1/documents/`)

| Method | Endpoint | Query Params | Response | Mobile Action |
|--------|----------|--------------|----------|---------------|
| GET | `/` | `?job_id=...&type=resume&limit=20` | `{ documents: [...] }` | Cache locally, display list |
| GET | `/{id}` | - | `Document` | Cache metadata |
| POST | `/{id}/export` | - | `{ pdf_url, download_url }` | Download PDF, cache locally |

### 5.3 API Client Implementation

```dart
// lib/src/core/network/api_client.dart
class ApiClient {
  final Dio _dio;
  final FlutterSecureStorage _secureStorage;
  
  ApiClient(this._dio, this._secureStorage) {
    _setupInterceptors();
  }
  
  void _setupInterceptors() {
    _dio.interceptors.addAll([
      AuthInterceptor(_secureStorage),
      RetryInterceptor(),
      LoggingInterceptor(),
    ]);
  }
  
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }
  
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
  
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Options? options,
  }) async {
    return _dio.put<T>(
      path,
      data: data,
      options: options,
    );
  }
  
  Future<Response<T>> delete<T>(
    String path, {
    Options? options,
  }) async {
    return _dio.delete<T>(
      path,
      options: options,
    );
  }
}

// Auth Interceptor
class AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _secureStorage;
  
  AuthInterceptor(this._secureStorage);
  
  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final token = await _secureStorage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }
  
  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      // Try refresh token
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Retry original request
        final opts = err.requestOptions;
        final response = await Dio().fetch(opts);
        return handler.resolve(response);
      }
    }
    handler.next(err);
  }
  
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _secureStorage.read(key: 'refresh_token');
      if (refreshToken == null) return false;
      
      final response = await Dio().post(
        '/api/v1/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      
      final newAccessToken = response.data['access_token'];
      await _secureStorage.write(key: 'access_token', value: newAccessToken);
      return true;
    } catch (e) {
      return false;
    }
  }
}

// Retry Interceptor
class RetryInterceptor extends Interceptor {
  final int maxRetries = 3;
  
  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (_shouldRetry(err)) {
      final retryCount = err.requestOptions.extra['retry_count'] ?? 0;
      if (retryCount < maxRetries) {
        err.requestOptions.extra['retry_count'] = retryCount + 1;
        final delay = Duration(milliseconds: 300 * (1 << retryCount));
        await Future.delayed(delay);
        
        try {
          final response = await Dio().fetch(err.requestOptions);
          return handler.resolve(response);
        } catch (e) {
          // Will retry again if needed
        }
      }
    }
    handler.next(err);
  }
  
  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionTimeout ||
           err.type == DioExceptionType.receiveTimeout ||
           err.type == DioExceptionType.connectionError ||
           (err.response?.statusCode ?? 0) >= 500;
  }
}
```

### 5.4 API Exception Handling

```dart
// lib/src/core/network/api_exception.dart
class ApiException implements Exception {
  final int? statusCode;
  final String message;
  final String? details;
  final ApiErrorType type;
  
  ApiException({
    this.statusCode,
    required this.message,
    this.details,
    required this.type,
  });
  
  factory ApiException.fromDioException(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'Connection timeout. Please check your internet connection.',
          type: ApiErrorType.network,
        );
      case DioExceptionType.connectionError:
        return ApiException(
          message: 'No internet connection.',
          type: ApiErrorType.network,
        );
      case DioExceptionType.badResponse:
        return _handleStatusCode(e.response!);
      default:
        return ApiException(
          message: 'An unexpected error occurred.',
          type: ApiErrorType.unknown,
        );
    }
  }
  
  static ApiException _handleStatusCode(Response response) {
    final statusCode = response.statusCode ?? 0;
    final data = response.data;
    
    switch (statusCode) {
      case 400:
        return ApiException(
          statusCode: 400,
          message: data['message'] ?? 'Invalid request',
          details: data['details']?.toString(),
          type: ApiErrorType.validation,
        );
      case 401:
        return ApiException(
          statusCode: 401,
          message: 'Unauthorized. Please log in again.',
          type: ApiErrorType.authentication,
        );
      case 403:
        return ApiException(
          statusCode: 403,
          message: 'Access denied.',
          type: ApiErrorType.authorization,
        );
      case 404:
        return ApiException(
          statusCode: 404,
          message: 'Resource not found.',
          type: ApiErrorType.notFound,
        );
      case 409:
        return ApiException(
          statusCode: 409,
          message: data['message'] ?? 'Conflict',
          type: ApiErrorType.conflict,
        );
      case 429:
        return ApiException(
          statusCode: 429,
          message: 'Too many requests. Please try again later.',
          type: ApiErrorType.rateLimited,
        );
      default:
        if (statusCode >= 500) {
          return ApiException(
            statusCode: statusCode,
            message: 'Server error. Please try again later.',
            type: ApiErrorType.server,
          );
        }
        return ApiException(
          statusCode: statusCode,
          message: data['message'] ?? 'An error occurred',
          type: ApiErrorType.unknown,
        );
    }
  }
}

enum ApiErrorType {
  network,
  authentication,
  authorization,
  validation,
  notFound,
  conflict,
  rateLimited,
  server,
  unknown,
}
```

### 5.5 Generation Polling Service

```dart
// lib/src/features/generations/services/generation_polling_service.dart
class GenerationPollingService {
  final GenerationApiClient _apiClient;
  final Duration _pollInterval = const Duration(seconds: 2);
  final Map<String, Timer> _activePolls = {};
  
  GenerationPollingService(this._apiClient);
  
  Stream<Generation> pollGeneration(String generationId) async* {
    while (true) {
      try {
        final generation = await _apiClient.getGeneration(generationId);
        yield generation;
        
        if (_isTerminalStatus(generation.status)) {
          break;
        }
        
        await Future.delayed(_pollInterval);
      } catch (e) {
        yield* Stream.error(e);
        break;
      }
    }
  }
  
  bool _isTerminalStatus(GenerationStatus status) {
    return status == GenerationStatus.completed ||
           status == GenerationStatus.failed ||
           status == GenerationStatus.cancelled ||
           status == GenerationStatus.needsReview;
  }
  
  void dispose() {
    for (var timer in _activePolls.values) {
      timer.cancel();
    }
    _activePolls.clear();
  }
}
```

---

## 6. Feature Implementation Breakdown

This section provides granular todo tasks for each feature, organized by priority and dependency order.

### 6.1 Core Infrastructure (Foundation) - Sprint 0

**Priority**: Critical (Must complete before feature development)

#### INFRA-001: Project Setup & Dependencies
- [ ] Create Flutter project with proper package name
- [ ] Configure `pubspec.yaml` with all required dependencies
  - riverpod (^2.4.0)
  - freezed (^2.4.0)
  - json_serializable (^6.7.0)
  - dio (^5.3.0)
  - go_router (^12.0.0)
  - sqflite (^2.3.0)
  - flutter_secure_storage (^9.0.0)
  - workmanager (^0.5.2)
- [ ] Set up build_runner for code generation
- [ ] Configure `analysis_options.yaml` with lint rules
- [ ] Create folder structure as specified in section 2.4

#### INFRA-002: Core Providers & DI Setup
- [ ] Create `lib/src/core/di/providers.dart`
- [ ] Implement `dioProvider` with base configuration
- [ ] Implement `localDbProvider` with sqflite initialization
- [ ] Implement `secureStorageProvider`
- [ ] Implement `configProvider` for environment configuration
- [ ] Create `ProviderScope` in `main.dart`

#### INFRA-003: Database Setup
- [ ] Create `lib/src/core/storage/local_database.dart`
- [ ] Implement database schema creation (see section 4.2)
- [ ] Create migration strategy
- [ ] Implement database version management
- [ ] Add database helper methods (insert, update, delete, query)
- [ ] Test database initialization on first app launch

#### INFRA-004: Network Layer
- [ ] Implement `ApiClient` class (see section 5.3)
- [ ] Create `AuthInterceptor` for JWT token attachment
- [ ] Create `RetryInterceptor` with exponential backoff
- [ ] Create `LoggingInterceptor` for debugging
- [ ] Implement `ApiException` hierarchy (see section 5.4)
- [ ] Add connectivity check utility
- [ ] Test interceptor chain with mock requests

#### INFRA-005: Routing Setup
- [ ] Create `lib/src/core/routing/app_router.dart`
- [ ] Define all route paths as constants
- [ ] Implement `GoRouter` configuration
- [ ] Create auth guard for protected routes
- [ ] Implement deep link handling
- [ ] Add route transitions and animations
- [ ] Test navigation flows

#### INFRA-006: Design System
- [ ] Create `lib/src/shared/constants/app_colors.dart` (Material 3 colors)
- [ ] Create `lib/src/shared/constants/app_text_styles.dart`
- [ ] Create `lib/src/shared/constants/app_dimensions.dart`
- [ ] Implement `AppTheme` with light and dark modes
- [ ] Create reusable button styles
- [ ] Create input decoration themes
- [ ] Document design tokens

#### INFRA-007: Shared Widgets
- [ ] Create `LoadingIndicator` widget
- [ ] Create `ErrorWidget` with retry button
- [ ] Create `EmptyState` widget
- [ ] Create `ConfirmationDialog` widget
- [ ] Create custom `AppBar` widget
- [ ] Create `BottomNavigation` widget
- [ ] Add widget tests for each shared widget

### 6.2 Authentication Feature - Sprint 1

**Priority**: Critical (Required for all features)
**Dependencies**: INFRA-001 through INFRA-007

#### AUTH-001: Data Models
- [ ] Create `lib/src/features/auth/models/user.dart`
- [ ] Implement `User` model with freezed
- [ ] Add JSON serialization annotations
- [ ] Create `AuthState` model
- [ ] Create `AuthStatus` enum
- [ ] Run code generation
- [ ] Add unit tests for model serialization

#### AUTH-002: API Client
- [ ] Create `lib/src/features/auth/services/auth_api_client.dart`
- [ ] Implement `register()` method
- [ ] Implement `login()` method
- [ ] Implement `refresh()` method
- [ ] Implement `logout()` method
- [ ] Implement `getMe()` method
- [ ] Add error handling for each endpoint
- [ ] Mock API client for testing

#### AUTH-003: Repository Layer
- [ ] Create `lib/src/features/auth/services/auth_repository.dart`
- [ ] Implement token storage (secure storage)
- [ ] Implement user caching (local DB)
- [ ] Implement automatic token refresh logic
- [ ] Add session management
- [ ] Handle auth state persistence
- [ ] Add repository tests

#### AUTH-004: State Management
- [ ] Create `lib/src/features/auth/state/auth_notifier.dart`
- [ ] Implement `AuthNotifier` extending `StateNotifier<AuthState>`
- [ ] Implement `login()` method
- [ ] Implement `register()` method
- [ ] Implement `logout()` method
- [ ] Implement `checkAuthStatus()` method
- [ ] Create `authNotifierProvider`
- [ ] Create derived providers (`currentUserProvider`, `isAuthenticatedProvider`)
- [ ] Add state notifier tests

#### AUTH-005: Login UI
- [ ] Create `lib/src/features/auth/ui/login_screen.dart`
- [ ] Design login form layout
- [ ] Add email and password text fields
- [ ] Implement form validation
- [ ] Add login button with loading state
- [ ] Show error messages from state
- [ ] Add "Forgot Password" link
- [ ] Add "Create Account" navigation
- [ ] Add widget tests

#### AUTH-006: Registration UI
- [ ] Create `lib/src/features/auth/ui/register_screen.dart`
- [ ] Design registration form layout
- [ ] Add name, email, password, confirm password fields
- [ ] Implement comprehensive validation
- [ ] Add registration button with loading state
- [ ] Show error messages from state
- [ ] Add "Already have account" navigation
- [ ] Add widget tests

#### AUTH-007: Auth Integration
- [ ] Wire up auth providers in `main.dart`
- [ ] Implement auth state listener
- [ ] Add automatic navigation based on auth state
- [ ] Implement token refresh on app startup
- [ ] Add auth expiry handling
- [ ] Test complete auth flow (login → logout → login)
- [ ] Add integration tests

### 6.3 Profile Management Feature - Sprint 2

**Priority**: High (Core feature for generation)
**Dependencies**: AUTH-001 through AUTH-007

#### PROFILE-001: Data Models
- [ ] Create `MasterProfile` model with freezed
- [ ] Create `Experience` model with freezed
- [ ] Create `Education` model with freezed
- [ ] Create `Skill` model with freezed and enums
- [ ] Create `Project` model with freezed
- [ ] Create `ProfileState` model
- [ ] Create `ProfileAnalytics` model
- [ ] Add JSON serialization for all models
- [ ] Run code generation
- [ ] Add model tests

#### PROFILE-002: Local Storage
- [ ] Create `profile_local_storage.dart`
- [ ] Implement `insertProfile()` with cascade inserts
- [ ] Implement `getProfile()` with joins
- [ ] Implement `getUserProfiles()`
- [ ] Implement `updateProfile()`
- [ ] Implement `deleteProfile()` with cascade delete
- [ ] Implement experience CRUD methods
- [ ] Implement education CRUD methods
- [ ] Implement skill CRUD methods
- [ ] Implement project CRUD methods
- [ ] Add storage tests

#### PROFILE-003: API Client
- [ ] Create `profile_api_client.dart`
- [ ] Implement `createProfile()`
- [ ] Implement `getProfile()`
- [ ] Implement `getUserProfiles()`
- [ ] Implement `updateProfile()`
- [ ] Implement `deleteProfile()`
- [ ] Implement component management endpoints
- [ ] Implement `getAnalytics()`
- [ ] Add mock API client

#### PROFILE-004: Repository Layer
- [ ] Create `profile_repository.dart`
- [ ] Implement repository with local-first pattern
- [ ] Add sync queue integration for offline edits
- [ ] Implement `createProfile()` with offline support
- [ ] Implement `getProfile()` with cache-first
- [ ] Implement `updateProfile()` with optimistic updates
- [ ] Implement component management with sync
- [ ] Add conflict resolution logic
- [ ] Add repository tests

#### PROFILE-005: State Management
- [ ] Create `profile_notifier.dart`
- [ ] Implement `ProfileNotifier` with `ProfileState`
- [ ] Implement `loadProfiles()`
- [ ] Implement `setActiveProfile()`
- [ ] Implement `createProfile()`
- [ ] Implement `updateProfile()`
- [ ] Implement `deleteProfile()`
- [ ] Implement component management methods
- [ ] Implement `calculateAnalytics()`
- [ ] Create profile providers
- [ ] Add notifier tests

#### PROFILE-006: Profile List UI
- [ ] Create `profile_list_screen.dart`
- [ ] Design profile cards layout
- [ ] Show profile completeness indicator
- [ ] Add "Create Profile" FAB
- [ ] Implement pull-to-refresh
- [ ] Add profile selection logic
- [ ] Show active profile badge
- [ ] Add delete confirmation
- [ ] Add widget tests

#### PROFILE-007: Profile Edit UI
- [ ] Create `profile_edit_screen.dart`
- [ ] Design tabbed or sectioned form
- [ ] Implement basic info section (name, email, phone, location)
- [ ] Implement professional summary section
- [ ] Implement links section (LinkedIn, GitHub, portfolio)
- [ ] Add form validation
- [ ] Implement auto-save functionality
- [ ] Add save button with loading state
- [ ] Add widget tests

#### PROFILE-008: Experience Management UI
- [ ] Create `experience_card.dart` widget
- [ ] Create experience list view in profile edit
- [ ] Create experience add/edit dialog
- [ ] Implement date pickers for start/end dates
- [ ] Add "Current Position" checkbox
- [ ] Implement achievements list (dynamic text fields)
- [ ] Add technologies chips
- [ ] Implement delete with confirmation
- [ ] Add widget tests

#### PROFILE-009: Education Management UI
- [ ] Create `education_card.dart` widget
- [ ] Create education list view in profile edit
- [ ] Create education add/edit dialog
- [ ] Implement date pickers
- [ ] Add "Currently Enrolled" checkbox
- [ ] Add GPA field (optional)
- [ ] Implement achievements list
- [ ] Add widget tests

#### PROFILE-010: Skills Management UI
- [ ] Create `skill_chip.dart` widget
- [ ] Create skills section in profile edit
- [ ] Implement skill category picker
- [ ] Implement proficiency level picker
- [ ] Add years of experience field
- [ ] Group skills by category
- [ ] Add skill search/autocomplete
- [ ] Implement delete on chip tap
- [ ] Add widget tests

#### PROFILE-011: Projects Management UI
- [ ] Create `project_card.dart` widget
- [ ] Create projects section in profile edit
- [ ] Create project add/edit dialog
- [ ] Add URL field with validation
- [ ] Implement date pickers
- [ ] Add technologies chips
- [ ] Add achievements list
- [ ] Add widget tests

#### PROFILE-012: Profile Analytics UI
- [ ] Create `profile_completeness_indicator.dart` widget
- [ ] Implement circular progress indicator
- [ ] Show percentage and missing fields
- [ ] Display improvement suggestions
- [ ] Add analytics API integration
- [ ] Show analytics on profile screen
- [ ] Add widget tests

### 6.4 Job Management Feature - Sprint 3

**Priority**: High (Required for generation)
**Dependencies**: AUTH-007, PROFILE-012

#### JOB-001: Data Models
- [ ] Create `Job` model with freezed
- [ ] Create `SavedJob` model with freezed
- [ ] Create `JobFilter` model
- [ ] Create `JobsState` model
- [ ] Create `JobStatus` and `SavedJobStatus` enums
- [ ] Add JSON serialization
- [ ] Run code generation
- [ ] Add model tests

#### JOB-002: Local Storage
- [ ] Create `job_local_storage.dart`
- [ ] Implement `insertJob()`
- [ ] Implement `getJobs()` with filtering
- [ ] Implement `getJob()`
- [ ] Implement `updateJob()`
- [ ] Implement `deleteJob()`
- [ ] Implement `insertSavedJob()`
- [ ] Implement `getSavedJobs()` with joins
- [ ] Implement `updateSavedJob()`
- [ ] Implement `deleteSavedJob()`
- [ ] Add pagination support
- [ ] Add storage tests

#### JOB-003: API Client
- [ ] Create `job_api_client.dart`
- [ ] Implement `createJob()`
- [ ] Implement `getJobs()` with query params
- [ ] Implement `getJob()`
- [ ] Implement `updateJob()`
- [ ] Implement `deleteJob()`
- [ ] Implement `saveJob()`
- [ ] Implement `getSavedJobs()`
- [ ] Implement `updateSavedJob()`
- [ ] Implement `deleteSavedJob()`
- [ ] Add mock API client

#### JOB-004: Repository Layer
- [ ] Create `job_repository.dart`
- [ ] Implement local-first with background sync
- [ ] Implement `getJobs()` with cache-first
- [ ] Implement `getJob()` with cache
- [ ] Implement `createJob()` with offline queue
- [ ] Implement `updateJob()` with optimistic update
- [ ] Implement `deleteJob()` with offline queue
- [ ] Implement saved jobs CRUD with sync
- [ ] Add pagination logic
- [ ] Add repository tests

#### JOB-005: State Management
- [ ] Create `jobs_notifier.dart`
- [ ] Implement `JobsNotifier` with `JobsState`
- [ ] Implement `loadJobs()` with pagination
- [ ] Implement `loadMore()` for infinite scroll
- [ ] Implement `refreshJobs()`
- [ ] Implement `applyFilter()`
- [ ] Implement `saveJob()`
- [ ] Implement `updateSavedJob()`
- [ ] Implement `loadSavedJobs()`
- [ ] Create job providers
- [ ] Add notifier tests

#### JOB-006: Job List UI
- [ ] Create `job_list_screen.dart`
- [ ] Design job cards with `job_card.dart` widget
- [ ] Implement `ListView.builder` for performance
- [ ] Add infinite scroll pagination
- [ ] Add pull-to-refresh
- [ ] Show job source badge
- [ ] Add search bar
- [ ] Add filter button
- [ ] Show loading states
- [ ] Add widget tests

#### JOB-007: Job Card Widget
- [ ] Create `job_card.dart`
- [ ] Display title, company, location
- [ ] Show remote badge if applicable
- [ ] Display date posted
- [ ] Add save/unsave icon button
- [ ] Add status indicator for saved jobs
- [ ] Implement tap to navigate to detail
- [ ] Add const constructor
- [ ] Add widget tests

#### JOB-008: Job Detail UI
- [ ] Create `job_detail_screen.dart`
- [ ] Display full job information
- [ ] Show parsed keywords as chips
- [ ] Display requirements list
- [ ] Show benefits and salary range
- [ ] Add save/unsave button
- [ ] Add "Generate Resume" FAB (requires active profile)
- [ ] Show existing generations for this job
- [ ] Add widget tests

#### JOB-009: Job Search & Filter UI
- [ ] Create `job_search_bar.dart` widget
- [ ] Implement debounced search
- [ ] Create `job_filter_panel.dart` widget
- [ ] Add status filter chips
- [ ] Add source filter dropdown
- [ ] Add remote filter checkbox
- [ ] Add location filter
- [ ] Implement "Clear All" button
- [ ] Wire up filters to state
- [ ] Add widget tests

#### JOB-010: Saved Jobs UI
- [ ] Create `saved_jobs_screen.dart`
- [ ] Group saved jobs by status
- [ ] Add status update dropdown
- [ ] Show notes in expandable section
- [ ] Add edit notes functionality
- [ ] Implement remove from saved
- [ ] Add "Applied on" date for applied jobs
- [ ] Add widget tests

#### JOB-011: Job Creation UI (User-Created Jobs)
- [ ] Create `job_create_screen.dart`
- [ ] Add title and company fields
- [ ] Add location field
- [ ] Add description text area (large)
- [ ] Add remote checkbox
- [ ] Add salary range field
- [ ] Implement save as draft
- [ ] Add save button with validation
- [ ] Add widget tests

### 6.5 Generation Feature - Sprint 4

**Priority**: Critical (Core AI feature)
**Dependencies**: PROFILE-012, JOB-011

#### GEN-001: Data Models
- [ ] Create `Generation` model with freezed
- [ ] Create `GenerationRequest` model
- [ ] Create `GenerationProgress` model
- [ ] Create `MatchScore` model
- [ ] Create `GenerationState` model
- [ ] Create `GenerationStatus` and `GenerationStage` enums
- [ ] Add JSON serialization
- [ ] Run code generation
- [ ] Add model tests

#### GEN-002: API Client
- [ ] Create `generation_api_client.dart`
- [ ] Implement `createResumeGeneration()`
- [ ] Implement `createCoverLetterGeneration()`
- [ ] Implement `getGeneration()`
- [ ] Implement `getGenerationResult()`
- [ ] Implement `regenerate()`
- [ ] Implement `cancelGeneration()`
- [ ] Implement `getGenerations()` with filters
- [ ] Implement `submitFeedback()`
- [ ] Implement `getTemplates()`
- [ ] Implement `getAnalytics()`
- [ ] Add mock API client

#### GEN-003: Polling Service
- [ ] Create `generation_polling_service.dart`
- [ ] Implement `pollGeneration()` stream
- [ ] Add configurable poll interval (2 seconds)
- [ ] Implement terminal status detection
- [ ] Add error handling with retry
- [ ] Implement poll cancellation
- [ ] Add polling service tests

#### GEN-004: Repository Layer
- [ ] Create `generation_repository.dart`
- [ ] Implement `startGeneration()`
- [ ] Implement `getGeneration()` with cache
- [ ] Implement `getGenerations()` list
- [ ] Implement `cancelGeneration()`
- [ ] Implement `regenerate()`
- [ ] Cache generation results locally
- [ ] Add repository tests

#### GEN-005: State Management
- [ ] Create `generation_notifier.dart`
- [ ] Implement `GenerationNotifier` with `GenerationState`
- [ ] Implement `startGeneration()` with polling
- [ ] Implement `watchGenerationProgress()`
- [ ] Implement `loadGenerations()`
- [ ] Implement `cancelGeneration()` with polling stop
- [ ] Implement `regenerate()`
- [ ] Create `generation_progress_notifier.dart` for active generation
- [ ] Create generation providers
- [ ] Add notifier tests

#### GEN-006: Generation List UI
- [ ] Create `generation_list_screen.dart`
- [ ] Design generation cards with `generation_card.dart`
- [ ] Group by status (in progress, completed, failed)
- [ ] Show generation metadata (job, date, type)
- [ ] Add tap to navigate to detail
- [ ] Add pull-to-refresh
- [ ] Show empty state for no generations
- [ ] Add widget tests

#### GEN-007: Generation Initiation UI
- [ ] Create generation options bottom sheet
- [ ] Add template picker (dropdown or radio buttons)
- [ ] Add document length picker (one-page, two-page)
- [ ] Add cover letter checkbox
- [ ] Show generation limits warning
- [ ] Add "Generate" button
- [ ] Navigate to progress screen on start
- [ ] Add widget tests

#### GEN-008: Generation Progress UI
- [ ] Create `generation_detail_screen.dart` for progress
- [ ] Create `progress_indicator_five_stage.dart` widget
- [ ] Display current stage name and message
- [ ] Show percentage progress
- [ ] Implement stage icons (analysis, scoring, generation, validation, export)
- [ ] Add cancel button
- [ ] Show estimated time remaining
- [ ] Auto-navigate to result on completion
- [ ] Add widget tests

#### GEN-009: Generation Result UI
- [ ] Update `generation_detail_screen.dart` for completed state
- [ ] Display match score with `match_score_widget.dart`
- [ ] Show keyword coverage with `keyword_coverage_chart.dart`
- [ ] Display recommendations list
- [ ] Add "View Document" button
- [ ] Add "Regenerate" button
- [ ] Add "Share" button
- [ ] Show ATS score
- [ ] Add widget tests

#### GEN-010: Match Score Widget
- [ ] Create `match_score_widget.dart`
- [ ] Implement circular gauge or progress ring
- [ ] Color code score (red < 60, yellow 60-80, green > 80)
- [ ] Display score percentage
- [ ] Add animation on load
- [ ] Add widget tests

#### GEN-011: Keyword Coverage Chart
- [ ] Create `keyword_coverage_chart.dart`
- [ ] Show required vs matched keywords count
- [ ] Display coverage percentage
- [ ] List top matched keywords as chips
- [ ] List missing keywords with warning icon
- [ ] Add widget tests

#### GEN-012: Template Selection
- [ ] Fetch templates from backend API
- [ ] Cache templates locally
- [ ] Create template picker widget
- [ ] Show template preview thumbnails
- [ ] Allow template selection in generation options
- [ ] Add widget tests

### 6.6 Document Management Feature - Sprint 5

**Priority**: High (Output of generation)
**Dependencies**: GEN-012

#### DOC-001: Data Models
- [ ] Create `Document` model with freezed
- [ ] Create `AtsScore` model
- [ ] Create `DocumentExportOptions` model
- [ ] Create `DocumentsState` model
- [ ] Create `DocumentFilter` model
- [ ] Add JSON serialization
- [ ] Run code generation
- [ ] Add model tests

#### DOC-002: PDF Cache Service
- [ ] Create `pdf_cache_service.dart`
- [ ] Implement local PDF storage directory
- [ ] Implement `downloadPdf()` from URL
- [ ] Implement `getCachedPdf()` path lookup
- [ ] Implement `deletePdf()`
- [ ] Implement `clearCache()`
- [ ] Add cache size management
- [ ] Add service tests

#### DOC-003: API Client
- [ ] Create `document_api_client.dart`
- [ ] Implement `getDocuments()` with filters
- [ ] Implement `getDocument()`
- [ ] Implement `exportDocument()`
- [ ] Add mock API client

#### DOC-004: Repository Layer
- [ ] Create `document_repository.dart`
- [ ] Implement `getDocuments()` with cache
- [ ] Implement `getDocument()` with cache
- [ ] Implement `downloadDocument()` with PDF cache
- [ ] Add repository tests

#### DOC-005: State Management
- [ ] Create `documents_notifier.dart`
- [ ] Implement `DocumentsNotifier` with `DocumentsState`
- [ ] Implement `loadDocuments()`
- [ ] Implement `applyFilter()`
- [ ] Implement `downloadDocument()`
- [ ] Create document providers
- [ ] Add notifier tests

#### DOC-006: Document List UI
- [ ] Create `document_list_screen.dart`
- [ ] Design document cards with `document_card.dart`
- [ ] Show document type icon (resume/cover letter)
- [ ] Display job title and company
- [ ] Show ATS score badge
- [ ] Display version number
- [ ] Add tap to navigate to viewer
- [ ] Add pull-to-refresh
- [ ] Add widget tests

#### DOC-007: Document Card Widget
- [ ] Create `document_card.dart`
- [ ] Show thumbnail preview (if available)
- [ ] Display creation date
- [ ] Add ATS score badge with color coding
- [ ] Add share icon button
- [ ] Add delete icon button with confirmation
- [ ] Add const constructor
- [ ] Add widget tests

#### DOC-008: ATS Score Badge
- [ ] Create `ats_score_badge.dart` widget
- [ ] Color code badge (red, yellow, green)
- [ ] Display score with one decimal
- [ ] Add tooltip with score breakdown
- [ ] Add widget tests

#### DOC-009: Document Viewer UI
- [ ] Create `document_viewer_screen.dart`
- [ ] Integrate PDF viewer widget (`pdf_viewer.dart`)
- [ ] Add page navigation controls
- [ ] Add zoom controls
- [ ] Add share button in app bar
- [ ] Add download to device button
- [ ] Show loading state while PDF loads
- [ ] Add widget tests

#### DOC-010: PDF Viewer Widget
- [ ] Create `pdf_viewer.dart` using `flutter_pdfview` or similar
- [ ] Implement page rendering
- [ ] Add gesture support (pinch to zoom, swipe to navigate)
- [ ] Show page number indicator
- [ ] Handle large PDF files efficiently
- [ ] Add widget tests

#### DOC-011: Document Search & Filter UI
- [ ] Add search bar to document list
- [ ] Implement search by job title
- [ ] Create filter panel for document type
- [ ] Add date range filter
- [ ] Add ATS score filter (slider or range)
- [ ] Wire up filters to state
- [ ] Add widget tests

#### DOC-012: Document Sharing
- [ ] Implement `share()` using `share_plus` package
- [ ] Share PDF file to other apps
- [ ] Add share options (email, messaging, cloud)
- [ ] Handle share completion callback
- [ ] Add integration tests

### 6.7 Offline & Sync Feature - Sprint 6

**Priority**: Medium (Enhances UX)
**Dependencies**: All previous features

#### SYNC-001: Sync Queue Implementation
- [ ] Create `sync_queue.dart` service
- [ ] Implement `enqueue()` for pending operations
- [ ] Implement `dequeue()` to retrieve next operation
- [ ] Implement `markComplete()` for successful sync
- [ ] Implement `markFailed()` with retry count
- [ ] Implement `clearQueue()`
- [ ] Add queue persistence tests

#### SYNC-002: Background Sync Service
- [ ] Set up `workmanager` for Android periodic tasks
- [ ] Set up `background_fetch` for iOS periodic tasks
- [ ] Create `SyncWorker` class
- [ ] Implement `syncProfiles()`
- [ ] Implement `syncJobs()`
- [ ] Implement `syncSavedJobs()`
- [ ] Implement `syncGenerations()`
- [ ] Add conflict resolution logic
- [ ] Test background sync on both platforms

#### SYNC-003: Connectivity Monitoring
- [ ] Integrate `connectivity_plus` package
- [ ] Create `ConnectivityService`
- [ ] Implement connectivity stream
- [ ] Trigger sync on reconnection
- [ ] Update UI to show offline indicator
- [ ] Add connectivity tests

#### SYNC-004: Offline Indicators UI
- [ ] Create offline banner widget
- [ ] Show "Offline" badge on app bar
- [ ] Display sync status icon
- [ ] Add "Pending Sync" badge on modified items
- [ ] Show last sync timestamp
- [ ] Add widget tests

#### SYNC-005: Optimistic Updates
- [ ] Implement optimistic update pattern in profile repo
- [ ] Implement optimistic update in job repo
- [ ] Implement optimistic update in saved job repo
- [ ] Revert on sync failure
- [ ] Show sync error notifications
- [ ] Add integration tests

### 6.8 Settings & Preferences - Sprint 7

**Priority**: Low (Nice to have)
**Dependencies**: All core features

#### SETTINGS-001: Settings Data Model
- [ ] Create `UserPreferences` model
- [ ] Add default template preference
- [ ] Add default document length preference
- [ ] Add theme preference (light/dark/system)
- [ ] Add notification preferences
- [ ] Persist preferences locally

#### SETTINGS-002: Settings UI
- [ ] Create `settings_screen.dart`
- [ ] Add account section (email, name, subscription tier)
- [ ] Add default template picker
- [ ] Add default length picker
- [ ] Add theme selector
- [ ] Add notification toggle
- [ ] Add "Clear Cache" button
- [ ] Add "Logout" button
- [ ] Add widget tests

#### SETTINGS-003: Theme Support
- [ ] Implement light theme
- [ ] Implement dark theme
- [ ] Add theme provider
- [ ] Wire up theme to MaterialApp
- [ ] Persist theme preference
- [ ] Test theme switching

### 6.9 Testing & Quality - Sprint 8

**Priority**: High (Required for release)
**Dependencies**: All features

#### TEST-001: Unit Tests
- [ ] Achieve 80%+ coverage for models
- [ ] Achieve 80%+ coverage for state notifiers
- [ ] Achieve 80%+ coverage for repositories
- [ ] Achieve 80%+ coverage for API clients
- [ ] Achieve 80%+ coverage for utility functions
- [ ] Run coverage report

#### TEST-002: Widget Tests
- [ ] Test all auth screens
- [ ] Test all profile screens and widgets
- [ ] Test all job screens and widgets
- [ ] Test all generation screens and widgets
- [ ] Test all document screens and widgets
- [ ] Test all shared widgets
- [ ] Test navigation flows

#### TEST-003: Integration Tests
- [ ] Test complete auth flow
- [ ] Test profile creation and editing flow
- [ ] Test job search and save flow
- [ ] Test generation flow from job detail to document
- [ ] Test offline → online sync flow
- [ ] Test logout and re-login with data persistence

#### TEST-004: Accessibility Testing
- [ ] Verify all text scales correctly
- [ ] Test with TalkBack (Android)
- [ ] Test with VoiceOver (iOS)
- [ ] Verify color contrast (WCAG AA)
- [ ] Verify touch target sizes (48x48dp minimum)
- [ ] Add semantic labels where missing

#### TEST-005: Performance Testing
- [ ] Profile app with Flutter DevTools
- [ ] Measure job list scroll performance (60fps target)
- [ ] Measure generation progress polling overhead
- [ ] Optimize large PDF rendering
- [ ] Reduce app size with tree shaking
- [ ] Test on low-end devices

### 6.10 CI/CD & Release - Sprint 9

**Priority**: High (Required for deployment)
**Dependencies**: TEST-001 through TEST-005

#### CICD-001: GitHub Actions Setup
- [ ] Create `.github/workflows/flutter.yml`
- [ ] Add `flutter analyze` step
- [ ] Add `dart format --set-exit-if-changed .` step
- [ ] Add `flutter test` step with coverage
- [ ] Add `flutter build apk` step
- [ ] Add `flutter build ios` step (if macOS runner available)
- [ ] Upload build artifacts

#### CICD-002: Code Quality
- [ ] Set up automated linting
- [ ] Enforce code formatting
- [ ] Add code coverage reporting
- [ ] Set coverage threshold (80%)
- [ ] Add badge to README

#### CICD-003: Release Preparation
- [ ] Update app version in `pubspec.yaml`
- [ ] Update changelog
- [ ] Create release builds (Android APK/AAB, iOS IPA)
- [ ] Test release builds on physical devices
- [ ] Generate app icons and splash screens
- [ ] Prepare app store listings

---

## 7. UI/UX Design System
-------------------------

Principles
- App must show cached data immediately and sync with backend in background.
- For write operations (save job, start generation): queue operations locally when offline and sync when network returns.

Implementation
- Local DB: `sqflite` or `sembast` for structured storage. Use a simple repository pattern to abstract: `IJobLocalRepo` / `IJobRemoteRepo`.
- Sync queue: simple persisted queue table for pending operations. Background worker (Workmanager on Android / background_fetch on iOS) to flush queue.
- Conflict resolution: last-write-wins for non-critical data (jobs), validate ownership on sync.

---

## 8. Offline-First Strategy

### 8.1 Principles

- **Cache-First Read**: Always return cached data immediately, sync in background
- **Queue-First Write**: Write operations saved locally first, then synced to backend
- **Optimistic Updates**: UI updates immediately, rollback on sync failure
- **Background Sync**: Periodic sync when network available via workmanager

### 8.2 Implementation

#### Local Database
- **Technology**: sqflite for structured storage
- **Strategy**: Repository pattern with `ILocalRepo` and `IRemoteRepo` interfaces
- **Tables**: See section 4.2 for complete schema

#### Sync Queue
```dart
// lib/src/core/storage/sync_queue.dart
class SyncQueue {
  final Database _db;
  
  Future<void> enqueue({
    required String entityType,
    required String entityId,
    required String operation,
    required Map<String, dynamic> payload,
  }) async {
    await _db.insert('sync_queue', {
      'entity_type': entityType,
      'entity_id': entityId,
      'operation': operation,
      'payload': jsonEncode(payload),
      'created_at': DateTime.now().millisecondsSinceEpoch,
      'retry_count': 0,
    });
  }
  
  Future<List<SyncQueueItem>> getPending() async {
    final rows = await _db.query(
      'sync_queue',
      orderBy: 'created_at ASC',
      limit: 50,
    );
    return rows.map((r) => SyncQueueItem.fromMap(r)).toList();
  }
  
  Future<void> markComplete(int id) async {
    await _db.delete('sync_queue', where: 'id = ?', whereArgs: [id]);
  }
  
  Future<void> markFailed(int id, String error) async {
    await _db.update(
      'sync_queue',
      {
        'retry_count': 'retry_count + 1',
        'last_error': error,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}
```

#### Conflict Resolution
- **Strategy**: Last-write-wins for non-critical data (jobs, profiles)
- **Ownership Validation**: Server validates user_id matches before applying updates
- **Timestamp Comparison**: Use `updated_at` to determine most recent version

### 8.3 Background Sync

```dart
// lib/src/core/sync/sync_worker.dart
class SyncWorker {
  final SyncQueue _syncQueue;
  final ProfileRepository _profileRepo;
  final JobRepository _jobRepo;
  
  Future<void> syncAll() async {
    final items = await _syncQueue.getPending();
    
    for (var item in items) {
      try {
        await _syncItem(item);
        await _syncQueue.markComplete(item.id);
      } catch (e) {
        await _syncQueue.markFailed(item.id, e.toString());
      }
    }
  }
  
  Future<void> _syncItem(SyncQueueItem item) async {
    switch (item.entityType) {
      case 'profile':
        await _syncProfile(item);
        break;
      case 'job':
        await _syncJob(item);
        break;
      // ... other entity types
    }
  }
}
```

---

## 9. Security & Authentication

### 9.1 Token Management

```dart
// lib/src/features/auth/services/token_manager.dart
class TokenManager {
  final FlutterSecureStorage _secureStorage;
  
  String? _accessToken; // In-memory only
  
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    _accessToken = accessToken;
    await _secureStorage.write(key: 'refresh_token', value: refreshToken);
  }
  
  Future<String?> getAccessToken() async {
    return _accessToken;
  }
  
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: 'refresh_token');
  }
  
  Future<void> clearTokens() async {
    _accessToken = null;
    await _secureStorage.delete(key: 'refresh_token');
  }
}
```

### 9.2 Authentication Flow

1. **Login**: User provides credentials → Backend returns access + refresh tokens → Tokens stored
2. **Request**: Access token attached to Authorization header
3. **Token Expiry**: 401 received → Attempt refresh → Retry original request
4. **Refresh Failure**: Clear tokens → Navigate to login screen
5. **Logout**: Clear tokens → Clear local data → Navigate to login

### 9.3 Security Best Practices

- **Never log PII or tokens**
- **Use HTTPS only in production**
- **Implement certificate pinning for production** (optional)
- **Encrypt sensitive data in local database** (future enhancement)
- **Implement biometric authentication** (future enhancement)

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Target Coverage**: 80%+

```dart
// Example: Profile notifier test
void main() {
  late ProfileNotifier notifier;
  late MockProfileRepository mockRepo;
  
  setUp(() {
    mockRepo = MockProfileRepository();
    notifier = ProfileNotifier(mockRepo, 'user-123');
  });
  
  test('loadProfiles updates state with fetched profiles', () async {
    final profiles = [createMockProfile()];
    when(() => mockRepo.getUserProfiles('user-123'))
        .thenAnswer((_) async => profiles);
    
    await notifier.loadProfiles();
    
    expect(notifier.state.profiles, profiles);
    expect(notifier.state.isLoading, false);
  });
  
  test('createProfile adds profile to state', () async {
    final profile = createMockProfile();
    when(() => mockRepo.createProfile(any()))
        .thenAnswer((_) async => profile);
    
    await notifier.createProfile(profile);
    
    expect(notifier.state.profiles, contains(profile));
  });
}
```

### 10.2 Widget Tests

```dart
// Example: Job card widget test
void main() {
  testWidgets('JobCard displays job information', (tester) async {
    final job = Job(
      id: '1',
      title: 'Software Engineer',
      company: 'TechCorp',
      location: 'Seattle, WA',
      description: 'Great job',
      source: 'user_created',
      status: JobStatus.active,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
    
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: JobCard(job: job, onTap: () {}),
        ),
      ),
    );
    
    expect(find.text('Software Engineer'), findsOneWidget);
    expect(find.text('TechCorp'), findsOneWidget);
    expect(find.text('Seattle, WA'), findsOneWidget);
  });
}
```

### 10.3 Integration Tests

```dart
// Example: Generation flow integration test
void main() {
  testWidgets('Complete generation flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    
    // Login
    await tester.enterText(find.byType(TextField).first, 'test@example.com');
    await tester.enterText(find.byType(TextField).last, 'password123');
    await tester.tap(find.text('Login'));
    await tester.pumpAndSettle();
    
    // Navigate to job detail
    await tester.tap(find.text('Software Engineer').first);
    await tester.pumpAndSettle();
    
    // Start generation
    await tester.tap(find.byIcon(Icons.description));
    await tester.pumpAndSettle();
    
    // Verify progress screen
    expect(find.text('Generating'), findsOneWidget);
    
    // Wait for completion (in real test, mock the polling)
    await tester.pumpAndSettle(const Duration(seconds: 30));
    
    // Verify result screen
    expect(find.text('Completed'), findsOneWidget);
    expect(find.byType(MatchScoreWidget), findsOneWidget);
  });
}
```

### 10.4 Accessibility Tests

```dart
void main() {
  testWidgets('JobCard meets accessibility requirements', (tester) async {
    final job = createMockJob();
    
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: JobCard(job: job, onTap: () {}),
        ),
      ),
    );
    
    // Verify semantic labels
    expect(
      tester.getSemantics(find.byType(JobCard)),
      matchesSemantics(label: 'Job: Software Engineer at TechCorp'),
    );
    
    // Verify touch target size
    final size = tester.getSize(find.byType(JobCard));
    expect(size.height, greaterThanOrEqualTo(48.0));
  });
}
```

---

## 11. Performance & Optimization

### 11.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| App Startup | < 3s to first screen | Time to interactive |
| Job List Scroll | 60 FPS | Flutter DevTools |
| Generation Poll | < 2s interval | Network tab |
| PDF Rendering | < 5s for 2-page doc | Stopwatch |
| Build Size (APK) | < 25 MB | Release build |
| Memory Usage | < 150 MB | Android Profiler |

### 11.2 Optimization Techniques

#### Const Constructors
```dart
class JobCard extends StatelessWidget {
  final Job job;
  final VoidCallback onTap;
  
  const JobCard({
    Key? key,
    required this.job,
    required this.onTap,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: const Padding( // const here
          padding: EdgeInsets.all(16.0),
          child: _JobCardContent(),
        ),
      ),
    );
  }
}
```

#### ListView.builder for Large Lists
```dart
ListView.builder(
  itemCount: jobs.length,
  itemBuilder: (context, index) {
    return JobCard(
      key: ValueKey(jobs[index].id), // Key for widget recycling
      job: jobs[index],
      onTap: () => _navigateToDetail(jobs[index]),
    );
  },
)
```

#### Image Caching
```dart
CachedNetworkImage(
  imageUrl: job.companyLogoUrl,
  placeholder: (context, url) => const CircularProgressIndicator(),
  errorWidget: (context, url, error) => const Icon(Icons.error),
  cacheManager: CacheManager(
    Config(
      'companyLogos',
      stalePeriod: const Duration(days: 7),
    ),
  ),
)
```

#### Debouncing Search
```dart
Timer? _debounce;

void _onSearchChanged(String query) {
  _debounce?.cancel();
  _debounce = Timer(const Duration(milliseconds: 300), () {
    ref.read(jobsNotifierProvider.notifier).applyFilter(
      JobFilter(searchQuery: query),
    );
  });
}
```

---

## 12. Implementation Roadmap

### Sprint Overview

| Sprint | Duration | Focus | Key Deliverables |
|--------|----------|-------|------------------|
| Sprint 0 | 1 week | Foundation | Project setup, core infrastructure, design system |
| Sprint 1 | 1 week | Authentication | Login, registration, token management |
| Sprint 2 | 2 weeks | Profile Management | Profile CRUD, component management, analytics |
| Sprint 3 | 2 weeks | Job Management | Job browsing, search, filters, saved jobs |
| Sprint 4 | 2 weeks | Generation | Resume/cover letter generation, progress tracking |
| Sprint 5 | 1 week | Document Management | Document list, viewer, PDF caching |
| Sprint 6 | 1 week | Offline & Sync | Sync queue, background sync, connectivity |
| Sprint 7 | 1 week | Settings & Polish | Settings UI, theme support, final UX polish |
| Sprint 8 | 1 week | Testing & QA | Unit, widget, integration tests, accessibility |
| Sprint 9 | 1 week | CI/CD & Release | GitHub Actions, release builds, deployment |

**Total Development Time**: 13 weeks

### Priority Matrix

| Priority | Features |
|----------|----------|
| P0 (Critical) | INFRA-001 to INFRA-007, AUTH-001 to AUTH-007, GEN-001 to GEN-012 |
| P1 (High) | PROFILE-001 to PROFILE-012, JOB-001 to JOB-011, DOC-001 to DOC-012 |
| P2 (Medium) | SYNC-001 to SYNC-005, TEST-001 to TEST-005 |
| P3 (Low) | SETTINGS-001 to SETTINGS-003, CICD-001 to CICD-003 |

### Milestones

1. **M1: Foundation Complete** (End of Sprint 0)
   - Project structure established
   - Core providers configured
   - Database initialized
   - Navigation working

2. **M2: MVP Authentication** (End of Sprint 1)
   - Users can register and login
   - Tokens stored securely
   - Protected routes working

3. **M3: Profile Management** (End of Sprint 2)
   - Users can create and edit profiles
   - All components (experience, education, skills, projects) manageable
   - Analytics displayed

4. **M4: Job Discovery** (End of Sprint 3)
   - Users can browse jobs
   - Search and filters working
   - Save jobs functionality

5. **M5: AI Generation** (End of Sprint 4)
   - Users can generate tailored resumes
   - Progress tracking working
   - Match scores displayed

6. **M6: Document Access** (End of Sprint 5)
   - Users can view generated documents
   - PDF viewer working
   - Document history available

7. **M7: Offline Support** (End of Sprint 6)
   - App works offline
   - Sync queue functional
   - Background sync working

8. **M8: Release Ready** (End of Sprint 9)
   - All tests passing
   - CI/CD pipeline working
   - App stores submission ready

---

## Appendix A: API Request/Response Examples

### Create Profile
```json
POST /api/v1/profiles/
{
  "full_name": "Alex Doe",
  "email": "alex@example.com",
  "phone": "+1-555-555-5555",
  "location": "Seattle, WA",
  "professional_summary": "Experienced software engineer...",
  "linkedin": "https://linkedin.com/in/alexdoe",
  "github": "https://github.com/alexdoe"
}

Response:
{
  "id": "uuid",
  "user_id": "uuid",
  "full_name": "Alex Doe",
  ...
  "created_at": "2025-10-21T10:00:00Z",
  "updated_at": "2025-10-21T10:00:00Z"
}
```

### Start Generation
```json
POST /api/v1/generations/resume
{
  "profile_id": "uuid",
  "job_id": "uuid",
  "template": "ATS",
  "length": "one-page"
}

Response:
{
  "generation_id": "uuid",
  "status": "pending",
  "created_at": "2025-10-21T10:00:00Z"
}
```

### Poll Generation Status
```json
GET /api/v1/generations/{id}

Response:
{
  "id": "uuid",
  "status": "generating",
  "stage_progress": {
    "current_stage": "scoring",
    "percentage": 40.0,
    "message": "Scoring profile sections for relevance..."
  },
  "match_score": null,
  ...
}
```

---

## Appendix B: Local Database Queries

### Get Profile with All Components
```sql
SELECT 
  p.*,
  (SELECT json_group_array(json_object(
    'id', e.id,
    'job_title', e.job_title,
    'company', e.company,
    ...
  )) FROM experiences e WHERE e.profile_id = p.id) as experiences,
  (SELECT json_group_array(json_object(
    'id', ed.id,
    'degree', ed.degree,
    ...
  )) FROM education ed WHERE ed.profile_id = p.id) as education,
  (SELECT json_group_array(json_object(
    'id', s.id,
    'name', s.name,
    ...
  )) FROM skills s WHERE s.profile_id = p.id) as skills,
  (SELECT json_group_array(json_object(
    'id', pr.id,
    'name', pr.name,
    ...
  )) FROM projects pr WHERE pr.profile_id = p.id) as projects
FROM master_profiles p
WHERE p.id = ?
```

---

## Appendix C: Logging Protocol

After every major development milestone or user interaction during development, update:

1. **`log/mobile-developer-log.md`** with detailed entry including:
   - User Request
   - Response Summary
   - Actions Taken (files created/modified)
   - Reason for changes

2. **`.context/mobile-developer-summary.md`** with:
   - UI Implementation progress
   - State Management status
   - API Integration status
   - Code Quality assessment
   - Recommendations
   - Confidence Level

---

**Document Version**: 1.0
**Last Updated**: October 21, 2025
**Status**: Comprehensive design complete, ready for implementation

**Next Actions**:
1. Review and approve design document
2. Begin Sprint 0 infrastructure tasks
3. Set up development environment
4. Initialize project with dependencies
