@echo off
REM PhilGEPS Public Scraper - Safe Stop Script for Windows
REM This script stops services running on specific ports

echo ========================================
echo PhilGEPS Public Scraper - Stopping Services
echo ========================================
echo.

REM Stop backend on port 8000
echo Checking for backend on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)

REM Stop frontend on port 5173
echo Checking for frontend on port 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    echo Stopping process %%a on port 5173...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo Services stopped successfully!
echo ========================================
echo.
echo You can now restart with: scripts\start.bat
echo.

pause
