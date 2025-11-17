// lib/services/api/preference_api_client.dart

import 'dart:io';
import 'package:dio/dio.dart';
import 'package:mime/mime.dart';
import 'package:http_parser/http_parser.dart';
import '../../models/preferences/example_resume.dart';
import '../../models/preferences/layout_config.dart';
import '../../models/preferences/writing_style_config.dart';
import '../../models/preferences/user_generation_profile.dart';
import 'base_http_client.dart';

class PreferenceApiClient {
  final BaseHttpClient _client;

  PreferenceApiClient(this._client);

  /// Upload sample resume and extract layout preferences
  Future<UploadResumeResult> uploadSampleResume({
    required File file,
    bool isPrimary = false,
    Function(int, int)? onUploadProgress,
  }) async {
    try {
      // Get MIME type
      final mimeType = lookupMimeType(file.path) ?? 'application/octet-stream';
      final contentType = MediaType.parse(mimeType);

      // Create multipart file
      final multipartFile = await MultipartFile.fromFile(
        file.path,
        filename: file.path.split(Platform.pathSeparator).last,
        contentType: contentType,
      );

      // Create form data
      final formData = FormData.fromMap({
        'file': multipartFile,
        'is_primary': isPrimary,
      });

      // Upload - BaseHttpClient handles auth tokens
      final response = await _client.post(
        '/preferences/upload-sample-resume',
        data: formData,
      );

      return UploadResumeResult.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 413) {
        throw FileUploadException(
            'File size too large. Maximum allowed size is 5 MB.');
      } else if (e.response?.statusCode == 415) {
        throw FileUploadException(
            'Unsupported file type. Please upload PDF, DOCX, or TXT.');
      }
      rethrow;
    }
  }

  /// Upload sample cover letter and extract writing style
  Future<UploadCoverLetterResult> uploadCoverLetter({
    required File file,
    Function(int, int)? onUploadProgress,
  }) async {
    try {
      // Get MIME type
      final mimeType = lookupMimeType(file.path) ?? 'application/octet-stream';
      final contentType = MediaType.parse(mimeType);

      // Create multipart file
      final multipartFile = await MultipartFile.fromFile(
        file.path,
        filename: file.path.split(Platform.pathSeparator).last,
        contentType: contentType,
      );

      // Create form data
      final formData = FormData.fromMap({
        'file': multipartFile,
      });

      // Upload - BaseHttpClient handles auth tokens
      final response = await _client.post(
        '/preferences/upload-cover-letter',
        data: formData,
      );

      return UploadCoverLetterResult.fromJson(response.data);
    } on DioException catch (e) {
      if (e.response?.statusCode == 413) {
        throw FileUploadException(
            'File size too large. Maximum allowed size is 5 MB.');
      } else if (e.response?.statusCode == 415) {
        throw FileUploadException(
            'Unsupported file type. Please upload PDF, DOCX, or TXT.');
      }
      rethrow;
    }
  }

  /// Get user's generation profile
  Future<UserGenerationProfile> getGenerationProfile() async {
    final response = await _client.get('/preferences/generation-profile');
    return UserGenerationProfile.fromJson(response.data);
  }

  /// Update generation profile settings
  Future<UserGenerationProfile> updateGenerationProfile({
    String? layoutConfigId,
    String? writingStyleConfigId,
    double? targetAtsScore,
    int? maxBulletsPerRole,
  }) async {
    final response = await _client.put(
      '/preferences/generation-profile',
      data: {
        if (layoutConfigId != null) 'layout_config_id': layoutConfigId,
        if (writingStyleConfigId != null)
          'writing_style_config_id': writingStyleConfigId,
        if (targetAtsScore != null) 'target_ats_score': targetAtsScore,
        if (maxBulletsPerRole != null)
          'max_bullets_per_role': maxBulletsPerRole,
      },
    );
    return UserGenerationProfile.fromJson(response.data);
  }

  /// List user's example resumes
  Future<List<ExampleResume>> getExampleResumes() async {
    final response = await _client.get('/preferences/example-resumes');
    final Map<String, dynamic> responseData = response.data;
    final List<dynamic> resumesJson = responseData['examples'] ?? [];
    return resumesJson.map((json) => ExampleResume.fromJson(json)).toList();
  }

  /// Delete example resume
  Future<void> deleteExampleResume(String resumeId) async {
    await _client.delete('/preferences/example-resumes/$resumeId');
  }

  /// Set primary example resume
  Future<void> setPrimaryExampleResume(String resumeId) async {
    await _client.post('/preferences/example-resumes/$resumeId/set-primary');
  }

  /// Get layout config by ID
  Future<LayoutConfig> getLayoutConfig(String id) async {
    final response = await _client.get('/preferences/layout-configs/$id');
    return LayoutConfig.fromJson(response.data);
  }

  /// Get writing style config by ID
  Future<WritingStyleConfig> getWritingStyleConfig(String id) async {
    final response =
        await _client.get('/preferences/writing-style-configs/$id');
    return WritingStyleConfig.fromJson(response.data);
  }
}

/// Result from uploading sample resume
class UploadResumeResult {
  final bool success;
  final String message;
  final String exampleResumeId;
  final String layoutConfigId;
  final Map<String, dynamic> extractionMetadata;
  final bool isPrimary;

  UploadResumeResult({
    required this.success,
    required this.message,
    required this.exampleResumeId,
    required this.layoutConfigId,
    required this.extractionMetadata,
    required this.isPrimary,
  });

  factory UploadResumeResult.fromJson(Map<String, dynamic> json) {
    return UploadResumeResult(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      exampleResumeId: json['example_resume_id'] ?? '',
      layoutConfigId: json['layout_config_id'] ?? '',
      extractionMetadata:
          json['extraction_metadata'] as Map<String, dynamic>? ?? {},
      isPrimary: json['is_primary'] ?? false,
    );
  }
}

/// Result from uploading cover letter
class UploadCoverLetterResult {
  final bool success;
  final String message;
  final String writingStyleConfigId;
  final Map<String, dynamic> extractionMetadata;

  UploadCoverLetterResult({
    required this.success,
    required this.message,
    required this.writingStyleConfigId,
    required this.extractionMetadata,
  });

  factory UploadCoverLetterResult.fromJson(Map<String, dynamic> json) {
    return UploadCoverLetterResult(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      writingStyleConfigId: json['writing_style_config_id'] ?? '',
      extractionMetadata:
          json['extraction_metadata'] as Map<String, dynamic>? ?? {},
    );
  }
}

/// Custom exception for file upload errors
class FileUploadException implements Exception {
  final String message;

  FileUploadException(this.message);

  @override
  String toString() => message;
}
