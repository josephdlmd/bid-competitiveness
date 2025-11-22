@echo off
REM ###############################################################################
REM PhilGEPS Scraper - Setup Script (Windows)
REM
REM This script installs all dependencies and sets up the environment
REM ###############################################################################

echo.
echo ================================================================================
echo 🚀 PhilGEPS Scraper - Setup
echo ================================================================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

python --version
echo ✅ Python found
echo.

REM Check if pip is installed
echo [2/6] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found. Please install pip.
    pause
    exit /b 1
)
echo ✅ pip found
echo.

REM Install Python dependencies
echo [3/6] Installing Python dependencies...
echo This may take a few minutes...
cd bidintel-main\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    cd ..\..
    pause
    exit /b 1
)
echo ✅ Python dependencies installed
echo.

REM Install Playwright browsers
echo [4/6] Installing Playwright browsers...
echo This will download Chromium browser...
python -m playwright install chromium
if errorlevel 1 (
    echo ⚠️  Warning: Playwright browser installation failed
    echo You may need to install manually: python -m playwright install chromium
)
echo ✅ Playwright browsers installed
echo.

REM Initialize database
echo [5/6] Initializing database...
cd ..\..
if exist philgeps_data.db (
    echo ⚠️  Database already exists. Skipping initialization.
) else (
    echo Creating database tables...
    python -c "import sys; sys.path.insert(0, 'bidintel-main/backend'); from models.database import Database; db = Database(); print('✅ Database initialized')"
)
echo.

REM Check Node.js and npm (optional, for frontend)
echo [6/6] Checking Node.js installation (for frontend)...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. Frontend setup skipped.
    echo    To use the dashboard, install Node.js from: https://nodejs.org
) else (
    node --version
    echo ✅ Node.js found

    npm --version >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  npm not found. Frontend setup skipped.
    ) else (
        npm --version
        echo ✅ npm found

        REM Install frontend dependencies
        echo Installing frontend dependencies...
        cd bidintel-main\frontend
        call npm install
        cd ..\..
        echo ✅ Frontend dependencies installed
    )
)
echo.

REM Setup complete
echo ================================================================================
echo ✅ Setup Complete!
echo ================================================================================
echo.
echo Next steps:
echo.
echo   1. Run the scraper:
echo      run.bat
echo.
echo   2. Or run individual commands:
echo      python scrape_all_awarded.py              # Scrape all pages
echo      python scrape_2_pages.py                  # Test with 2 pages
echo      python view_data.py                       # View scraped data
echo.
echo   3. Start the dashboard:
echo      cd bidintel-main\backend ^&^& python backend_api.py
echo      cd bidintel-main\frontend ^&^& npm run dev
echo.
echo For more information, see: README_SCRAPER.md
echo.
pause
