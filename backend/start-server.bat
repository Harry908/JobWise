@echo off
REM JobWise Backend Server Startup Script (Batch Version)
REM This script starts the FastAPI server for the JobWise backend application

echo 🚀 Starting JobWise Backend Server...

REM Change to the script's directory
cd /d "%~dp0"

REM Check if we're in the backend directory
if not exist "app\main.py" (
    echo ❌ Error: Not in backend directory. Please run this script from the backend folder.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Error: Virtual environment not found. Please run setup first.
    echo Run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if activation was successful
if %errorlevel% neq 0 (
    echo ❌ Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Set environment variables if .env file exists
if exist ".env" (
    echo 📄 Loading environment variables from .env...
    REM Note: In production, use a proper .env loader
) else (
    echo ⚠️  Warning: .env file not found. Using default configuration.
)

REM Start the FastAPI server
echo 🌐 Starting FastAPI server...
echo 📍 Server will be available at: http://localhost:8000
echo 📖 API Documentation at: http://localhost:8000/docs
echo 🔄 Alternative docs at: http://localhost:8000/redoc
echo.
echo 💡 To test the server in another terminal:
echo    1. Open a new Command Prompt or PowerShell
echo    2. Navigate to the backend directory: cd backend
echo    3. Activate venv: venv\Scripts\activate.bat (CMD) or .\venv\Scripts\Activate.ps1 (PowerShell)
echo    4. Test health endpoint: curl http://localhost:8000/health
echo    5. Or run tests: python -m pytest tests/ -v
echo.

REM Start uvicorn server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if %errorlevel% neq 0 (
    echo ❌ Error: Failed to start server
    pause
    exit /b 1
)