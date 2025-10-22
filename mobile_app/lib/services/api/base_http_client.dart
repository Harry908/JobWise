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
          handler.next(options);
        },
        onError: (error, handler) async {
          // Auto retry on 401 (token expired)
          if (error.response?.statusCode == 401) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry original request with new token
              final opts = error.requestOptions;
              final newToken = await _storage.getToken();
              opts.headers['Authorization'] = 'Bearer $newToken';
              final response = await _dio.fetch(opts);
              return handler.resolve(response);
            }
          }

          // Handle other errors by extracting meaningful error messages
          if (error.response != null) {
            final data = error.response!.data;

            String errorMessage = 'An error occurred';

            if (data is Map<String, dynamic>) {
              // Try to extract error message from response
              if (data.containsKey('detail')) {
                errorMessage = data['detail'].toString();
              } else if (data.containsKey('message')) {
                errorMessage = data['message'].toString();
              } else if (data.containsKey('error')) {
                errorMessage = data['error'].toString();
              }
            } else if (data is String) {
              errorMessage = data;
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

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      await _storage.saveTokens(
        response.data['access_token'],
        response.data['refresh_token'],
      );
      return true;
    } catch (e) {
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

  Future<Response> delete(String path) {
    return _dio.delete(path);
  }

  Future<Response> patch(String path, {dynamic data}) {
    return _dio.patch(path, data: data);
  }
}