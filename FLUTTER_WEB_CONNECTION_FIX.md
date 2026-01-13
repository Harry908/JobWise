# Flutter Web to Backend Connection Fix

## Issue Identified
Your Flutter web app was configured to connect to `http://10.0.2.2:8000/api/v1`, which is the Android emulator address. Web browsers cannot access this address.

## Changes Made

### 1. Mobile App `.env` Configuration
**File:** `mobile_app/.env`

Changed from:
```env
API_BASE_URL=http://10.0.2.2:8000/api/v1
```

To:
```env
API_BASE_URL=http://localhost:8000/api/v1
WEB_API_BASE_URL=http://localhost:8000/api/v1
```

### 2. Backend CORS Configuration
**Already Configured:** Backend [main.py](backend/app/main.py#L58-L68) already has proper CORS setup:
- ✅ Explicit origins for common ports
- ✅ Regex pattern allowing `localhost` and `127.0.0.1` on any port
- ✅ Credentials support enabled

## Testing Steps

### Step 1: Rebuild Flutter Web
```powershell
cd mobile_app
flutter build web
```

### Step 2: Start Backend Server
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Run Flutter Web
```powershell
cd mobile_app
flutter run -d chrome
```

Or serve the built web app:
```powershell
cd mobile_app\build\web
python -m http.server 8080
```

### Step 4: Verify Connection
1. Open browser console (F12)
2. Login to the app
3. Check Network tab for API calls to `http://localhost:8000/api/v1`
4. Verify no CORS errors

## Platform-Specific URLs

The app now automatically detects the platform and uses appropriate URLs:

| Platform | API Base URL |
|----------|--------------|
| **Web** | `http://localhost:8000/api/v1` |
| **Android Emulator** | `http://10.0.2.2:8000/api/v1` |
| **iOS Simulator** | `http://localhost:8000/api/v1` |
| **Physical Device** | Configure your computer's IP in `.env` |

## Switching Between Platforms

To test on Android emulator, update `.env`:
```env
API_BASE_URL=http://10.0.2.2:8000/api/v1
```

To test on web or iOS:
```env
API_BASE_URL=http://localhost:8000/api/v1
```

## Common Issues

### Issue 1: CORS Error
**Symptom:** Browser shows "CORS policy blocked"
**Solution:** 
- Verify backend is running on port 8000
- Check backend logs show CORS middleware loaded
- Confirm Flutter web is running on localhost

### Issue 2: Connection Refused
**Symptom:** "net::ERR_CONNECTION_REFUSED"
**Solution:**
- Start backend server first
- Verify backend is accessible at `http://localhost:8000/docs`

### Issue 3: 404 Not Found
**Symptom:** API endpoints return 404
**Solution:**
- Check API URLs have `/api/v1` prefix
- Verify endpoint paths in Flutter match backend routes

## Backend CORS Configuration Reference

Located in [backend/app/main.py](backend/app/main.py#L62):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This configuration:
- Allows localhost and 127.0.0.1 on any port (for development)
- Enables credentials (cookies, auth headers)
- Allows all HTTP methods and headers

## Production Deployment

For production, update backend CORS to allow only your deployed frontend URL:

```python
# In backend/.env or config
ALLOWED_ORIGINS=["https://yourapp.com","https://www.yourapp.com"]
```

Remove or restrict `allow_origin_regex` in production for security.
