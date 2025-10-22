@echo off
echo Activating virtual environment...
call .\.venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Loading environment variables from .env
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
) else (
    echo Warning: .env file not found
)

echo Starting FastAPI server...
echo Server available: http://localhost:8000
echo API documentation (Swagger UI): http://localhost:8000/docs
echo To test in another terminal:
echo   1. cd backend
echo   2. .\.venv\Scripts\Activate.ps1  (PowerShell) or .venv\Scripts\activate.bat (CMD)
echo   3. curl http://localhost:8000/health
echo   4. python -m pytest tests/ -v
echo.

.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause