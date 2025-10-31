import 'dart:developer' as developer;
import 'package:dio/dio.dart';
import '../storage_service.dart';

class BaseHttpClient {
  final Dio _dio;
  final StorageService _storage;

  BaseHttpClient({
    required String baseUrl,
    required StorageService storage,
  })  : _storage = storage,
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        )) {
    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token to all requests
          final token = await _storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }

          // Log outgoing request
          developer.log(
            'HTTP Request: ${options.method} ${options.uri}',
            name: 'HTTP',
          );

          handler.next(options);
        },
        onResponse: (response, handler) {
          // Log successful response
          developer.log(
            'HTTP Response: ${response.statusCode} ${response.requestOptions.method} ${response.requestOptions.uri}',
            name: 'HTTP',
          );
          developer.log(
            'Response data type: ${response.data.runtimeType}',
            name: 'HTTP',
          );
          if (response.data != null) {
            developer.log(
              'Response data: ${response.data}',
              name: 'HTTP',
            );
          }

          handler.next(response);
        },
        onError: (error, handler) async {
          // Auto retry on 401 (token expired) - but NOT for refresh endpoint itself
          if (error.response?.statusCode == 401 && 
              !error.requestOptions.path.contains('/auth/refresh')) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry original request with new token
              final opts = error.requestOptions;
              final newToken = await _storage.getToken();
              opts.headers['Authorization'] = 'Bearer $newToken';
              try {
                final response = await _dio.fetch(opts);
                return handler.resolve(response);
              } catch (retryError) {
                // If retry fails, pass the error through
                return handler.next(error);
              }
            } else {
              // Refresh failed - clear tokens and pass error through
              developer.log(
                'Token refresh failed, user needs to log in again',
                name: 'HTTP',
              );
            }
          }

          // Handle other errors by extracting meaningful error messages
          if (error.response != null) {
            final data = error.response!.data;
            final statusCode = error.response!.statusCode;

            String errorMessage = _extractErrorMessage(data, statusCode);

            // Log error details
            developer.log(
              'HTTP Error: $statusCode ${error.requestOptions.method} ${error.requestOptions.uri} - $errorMessage',
              name: 'HTTP',
            );

            // Only log full response data for non-422 errors
            if (statusCode != 422) {
              developer.log(
                'Response data: $data',
                name: 'HTTP',
              );
            }

            // Create a new DioError with the extracted message
            final newError = DioException(
              requestOptions: error.requestOptions,
              response: error.response,
              type: error.type,
              error: errorMessage,
            );

            handler.next(newError);
          } else {
            handler.next(error);
          }
        },
      ),
    );
  }

  String _extractErrorMessage(dynamic data, int? statusCode) {
    // Handle 422 Unprocessable Entity (validation errors) specifically
    if (statusCode == 422 && data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is List && detail.isNotEmpty) {
        // FastAPI validation errors come as a list of field errors
        final firstError = detail[0];
        if (firstError is Map<String, dynamic>) {
          // Return just the message, not the field name
          final message = firstError['msg']?.toString() ?? 'Invalid input';
          return message;
        }
        return detail[0].toString();
      }
    }

    // Handle other error formats
    if (data is Map<String, dynamic>) {
      // Try to extract error message from response
      if (data.containsKey('detail')) {
        final detail = data['detail'];
        if (detail is String) {
          return detail;
        } else if (detail is List && detail.isNotEmpty) {
          return detail[0].toString();
        }
      }
      if (data.containsKey('message')) {
        return data['message'].toString();
      }
      if (data.containsKey('error')) {
        return data['error'].toString();
      }
    } else if (data is String) {
      return data;
    }

    // Default error messages based on status code
    switch (statusCode) {
      case 400:
        return 'Bad request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in again.';
      case 403:
        return 'Access denied. You don\'t have permission.';
      case 404:
        return 'Resource not found.';
      case 409:
        return 'This email is already registered.';
      case 422:
        return 'Please check your input and try again.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return 'An error occurred. Please try again.';
    }
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) {
        developer.log('No refresh token available', name: 'HTTP');
        return false;
      }

      developer.log('Attempting token refresh', name: 'HTTP');

      // Create a separate Dio instance without interceptors to avoid infinite loop
      final refreshDio = Dio(BaseOptions(
        baseUrl: _dio.options.baseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ));

      final response = await refreshDio.post('/api/v1/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      await _storage.saveTokens(
        response.data['access_token'],
        response.data['refresh_token'],
      );
      
      developer.log('Token refresh successful', name: 'HTTP');
      return true;
    } catch (e) {
      developer.log('Token refresh failed: $e', name: 'HTTP');
      await _storage.clearTokens();
      return false;
    }
  }

  // Expose HTTP methods
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }

  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }

  Future<Response> put(String path, {dynamic data}) {
    return _dio.put(path, data: data);
  }

  Future<Response> delete(String path, {dynamic data}) {
    return _dio.delete(path, data: data);
  }

  Future<Response> patch(String path, {dynamic data}) {
    return _dio.patch(path, data: data);
  }
}