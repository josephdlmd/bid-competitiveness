@echo off
REM PhilGEPS Public Scraper - Start Script for Windows
REM This script starts both the backend API and frontend development server

echo ========================================
echo PhilGEPS Public Scraper - Starting
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

REM Start backend in a new window
echo Starting backend API server...
start "PhilGEPS Backend" cmd /c "cd /d %CD% && call venv\Scripts\activate.bat && cd backend && python backend_api.py"
echo Backend API started in new window
echo    API available at: http://localhost:8000

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Check if backend is ready
echo.
echo Waiting for backend to be ready...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo Backend is ready!
        goto :start_frontend
    )
    timeout /t 1 /nobreak >nul
)
echo Warning: Backend might not have started successfully
echo Check the backend window for errors

:start_frontend
REM Start frontend in a new window
echo.
echo Starting frontend development server...
start "PhilGEPS Frontend" cmd /c "cd /d %CD%\frontend && npm run dev"
echo Frontend started in new window
echo    Frontend available at: http://localhost:5173

REM Show status
echo.
echo ========================================
echo Application is running!
echo ========================================
echo.
echo Access the application at: http://localhost:5173
echo API documentation at: http://localhost:8000/docs
echo.
echo Both services are running in separate windows
echo Close those windows to stop the services
echo.
pause
