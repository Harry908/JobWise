# API Configuration - Mobile Integration

**Version**: 1.0  
**Purpose**: Centralized API configuration and connection specifications  
**Last Updated**: October 22, 2025

---

## Backend Server Configuration

### Development Environment

#### Server Details
- **Backend Framework**: FastAPI (Python)
- **Server Host**: `0.0.0.0` (all interfaces)
- **Server Port**: `8000`
- **Protocol**: HTTP (Development only)
- **API Version**: `v1`
- **API Base Path**: `/api/v1`

#### Environment Variables (Backend `.env`)
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./test.db

# JWT Configuration
SECRET_KEY=051fa1e760e37e6eabb0b49f0b32540d95e09316b3d3a3df78aae909856edf9e30c1006798f978502223d706ceb0519cf1469d63eb68d6c62df562b3aae6727e
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

### AppConfig (Dart) - Current Implementation
```dart
// lib/config/app_config.dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

class AppConfig {
  // The API base URL is provided via the environment variable API_BASE_URL.
  // Example: http://10.0.2.2:8000/api/v1 for Android emulator.
  static String get apiBaseUrl {
    return dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
  }

  static Future<void> load() async {
    await dotenv.load(fileName: '.env');
  }
}
```

  // ============================================================
  // API CONFIGURATION
  // ============================================================
  
  // Base URL: The app reads `API_BASE_URL` from the `.env` file and uses
  // `AppConfig.apiBaseUrl` at runtime. Timeouts and other HTTP options are
  // configured within `BaseHttpClient`.

  // Note: AppConfig in the current codebase is minimal and only exposes
  // `apiBaseUrl` (from `.env`). To change timeout values, adjust the
  // `BaseHttpClient` implementation or provide explicit environment keys.

  // ============================================================
  // HTTP CLIENT (BaseHttpClient)
  // ============================================================
  
  // Timeouts and headers are configured in `BaseHttpClient`. The Dio
  // validateStatus function is set to accept <500 so the app can handle
  // non-2xx responses with custom error handling.

  // API rate limiting is enforced server-side. The app should respect
  // rate limit errors (429) and expose user-friendly messages.
```

---

## API Endpoints by Service

### 1. Authentication API
**Base Path**: `/api/v1/auth`

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/register` | POST | No | Create new account |
| `/login` | POST | No | Authenticate user |
| `/refresh` | POST | No | Refresh access token |
| `/me` | GET | Yes | Get current user |
| `/logout` | POST | Yes | Invalidate session |
| `/change-password` | POST | Yes | Change password |

**Full URLs**:
```
POST http://10.0.2.2:8000/api/v1/auth/register
POST http://10.0.2.2:8000/api/v1/auth/login
POST http://10.0.2.2:8000/api/v1/auth/refresh
GET  http://10.0.2.2:8000/api/v1/auth/me
```

### 2. Profile API
**Base Path**: `/api/v1/profiles`

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/profiles` | POST | Yes | Create profile |
| `/profiles` | GET | Yes | List profiles |
| `/profiles/me` | GET | Yes | Get current user's profile |
| `/profiles/{id}` | GET | Yes | Get specific profile |
| `/profiles/{id}` | PUT | Yes | Update profile |
| `/profiles/{id}` | DELETE | Yes | Delete profile |
| `/profiles/{id}/analytics` | GET | Yes | Profile analytics |
| `/profiles/{id}/experiences` | POST | Yes | Add experiences (bulk) |
| `/profiles/{id}/experiences` | PUT | Yes | Update experiences (bulk) |
| `/profiles/{id}/experiences` | DELETE | Yes | Delete experiences (bulk) |
| `/profiles/{id}/education` | POST/PUT/DELETE | Yes | Education operations |
| `/profiles/{id}/projects` | POST/PUT/DELETE | Yes | Project operations |
| `/profiles/{id}/skills` | GET/PUT | Yes | Skills management |

### 3. Job API
**Base Path**: `/api/v1/jobs`

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/jobs` | POST | Yes | Create job (text/structured) |
| `/jobs` | GET | Yes | List jobs (with filters) |
| `/jobs/{id}` | GET | Yes | Get job details |
| `/jobs/{id}` | PUT | Yes | Update job |
| `/jobs/{id}` | DELETE | Yes | Delete job (hard delete) |

**Query Parameters for GET /jobs**:
- `status`: `active`, `archived`, `draft`
- `source`: `user_created`, `indeed`, `linkedin`
- `limit`: 1-100 (default: 20)
- `offset`: integer (default: 0)

### 4. Generation API
**Base Path**: `/api/v1/generations`

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/generations/resume` | POST | Yes | Start resume generation |
| `/generations/cover-letter` | POST | Yes | Start cover letter generation |
| `/generations/{id}` | GET | Yes | Get generation status (polling) |
| `/generations/{id}/result` | GET | Yes | Get final result |
| `/generations/{id}/regenerate` | POST | Yes | Regenerate with new options |
| `/generations/{id}` | DELETE | Yes | Cancel/delete generation |
| `/generations` | GET | Yes | List generations |
| `/generations/templates` | GET | Yes | List available templates |

**Polling Pattern**:
```dart
// Poll every 2 seconds until completion
while (status != 'completed' && status != 'failed') {
  await Future.delayed(Duration(seconds: 2));
  status = await getGenerationStatus(id);
}
```

### 5. Document API
**Base Path**: `/api/v1/documents`

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/documents` | GET | Yes | List documents |
| `/documents/{id}` | GET | Yes | Get document details |
| `/documents/{id}/download` | GET | Yes | Download PDF |
| `/documents/{id}` | PUT | Yes | Update metadata |
| `/documents/{id}` | DELETE | Yes | Delete document |
| `/documents/export-formats` | GET | Yes | List export formats |

---

## CORS Configuration

### Backend CORS Setup

The backend allows requests from multiple origins (configured in `.env`):

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Web dev
        "http://localhost:8080",      # Alternative web port
        "http://10.0.2.2:8000",       # Android emulator
        "http://127.0.0.1:8000",      # iOS simulator
        "http://10.229.64.194:8000",  # Specific local IP
        "*",                          # Development wildcard
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Mobile CORS Considerations

**Important**: Mobile apps (using Dio HTTP client) are **NOT** subject to browser CORS restrictions. CORS is a browser security feature. However:

1. **Backend must still accept connections** from mobile device IPs
2. **Authentication headers** must be properly configured
3. **Content-Type** headers must match backend expectations

---

## HTTP Client Setup (Dio)

### Complete Dio Configuration

```dart
// lib/services/api/base_http_client.dart
import 'package:dio/dio.dart';
import '../../config/app_config.dart';

class BaseHttpClient {
  late final Dio _dio;

  BaseHttpClient(StorageService storage) {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: AppConfig.connectTimeout,
        receiveTimeout: AppConfig.receiveTimeout,
        sendTimeout: AppConfig.sendTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        validateStatus: (status) {
          // Accept all status codes to handle errors manually
          return status != null && status < 500;
        },
      ),
    );

    // Request interceptor (add auth token)
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await storage.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          
          // Logging (developer.log informs console output for debugging)
          developer.log('HTTP OUT: ${options.method} ${options.uri}', name: 'HTTP');
          
          return handler.next(options);
        },
        
        onResponse: (response, handler) {
          developer.log('HTTP IN: ${response.statusCode} ${response.requestOptions.uri}', name: 'HTTP');
          developer.log('Response data type: ${response.data.runtimeType}', name: 'HTTP');
          return handler.next(response);
        },
        
        onError: (error, handler) async {
          developer.log('HTTP ERROR: ${error.response?.statusCode} ${error.requestOptions.uri}', name: 'HTTP');
          if (error.response?.data != null) {
            developer.log('HTTP ERROR DATA: ${error.response?.data}', name: 'HTTP');
          }
          
          // Handle 401 (token expired) - attempt refresh
          if (error.response?.statusCode == 401) {
            try {
              final refreshToken = await storage.getRefreshToken();
              if (refreshToken != null) {
                // Refresh token
                final response = await _dio.post('/auth/refresh', data: {
                  'refresh_token': refreshToken,
                });
                
                // Save new tokens
                await storage.saveTokens(
                  response.data['access_token'],
                  response.data['refresh_token'],
                );
                
                // Retry original request
                error.requestOptions.headers['Authorization'] =
                    'Bearer ${response.data['access_token']}';
                final retryResponse = await _dio.fetch(error.requestOptions);
                return handler.resolve(retryResponse);
              }
            } catch (e) {
              // Refresh failed, clear tokens
              await storage.clearTokens();
            }
          }
          
          return handler.next(error);
        },
      ),
    );
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

  Future<Response> delete(String path, {dynamic data}) {
    return _dio.delete(path, data: data);
  }
}
```

---

## Testing API Connection

### Health Check Endpoint

```dart
// Test backend connectivity
Future<bool> testConnection() async {
  try {
    final dio = Dio(BaseOptions(baseUrl: AppConfig.baseUrl));
    final response = await dio.get('/health');
    return response.statusCode == 200;
  } catch (e) {
    print('Connection test failed: $e');
    return false;
  }
}
```

### Expected Response
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00Z"
}
```

---

## Common Connection Issues

### Issue 1: Connection Refused (Android Emulator)
**Problem**: Using `http://localhost:8000` on Android emulator  
**Solution**: Use `http://10.0.2.2:8000` instead

### Issue 2: Network Unreachable (Physical Device)
**Problem**: Using `localhost` or `10.0.2.2` on physical device  
**Solution**: Use computer's local IP (e.g., `http://192.168.1.10:8000`)

### Issue 3: Backend Not Running
**Problem**: Backend server not started  
**Solution**: Run `.\start-server.bat` (Windows) or `python -m uvicorn app.main:app --reload` in backend directory

### Issue 4: CORS Errors (Future Web Version)
**Problem**: Browser blocks requests  
**Solution**: Add web URL to `ALLOWED_ORIGINS` in backend `.env`

### Issue 5: Firewall Blocking
**Problem**: Firewall blocks port 8000  
**Solution**: Allow port 8000 in Windows Firewall / macOS Firewall

---

## Environment-Specific Configuration

### Development (.env.development)
```
API_BASE_URL=http://10.0.2.2:8000/api/v1
ENABLE_LOGGING=true
ENABLE_ANALYTICS=false
```

### Production (.env.production)
```
API_BASE_URL=https://api.jobwise.com/api/v1
ENABLE_LOGGING=false
ENABLE_ANALYTICS=true
```

### Usage
```dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future main() async {
  await dotenv.load(fileName: ".env.development");
  String apiUrl = dotenv.env['API_BASE_URL']!;
  runApp(MyApp());
}
```

---

## API Response Format Standards

### Success Response
```json
{
  "id": "uuid",
  "field1": "value1",
  "created_at": "2025-10-22T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "error_code_snake_case",
  "message": "Human-readable error message",
  "details": {
    "field": "specific validation error"
  }
}
```

### Pagination Response
```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## Complete API Endpoint Summary

| Service | Base Path | Endpoints | Auth |
|---------|-----------|-----------|------|
| **Authentication** | `/api/v1/auth` | 6 | Mixed |
| **Profile** | `/api/v1/profiles` | 12+ | Required |
| **Job** | `/api/v1/jobs` | 5 | Required |
| **Generation** | `/api/v1/generations` | 8 | Required |
| **Document** | `/api/v1/documents` | 6 | Required |

**Total**: 37+ endpoints

---

**Document Status**: Complete  
**Last Verified**: October 22, 2025
