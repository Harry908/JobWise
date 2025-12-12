import 'package:dio/dio.dart';
import '../../models/exported_file.dart';
import '../../models/template.dart' as template_models;

class ExportsApiClient {
  final Dio _dio;

  ExportsApiClient(this._dio);

  Future<ExportedFile> exportToPDF({
    required String generationId,
    required String templateId,
    Map<String, dynamic>? options,
    Function(double)? onProgress,
  }) async {
    try {
      final requestData = {
        'generation_id': generationId,
        'template': templateId,
        'format': 'pdf',
        if (options != null) 'options': options,
      };

      final response = await _dio.post(
        '/api/v1/exports/pdf',
        data: requestData,
        onSendProgress: (sent, total) {
          if (onProgress != null && total != -1) {
            onProgress(sent / total);
          }
        },
      );

      return ExportedFile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<ExportedFile> exportToDOCX({
    required String generationId,
    required String templateId,
    Map<String, dynamic>? options,
    Function(double)? onProgress,
  }) async {
    try {
      final requestData = {
        'generation_id': generationId,
        'template': templateId,
        'format': 'docx',
        if (options != null) 'options': options,
      };

      final response = await _dio.post(
        '/api/v1/exports/docx',
        data: requestData,
        onSendProgress: (sent, total) {
          if (onProgress != null && total != -1) {
            onProgress(sent / total);
          }
        },
      );

      return ExportedFile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<ExportedFile> batchExport({
    required List<String> generationIds,
    required String templateId,
    required String format,
    Map<String, dynamic>? options,
  }) async {
    try {
      final requestData = {
        'generation_ids': generationIds,
        'template': templateId,
        'format': format,
        if (options != null) 'options': options,
      };

      final response = await _dio.post(
        '/api/v1/exports/batch',
        data: requestData,
      );

      return ExportedFile.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<template_models.Template>> getTemplates() async {
    try {
      final response = await _dio.get('/api/v1/exports/templates');

      final templatesData = response.data['templates'] as List;
      return templatesData.map((json) => template_models.Template.fromJson(json)).toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<template_models.Template> getTemplate(String templateId) async {
    try {
      final response = await _dio.get('/api/v1/exports/templates/$templateId');
      return template_models.Template.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<Map<String, dynamic>> getExportedFiles({
    String? jobId,
    String? format,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };

      if (jobId != null) queryParams['job_id'] = jobId;
      if (format != null) queryParams['format'] = format;

      final response = await _dio.get(
        '/api/v1/exports/files',
        queryParameters: queryParams,
      );

      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<String> getDownloadUrl(String exportId) async {
    try {
      final response = await _dio.get('/api/v1/exports/files/$exportId/download');
      return response.data['download_url'];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> downloadFile({
    required String exportId,
    required String savePath,
    Function(double)? onProgress,
  }) async {
    try {
      await _dio.download(
        '/api/v1/exports/files/$exportId/download',
        savePath,
        onReceiveProgress: (received, total) {
          if (onProgress != null && total != -1) {
            onProgress(received / total);
          }
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteFile(String exportId) async {
    try {
      await _dio.delete('/api/v1/exports/files/$exportId');
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
      return Exception('Server error: ${error.response?.statusCode}');
    }
    if (error.type == DioExceptionType.connectionTimeout) {
      return Exception('Connection timeout. Please check your internet connection.');
    }
    if (error.type == DioExceptionType.receiveTimeout) {
      return Exception('Server took too long to respond.');
    }
    return Exception('Network error occurred. Please try again.');
  }
}
