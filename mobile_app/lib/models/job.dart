import 'package:freezed_annotation/freezed_annotation.dart';

part 'job.freezed.dart';
part 'job.g.dart';

/// Represents a job posting from any source (user-created, mock, or external)
@freezed
class Job with _$Job {
  const factory Job({
    required String id,
    String? userId,
    required JobSource source,
    required String title,
    required String company,
    String? location,
    String? description,
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

/// Job source enum indicating where the job came from
enum JobSource {
  @JsonValue('user_created')
  userCreated,
  @JsonValue('indeed')
  indeed,
  @JsonValue('linkedin')
  linkedin,
  @JsonValue('glassdoor')
  glassdoor,
  @JsonValue('mock')
  mock,
  @JsonValue('imported')
  imported,
  @JsonValue('url_import')
  urlImport,
}

/// Job status enum
enum JobStatus {
  @JsonValue('active')
  active,
  @JsonValue('archived')
  archived,
  @JsonValue('draft')
  draft,
}

/// Represents a browsable job (from mock data or external sources)
/// Used when browsing jobs before saving them
@freezed
class BrowseJob with _$BrowseJob {
  const factory BrowseJob({
    required JobSource source,
    required String title,
    required String company,
    String? location,
    String? description,
    @Default([]) List<String> parsedKeywords,
    @Default([]) List<String> requirements,
    @Default([]) List<String> benefits,
    String? salaryRange,
    @Default(false) bool remote,
  }) = _BrowseJob;

  factory BrowseJob.fromJson(Map<String, dynamic> json) =>
      _$BrowseJobFromJson(json);
}

/// API response for job lists (user's saved jobs)
@freezed
class JobListResponse with _$JobListResponse {
  const factory JobListResponse({
    required List<Job> jobs,
    required int total,
    required PaginationMeta pagination,
  }) = _JobListResponse;

  factory JobListResponse.fromJson(Map<String, dynamic> json) =>
      _$JobListResponseFromJson(json);
}

/// API response for browse jobs (mock or external jobs)
@freezed
class BrowseJobListResponse with _$BrowseJobListResponse {
  const factory BrowseJobListResponse({
    required List<BrowseJob> jobs,
    required int total,
    required PaginationMeta pagination,
  }) = _BrowseJobListResponse;

  factory BrowseJobListResponse.fromJson(Map<String, dynamic> json) =>
      _$BrowseJobListResponseFromJson(json);
}

/// Pagination metadata
@freezed
class PaginationMeta with _$PaginationMeta {
  const factory PaginationMeta({
    required int limit,
    required int offset,
    required int total,
    required bool hasMore,
  }) = _PaginationMeta;

  factory PaginationMeta.fromJson(Map<String, dynamic> json) =>
      _$PaginationMetaFromJson(json);
}

/// Request model for creating a job from raw text
@freezed
class CreateJobFromTextRequest with _$CreateJobFromTextRequest {
  const factory CreateJobFromTextRequest({
    @Default(JobSource.userCreated) JobSource source,
    required String rawText,
  }) = _CreateJobFromTextRequest;

  factory CreateJobFromTextRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateJobFromTextRequestFromJson(json);

  @override
  Map<String, dynamic> toJson() => {
        'source': source.name,
        'raw_text': rawText,
      };
}

/// Request model for creating a job from URL
@freezed
class CreateJobFromUrlRequest with _$CreateJobFromUrlRequest {
  const factory CreateJobFromUrlRequest({
    @Default(JobSource.urlImport) JobSource source,
    required String url,
  }) = _CreateJobFromUrlRequest;

  factory CreateJobFromUrlRequest.fromJson(Map<String, dynamic> json) =>
      _$CreateJobFromUrlRequestFromJson(json);

  @override
  Map<String, dynamic> toJson() => {
        'source': source.name,
        'url': url,
      };
}

/// Request model for updating a job
@freezed
class UpdateJobRequest with _$UpdateJobRequest {
  const factory UpdateJobRequest({
    String? title,
    String? company,
    String? location,
    String? description,
    List<String>? requirements,
    List<String>? benefits,
    String? salaryRange,
    bool? remote,
    JobStatus? status,
  }) = _UpdateJobRequest;

  factory UpdateJobRequest.fromJson(Map<String, dynamic> json) =>
      _$UpdateJobRequestFromJson(json);
}
