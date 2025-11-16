import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../models/job.dart';
import '../services/api/jobs_api_client.dart';

part 'job_provider.g.dart';
part 'job_provider.freezed.dart';

@riverpod
class UserJobs extends _$UserJobs {
  JobsApiClient get _jobsApi => ref.read(jobsApiClientProvider);

  @override
  Future<List<Job>> build() async {
    final response = await _jobsApi.getUserJobs();
    return response.jobs;
  }

  Future<void> addJob(Job job) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final newJob = await _jobsApi.createJob(
        source: job.source,
        title: job.title,
        company: job.company,
        location: job.location,
        description: job.description,
        requirements: job.requirements,
        benefits: job.benefits,
        salaryRange: job.salaryRange,
        remote: job.remote,
      );
      final previousState = await future;
      return [...previousState, newJob];
    });
  }

  Future<void> updateJob(Job job) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final updatedJob = await _jobsApi.updateJob(
        jobId: job.id,
        parsedKeywords: job.parsedKeywords,
        status: job.status,
        applicationStatus: job.applicationStatus,
      );
      final previousState = await future;
      return [
        for (final j in previousState)
          if (j.id == updatedJob.id) updatedJob else j
      ];
    });
  }

  Future<void> deleteJob(String jobId) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      await _jobsApi.deleteJob(jobId);
      final previousState = await future;
      return previousState.where((j) => j.id != jobId).toList();
    });
  }
}

@riverpod
class JobActions extends _$JobActions {
  @override
  Future<void> build() async {
    return;
  }

  Future<void> saveBrowseJob(BrowseJob browseJob) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final jobsApi = ref.read(jobsApiClientProvider);
      await jobsApi.createJob(
        source: browseJob.source,
        title: browseJob.title,
        company: browseJob.company,
        location: browseJob.location,
        description: browseJob.description,
        requirements: browseJob.requirements,
        benefits: browseJob.benefits,
        salaryRange: browseJob.salaryRange,
        remote: browseJob.remote,
      );
      // Refresh the user jobs list
      ref.invalidate(userJobsProvider);
    });
  }
}

@riverpod
Future<List<BrowseJob>> browseJobs(
  Ref ref, {
  String? query,
  String? location,
  bool remote = false,
}) async {
  final jobsApi = ref.watch(jobsApiClientProvider);
  final response = await jobsApi.browseJobs(
    query: query,
    location: location,
    remote: remote,
  );
  return response.jobs;
}

@riverpod
Future<Job?> selectedJob(Ref ref, String jobId) async {
  final jobsApi = ref.read(jobsApiClientProvider);
  try {
    return await jobsApi.getJobById(jobId);
  } catch (e) {
    return null; // Not found
  }
}

@freezed
class JobFilterState with _$JobFilterState {
  const factory JobFilterState({
    JobStatus? status,
    JobSource? source,
  }) = _JobFilterState;
}

@riverpod
class JobFilters extends _$JobFilters {
  @override
  JobFilterState build() {
    return const JobFilterState();
  }

  void setStatus(JobStatus? status) {
    state = state.copyWith(status: status);
  }

  void setSource(JobSource? source) {
    state = state.copyWith(source: source);
  }

  void clear() {
    state = const JobFilterState();
  }
}

@riverpod
List<Job> filteredUserJobs(Ref ref) {
  final jobs = ref.watch(userJobsProvider);
  final filters = ref.watch(jobFiltersProvider);

  return jobs.maybeWhen(
    data: (jobList) {
      var filtered = jobList.toList();

      if (filters.status != null) {
        filtered.retainWhere((job) => job.status == filters.status);
      }
      if (filters.source != null) {
        filtered.retainWhere((job) => job.source == filters.source);
      }
      return filtered;
    },
    orElse: () => [],
  );
}
