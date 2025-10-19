@echo off
REM JobWise Backend Testing Script (Batch Version)
REM This script runs the test suite for the JobWise backend application

echo 🧪 Starting JobWise Backend Tests...

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

REM Run health check first
echo 🔍 Running health check...
python -c "import requests; print('Health check:', requests.get('http://localhost:8000/health').json() if requests.get('http://localhost:8000/health').status_code == 200 else 'Server not running')" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Server health check failed. Make sure the server is running.
    echo 💡 Start the server first with: start-server.bat
    echo.
)

REM Run the test suite
echo 🧪 Running test suite...
echo 📊 Test Results:
echo.

python -m pytest tests/ -v --tb=short

REM Check test results
if %errorlevel% equ 0 (
    echo.
    echo 🎉 All tests passed!
    echo ✅ Backend is ready for development.
) else (
    echo.
    echo ❌ Some tests failed. Please check the output above.
    echo 💡 Common fixes:
    echo    - Make sure the server is running: start-server.bat
    echo    - Check database connections
    echo    - Verify environment variables
    pause
    exit /b 1
)

echo.
echo 🎯 Testing complete!