@echo off
REM PhilGEPS Public Scraper - Setup Script for Windows
REM This script sets up the application for the first time

echo ========================================
echo PhilGEPS Public Scraper - Setup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the philgeps-public-bundle directory
    pause
    exit /b 1
)

REM Step 1: Check Python version
echo Step 1: Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Step 2: Create virtual environment
echo.
echo Step 2: Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Step 3: Activate virtual environment and install dependencies
echo.
echo Step 3: Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Python dependencies installed

REM Step 4: Install Playwright browsers
echo.
echo Step 4: Installing Playwright browsers...
playwright install chromium
echo Playwright browsers installed

REM Step 5: Setup .env file
echo.
echo Step 5: Setting up configuration...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from .env.example
    echo WARNING: Please edit .env file to configure your settings
) else (
    echo .env file already exists
)

REM Step 6: Create necessary directories
echo.
echo Step 6: Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "browser_profile" mkdir browser_profile
echo Directories created

REM Step 7: Initialize database
echo.
echo Step 7: Initializing database...
python -c "import sys; sys.path.insert(0, 'backend'); from models.database import Database; db = Database(); print('Database initialized')"

REM Step 8: Check Node.js for frontend
echo.
echo Step 8: Checking Node.js for frontend...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Node.js is not installed
    echo Please install Node.js 18 or higher from nodejs.org
    echo Frontend will not be available until Node.js is installed
    goto :done
)

for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo Found Node.js %NODE_VERSION%

REM Install frontend dependencies
echo.
echo Step 9: Installing frontend dependencies...
cd frontend
call npm install
echo Frontend dependencies installed
cd ..

:done
REM Done
echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env file with your configuration
echo   2. Run: scripts\start.bat
echo.
pause
