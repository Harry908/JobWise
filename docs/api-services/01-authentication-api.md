# Authentication API Service

**Version**: 1.0
**Base Path**: `/api/v1/auth`
**Status**: Implemented

## Service Overview

Handles user registration, authentication, and session management using JWT tokens. All other services depend on this for user identity verification.

## Specification

**Purpose**: User authentication and authorization
**Authentication Method**: JWT Bearer tokens
**Token Expiry**: Access token (1 hour), Refresh token (7 days)
**Password Security**: bcrypt with cost factor 12
**Rate Limiting**: 100 requests/minute per IP (planned)

## Dependencies

### Internal
- Database: UserModel, UserSessionModel
- Core: JWT utilities, password hashing (bcrypt)
- Middleware: CORS configuration

### External
None

## Data Flow

```
Client Registration:
1. Client → POST /register {email, password, full_name}
2. API validates email uniqueness
3. API hashes password (bcrypt)
4. API creates user record
5. API generates JWT tokens
6. API ← {access_token, refresh_token, user}

Client Login:
1. Client → POST /login {email, password}
2. API retrieves user by email
3. API verifies password hash
4. API generates JWT tokens
5. API ← {access_token, refresh_token, user}

Token Refresh:
1. Client → POST /refresh {refresh_token}
2. API validates refresh token
3. API generates new access token
4. API ← {access_token, refresh_token}
```

## API Contract

### POST /register

**Description**: Create new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

**Errors**:
- 400: Validation error (invalid email, weak password)
- 409: Email already registered

### POST /login

**Description**: Authenticate user

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK): Same as /register

**Errors**:
- 401: Invalid credentials
- 400: Validation error

### POST /refresh

**Description**: Refresh access token

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Errors**:
- 401: Invalid or expired refresh token

### GET /me

**Description**: Get current user profile

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-10-21T10:00:00Z",
  "updated_at": "2025-10-21T10:00:00Z"
}
```

**Errors**:
- 401: Invalid or missing token

### POST /logout

**Description**: Invalidate session (planned)

**Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

### POST /change-password

**Description**: Change current user's password

**Headers**: `Authorization: Bearer <access_token>`

**Request**:
```json
{
  "current_password": "CurrentPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

**Errors**:
- 400: Validation error (weak password, same as current)
- 401: Invalid current password or missing token

### POST /forgot-password

**Description**: Request password reset (mock implementation)

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "message": "If the email exists, a reset link has been sent"
}
```

**Errors**:
- 400: Invalid email format

### POST /reset-password

**Description**: Reset password with token (mock implementation)

**Request**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePass456!"
}
```

**Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

**Errors**:
- 400: Invalid or expired token, weak password
- 404: Token not found

## Mobile Integration Notes

### Token Storage
Store tokens securely:
- iOS: Keychain
- Android: EncryptedSharedPreferences
- Flutter: flutter_secure_storage package

### Token Management
```dart
// Example Flutter implementation
class AuthService {
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  Future<void> saveTokens(String access, String refresh) async {
    await _storage.write(key: 'access_token', value: access);
    await _storage.write(key: 'refresh_token', value: refresh);
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }
}
```

### HTTP Client Configuration
```dart
class ApiClient {
  final Dio _dio = Dio();

  ApiClient() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _authService.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token expired, try refresh
            final refreshed = await _authService.refreshToken();
            if (refreshed) {
              // Retry original request
              return handler.resolve(await _dio.fetch(error.requestOptions));
            }
          }
          return handler.next(error);
        },
      ),
    );
  }
}
```

### Password Validation
Enforce client-side:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number

### Error Handling
```dart
try {
  final response = await apiClient.post('/auth/login', data: credentials);
  await authService.saveTokens(response.data['access_token'], response.data['refresh_token']);
  return User.fromJson(response.data['user']);
} on DioError catch (e) {
  if (e.response?.statusCode == 401) {
    throw AuthenticationException('Invalid credentials');
  } else if (e.response?.statusCode == 409) {
    throw ConflictException('Email already registered');
  } else {
    throw NetworkException('Connection failed');
  }
}
```

### Token Expiry Handling
- Access token expires in 1 hour
- Refresh token expires in 7 days
- Auto-refresh access token when 401 received
- Force re-login when refresh token expired

## Implementation Notes

### Repository
- `app/infrastructure/repositories/user_repository.py`
- Methods: `create_user()`, `get_by_email()`, `get_by_id()`

### Service
- `app/application/services/auth_service.py`
- Methods: `register()`, `login()`, `refresh_token()`, `verify_token()`

### Security
- Never log passwords or tokens
- Hash passwords before database insert
- Validate JWT signature on every protected request
- Use HTTPS in production
- Implement rate limiting to prevent brute force

### Testing
- Test password hashing/verification
- Test JWT generation/validation
- Test token expiry
- Test duplicate email registration
- Test invalid credentials
