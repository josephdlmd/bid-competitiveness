@echo off
REM PhilGEPS Public Scraper - Run Scraper Manually (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo Running Public Scraper
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

REM Default workers
set WORKERS=2

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run_scraper
if /i "%~1"=="--workers" (
    set WORKERS=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
echo Usage: scripts\run-scraper.bat [--workers N]
pause
exit /b 1

:run_scraper
REM Activate virtual environment and run scraper
call venv\Scripts\activate.bat
cd backend

echo Running public scraper with %WORKERS% workers...
echo.

python run_public_scraper.py --workers %WORKERS%

echo.
pause
