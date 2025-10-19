# JobWise Backend - Server Startup Guide

This guide explains how to start and test the JobWise backend server.

## Prerequisites

1. **Python 3.9+** installed
2. **Virtual Environment** set up in the backend directory
3. **Dependencies** installed via `pip install -r requirements.txt`

## Quick Start

### Option 1: PowerShell Script (Recommended for Windows)

1. **Start the server** in one PowerShell terminal:
   ```powershell
   cd backend
   .\start-server.ps1
   ```

2. **Test the server** in another PowerShell terminal:
   ```powershell
   cd backend
   .\test-server.ps1
   ```

### Option 2: Batch Script (Windows CMD)

1. **Start the server** in one Command Prompt:
   ```cmd
   cd backend
   start-server.bat
   ```

2. **Test the server** in another Command Prompt:
   ```cmd
   cd backend
   test-server.bat
   ```

### Option 3: Python Script (Cross-platform)

1. **Start the server** in one terminal:
   ```bash
   cd backend
   python start_server.py
   ```

2. **Test manually** in another terminal:
   ```bash
   cd backend
   # Activate venv (platform-specific)
   python -m pytest tests/ -v
   ```

### Option 4: Manual Commands

1. **Terminal 1 - Start Server:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2 - Run Tests:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m pytest tests/ -v
   ```

## Server URLs

Once started, the server will be available at:
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Available Endpoints

### Public Endpoints
- `GET /health` - Server health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /jobs/search` - Job search (with optional auth)
- `GET /jobs/{job_id}` - Job details
- `GET /jobs/filters` - Available filter options

### Protected Endpoints (Require Authentication)
- `GET /auth/me` - Current user info
- `GET /profiles/me` - User profile
- `POST /profiles` - Create profile
- `PUT /profiles/{id}` - Update profile
- `DELETE /profiles/{id}` - Delete profile

## Testing

The `test-server.ps1` and `test-server.bat` scripts perform:
- ✅ Health endpoint check
- ✅ API documentation accessibility
- ✅ Authentication endpoint validation
- ✅ Full test suite execution

## Troubleshooting

### Server Won't Start
- Ensure virtual environment is activated
- Check if port 8000 is available
- Verify all dependencies are installed
- Check Python version (3.9+ required)

### Tests Fail
- Ensure server is running in another terminal
- Check database connection if using real DB
- Verify environment variables are set
- Check test data files exist

### Permission Errors
- Run PowerShell as Administrator
- Check execution policy: `Set-ExecutionPolicy RemoteSigned`
- Ensure virtual environment Scripts are executable

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/jobwise

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers (optional)
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
```

## Development Workflow

1. **Start server** in one terminal with `.\start-server.ps1` or `start-server.bat`
2. **Run tests** in another terminal with `.\test-server.ps1` or `test-server.bat`
3. **Make changes** - server auto-reloads
4. **Check logs** in the server terminal
5. **Re-run tests** as needed

## Production Deployment

For production, use:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Consider using a process manager like Gunicorn or a container orchestration system.