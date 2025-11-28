# API Configuration

**Version**: 1.0
**Last Updated**: November 2025

---

## Overview

This document describes the base HTTP client configuration and API connectivity setup for the JobWise mobile app.

---

## Base HTTP Client

**File**: `lib/services/api/base_http_client.dart`

### Responsibilities

1. **Dio Configuration**: Configure HTTP client with base URL, timeouts, headers
2. **Request Interceptor**: Inject JWT token into all authenticated requests
3. **Response Interceptor**: Log responses for debugging
4. **Error Interceptor**: Handle 401 errors with automatic token refresh
5. **Timeout Configuration**: Set connection and receive timeouts

### Implementation

```dart
class BaseHttpClient {
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  final Dio _dio;
  final FlutterSecureStorage _secureStorage;

  BaseHttpClient(this._secureStorage) : _dio = Dio() {
    _configureDio();
    _addInterceptors();
  }

  void _configureDio() {
    _dio.options = BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: connectTimeout,
      receiveTimeout: receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    );
  }

  void _addInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: _onRequest,
        onResponse: _onResponse,
        onError: _onError,
      ),
    );
  }

  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Add JWT token to all requests except auth endpoints
    if (!options.path.contains('/auth/')) {
      final token = await _secureStorage.read(key: 'access_token');
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  void _onResponse(
    Response response,
    ResponseInterceptorHandler handler,
  ) {
    // Log successful responses in debug mode
    print('Response [${response.statusCode}]: ${response.data}');
    handler.next(response);
  }

  Future<void> _onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Handle 401 Unauthorized - attempt token refresh
    if (err.response?.statusCode == 401) {
      final refreshed = await _refreshToken();
      if (refreshed) {
        // Retry original request with new token
        final options = err.requestOptions;
        final token = await _secureStorage.read(key: 'access_token');
        options.headers['Authorization'] = 'Bearer $token';

        try {
          final response = await _dio.fetch(options);
          return handler.resolve(response);
        } catch (e) {
          return handler.reject(err);
        }
      }
    }
    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _secureStorage.read(key: 'refresh_token');
      if (refreshToken == null) return false;

      final response = await _dio.post(
        '/api/v1/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      final newAccessToken = response.data['access_token'];
      final newRefreshToken = response.data['refresh_token'];

      await _secureStorage.write(key: 'access_token', value: newAccessToken);
      await _secureStorage.write(key: 'refresh_token', value: newRefreshToken);

      return true;
    } catch (e) {
      // Refresh failed - user needs to re-login
      await _secureStorage.deleteAll();
      return false;
    }
  }

  Dio get dio => _dio;
}
```

---

## Base URL Configuration

### Development Environments

**Android Emulator**:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```
- `10.0.2.2` is the special alias for `localhost` on Android emulator
- Port 8000 matches the backend FastAPI server

**iOS Simulator**:
```dart
static const String baseUrl = 'http://localhost:8000';
```
- iOS simulator can use `localhost` directly

**Physical Device**:
```dart
static const String baseUrl = 'http://192.168.1.10:8000';
```
- Use your computer's local IP address on the same Wi-Fi network
- Find with `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

**Production**:
```dart
static const String baseUrl = 'https://api.jobwise.app';
```
- Use HTTPS for production
- Configure in `.env` file

---

## Environment Configuration

**File**: `lib/config/environment.dart`

```dart
class Environment {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static const String environment = String.fromEnvironment(
    'ENVIRONMENT',
    defaultValue: 'development',
  );

  static bool get isDevelopment => environment == 'development';
  static bool get isProduction => environment == 'production';
}
```

**Usage**:
```dart
final client = BaseHttpClient(secureStorage);
// Automatically uses Environment.apiBaseUrl
```

---

## Error Handling

### Error Types

```dart
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException(this.message, {this.statusCode, this.data});

  @override
  String toString() => 'ApiException: $message (Status: $statusCode)';
}

class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);

  @override
  String toString() => 'NetworkException: $message';
}

class AuthenticationException implements Exception {
  final String message;
  AuthenticationException(this.message);

  @override
  String toString() => 'AuthenticationException: $message';
}
```

### Error Handler

```dart
class ApiErrorHandler {
  static Exception handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return NetworkException('Connection timeout. Please check your internet connection.');

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final message = error.response?.data['detail'] ?? 'An error occurred';

        if (statusCode == 401) {
          return AuthenticationException('Authentication failed. Please login again.');
        } else if (statusCode == 403) {
          return ApiException('Access forbidden', statusCode: statusCode);
        } else if (statusCode == 404) {
          return ApiException('Resource not found', statusCode: statusCode);
        } else if (statusCode == 422) {
          return ApiException('Validation error: $message', statusCode: statusCode);
        } else {
          return ApiException(message, statusCode: statusCode);
        }

      case DioExceptionType.cancel:
        return ApiException('Request cancelled');

      default:
        return NetworkException('Network error occurred. Please try again.');
    }
  }
}
```

---

## Token Storage

### Secure Storage

**Package**: `flutter_secure_storage: ^9.0.0`

**Implementation**:
```dart
class TokenStorage {
  final FlutterSecureStorage _storage;

  TokenStorage(this._storage);

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }

  Future<bool> hasValidToken() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
```

---

## Riverpod Providers

**File**: `lib/providers/api_providers.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';

// Secure storage provider
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

// Token storage provider
final tokenStorageProvider = Provider<TokenStorage>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  return TokenStorage(secureStorage);
});

// Base HTTP client provider
final baseHttpClientProvider = Provider<BaseHttpClient>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  return BaseHttpClient(secureStorage);
});

// Dio instance provider (for feature-specific API clients)
final dioProvider = Provider<Dio>((ref) {
  final baseClient = ref.watch(baseHttpClientProvider);
  return baseClient.dio;
});
```

---

## Testing

### Mock HTTP Client

```dart
class MockDio extends Mock implements Dio {}

void main() {
  group('BaseHttpClient', () {
    late MockDio mockDio;
    late FlutterSecureStorage mockStorage;
    late BaseHttpClient client;

    setUp(() {
      mockDio = MockDio();
      mockStorage = MockFlutterSecureStorage();
      client = BaseHttpClient(mockStorage);
    });

    test('adds Authorization header when token exists', () async {
      when(mockStorage.read(key: 'access_token'))
          .thenAnswer((_) async => 'test_token');

      final options = RequestOptions(path: '/api/v1/profiles/me');
      await client._onRequest(options, MockRequestInterceptorHandler());

      expect(options.headers['Authorization'], 'Bearer test_token');
    });

    test('refreshes token on 401 error', () async {
      when(mockStorage.read(key: 'refresh_token'))
          .thenAnswer((_) async => 'refresh_token');

      when(mockDio.post('/api/v1/auth/refresh', data: any))
          .thenAnswer((_) async => Response(
                data: {
                  'access_token': 'new_access_token',
                  'refresh_token': 'new_refresh_token',
                },
                statusCode: 200,
                requestOptions: RequestOptions(path: '/api/v1/auth/refresh'),
              ));

      final refreshed = await client._refreshToken();

      expect(refreshed, true);
      verify(mockStorage.write(key: 'access_token', value: 'new_access_token'));
      verify(mockStorage.write(key: 'refresh_token', value: 'new_refresh_token'));
    });
  });
}
```

---

## Backend Server Setup

### Start Backend Server

**PowerShell** (Windows):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Bash** (Mac/Linux):
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Network Security Configuration (Android)

**File**: `android/app/src/main/res/xml/network_security_config.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>
</network-security-config>
```

**AndroidManifest.xml**:
```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ...>
</application>
```

---

## Dependencies

```yaml
dependencies:
  dio: ^5.4.0
  flutter_secure_storage: ^9.0.0
  flutter_riverpod: ^2.4.9

dev_dependencies:
  mockito: ^5.4.4
  build_runner: ^2.4.6
```

---

**Status**: ✅ Fully Implemented
**Used By**: All API clients (Auth, Profile, Job, Generation, Export)
**Last Updated**: November 2025
