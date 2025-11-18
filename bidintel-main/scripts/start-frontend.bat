@echo off
REM PhilGEPS Public Scraper - Start Frontend Only (Windows)

echo ========================================
echo Starting Frontend Development Server
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the philgeps-public-bundle directory
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed
    echo Please install Node.js 18 or higher from nodejs.org
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo Error: Frontend dependencies not installed
    echo Please run scripts\setup.bat first
    pause
    exit /b 1
)

REM Start frontend
cd frontend

echo Starting Vite dev server on http://localhost:5173
echo Press Ctrl+C to stop
echo.

npm run dev
pause
