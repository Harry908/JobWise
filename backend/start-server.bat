@echo off
REM JobWise Backend Server Startup Script

cd /d "%~dp0"

IF NOT EXIST "app\main.py" (
    echo Error: This script must be run from the backend directory.
    exit /b 1
)

IF NOT EXIST "venv" (
    echo Error: Virtual environment not found. Create one with:
    echo    python -m venv venv
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
IF %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    exit /b 1
)

IF EXIST ".env" (
    echo Loading environment variables from .env
) ELSE (
    echo Warning: .env file not found; using defaults
)

echo Starting FastAPI server...
echo Server available: http://localhost:8000
echo API documentation (Swagger UI): http://localhost:8000/docs
echo.
echo To test in another terminal:
echo    1. cd backend
echo    2. .\venv\Scripts\Activate.ps1  (PowerShell) or venv\Scripts\activate.bat (CMD)
echo    3. curl http://localhost:8000/health
echo    4. python -m pytest tests/ -v

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

IF %errorlevel% neq 0 (
    echo Error: Failed to start server
    exit /b 1
)