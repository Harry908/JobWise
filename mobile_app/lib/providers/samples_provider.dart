import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api/base_http_client.dart';
import 'auth_provider.dart';

/// State for sample documents (resumes and cover letters)
class SamplesState {
  final List<Sample> samples;
  final bool isLoading;
  final String? errorMessage;

  const SamplesState({
    this.samples = const [],
    this.isLoading = false,
    this.errorMessage,
  });

  SamplesState copyWith({
    List<Sample>? samples,
    bool? isLoading,
    String? errorMessage,
  }) {
    return SamplesState(
      samples: samples ?? this.samples,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  // Convenience getters
  List<Sample> get resumes =>
      samples.where((s) => s.documentType == 'resume').toList();

  List<Sample> get coverLetters =>
      samples.where((s) => s.documentType == 'cover_letter').toList();

  List<Sample> get resumeSamples => resumes;
  
  Sample? get activeResumeSample =>
      resumes.where((s) => s.isActive).isNotEmpty 
          ? resumes.where((s) => s.isActive).first 
          : null;
  
  Sample? get activeCoverLetterSample =>
      coverLetters.where((s) => s.isActive).isNotEmpty
          ? coverLetters.where((s) => s.isActive).first 
          : null;
}

/// Samples provider using StateNotifier
class SamplesNotifier extends StateNotifier<SamplesState> {
  final SamplesApiClient _apiClient;

  SamplesNotifier(this._apiClient) : super(const SamplesState());

  /// Load all samples for the current user
  Future<void> loadSamples() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final samples = await _apiClient.getSamples();
      state = state.copyWith(samples: samples, isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: e.toString(),
      );
    }
  }

  /// Upload a new sample document
  Future<void> uploadSample({
    required String documentType,
    required String fileName,
    required List<int> fileBytes,
  }) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final sample = await _apiClient.uploadSample(
        documentType: documentType,
        fileName: fileName,
        fileBytes: fileBytes,
      );

      // Add new sample to list
      state = state.copyWith(
        samples: [...state.samples, sample],
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

  /// Delete a sample by ID
  Future<void> deleteSample(String sampleId) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _apiClient.deleteSample(sampleId);

      // Remove sample from list
      state = state.copyWith(
        samples: state.samples.where((s) => s.id != sampleId).toList(),
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

  /// Clear error message
  void clearError() {
    state = state.copyWith(errorMessage: null);
  }
}

/// Provider for samples management
final samplesProvider =
    StateNotifierProvider<SamplesNotifier, SamplesState>((ref) {
  final apiClient = ref.watch(samplesApiClientProvider);
  return SamplesNotifier(apiClient);
});

/// Sample model matching backend API response
class Sample {
  final String id;
  final int userId;
  final String documentType; // 'resume' or 'cover_letter'
  final String originalFilename;
  final String? fullText; // Only included in detail responses
  final int wordCount;
  final int characterCount;
  final Map<String, dynamic>? writingStyle; // Optional AI-derived style
  final bool isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const Sample({
    required this.id,
    required this.userId,
    required this.documentType,
    required this.originalFilename,
    this.fullText,
    required this.wordCount,
    required this.characterCount,
    this.writingStyle,
    required this.isActive,
    required this.createdAt,
    this.updatedAt,
  });

  factory Sample.fromJson(Map<String, dynamic> json) {
    return Sample(
      id: json['id'] as String,
      userId: json['user_id'] as int,
      documentType: json['document_type'] as String,
      originalFilename: json['original_filename'] as String,
      fullText: json['full_text'] as String?,
      wordCount: json['word_count'] as int,
      characterCount: json['character_count'] as int,
      writingStyle: json['writing_style'] as Map<String, dynamic>?,
      isActive: json['is_active'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'] as String) 
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'document_type': documentType,
      'original_filename': originalFilename,
      if (fullText != null) 'full_text': fullText,
      'word_count': wordCount,
      'character_count': characterCount,
      if (writingStyle != null) 'writing_style': writingStyle,
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
      if (updatedAt != null) 'updated_at': updatedAt!.toIso8601String(),
    };
  }
  
  // Convenience getter for display
  String get fileName => originalFilename;
}

/// API Client for samples
class SamplesApiClient {
  final BaseHttpClient _httpClient;

  SamplesApiClient(this._httpClient);

  /// Get all samples for the current user
  /// GET /api/v1/samples
  Future<List<Sample>> getSamples() async {
    try {
      final response = await _httpClient.get('/samples');
      final data = response.data as Map<String, dynamic>;
      final samples = data['samples'] as List;
      return samples.map((json) => Sample.fromJson(json as Map<String, dynamic>)).toList();
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Get a specific sample by ID
  /// GET /api/v1/samples/{id}
  Future<Sample> getSample(String sampleId) async {
    try {
      final response = await _httpClient.get('/samples/$sampleId');
      return Sample.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Upload a new sample document (.txt only)
  /// POST /api/v1/samples/upload
  Future<Sample> uploadSample({
    required String documentType,
    required String fileName,
    required List<int> fileBytes,
  }) async {
    try {
      // Validate file extension
      if (!fileName.toLowerCase().endsWith('.txt')) {
        throw Exception('Only .txt files are supported for sample uploads.');
      }

      // Validate file size (1MB limit per API spec)
      if (fileBytes.length > 1 * 1024 * 1024) {
        throw Exception('File size exceeds 1MB limit.');
      }

      // Prepare form data with proper multipart file
      final formData = FormData.fromMap({
        'document_type': documentType,
        'file': MultipartFile.fromBytes(
          fileBytes,
          filename: fileName,
        ),
      });

      final response = await _httpClient.post(
        '/samples/upload',
        data: formData,
      );

      return Sample.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw _handleError(e);
    }
  }

  /// Delete a sample
  /// DELETE /api/v1/samples/{id}
  Future<void> deleteSample(String sampleId) async {
    try {
      await _httpClient.delete('/samples/$sampleId');
    } catch (e) {
      throw _handleError(e);
    }
  }

  String _handleError(dynamic error) {
    if (error is DioException) {
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
          return 'Please log in to upload samples.';
        case 403:
          return 'You don\'t have permission to perform this action.';
        case 404:
          return 'Sample not found.';
        case 413:
          return 'File size too large. Maximum allowed size is 1 MB.';
        case 422:
          return 'Invalid file format. Only .txt files are supported.';
        case 429:
          return 'Too many requests. Please try again later.';
        case 500:
          return 'Server error. Please try again later.';
        default:
          return 'An error occurred. Please try again.';
      }
    }
    return error.toString();
  }
}

final samplesApiClientProvider = Provider<SamplesApiClient>((ref) {
  final httpClient = ref.watch(baseHttpClientProvider);
  return SamplesApiClient(httpClient);
});
