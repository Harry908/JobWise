import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/job.dart';
import '../services/api/jobs_api_client.dart';

part 'job_provider.freezed.dart';

/// Job state using Freezed for immutability
@freezed
class JobState with _$JobState {
  const factory JobState({
    @Default([]) List<Job> userJobs,
    @Default([]) List<BrowseJob> browseJobs,
    Job? selectedJob,
    @Default(false) bool isLoading,
    @Default(false) bool isLoadingMore,
    @Default(false) bool isBrowseLoading,
    String? error,
    @Default(0) int userJobsTotal,
    @Default(0) int browseJobsTotal,
    @Default(true) bool hasMoreUserJobs,
    @Default(true) bool hasMoreBrowseJobs,
  }) = _JobState;
}

/// Job Notifier for managing job-related state
class JobNotifier extends StateNotifier<JobState> {
  final JobsApiClient _jobsApi;

  JobNotifier(this._jobsApi) : super(const JobState());

  /// Load user's saved jobs with optional filters
  Future<void> loadUserJobs({
    JobStatus? status,
    JobSource? source,
    bool refresh = false,
  }) async {
    if (refresh) {
      state = state.copyWith(
        isLoading: true,
        error: null,
        userJobs: [],
      );
    } else if (state.isLoading) {
      return; // Already loading
    }

    try {
      state = state.copyWith(isLoading: true, error: null);

      final response = await _jobsApi.getUserJobs(
        status: status,
        source: source,
        limit: 20,
        offset: 0,
      );

      state = state.copyWith(
        userJobs: response.jobs,
        userJobsTotal: response.total,
        hasMoreUserJobs: response.pagination.hasMore,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load more user jobs (pagination)
  Future<void> loadMoreUserJobs({
    JobStatus? status,
    JobSource? source,
  }) async {
    if (state.isLoadingMore || !state.hasMoreUserJobs) {
      return;
    }

    try {
      state = state.copyWith(isLoadingMore: true);

      final response = await _jobsApi.getUserJobs(
        status: status,
        source: source,
        limit: 20,
        offset: state.userJobs.length,
      );

      state = state.copyWith(
        userJobs: [...state.userJobs, ...response.jobs],
        userJobsTotal: response.total,
        hasMoreUserJobs: response.pagination.hasMore,
        isLoadingMore: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingMore: false,
        error: e.toString(),
      );
    }
  }

  /// Browse mock/external jobs with search and filters
  Future<void> browseJobs({
    String? query,
    String? location,
    bool? remote,
    bool refresh = false,
  }) async {
    if (refresh) {
      state = state.copyWith(
        isBrowseLoading: true,
        error: null,
        browseJobs: [],
      );
    } else if (state.isBrowseLoading) {
      return; // Already loading
    }

    try {
      state = state.copyWith(isBrowseLoading: true, error: null);

      final response = await _jobsApi.browseJobs(
        query: query,
        location: location,
        remote: remote,
        limit: 20,
        offset: 0,
      );

      state = state.copyWith(
        browseJobs: response.jobs,
        browseJobsTotal: response.total,
        hasMoreBrowseJobs: response.pagination.hasMore,
        isBrowseLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isBrowseLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load more browse jobs (pagination)
  Future<void> loadMoreBrowseJobs({
    String? query,
    String? location,
    bool? remote,
  }) async {
    if (state.isLoadingMore || !state.hasMoreBrowseJobs) {
      return;
    }

    try {
      state = state.copyWith(isLoadingMore: true);

      final response = await _jobsApi.browseJobs(
        query: query,
        location: location,
        remote: remote,
        limit: 20,
        offset: state.browseJobs.length,
      );

      state = state.copyWith(
        browseJobs: [...state.browseJobs, ...response.jobs],
        browseJobsTotal: response.total,
        hasMoreBrowseJobs: response.pagination.hasMore,
        isLoadingMore: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingMore: false,
        error: e.toString(),
      );
    }
  }

  /// Create job from raw text
  Future<Job?> createJobFromText(String rawText) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final job = await _jobsApi.createFromText(rawText: rawText);

      // Add to user jobs list
      state = state.copyWith(
        userJobs: [job, ...state.userJobs],
        userJobsTotal: state.userJobsTotal + 1,
        isLoading: false,
      );

      return job;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Create job from URL
  Future<Job?> createJobFromUrl(String url) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final job = await _jobsApi.createFromUrl(url: url);

      // Add to user jobs list
      state = state.copyWith(
        userJobs: [job, ...state.userJobs],
        userJobsTotal: state.userJobsTotal + 1,
        isLoading: false,
      );

      return job;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Save a browsed job to user's jobs
  Future<Job?> saveBrowseJob(BrowseJob browseJob) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final job = await _jobsApi.createJob(
        source: JobSource.userCreated,
        title: browseJob.title,
        company: browseJob.company,
        location: browseJob.location,
        description: browseJob.description,
        requirements: browseJob.requirements,
        benefits: browseJob.benefits,
        salaryRange: browseJob.salaryRange,
        remote: browseJob.remote,
      );

      // Add to user jobs list
      state = state.copyWith(
        userJobs: [job, ...state.userJobs],
        userJobsTotal: state.userJobsTotal + 1,
        isLoading: false,
      );

      return job;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Get job by ID
  Future<void> loadJobById(String jobId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final job = await _jobsApi.getJobById(jobId);

      state = state.copyWith(
        selectedJob: job,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Update job metadata (keywords, status, application status)
  /// Job posting content is READ-ONLY
  Future<Job?> updateJob({
    required String jobId,
    List<String>? parsedKeywords,
    JobStatus? status,
    ApplicationStatus? applicationStatus,
  }) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      final updatedJob = await _jobsApi.updateJob(
        jobId: jobId,
        parsedKeywords: parsedKeywords,
        status: status,
        applicationStatus: applicationStatus,
      );

      // Update in user jobs list
      final updatedList = state.userJobs.map((job) {
        return job.id == jobId ? updatedJob : job;
      }).toList();

      state = state.copyWith(
        userJobs: updatedList,
        selectedJob: updatedJob,
        isLoading: false,
      );

      return updatedJob;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }

  /// Delete job
  Future<bool> deleteJob(String jobId) async {
    try {
      state = state.copyWith(isLoading: true, error: null);

      await _jobsApi.deleteJob(jobId);

      // Remove from user jobs list
      final updatedList = state.userJobs.where((job) => job.id != jobId).toList();

      state = state.copyWith(
        userJobs: updatedList,
        userJobsTotal: state.userJobsTotal - 1,
        selectedJob: state.selectedJob?.id == jobId ? null : state.selectedJob,
        isLoading: false,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }

  /// Clear selected job
  void clearSelectedJob() {
    state = state.copyWith(selectedJob: null);
  }
}

/// Provider for JobNotifier
final jobProvider = StateNotifierProvider<JobNotifier, JobState>((ref) {
  return JobNotifier(ref.watch(jobsApiClientProvider));
});
