import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/job.dart';
import 'base_http_client.dart';
import '../../providers/auth_provider.dart';

/// Helper function to convert snake_case keys to camelCase
/// Also handles type conversions (e.g., int user_id -> String userId)
Map<String, dynamic> _toCamelCase(Map<String, dynamic> json) {
  final result = <String, dynamic>{};
  json.forEach((key, value) {
    final camelKey = key.replaceAllMapped(
      RegExp(r'_([a-z])'),
      (match) => match.group(1)!.toUpperCase(),
    );
    
    // Special handling for userId - convert int to String
    if (camelKey == 'userId' && value is int) {
      result[camelKey] = value.toString();
    } else {
      result[camelKey] = value;
    }
  });
  return result;
}

/// API client for job-related endpoints
class JobsApiClient {
  final BaseHttpClient _client;

  JobsApiClient(this._client);

  /// Create a job from raw text (backend will parse it)
  /// POST /api/v1/jobs
  Future<Job> createFromText({
    required String rawText,
    JobSource source = JobSource.userCreated,
  }) async {
    try {
      final response = await _client.post(
        '/jobs',
        data: {
          'source': _sourceToString(source),
          'raw_text': rawText,
        },
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Job.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create a job from URL (backend will scrape and parse)
  /// POST /api/v1/jobs
  Future<Job> createFromUrl({
    required String url,
    JobSource source = JobSource.urlImport,
  }) async {
    try {
      final response = await _client.post(
        '/jobs',
        data: {
          'source': _sourceToString(source),
          'url': url,
        },
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Job.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create a job from structured data (e.g., when saving a browsed job)
  /// POST /api/v1/jobs
  Future<Job> createJob({
    required JobSource source,
    required String title,
    required String company,
    String? location,
    String? description,
    List<String>? requirements,
    List<String>? benefits,
    String? salaryRange,
    bool? remote,
  }) async {
    try {
      final response = await _client.post(
        '/jobs',
        data: {
          'source': _sourceToString(source),
          'title': title,
          'company': company,
          if (location != null) 'location': location,
          if (description != null) 'description': description,
          if (requirements != null) 'requirements': requirements,
          if (benefits != null) 'benefits': benefits,
          if (salaryRange != null) 'salary_range': salaryRange,
          if (remote != null) 'remote': remote,
        },
      );

      // Convert snake_case response to camelCase before parsing
      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Job.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get user's saved jobs with optional filters
  /// GET /api/v1/jobs
  Future<JobListResponse> getUserJobs({
    JobStatus? status,
    JobSource? source,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (status != null) {
        queryParams['status'] = _statusToString(status);
      }

      if (source != null) {
        queryParams['source'] = _sourceToString(source);
      }

      final response = await _client.get(
        '/jobs',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;

      return JobListResponse(
        jobs: (data['jobs'] as List)
            .map((json) {
              final camelCaseJson = _toCamelCase(json as Map<String, dynamic>);
              return Job.fromJson(camelCaseJson);
            })
            .toList(),
        total: data['total'] as int,
        pagination: PaginationMeta.fromJson(
            data['pagination'] as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Browse mock/external jobs (no authentication required for discovery)
  /// GET /api/v1/jobs/browse
  Future<BrowseJobListResponse> browseJobs({
    String? query,
    String? location,
    bool? remote,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (query != null && query.isNotEmpty) {
        queryParams['query'] = query;
      }

      if (location != null && location.isNotEmpty) {
        queryParams['location'] = location;
      }

      if (remote != null) {
        queryParams['remote'] = remote;
      }

      final response = await _client.get(
        '/jobs/browse',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;

      return BrowseJobListResponse(
        jobs: (data['jobs'] as List)
            .map((json) {
              final camelCaseJson = _toCamelCase(json as Map<String, dynamic>);
              return BrowseJob.fromJson(camelCaseJson);
            })
            .toList(),
        total: data['total'] as int,
        pagination: PaginationMeta.fromJson(
            data['pagination'] as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get job details by ID
  /// GET /api/v1/jobs/{id}
  Future<Job> getJobById(String jobId) async {
    try {
      final response = await _client.get('/jobs/$jobId');

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Job.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Update job details
  /// PUT /api/v1/jobs/{id}
  Future<Job> updateJob({
    required String jobId,
    String? title,
    String? company,
    String? location,
    String? description,
    List<String>? requirements,
    List<String>? benefits,
    String? salaryRange,
    bool? remote,
    JobStatus? status,
  }) async {
    try {
      final updateData = <String, dynamic>{};

      if (title != null) updateData['title'] = title;
      if (company != null) updateData['company'] = company;
      if (location != null) updateData['location'] = location;
      if (description != null) updateData['description'] = description;
      if (requirements != null) updateData['requirements'] = requirements;
      if (benefits != null) updateData['benefits'] = benefits;
      if (salaryRange != null) updateData['salary_range'] = salaryRange;
      if (remote != null) updateData['remote'] = remote;
      if (status != null) updateData['status'] = _statusToString(status);

      final response = await _client.put(
        '/jobs/$jobId',
        data: updateData,
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Job.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete job (hard delete)
  /// DELETE /api/v1/jobs/{id}
  Future<void> deleteJob(String jobId) async {
    try {
      await _client.delete('/jobs/$jobId');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Helper methods for enum conversions
  String _sourceToString(JobSource source) {
    switch (source) {
      case JobSource.userCreated:
        return 'user_created';
      case JobSource.indeed:
        return 'indeed';
      case JobSource.linkedin:
        return 'linkedin';
      case JobSource.glassdoor:
        return 'glassdoor';
      case JobSource.mock:
        return 'mock';
      case JobSource.imported:
        return 'imported';
      case JobSource.urlImport:
        return 'url_import';
    }
  }

  String _statusToString(JobStatus status) {
    switch (status) {
      case JobStatus.active:
        return 'active';
      case JobStatus.archived:
        return 'archived';
      case JobStatus.draft:
        return 'draft';
    }
  }

  // Error handling
  String _handleError(DioException error) {
    if (error.error is String) {
      return error.error as String;
    }

    // Extract error message from response
    if (error.response != null) {
      final data = error.response!.data;
      if (data is Map && data.containsKey('detail')) {
        if (data['detail'] is String) {
          return data['detail'];
        }
      }
    }

    // Default error messages based on status code
    switch (error.response?.statusCode) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Please log in to continue.';
      case 403:
        return 'You don\'t have permission to perform this action.';
      case 404:
        return 'Job not found.';
      case 422:
        return 'Failed to parse job description. Please try again.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return 'An error occurred. Please try again.';
    }
  }
}

// Provider for JobsApiClient
final jobsApiClientProvider = Provider<JobsApiClient>((ref) {
  final client = ref.watch(baseHttpClientProvider);
  return JobsApiClient(client);
});
