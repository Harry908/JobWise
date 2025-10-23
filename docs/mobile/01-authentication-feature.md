# Authentication Feature - Mobile Design Document

**Version**: 1.0  
**Feature**: User Registration, Login, and JWT Token Management  
**API Service**: Authentication API  
**Status**: Design Complete  
**Last Updated**: October 22, 2025

---

## Table of Contents

1. [Feature Overview](#feature-overview)
2. [API Integration](#api-integration)
3. [Data Models](#data-models)
4. [State Management](#state-management)
5. [Service Layer](#service-layer)
6. [UI Components](#ui-components)
7. [Security Implementation](#security-implementation)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)

---

## Feature Overview

### Purpose
Handle user authentication, session management, and secure token storage for the JobWise mobile application.

### User Stories
- **Registration**: As a new user, I want to create an account with email and password
- **Login**: As a returning user, I want to log in securely
- **Token Management**: As a user, I want my session to persist across app restarts
- **Auto-refresh**: As a user, I want automatic token refresh when expired

### Key Features
- Email/password registration and login
- JWT token-based authentication
- Secure token storage with flutter_secure_storage
- Automatic token refresh on 401 errors
- Password validation (client-side)
- Logout and session clearing

---

## API Integration

### Backend Connection

#### Base Configuration
```dart
// lib/config/app_config.dart
class AppConfig {
  // Development
  static const String devBaseUrl = 'http://10.0.2.2:8000'; // Android emulator
  static const String devBaseUrlIOS = 'http://localhost:8000'; // iOS simulator
  
  // Production (future)
  static const String prodBaseUrl = 'https://api.jobwise.com';
  
  // Current environment
  static const String apiBaseUrl = devBaseUrl;
  static const String apiVersion = 'v1';
  static const String apiPrefix = '/api/$apiVersion';
  
  // Full API URL
  static String get baseUrl => '$apiBaseUrl$apiPrefix';
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
```

#### API Endpoints
| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/v1/auth/register` | POST | Create new account | No |
| `/api/v1/auth/login` | POST | Authenticate user | No |
| `/api/v1/auth/refresh` | POST | Refresh access token | No (refresh token) |
| `/api/v1/auth/me` | GET | Get current user | Yes |
| `/api/v1/auth/logout` | POST | Invalidate session | Yes |

#### CORS Configuration
Backend `.env` configuration:
```env
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://10.0.2.2:8000", "http://127.0.0.1:8000", "*"]
```

**Mobile Note**: CORS is primarily a browser concern. Mobile HTTP clients (Dio) are not subject to CORS restrictions, but backend must allow connections from mobile IPs.

#### Network Requirements
- **Development**: Android emulator uses `10.0.2.2` to access host machine's localhost
- **iOS Simulator**: Uses `localhost` or `127.0.0.1`
- **Physical Device**: Requires computer's local IP (e.g., `http://192.168.1.10:8000`)
- **Port**: Backend runs on `:8000` by default

---

## Data Models

### User Model

```dart
// lib/models/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required String fullName,
    @Default(true) bool isActive,
    @Default(false) bool isVerified,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

### Authentication Response Model

```dart
// lib/models/auth_response.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import 'user.dart';

part 'auth_response.freezed.dart';
part 'auth_response.g.dart';

@freezed
class AuthResponse with _$AuthResponse {
  const factory AuthResponse({
    required String accessToken,
    required String refreshToken,
    @Default('Bearer') String tokenType,
    @Default(3600) int expiresIn,
    required User user,
  }) = _AuthResponse;

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);
}
```

### Login/Register Request Models

```dart
// lib/models/auth_requests.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'auth_requests.freezed.dart';
part 'auth_requests.g.dart';

@freezed
class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    required String email,
    required String password,
  }) = _LoginRequest;

  Map<String, dynamic> toJson() => {
    'email': email,
    'password': password,
  };
}

@freezed
class RegisterRequest with _$RegisterRequest {
  const factory RegisterRequest({
    required String email,
    required String password,
    required String fullName,
  }) = _RegisterRequest;

  Map<String, dynamic> toJson() => {
    'email': email,
    'password': password,
    'full_name': fullName,
  };
}
```

---

## State Management

### Auth State (Riverpod)

```dart
// lib/providers/auth_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import '../models/user.dart';
import '../services/api/auth_api_client.dart';
import '../services/storage_service.dart';

part 'auth_provider.freezed.dart';

@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    User? user,
    @Default(false) bool isAuthenticated,
    @Default(false) bool isLoading,
    String? errorMessage,
  }) = _AuthState;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthApiClient _authApi;
  final StorageService _storage;

  AuthNotifier(this._authApi, this._storage) : super(const AuthState()) {
    _initializeAuth();
  }

  // Initialize auth state on app start
  Future<void> _initializeAuth() async {
    state = state.copyWith(isLoading: true);
    try {
      final accessToken = await _storage.getAccessToken();
      if (accessToken != null) {
        // Validate token by fetching current user
        final user = await _authApi.getCurrentUser();
        state = state.copyWith(
          user: user,
          isAuthenticated: true,
          isLoading: false,
        );
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      // Token invalid or expired, clear storage
      await _storage.clearTokens();
      state = state.copyWith(isLoading: false);
    }
  }

  // Register new user
  Future<void> register(String email, String password, String fullName) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final authResponse = await _authApi.register(
        email: email,
        password: password,
        fullName: fullName,
      );
      await _storage.saveTokens(
        authResponse.accessToken,
        authResponse.refreshToken,
      );
      state = state.copyWith(
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: _parseErrorMessage(e),
      );
      rethrow;
    }
  }

  // Login existing user
  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final authResponse = await _authApi.login(
        email: email,
        password: password,
      );
      await _storage.saveTokens(
        authResponse.accessToken,
        authResponse.refreshToken,
      );
      state = state.copyWith(
        user: authResponse.user,
        isAuthenticated: true,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: _parseErrorMessage(e),
      );
      rethrow;
    }
  }

  // Logout user
  Future<void> logout() async {
    await _storage.clearTokens();
    state = const AuthState();
  }

  // Refresh access token
  Future<void> refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) {
        throw Exception('No refresh token available');
      }
      final authResponse = await _authApi.refreshToken(refreshToken);
      await _storage.saveTokens(
        authResponse.accessToken,
        authResponse.refreshToken,
      );
    } catch (e) {
      // Refresh failed, logout user
      await logout();
      rethrow;
    }
  }

  String _parseErrorMessage(dynamic error) {
    if (error.toString().contains('409')) {
      return 'Email already registered';
    } else if (error.toString().contains('401')) {
      return 'Invalid email or password';
    } else if (error.toString().contains('400')) {
      return 'Invalid input. Please check your information.';
    }
    return 'An error occurred. Please try again.';
  }
}

// Provider definition
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(
    ref.watch(authApiClientProvider),
    ref.watch(storageServiceProvider),
  );
});
```

---

## Service Layer

### Storage Service (Secure Token Storage)

```dart
// lib/services/storage_service.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class StorageService {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  static const String _accessTokenKey = 'access_token';
  static const String _refreshTokenKey = 'refresh_token';

  // Save tokens
  Future<void> saveTokens(String accessToken, String refreshToken) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  // Get access token
  Future<String?> getAccessToken() async {
    return await _storage.read(key: _accessTokenKey);
  }

  // Get refresh token
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _refreshTokenKey);
  }

  // Clear tokens
  Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }
}

// Provider
final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});
```

### Auth API Client

```dart
// lib/services/api/auth_api_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/auth_response.dart';
import '../../models/user.dart';
import 'base_http_client.dart';

class AuthApiClient {
  final BaseHttpClient _client;

  AuthApiClient(this._client);

  // Register new user
  Future<AuthResponse> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final response = await _client.post('/auth/register', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
    });
    return AuthResponse.fromJson(response.data);
  }

  // Login user
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _client.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    return AuthResponse.fromJson(response.data);
  }

  // Refresh access token
  Future<AuthResponse> refreshToken(String refreshToken) async {
    final response = await _client.post('/auth/refresh', data: {
      'refresh_token': refreshToken,
    });
    return AuthResponse.fromJson(response.data);
  }

  // Get current user
  Future<User> getCurrentUser() async {
    final response = await _client.get('/auth/me');
    return User.fromJson(response.data);
  }

  // Logout (future)
  Future<void> logout() async {
    await _client.post('/auth/logout');
  }
}

// Provider
final authApiClientProvider = Provider<AuthApiClient>((ref) {
  return AuthApiClient(ref.watch(baseHttpClientProvider));
});
```

### Base HTTP Client (with Interceptors)

```dart
// lib/services/api/base_http_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../config/app_config.dart';
import '../storage_service.dart';

class BaseHttpClient {
  late final Dio _dio;
  final StorageService _storage;

  BaseHttpClient(this._storage) {
    _dio = Dio(BaseOptions(
      baseUrl: AppConfig.baseUrl,
      connectTimeout: AppConfig.connectTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: _onRequest,
        onError: _onError,
      ),
    );
  }

  // Add auth token to requests
  Future<void> _onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final accessToken = await _storage.getAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    handler.next(options);
  }

  // Handle errors and retry with refresh token
  Future<void> _onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      // Try to refresh token
      try {
        final refreshToken = await _storage.getRefreshToken();
        if (refreshToken != null) {
          final response = await _dio.post('/auth/refresh', data: {
            'refresh_token': refreshToken,
          });
          final newAccessToken = response.data['access_token'];
          final newRefreshToken = response.data['refresh_token'];
          await _storage.saveTokens(newAccessToken, newRefreshToken);

          // Retry original request
          err.requestOptions.headers['Authorization'] =
              'Bearer $newAccessToken';
          final retryResponse = await _dio.fetch(err.requestOptions);
          return handler.resolve(retryResponse);
        }
      } catch (e) {
        // Refresh failed, clear tokens
        await _storage.clearTokens();
      }
    }
    handler.next(err);
  }

  // HTTP methods
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
}

// Provider
final baseHttpClientProvider = Provider<BaseHttpClient>((ref) {
  return BaseHttpClient(ref.watch(storageServiceProvider));
});
```

---

## UI Components

### Auth Screens (Login + Register)

```dart
// lib/screens/auth_screens.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/auth_provider.dart';
import '../utils/validators.dart';
import '../widgets/loading_overlay.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await ref.read(authProvider.notifier).login(
            _emailController.text.trim(),
            _passwordController.text,
          );
      // Navigation handled by auth state listener in main.dart
    } catch (e) {
      // Error is already set in state
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(ref.read(authProvider).errorMessage ?? 'Login failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final theme = Theme.of(context);

    return LoadingOverlay(
      isLoading: authState.isLoading,
      child: Scaffold(
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 60),
                  // Logo
                  Icon(
                    Icons.work_outline,
                    size: 80,
                    color: theme.primaryColor,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'JobWise',
                    style: theme.textTheme.headlineLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'AI-Powered Resume Builder',
                    style: theme.textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 48),
                  // Email field
                  TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Email',
                      prefixIcon: Icon(Icons.email_outlined),
                      border: OutlineInputBorder(),
                    ),
                    validator: Validators.validateEmail,
                  ),
                  const SizedBox(height: 16),
                  // Password field
                  TextFormField(
                    controller: _passwordController,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscurePassword
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _obscurePassword = !_obscurePassword;
                          });
                        },
                      ),
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Password is required';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),
                  // Login button
                  ElevatedButton(
                    onPressed: _handleLogin,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Login'),
                  ),
                  const SizedBox(height: 16),
                  // Register link
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text("Don't have an account? "),
                      TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const RegisterScreen(),
                            ),
                          );
                        },
                        child: const Text('Register'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      await ref.read(authProvider.notifier).register(
            _emailController.text.trim(),
            _passwordController.text,
            _fullNameController.text.trim(),
          );
      // Navigation handled by auth state listener
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
              ref.read(authProvider).errorMessage ?? 'Registration failed'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final theme = Theme.of(context);

    return LoadingOverlay(
      isLoading: authState.isLoading,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Create Account'),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Full Name
                  TextFormField(
                    controller: _fullNameController,
                    decoration: const InputDecoration(
                      labelText: 'Full Name',
                      prefixIcon: Icon(Icons.person_outline),
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Full name is required';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  // Email
                  TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Email',
                      prefixIcon: Icon(Icons.email_outlined),
                      border: OutlineInputBorder(),
                    ),
                    validator: Validators.validateEmail,
                  ),
                  const SizedBox(height: 16),
                  // Password
                  TextFormField(
                    controller: _passwordController,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscurePassword
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _obscurePassword = !_obscurePassword;
                          });
                        },
                      ),
                      border: const OutlineInputBorder(),
                    ),
                    validator: Validators.validatePassword,
                  ),
                  const SizedBox(height: 16),
                  // Confirm Password
                  TextFormField(
                    controller: _confirmPasswordController,
                    obscureText: _obscureConfirmPassword,
                    decoration: InputDecoration(
                      labelText: 'Confirm Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscureConfirmPassword
                              ? Icons.visibility
                              : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _obscureConfirmPassword = !_obscureConfirmPassword;
                          });
                        },
                      ),
                      border: const OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value != _passwordController.text) {
                        return 'Passwords do not match';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),
                  // Register button
                  ElevatedButton(
                    onPressed: _handleRegister,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Register'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
```

### Password Validators

```dart
// lib/utils/validators.dart
class Validators {
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return 'Enter a valid email';
    }
    return null;
  }

  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    if (!value.contains(RegExp(r'[A-Z]'))) {
      return 'Password must contain at least 1 uppercase letter';
    }
    if (!value.contains(RegExp(r'[a-z]'))) {
      return 'Password must contain at least 1 lowercase letter';
    }
    if (!value.contains(RegExp(r'[0-9]'))) {
      return 'Password must contain at least 1 number';
    }
    return null;
  }
}
```

---

## Security Implementation

### Token Storage Security
- **Platform-specific encryption**:
  - iOS: Keychain
  - Android: EncryptedSharedPreferences
- **Package**: `flutter_secure_storage` v9.0.0
- **No plaintext storage**: Never store tokens in SharedPreferences

### Token Lifecycle
1. **Login/Register**: Store access + refresh tokens
2. **API Call**: Attach access token via interceptor
3. **401 Error**: Attempt refresh with refresh token
4. **Refresh Success**: Update both tokens, retry original request
5. **Refresh Failure**: Clear tokens, redirect to login

### Password Security
- **Client-side validation**: 8+ chars, uppercase, lowercase, number
- **Server-side hashing**: bcrypt (backend responsibility)
- **Never logged**: Passwords never appear in logs or analytics

### Network Security
- **HTTPS Only**: Production must use HTTPS
- **Development**: HTTP allowed for local testing only
- **Certificate Pinning**: Future enhancement for production

---

## Error Handling

### HTTP Error Handling Implementation

The `BaseHttpClient` provides comprehensive error handling with the following features:

#### 422 Validation Error Handling
```dart
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
  // ... other error handling logic
}
```

**Key Features:**
- Extracts clean validation messages from FastAPI's structured error responses
- Returns only the error message (e.g., "String should have at least 8 characters") without field names
- Handles various error response formats gracefully

#### HTTP Logging and Debugging
```dart
// Request logging
developer.log(
  'HTTP Request: ${options.method} ${options.uri}',
  name: 'HTTP',
);

// Response logging
developer.log(
  'HTTP Response: ${response.statusCode} ${response.requestOptions.method} ${response.requestOptions.uri}',
  name: 'HTTP',
);

// Error logging with selective detail
developer.log(
  'HTTP Error: $statusCode ${error.requestOptions.method} ${error.requestOptions.uri} - $errorMessage',
  name: 'HTTP',
);
// Only log full response data for non-422 errors
if (statusCode != 422) {
  developer.log('Response data: $data', name: 'HTTP');
}
```

**Logging Strategy:**
- All HTTP requests and responses are logged to console
- 422 validation errors show clean messages only (no full response body)
- Other errors include full response data for debugging
- Uses Dart's `developer.log` with 'HTTP' name for easy filtering

#### Automatic Token Refresh
```dart
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
  // ... error message extraction
}
```

**Token Management:**
- Automatic token refresh on 401 responses
- Seamless retry of failed requests with new tokens
- Fallback to login screen if refresh fails

### Error Types and User Messages

The system provides user-friendly error messages for common scenarios:

| Status Code | Error Message |
|-------------|---------------|
| 400 | Bad request. Please check your input. |
| 401 | Authentication required. Please log in again. |
| 403 | Access denied. You don't have permission. |
| 404 | Resource not found. |
| 409 | This email is already registered. |
| 422 | Please check your input and try again. *(or specific validation message)* |
| 429 | Too many requests. Please try again later. |
| 500 | Server error. Please try again later. |

### Error Display Patterns

#### UI Error Handling Strategy
- **Form Validation Errors**: Display inline below form fields using `TextFormField` validators
- **API Errors**: Show as SnackBar notifications with action buttons
- **Network Errors**: Display retry dialogs with loading indicators
- **Authentication Errors**: Redirect to login screen with appropriate messaging

#### Example Error Widget
```dart
class ErrorHandler {
  static void showErrorSnackBar(BuildContext context, String message, {
    VoidCallback? onRetry,
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        action: onRetry != null ? SnackBarAction(
          label: 'Retry',
          onPressed: onRetry,
        ) : null,
      ),
    );
  }
}
```

---

## Testing Strategy

### Unit Tests
```dart
// test/services/auth_api_client_test.dart
void main() {
  group('AuthApiClient', () {
    late MockDio mockDio;
    late AuthApiClient authApiClient;

    setUp(() {
      mockDio = MockDio();
      authApiClient = AuthApiClient(BaseHttpClient(mockDio));
    });

    test('register returns AuthResponse on success', () async {
      when(mockDio.post('/auth/register', data: anyNamed('data')))
          .thenAnswer((_) async => Response(
                data: {
                  'access_token': 'token123',
                  'refresh_token': 'refresh123',
                  'user': {'id': '1', 'email': 'test@test.com'},
                },
                statusCode: 201,
              ));

      final result = await authApiClient.register(
        email: 'test@test.com',
        password: 'Password123',
        fullName: 'Test User',
      );

      expect(result.accessToken, 'token123');
      expect(result.user.email, 'test@test.com');
    });
  });
}
```

### Widget Tests
```dart
// test/screens/login_screen_test.dart
void main() {
  testWidgets('LoginScreen displays correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(home: LoginScreen()),
      ),
    );

    expect(find.text('JobWise'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2)); // Email + Password
    expect(find.text('Login'), findsOneWidget);
  });
}
```

### Integration Tests
- Test full login flow (UI → API → Storage → State)
- Test token refresh on 401
- Test logout clears tokens
- Test app restart preserves session

---

## Implementation Checklist

- [x] Create User and AuthResponse models with freezed
- [x] Implement StorageService with flutter_secure_storage
- [x] Create BaseHttpClient with token interceptor
- [x] Implement AuthApiClient
- [x] Create AuthNotifier with Riverpod
- [x] Build LoginScreen UI
- [x] Build RegisterScreen UI
- [x] Add password validators
- [x] Implement comprehensive HTTP error handling (422 validation, logging, token refresh)
- [x] Add unit tests for services
- [x] Add widget tests for screens
- [x] Add integration tests
- [ ] Test on physical Android device
- [ ] Test on iOS simulator
- [ ] Document API errors and handling

---

## Dependencies

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  
  # State Management
  flutter_riverpod: ^2.4.9
  
  # HTTP Client
  dio: ^5.4.0
  
  # Secure Storage
  flutter_secure_storage: ^9.0.0
  
  # Code Generation
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1

dev_dependencies:
  # Code Generators
  build_runner: ^2.4.6
  freezed: ^2.4.6
  json_serializable: ^6.7.1
  
  # Testing
  flutter_test:
    sdk: flutter
  mockito: ^5.4.4
```

---

## Future Enhancements

1. **Biometric Authentication**: Face ID / Fingerprint support
2. **Social Login**: Google, Apple Sign-In
3. **Password Reset**: Email-based password recovery
4. **Email Verification**: Verify email before full access
5. **Multi-factor Authentication (MFA)**: SMS or authenticator app
6. **Session Management**: Multiple device sessions
7. **Analytics**: Track login success/failure rates

---

**Document Status**: Complete  
**Next Steps**: Implement Profile Feature Design
