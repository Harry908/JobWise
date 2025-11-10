import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/generation.dart';
import 'base_http_client.dart';
import '../../providers/auth_provider.dart'; // For baseHttpClientProvider

/// Helper function to convert snake_case keys to camelCase
Map<String, dynamic> _toCamelCase(Map<String, dynamic> json) {
  final result = <String, dynamic>{};
  json.forEach((key, value) {
    final camelKey = key.replaceAllMapped(
      RegExp(r'_([a-z])'),
      (match) => match.group(1)!.toUpperCase(),
    );

    // Recursively handle nested maps
    if (value is Map<String, dynamic>) {
      result[camelKey] = _toCamelCase(value);
    } else if (value is List) {
      result[camelKey] = value.map((item) {
        if (item is Map<String, dynamic>) {
          return _toCamelCase(item);
        }
        return item;
      }).toList();
    } else {
      result[camelKey] = value;
    }
  });
  return result;
}

/// API client for generation-related endpoints
class GenerationApiClient {
  final BaseHttpClient _client;

  GenerationApiClient(this._client);

  /// Start resume generation
  /// POST /api/v1/generations/resume
  Future<Generation> startResumeGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    try {
      final response = await _client.post(
        '/generations/resume',
        data: {
          'profile_id': profileId,
          'job_id': jobId,
          if (options != null)
            'options': GenerationOptions.toRequestJson(options),
        },
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Start cover letter generation
  /// POST /api/v1/generations/cover-letter
  Future<Generation> startCoverLetterGeneration({
    required String profileId,
    required String jobId,
    GenerationOptions? options,
  }) async {
    try {
      final response = await _client.post(
        '/generations/cover-letter',
        data: {
          'profile_id': profileId,
          'job_id': jobId,
          if (options != null)
            'options': GenerationOptions.toRequestJson(options),
        },
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get generation status (for polling)
  /// GET /api/v1/generations/{id}
  Future<Generation> getGenerationStatus(String id) async {
    try {
      final response = await _client.get('/generations/$id');

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get final generation result with full content
  /// GET /api/v1/generations/{id}/result
  Future<Map<String, dynamic>> getGenerationResult(String id) async {
    try {
      final response = await _client.get('/generations/$id/result');

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return camelCaseData;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Regenerate with updated options
  /// POST /api/v1/generations/{id}/regenerate
  Future<Generation> regenerateGeneration({
    required String id,
    GenerationOptions? options,
  }) async {
    try {
      final response = await _client.post(
        '/generations/$id/regenerate',
        data: {
          if (options != null)
            'options': GenerationOptions.toRequestJson(options),
        },
      );

      final camelCaseData = _toCamelCase(response.data as Map<String, dynamic>);
      return Generation.fromJson(camelCaseData);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// List user's generations with optional filters
  /// GET /api/v1/generations
  Future<(List<GenerationListItem>, Pagination, GenerationStatistics)>
      getGenerations({
    String? jobId,
    GenerationStatus? status,
    DocumentType? documentType,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (jobId != null) queryParams['job_id'] = jobId;
      if (status != null) queryParams['status'] = _statusToString(status);
      if (documentType != null) {
        queryParams['document_type'] = _documentTypeToString(documentType);
      }

      final response = await _client.get(
        '/generations',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;

      // Parse generations list
      final generationsList = (data['generations'] as List)
          .map((json) => GenerationListItem.fromJson(
              _toCamelCase(json as Map<String, dynamic>)))
          .toList();

      // Parse pagination
      final pagination =
          Pagination.fromJson(_toCamelCase(data['pagination'] as Map<String, dynamic>));

      // Parse statistics
      final statistics = GenerationStatistics.fromJson(
          _toCamelCase(data['statistics'] as Map<String, dynamic>));

      return (generationsList, pagination, statistics);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Cancel ongoing generation or delete completed generation
  /// DELETE /api/v1/generations/{id}
  Future<void> cancelGeneration(String id) async {
    try {
      await _client.delete('/generations/$id');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get available templates
  /// GET /api/v1/generations/templates
  Future<List<Template>> getTemplates() async {
    try {
      final response = await _client.get('/generations/templates');

      final data = response.data as Map<String, dynamic>;
      final templatesList = (data['templates'] as List)
          .map((json) =>
              Template.fromJson(_toCamelCase(json as Map<String, dynamic>)))
          .toList();

      return templatesList;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Poll generation until completion (returns stream)
  ///
  /// Polls every 2 seconds by default
  /// Stops when generation is no longer processing (completed, failed, or cancelled)
  /// Throws TimeoutException if polling exceeds maxAttempts
  Stream<Generation> pollGeneration(
    String id, {
    Duration interval = const Duration(seconds: 2),
    int maxAttempts = 60, // 2 minutes max (20x expected 6s duration)
  }) async* {
    int attempts = 0;

    while (attempts < maxAttempts) {
      final generation = await getGenerationStatus(id);
      yield generation;

      // Stop polling if not processing anymore
      if (!generation.isProcessing) {
        break;
      }

      await Future.delayed(interval);
      attempts++;
    }

    if (attempts >= maxAttempts) {
      throw TimeoutException(
        'Generation polling timeout after ${maxAttempts * interval.inSeconds} seconds',
      );
    }
  }

  /// Helper: Convert GenerationStatus enum to string
  String _statusToString(GenerationStatus status) {
    switch (status) {
      case GenerationStatus.pending:
        return 'pending';
      case GenerationStatus.generating:
        return 'generating';
      case GenerationStatus.completed:
        return 'completed';
      case GenerationStatus.failed:
        return 'failed';
      case GenerationStatus.cancelled:
        return 'cancelled';
    }
  }

  /// Helper: Convert DocumentType enum to string
  String _documentTypeToString(DocumentType type) {
    switch (type) {
      case DocumentType.resume:
        return 'resume';
      case DocumentType.coverLetter:
        return 'cover_letter';
    }
  }

  /// Handle Dio errors and convert to user-friendly exceptions
  Exception _handleError(DioException e) {
    if (e.response != null) {
      final statusCode = e.response!.statusCode;
      final data = e.response!.data;

      // Handle structured error responses
      if (data is Map<String, dynamic> && data.containsKey('error')) {
        final error = data['error'] as Map<String, dynamic>;
        final code = error['code'] as String?;
        final message = error['message'] as String?;
        final details = error['details'] as Map<String, dynamic>?;

        // Special handling for rate limiting
        if (statusCode == 429) {
          return RateLimitException(
            message: message ?? 'Too many requests',
            retryAfter: details?['retry_after'] as int?,
            currentUsage: details?['current_usage'] as int?,
            limit: details?['limit'] as int?,
            resetAt: details?['reset_at'] as String?,
          );
        }

        return ApiException(
          statusCode: statusCode ?? 500,
          code: code ?? 'unknown_error',
          message: message ?? 'An error occurred',
          details: details,
        );
      }

      return ApiException(
        statusCode: statusCode ?? 500,
        message: e.response!.statusMessage ?? 'An error occurred',
      );
    }

    // Network errors
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return NetworkException('Connection timeout. Please check your internet connection.');
    }

    if (e.type == DioExceptionType.unknown) {
      return NetworkException('Network error. Please check your internet connection.');
    }

    return Exception('Unexpected error: ${e.message}');
  }
}

/// Custom exception for API errors
class ApiException implements Exception {
  final int statusCode;
  final String? code;
  final String message;
  final Map<String, dynamic>? details;

  ApiException({
    required this.statusCode,
    this.code,
    required this.message,
    this.details,
  });

  @override
  String toString() => message;
}

/// Custom exception for rate limiting
class RateLimitException implements Exception {
  final String message;
  final int? retryAfter; // seconds
  final int? currentUsage;
  final int? limit;
  final String? resetAt; // ISO 8601 timestamp

  RateLimitException({
    required this.message,
    this.retryAfter,
    this.currentUsage,
    this.limit,
    this.resetAt,
  });

  @override
  String toString() => message;

  /// Get DateTime when rate limit resets
  DateTime? get resetTime {
    if (resetAt != null) {
      return DateTime.tryParse(resetAt!);
    }
    if (retryAfter != null) {
      return DateTime.now().add(Duration(seconds: retryAfter!));
    }
    return null;
  }
}

/// Custom exception for network errors
class NetworkException implements Exception {
  final String message;

  NetworkException(this.message);

  @override
  String toString() => message;
}

// ============================================================================
// RIVERPOD PROVIDER
// ============================================================================

/// Provider for GenerationApiClient
/// This provider is referenced by generation_provider.dart
final generationApiClientProvider = Provider<GenerationApiClient>((ref) {
  final client = ref.watch(baseHttpClientProvider);
  return GenerationApiClient(client);
});
