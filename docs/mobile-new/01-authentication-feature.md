# Authentication Feature

**Backend API**: [Authentication API](../api-services/01-authentication-api.md)
**Base Path**: `/api/v1/auth`
**Status**: ✅ Fully Implemented
**Last Updated**: November 2025

---

## Overview

The Authentication feature provides user registration, login, password management, and JWT token handling for the JobWise mobile app.

### User Stories

**As a new user**, I want to:
- Register for an account with email and password
- Receive immediate feedback if my email is already registered
- Create a secure password that meets requirements

**As a returning user**, I want to:
- Login with my email and password
- Stay logged in across app restarts
- Have my session automatically refreshed when tokens expire

**As an authenticated user**, I want to:
- Change my password securely
- Reset my password if I forget it
- Logout and clear my session

---

## Screens

### 1. LoginScreen

**Route**: `/login`
**File**: `lib/screens/auth/login_screen.dart`

**UI Components**:
- Email text field with validation
- Password text field with show/hide toggle
- "Login" button (primary action)
- "Forgot Password?" link
- "Don't have an account? Register" link
- Loading overlay during authentication

**Form Validation**:
- Email: Required, valid email format
- Password: Required, minimum 8 characters

**User Flow**:
```
1. User enters email and password
2. Tap "Login" button
3. Show loading overlay
4. Call AuthApiClient.login()
5. On success:
   - Save tokens to secure storage
   - Update AuthNotifier state
   - Navigate to /home
6. On error:
   - Hide loading overlay
   - Show error message (SnackBar)
```

**Error Handling**:
- Invalid credentials → "Invalid email or password"
- Network error → "Connection failed. Please check your internet."
- Server error → "An error occurred. Please try again later."

### 2. RegisterScreen

**Route**: `/register`
**File**: `lib/screens/auth/register_screen.dart`

**UI Components**:
- Full name text field
- Email text field with real-time availability check
- Password text field with strength indicator
- Confirm password text field
- "Register" button (primary action)
- "Already have an account? Login" link
- Loading overlay during registration

**Form Validation**:
- Full name: Required, minimum 2 characters
- Email: Required, valid email format, check availability
- Password: Required, minimum 8 characters, strength indicator
- Confirm password: Required, must match password

**Password Strength Indicator**:
```dart
enum PasswordStrength { weak, medium, strong }

PasswordStrength calculateStrength(String password) {
  if (password.length < 8) return PasswordStrength.weak;
  if (password.length >= 12 &&
      password.contains(RegExp(r'[A-Z]')) &&
      password.contains(RegExp(r'[0-9]')) &&
      password.contains(RegExp(r'[!@#$%^&*]'))) {
    return PasswordStrength.strong;
  }
  return PasswordStrength.medium;
}
```

**User Flow**:
```
1. User enters full name, email, password
2. Check email availability (debounced)
3. Tap "Register" button
4. Show loading overlay
5. Call AuthApiClient.register()
6. On success:
   - Save tokens to secure storage
   - Update AuthNotifier state
   - Navigate to /profile/create (new user onboarding)
7. On error:
   - Hide loading overlay
   - Show error message
```

---

## Backend API Integration

### API Endpoints

All endpoints from [Authentication API](../api-services/01-authentication-api.md):

#### 1. POST /api/v1/auth/register

**Request**:
```dart
final response = await authApiClient.register(
  email: 'user@example.com',
  password: 'SecurePass123',
  fullName: 'John Doe',
);
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-11-15T10:30:00Z"
  }
}
```

#### 2. POST /api/v1/auth/login

**Request**:
```dart
final response = await authApiClient.login(
  email: 'user@example.com',
  password: 'SecurePass123',
);
```

**Response**: Same as register

#### 3. POST /api/v1/auth/refresh

**Request**:
```dart
final response = await authApiClient.refreshToken(
  refreshToken: 'eyJ0eXAiOiJKV1QiLCJhbGc...',
);
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### 4. GET /api/v1/auth/me

**Request**:
```dart
final user = await authApiClient.getCurrentUser();
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

#### 5. POST /api/v1/auth/logout

**Request**:
```dart
await authApiClient.logout();
```

**Response**: `204 No Content`

#### 6. POST /api/v1/auth/change-password

**Request**:
```dart
await authApiClient.changePassword(
  currentPassword: 'OldPass123',
  newPassword: 'NewPass123',
);
```

**Response**:
```json
{
  "message": "Password changed successfully"
}
```

#### 7. POST /api/v1/auth/forgot-password

**Request**:
```dart
await authApiClient.forgotPassword(email: 'user@example.com');
```

**Response**:
```json
{
  "message": "Password reset email sent"
}
```

#### 8. POST /api/v1/auth/reset-password

**Request**:
```dart
await authApiClient.resetPassword(
  token: 'reset_token_from_email',
  newPassword: 'NewPass123',
);
```

**Response**:
```json
{
  "message": "Password reset successfully"
}
```

#### 9. GET /api/v1/auth/check-email

**Request**:
```dart
final isAvailable = await authApiClient.checkEmailAvailability(
  email: 'user@example.com',
);
```

**Response**:
```json
{
  "available": false,
  "message": "Email is already registered"
}
```

---

## Data Models

### User

**File**: `lib/models/user.dart`

```dart
class User {
  final int id;
  final String email;
  final String fullName;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.createdAt,
    required this.updatedAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  User copyWith({
    int? id,
    String? email,
    String? fullName,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
```

### AuthResponse

**File**: `lib/models/auth_response.dart`

```dart
class AuthResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  AuthResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      tokenType: json['token_type'],
      expiresIn: json['expires_in'],
      user: User.fromJson(json['user']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'access_token': accessToken,
      'refresh_token': refreshToken,
      'token_type': tokenType,
      'expires_in': expiresIn,
      'user': user.toJson(),
    };
  }
}
```

---

## State Management

### AuthState

**File**: `lib/providers/auth/auth_state.dart`

```dart
enum AuthStatus {
  initial,
  authenticated,
  unauthenticated,
  loading,
}

class AuthState {
  final AuthStatus status;
  final User? user;
  final String? errorMessage;

  AuthState({
    required this.status,
    this.user,
    this.errorMessage,
  });

  factory AuthState.initial() {
    return AuthState(status: AuthStatus.initial);
  }

  factory AuthState.authenticated(User user) {
    return AuthState(
      status: AuthStatus.authenticated,
      user: user,
    );
  }

  factory AuthState.unauthenticated() {
    return AuthState(status: AuthStatus.unauthenticated);
  }

  factory AuthState.loading() {
    return AuthState(status: AuthStatus.loading);
  }

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}
```

### AuthNotifier

**File**: `lib/providers/auth/auth_notifier.dart`

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:jobwise/models/user.dart';
import 'package:jobwise/models/auth_response.dart';
import 'package:jobwise/services/api/auth_api_client.dart';
import 'package:jobwise/services/token_storage.dart';
import 'auth_state.dart';

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthApiClient _apiClient;
  final TokenStorage _tokenStorage;

  AuthNotifier(this._apiClient, this._tokenStorage)
      : super(AuthState.initial()) {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    state = AuthState.loading();

    try {
      final hasToken = await _tokenStorage.hasValidToken();
      if (hasToken) {
        final user = await _apiClient.getCurrentUser();
        state = AuthState.authenticated(user);
      } else {
        state = AuthState.unauthenticated();
      }
    } catch (e) {
      state = AuthState.unauthenticated();
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    state = AuthState.loading();

    try {
      final response = await _apiClient.register(
        email: email,
        password: password,
        fullName: fullName,
      );

      await _tokenStorage.saveTokens(
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );

      state = AuthState.authenticated(response.user);
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = AuthState.loading();

    try {
      final response = await _apiClient.login(
        email: email,
        password: password,
      );

      await _tokenStorage.saveTokens(
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );

      state = AuthState.authenticated(response.user);
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.unauthenticated,
        errorMessage: e.toString(),
      );
      rethrow;
    }
  }

  Future<void> logout() async {
    try {
      await _apiClient.logout();
    } catch (e) {
      // Continue with logout even if API call fails
    } finally {
      await _tokenStorage.clearTokens();
      state = AuthState.unauthenticated();
    }
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      await _apiClient.changePassword(
        currentPassword: currentPassword,
        newPassword: newPassword,
      );
    } catch (e) {
      rethrow;
    }
  }

  Future<bool> checkEmailAvailability(String email) async {
    try {
      return await _apiClient.checkEmailAvailability(email: email);
    } catch (e) {
      return false;
    }
  }
}

// Provider
final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>(
  (ref) {
    final apiClient = ref.watch(authApiClientProvider);
    final tokenStorage = ref.watch(tokenStorageProvider);
    return AuthNotifier(apiClient, tokenStorage);
  },
);
```

---

## Service Layer

### AuthApiClient

**File**: `lib/services/api/auth_api_client.dart`

```dart
import 'package:dio/dio.dart';
import 'package:jobwise/models/user.dart';
import 'package:jobwise/models/auth_response.dart';

class AuthApiClient {
  final Dio _dio;

  AuthApiClient(this._dio);

  Future<AuthResponse> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/auth/register',
        data: {
          'email': email,
          'password': password,
          'full_name': fullName,
        },
      );

      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<AuthResponse> refreshToken({
    required String refreshToken,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/auth/refresh',
        data: {
          'refresh_token': refreshToken,
        },
      );

      return AuthResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _dio.get('/api/v1/auth/me');
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _dio.post('/api/v1/auth/logout');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    try {
      await _dio.post(
        '/api/v1/auth/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> forgotPassword({required String email}) async {
    try {
      await _dio.post(
        '/api/v1/auth/forgot-password',
        data: {'email': email},
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    try {
      await _dio.post(
        '/api/v1/auth/reset-password',
        data: {
          'token': token,
          'new_password': newPassword,
        },
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Future<bool> checkEmailAvailability({required String email}) async {
    try {
      final response = await _dio.get(
        '/api/v1/auth/check-email',
        queryParameters: {'email': email},
      );
      return response.data['available'];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  Exception _handleError(DioException error) {
    if (error.response != null) {
      final message = error.response?.data['detail'] ?? 'An error occurred';
      return Exception(message);
    }
    return Exception('Network error occurred');
  }
}

// Provider
final authApiClientProvider = Provider<AuthApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return AuthApiClient(dio);
});
```

---

## Navigation & Routing

### GoRouter Configuration

**File**: `lib/routing/app_router.dart`

```dart
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/login',
    redirect: (context, state) {
      final isAuthenticated = authState.isAuthenticated;
      final isAuthRoute = state.location.startsWith('/login') ||
          state.location.startsWith('/register');

      if (!isAuthenticated && !isAuthRoute) {
        return '/login';
      }

      if (isAuthenticated && isAuthRoute) {
        return '/home';
      }

      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      // ... other routes
    ],
  );
});
```

---

## Security

### Password Validation

**File**: `lib/utils/validators.dart`

```dart
class Validators {
  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }

    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email';
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

    return null;
  }

  static String? validateFullName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Full name is required';
    }

    if (value.length < 2) {
      return 'Full name must be at least 2 characters';
    }

    return null;
  }

  static String? validateConfirmPassword(String? value, String password) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }

    if (value != password) {
      return 'Passwords do not match';
    }

    return null;
  }
}
```

### Secure Token Storage

- Uses `flutter_secure_storage` for iOS Keychain and Android Keystore
- Never store tokens in SharedPreferences or plain text
- Automatic token refresh on 401 errors
- Clear tokens on logout

---

## Testing

### Unit Tests

**File**: `test/services/auth_api_client_test.dart`

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:dio/dio.dart';

void main() {
  group('AuthApiClient', () {
    late MockDio mockDio;
    late AuthApiClient client;

    setUp(() {
      mockDio = MockDio();
      client = AuthApiClient(mockDio);
    });

    test('register returns AuthResponse on success', () async {
      when(mockDio.post('/api/v1/auth/register', data: anyNamed('data')))
          .thenAnswer((_) async => Response(
                data: {
                  'access_token': 'test_token',
                  'refresh_token': 'test_refresh',
                  'token_type': 'Bearer',
                  'expires_in': 3600,
                  'user': {
                    'id': 1,
                    'email': 'test@example.com',
                    'full_name': 'Test User',
                    'created_at': '2025-11-15T10:30:00Z',
                    'updated_at': '2025-11-15T10:30:00Z',
                  },
                },
                statusCode: 201,
                requestOptions: RequestOptions(path: '/api/v1/auth/register'),
              ));

      final response = await client.register(
        email: 'test@example.com',
        password: 'password123',
        fullName: 'Test User',
      );

      expect(response.accessToken, 'test_token');
      expect(response.user.email, 'test@example.com');
    });

    test('login throws exception on invalid credentials', () async {
      when(mockDio.post('/api/v1/auth/login', data: anyNamed('data')))
          .thenThrow(DioException(
        response: Response(
          data: {'detail': 'Invalid email or password'},
          statusCode: 401,
          requestOptions: RequestOptions(path: '/api/v1/auth/login'),
        ),
        requestOptions: RequestOptions(path: '/api/v1/auth/login'),
      ));

      expect(
        () => client.login(
          email: 'test@example.com',
          password: 'wrongpassword',
        ),
        throwsException,
      );
    });
  });
}
```

### Widget Tests

**File**: `test/screens/login_screen_test.dart`

```dart
testWidgets('LoginScreen shows error on invalid credentials', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      child: MaterialApp(home: LoginScreen()),
    ),
  );

  await tester.enterText(find.byKey(Key('email_field')), 'test@example.com');
  await tester.enterText(find.byKey(Key('password_field')), 'wrongpass');
  await tester.tap(find.byKey(Key('login_button')));
  await tester.pump();

  expect(find.text('Invalid email or password'), findsOneWidget);
});
```

---

## Error Handling

### Common Errors

| Error | Status Code | User Message |
|-------|-------------|--------------|
| Invalid credentials | 401 | "Invalid email or password" |
| Email already exists | 409 | "This email is already registered" |
| Network timeout | - | "Connection timeout. Please check your internet." |
| Server error | 500 | "An error occurred. Please try again later." |
| Validation error | 422 | Display field-specific errors |

---

## Performance Considerations

1. **Email Availability Check**: Debounce by 500ms to avoid excessive API calls
2. **Token Refresh**: Automatic and transparent to user
3. **Secure Storage**: Asynchronous operations, use FutureBuilder where needed
4. **Form Validation**: Client-side validation before API call

---

**Status**: ✅ Fully Implemented
**Screens**: 2 (Login, Register)
**API Endpoints**: 9 endpoints
**Dependencies**: dio, flutter_secure_storage, flutter_riverpod
**Last Updated**: November 2025
