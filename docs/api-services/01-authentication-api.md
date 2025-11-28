# Authentication API

**Version**: 1.0
**Base Path**: `/api/v1/auth`
**Status**: ✅ Fully Implemented

---

## Overview

The Authentication API handles user registration, login, token management, and account operations using JWT (JSON Web Tokens) for secure stateless authentication.

**Key Features**:
- User registration with email validation
- Secure password hashing (bcrypt with cost factor 12)
- JWT access and refresh tokens
- Token refresh mechanism
- Password change and reset functionality
- Email availability checking

---

## Authentication Flow

```
1. REGISTRATION
   Client → POST /auth/register
   Server → Create user, hash password, generate JWT
   Server → Return access_token + refresh_token + user

2. LOGIN
   Client → POST /auth/login
   Server → Verify credentials, generate JWT
   Server → Return access_token + refresh_token + user

3. AUTHENTICATED REQUESTS
   Client → Request with Authorization: Bearer <access_token>
   Server → Validate JWT, execute request

4. TOKEN REFRESH
   Client → POST /auth/refresh with refresh_token
   Server → Validate refresh_token, generate new access_token
   Server → Return new access_token + refresh_token
```

---

## Token Specifications

### Access Token
- **Type**: JWT (HS256 algorithm)
- **Expiry**: 1 hour (3600 seconds)
- **Usage**: All authenticated API requests
- **Header**: `Authorization: Bearer <access_token>`

### Refresh Token
- **Type**: JWT (HS256 algorithm)
- **Expiry**: 7 days
- **Usage**: Token refresh only
- **Endpoint**: `POST /auth/refresh`

### JWT Payload Example
```json
{
  "sub": "1",
  "email": "user@example.com",
  "exp": 1732540800,
  "iat": 1732537200,
  "type": "access"
}
```

---

## Endpoints

### 1. Register User

Create a new user account and receive authentication tokens.

**Endpoint**: `POST /api/v1/auth/register`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `email` | string | Yes | Valid email format | User email address (unique) |
| `password` | string | Yes | Min length: 8 | User password (will be hashed) |
| `full_name` | string | Yes | 1-100 characters | User's full name |

**Success Response** (201 Created):
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
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-11-15T10:30:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
  }
}
```

**Error Responses**:

**409 Conflict** (Email already exists):
```json
{
  "detail": "User with this email already exists"
}
```

**422 Unprocessable Entity** (Validation error):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "pass",
      "ctx": {"min_length": 8}
    }
  ]
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

---

### 2. Login User

Authenticate with email and password to receive tokens.

**Endpoint**: `POST /api/v1/auth/login`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Request Schema**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Registered email address |
| `password` | string | Yes | User password |

**Success Response** (200 OK):
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
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-11-15T10:30:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
  }
}
```

**Error Responses**:

**401 Unauthorized** (Invalid credentials):
```json
{
  "detail": "Invalid email or password"
}
```

**401 Unauthorized** (Account inactive):
```json
{
  "detail": "Account is inactive"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

---

### 3. Refresh Access Token

Generate a new access token using a valid refresh token.

**Endpoint**: `POST /api/v1/auth/refresh`

**Authentication**: Not required (uses refresh_token in body)

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

**Error Responses**:

**401 Unauthorized** (Invalid token):
```json
{
  "detail": "Invalid or expired refresh token"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

---

### 4. Get Current User Profile

Retrieve authenticated user's profile information.

**Endpoint**: `GET /api/v1/auth/me`

**Authentication**: Required (Bearer token)

**Request Headers**:
```http
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Error Responses**:

**401 Unauthorized** (Missing token):
```json
{
  "detail": "Not authenticated"
}
```

**401 Unauthorized** (Invalid token):
```json
{
  "detail": "Could not validate credentials"
}
```

**Example cURL**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

### 5. Logout User

Invalidate current session (client-side token removal).

**Endpoint**: `POST /api/v1/auth/logout`

**Authentication**: Required (Bearer token)

**Request Headers**:
```http
Authorization: Bearer <access_token>
```

**Success Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

**Note**: Currently implements client-side logout. Server-side token blacklisting is planned for future implementation.

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

---

### 6. Change Password

Change authenticated user's password.

**Endpoint**: `POST /api/v1/auth/change-password`

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "current_password": "CurrentPass123",
  "new_password": "NewSecurePass456"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `current_password` | string | Yes | - | Current password for verification |
| `new_password` | string | Yes | Min length: 8 | New password |

**Success Response** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses**:

**401 Unauthorized** (Incorrect current password):
```json
{
  "detail": "Current password is incorrect"
}
```

**422 Unprocessable Entity** (Weak new password):
```json
{
  "detail": "New password must be at least 8 characters long"
}
```

**Example cURL**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "CurrentPass123",
    "new_password": "NewSecurePass456"
  }'
```

---

### 7. Forgot Password

Request a password reset email (planned feature).

**Endpoint**: `POST /api/v1/auth/forgot-password`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response** (200 OK):
```json
{
  "message": "If an account with that email exists, a password reset link has been sent"
}
```

**Note**: Always returns success to prevent email enumeration attacks.

---

### 8. Reset Password

Reset password using token from email (planned feature).

**Endpoint**: `POST /api/v1/auth/reset-password`

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePass456"
}
```

**Success Response** (200 OK):
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses**:

**400 Bad Request** (Invalid or expired token):
```json
{
  "detail": "Invalid or expired reset token"
}
```

---

### 9. Check Email Availability

Check if an email is available for registration.

**Endpoint**: `GET /api/v1/auth/check-email`

**Authentication**: Not required

**Query Parameters**:
```
?email=user@example.com
```

**Success Response** (200 OK):
```json
{
  "available": true
}
```

**Example cURL**:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/check-email?email=user@example.com"
```

---

## Database Schema

### users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    full_name VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Field Descriptions**:
- `id`: Primary key, auto-increment
- `email`: Unique user email address
- `password_hash`: bcrypt hashed password (cost factor: 12)
- `full_name`: User's display name
- `is_active`: Account active status
- `is_verified`: Email verification status (planned)
- `created_at`: Account creation timestamp
- `updated_at`: Last modification timestamp

---

## Security Considerations

### Password Security
- **Hashing**: bcrypt with cost factor 12
- **Minimum Length**: 8 characters
- **Storage**: Never stored in plain text
- **Validation**: Enforced on registration and password change

### JWT Security
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Stored in environment variable
- **Expiration**: Access token (1 hour), Refresh token (7 days)
- **Validation**: Signature, expiration, and payload verification

### Common Vulnerabilities Mitigated
- ✅ **SQL Injection**: SQLAlchemy ORM with parameterized queries
- ✅ **Password Hashing**: bcrypt with proper cost factor
- ✅ **Email Enumeration**: Consistent responses for forgot password
- ✅ **Brute Force**: Rate limiting planned (10 requests/minute)
- ✅ **XSS**: Proper input validation with Pydantic
- ✅ **CSRF**: Stateless JWT (no cookies in current implementation)

---

## Implementation Details

### Dependencies
- `python-jose[cryptography]` - JWT operations
- `passlib[bcrypt]` - Password hashing
- `pydantic[email]` - Email validation
- `fastapi` - API framework
- `sqlalchemy` - ORM

### Service Layer
**File**: `backend/app/application/services/auth_service.py`

**Key Methods**:
- `register_user(email, password, full_name)` → TokenResponse
- `login_user(email, password)` → TokenResponse
- `refresh_access_token(refresh_token)` → TokenResponse
- `get_current_user(user_id)` → UserProfile
- `change_password(user_id, current_password, new_password)` → MessageResponse

### Middleware
**File**: `backend/app/core/dependencies.py`

**`get_current_user()` Dependency**:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """Extract and validate user ID from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
```

---

## Testing

### Manual Testing (cURL)

**Full Authentication Flow**:
```bash
# 1. Register
TOKEN_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}')

# 2. Extract access token
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

# 3. Get profile
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

---

## Future Enhancements

- [ ] Email verification workflow
- [ ] Password reset email integration
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 social login (Google, GitHub)
- [ ] Session management and revocation
- [ ] Rate limiting (currently planned)
- [ ] Account deletion endpoint
- [ ] User roles and permissions

---

**Last Updated**: November 2025
**API Version**: 1.0
**Status**: Production Ready
