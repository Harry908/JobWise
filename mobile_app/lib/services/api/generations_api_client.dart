import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/sample.dart';
import 'base_http_client.dart';
import '../../providers/auth_provider.dart';

/// API client for V3 generation endpoints
class GenerationsApiClient {
  final BaseHttpClient _client;

  GenerationsApiClient(this._client);

  /// Upload a sample document (resume or cover letter)
  /// POST /api/v1/samples/upload
  ///
  /// Parameters:
  /// - [file]: PlatformFile from file_picker (must be .txt file)
  /// - [documentType]: 'resume' or 'cover_letter'
  ///
  /// Throws:
  /// - Exception with message if upload fails
  /// - DioException for network errors
  Future<Sample> uploadSample({
    required PlatformFile file,
    required String documentType,
  }) async {
    try {
      // Validate file exists and has path
      if (file.path == null) {
        throw Exception('File path is null. Cannot upload file.');
      }

      // Validate file extension
      if (!file.name.toLowerCase().endsWith('.txt')) {
        throw Exception('Only .txt files are supported');
      }

      // Validate document type
      if (documentType != 'resume' && documentType != 'cover_letter') {
        throw Exception(
            'Invalid document type. Must be "resume" or "cover_letter"');
      }

      // Create FormData with file and document type
      final formData = FormData.fromMap({
        'document_type': documentType,
        'file': await MultipartFile.fromFile(
          file.path!,
          filename: file.name,
        ),
      });

      // Send POST request
      final response = await _client.post(
        '/samples/upload',
        data: formData,
      );

      // Parse response - backend returns snake_case, convert to camelCase
      final responseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Sample.fromJson(responseData);
    } on DioException catch (e) {
      throw _handleError(e);
    } catch (e) {
      // Re-throw validation errors
      rethrow;
    }
  }

  /// Convert snake_case keys to camelCase for Freezed models
  Map<String, dynamic> _toCamelCase(Map<String, dynamic> json) {
    final result = <String, dynamic>{};
    json.forEach((key, value) {
      final camelKey = key.replaceAllMapped(
        RegExp(r'_([a-z])'),
        (match) => match.group(1)!.toUpperCase(),
      );

      // Handle nested lists
      if (value is List) {
        result[camelKey] = value
            .map((item) =>
                item is Map<String, dynamic> ? _toCamelCase(item) : item)
            .toList();
      }
      // Handle nested maps
      else if (value is Map<String, dynamic>) {
        result[camelKey] = _toCamelCase(value);
      }
      // Handle regular values
      else {
        result[camelKey] = value;
      }
    });
    return result;
  }

  /// Get list of sample documents
  /// GET /api/v1/samples
  Future<SampleListResponse> getSamples() async {
    try {
      final response = await _client.get('/samples');
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return SampleListResponse.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete a sample document
  /// DELETE /api/v1/samples/{id}
  Future<void> deleteSample(String sampleId) async {
    try {
      await _client.delete('/samples/$sampleId');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate resume for a job
  /// POST /api/v1/generations/resume
  // TODO: Implement after creating V3-compatible Generation model
  // Currently Generation model in generation.dart has different structure than V3 API
  /* 
  Future<Generation> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
  }) async {
    try {
      final response = await _client.post(
        '/generations/resume',
        data: {
          'job_id': jobId,
          'max_experiences': maxExperiences,
          'max_projects': maxProjects,
          'include_summary': includeSummary,
        },
      );
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate cover letter for a job
  /// POST /api/v1/generations/cover-letter
  Future<Generation> generateCoverLetter({
    required String jobId,
    String tone = 'professional',
    String length = 'medium',
  }) async {
    try {
      final response = await _client.post(
        '/generations/cover-letter',
        data: {
          'job_id': jobId,
          'tone': tone,
          'length': length,
        },
      );
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create job-specific rankings
  /// POST /api/v1/rankings/create
  Future<Ranking> createRankings({required String jobId}) async {
    try {
      final response = await _client.post(
        '/rankings/create',
        data: {'job_id': jobId},
      );
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return Ranking.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get rankings for a job
  /// GET /api/v1/rankings/job/{job_id}
  Future<Ranking> getRankingsForJob(String jobId) async {
    try {
      final response = await _client.get('/rankings/job/$jobId');
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return Ranking.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Enhance profile with AI
  /// POST /api/v1/profile/enhance
  Future<ProfileEnhancementResponse> enhanceProfile({
    required String profileId,
    List<String>? sampleIds,
  }) async {
    try {
      final response = await _client.post(
        '/profile/enhance',
        data: {
          'profile_id': profileId,
          if (sampleIds != null) 'sample_ids': sampleIds,
        },
      );
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return ProfileEnhancementResponse.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get generation history
  /// GET /api/v1/generations/history
  Future<GenerationHistoryResponse> getGenerationHistory({
    String? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = {
        'limit': limit.toString(),
        'offset': offset.toString(),
        if (documentType != null) 'document_type': documentType,
      };
      final response = await _client.get(
        '/generations/history',
        queryParameters: queryParams,
      );
      final data = _toCamelCase(response.data as Map<String, dynamic>);
      return GenerationHistoryResponse.fromJson(data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }
  */

  /// Extract meaningful error messages from DioException
  Exception _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response!.data;
      final statusCode = error.response!.statusCode;

      // Try to extract error message from response
      String? errorMessage;
      if (data is Map<String, dynamic>) {
        errorMessage = data['detail']?.toString();
      } else if (data is String) {
        errorMessage = data;
      }

      // Default messages based on status code
      switch (statusCode) {
        case 400:
          return Exception(errorMessage ?? 'Invalid file or request');
        case 401:
          return Exception('Authentication required. Please log in again.');
        case 404:
          return Exception(errorMessage ?? 'Resource not found');
        case 413:
          return Exception('File size exceeds 1MB limit');
        case 422:
          return Exception(errorMessage ?? 'Invalid file format');
        case 500:
          return Exception('Server error. Please try again later.');
        default:
          return Exception(errorMessage ?? 'Request failed. Please try again.');
      }
    }

    // Network errors
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout) {
      return Exception('Connection timeout. Please check your internet.');
    }

    return Exception('Network error. Please try again.');
  }
}

/// Provider for GenerationsApiClient
final generationsApiClientProvider = Provider<GenerationsApiClient>((ref) {
  final baseClient = ref.watch(baseHttpClientProvider);
  return GenerationsApiClient(baseClient);
});
