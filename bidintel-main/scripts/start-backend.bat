@echo off
REM PhilGEPS Public Scraper - Start Backend Only (Windows)

echo ========================================
echo Starting Backend API Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the philgeps-public-bundle directory
    pause
    exit /b 1
)

REM Check if setup was run
if not exist "venv" (
    echo Error: Virtual environment not found
    echo Please run scripts\setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment and start backend
call venv\Scripts\activate.bat
cd backend

echo Starting FastAPI server on http://0.0.0.0:8000
echo Press Ctrl+C to stop
echo.

python backend_api.py
pause
