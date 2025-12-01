import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'base_http_client.dart';
import '../../providers/auth_provider.dart';

/// API client for AI generation endpoints
class GenerationsApiClient {
  final BaseHttpClient _client;

  GenerationsApiClient(this._client);

  /// Enhance profile with AI
  /// POST /profile/enhance
  Future<Map<String, dynamic>> enhanceProfile({
    required String profileId,
    String? customPrompt,
  }) async {
    try {
      final response = await _client.post(
        '/profile/enhance',
        data: {
          'profile_id': profileId,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create job-specific rankings
  /// POST /rankings/create
  Future<Map<String, dynamic>> createRankings({
    required String jobId,
    String? customPrompt,
  }) async {
    try {
      final response = await _client.post(
        '/rankings/create',
        data: {
          'job_id': jobId,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get cached rankings for a job
  /// GET /rankings/job/{job_id}
  Future<Map<String, dynamic>> getRankingsForJob(String jobId) async {
    try {
      final response = await _client.get('/rankings/job/$jobId');
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate resume for a job
  /// POST /generations/resume
  Future<Map<String, dynamic>> generateResume({
    required String jobId,
    int maxExperiences = 5,
    int maxProjects = 3,
    bool includeSummary = true,
    String? customPrompt,
  }) async {
    try {
      final response = await _client.post(
        '/generations/resume',
        data: {
          'job_id': jobId,
          'max_experiences': maxExperiences,
          'max_projects': maxProjects,
          'include_summary': includeSummary,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Generate cover letter for a job
  /// POST /generations/cover-letter
  Future<Map<String, dynamic>> generateCoverLetter({
    required String jobId,
    String? companyName,
    String? hiringManagerName,
    int maxParagraphs = 4,
    String? customPrompt,
  }) async {
    try {
      final response = await _client.post(
        '/generations/cover-letter',
        data: {
          'job_id': jobId,
          if (companyName != null) 'company_name': companyName,
          if (hiringManagerName != null) 'hiring_manager_name': hiringManagerName,
          'max_paragraphs': maxParagraphs,
          if (customPrompt != null) 'custom_prompt': customPrompt,
        },
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get generation history
  /// GET /generations/history
  Future<Map<String, dynamic>> getGenerationHistory({
    String? documentType,
    String? jobId,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
        if (documentType != null) 'document_type': documentType,
        if (jobId != null) 'job_id': jobId,
      };

      final response = await _client.get(
        '/generations/history',
        queryParameters: queryParams,
      );
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    if (error.response != null) {
      final data = error.response?.data;
      if (data is Map<String, dynamic> && data.containsKey('detail')) {
        return Exception(data['detail']);
      }
      return Exception('An error occurred: ${error.response?.statusCode}');
    }
    return Exception('Network error occurred');
  }
}

/// Provider for GenerationsApiClient
final generationsApiClientProvider = Provider<GenerationsApiClient>((ref) {
  final client = ref.watch(baseHttpClientProvider);
  return GenerationsApiClient(client);
});
