@echo off
REM ###############################################################################
REM PhilGEPS Scraper - Run Script (Windows)
REM
REM Interactive menu to run scraper, API, frontend, or all services
REM ###############################################################################

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ================================================================================
echo 🌐 PhilGEPS Scraper - Main Menu
echo ================================================================================
echo.
echo SCRAPER OPTIONS:
echo   1 - Test Scraper (2 pages, visible browser)
echo   2 - Quick Scrape (10 pages, headless)
echo   3 - Full Scrape (all 67 pages, headless)
echo   4 - Custom Scrape (choose options)
echo.
echo DATA ^& API:
echo   5 - View Scraped Data
echo   6 - Start Backend API
echo   7 - Start Frontend Dashboard
echo   8 - Start Full Stack (API + Frontend)
echo.
echo DATABASE:
echo   9 - Database Stats
echo   10 - Backup Database
echo   11 - Clear Database
echo.
echo   0 - Exit
echo.
echo ================================================================================
set /p choice="Select an option: "

if "%choice%"=="1" goto test_scraper
if "%choice%"=="2" goto quick_scrape
if "%choice%"=="3" goto full_scrape
if "%choice%"=="4" goto custom_scrape
if "%choice%"=="5" goto view_data
if "%choice%"=="6" goto start_backend
if "%choice%"=="7" goto start_frontend
if "%choice%"=="8" goto start_fullstack
if "%choice%"=="9" goto db_stats
if "%choice%"=="10" goto backup_db
if "%choice%"=="11" goto clear_db
if "%choice%"=="0" goto exit_script

echo Invalid option. Please try again.
timeout /t 2 >nul
goto menu

:test_scraper
echo.
echo 🧪 Running Test Scraper (2 pages)...
echo.
python scrape_2_pages.py
pause
goto menu

:quick_scrape
echo.
echo ⚡ Running Quick Scrape (10 pages)...
echo.
python scrape_all_awarded.py --max-pages 10
pause
goto menu

:full_scrape
echo.
echo 🚀 Running Full Scrape (all 67 pages)...
echo ⚠️  This will take approximately 60-90 minutes
echo.
set /p confirm="Continue? (y/n): "
if /i "%confirm%"=="y" (
    python scrape_all_awarded.py
) else (
    echo Cancelled.
)
pause
goto menu

:custom_scrape
echo.
echo ⚙️  Custom Scrape Configuration
echo.

set "VISIBLE_FLAG="
set "MAX_PAGES_FLAG="
set "START_PAGE_FLAG="

set /p visible="Run browser in visible mode? (y/n, default: n): "
if /i "%visible%"=="y" set "VISIBLE_FLAG=--visible"

set /p max_pages="Maximum number of pages (1-67, leave blank for all): "
if not "%max_pages%"=="" set "MAX_PAGES_FLAG=--max-pages %max_pages%"

set /p start_page="Start from page (default: 1): "
if not "%start_page%"=="" if not "%start_page%"=="1" set "START_PAGE_FLAG=--start-page %start_page%"

echo.
echo Running: python scrape_all_awarded.py %VISIBLE_FLAG% %MAX_PAGES_FLAG% %START_PAGE_FLAG%
echo.
python scrape_all_awarded.py %VISIBLE_FLAG% %MAX_PAGES_FLAG% %START_PAGE_FLAG%
pause
goto menu

:view_data
echo.
echo 📊 View Scraped Data
echo.
set /p limit="Number of records to display (default: 5, 'all' for all): "

if "%limit%"=="all" (
    python view_data.py --all
) else if not "%limit%"=="" (
    python view_data.py --limit %limit%
) else (
    python view_data.py
)
pause
goto menu

:start_backend
echo.
echo 🔧 Starting Backend API...
echo API will be available at: http://localhost:8000
echo Press Ctrl+C to stop
echo.
cd bidintel-main\backend
python backend_api.py
cd ..\..
goto menu

:start_frontend
echo.
echo 🎨 Starting Frontend Dashboard...
echo Dashboard will be available at: http://localhost:5173
echo Press Ctrl+C to stop
echo.

if not exist "bidintel-main\frontend\node_modules" (
    echo ⚠️  node_modules not found. Running npm install...
    cd bidintel-main\frontend
    call npm install
) else (
    cd bidintel-main\frontend
)

npm run dev
cd ..\..
goto menu

:start_fullstack
echo.
echo 🚀 Starting Full Stack (API + Frontend)...
echo.
echo Backend API: http://localhost:8000
echo Frontend Dashboard: http://localhost:5173
echo.
echo ⚠️  Both services will start in new windows
echo    Close the windows to stop services
echo.

if not exist "bidintel-main\frontend\node_modules" (
    echo ⚠️  node_modules not found. Running npm install...
    cd bidintel-main\frontend
    call npm install
    cd ..\..
)

start "PhilGEPS Backend API" cmd /k "cd bidintel-main\backend && python backend_api.py"
timeout /t 3 >nul
start "PhilGEPS Frontend" cmd /k "cd bidintel-main\frontend && npm run dev"

echo.
echo ✅ Both services started in separate windows
echo.
pause
goto menu

:db_stats
echo.
echo 📊 Database Statistics
echo.
python -c "import sys; sys.path.insert(0, 'bidintel-main/backend'); from models.database import Database; from sqlalchemy import func; from models.schemas import AwardedContract, BidNotice; db = Database(); session = db.get_session(); awarded_count = session.query(AwardedContract).count(); bid_count = session.query(BidNotice).count(); print(f'🏆 Awarded Contracts: {awarded_count:,}'); print(f'📋 Bid Notices: {bid_count:,}'); total_abc = session.query(func.sum(AwardedContract.approved_budget)).scalar() or 0; total_contract = session.query(func.sum(AwardedContract.contract_amount)).scalar() or 0; print(f'💰 Total ABC: PHP {total_abc:,.2f}'); print(f'💵 Total Contract Amount: PHP {total_contract:,.2f}'); savings = total_abc - total_contract; savings_pct = (savings / total_abc * 100) if total_abc > 0 else 0; print(f'💡 Total Savings: PHP {savings:,.2f} ({savings_pct:.1f}%%)'); session.close()"
pause
goto menu

:backup_db
echo.
echo 💾 Backup Database
echo.

if not exist philgeps_data.db (
    echo ❌ Database file not found!
    pause
    goto menu
)

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set TIMESTAMP=%mydate%_%mytime%

set BACKUP_FILE=philgeps_data_backup_%TIMESTAMP%.db

copy philgeps_data.db %BACKUP_FILE% >nul
echo ✅ Database backed up to: %BACKUP_FILE%
pause
goto menu

:clear_db
echo.
echo ⚠️  WARNING: Clear Database
echo.
echo This will DELETE ALL scraped data!
set /p confirm="Are you sure? Type 'yes' to confirm: "

if "%confirm%"=="yes" (
    if exist philgeps_data.db (
        REM Create backup first
        for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
        for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
        set TIMESTAMP=%mydate%_%mytime%
        set BACKUP_FILE=philgeps_data_backup_before_clear_%TIMESTAMP%.db

        copy philgeps_data.db !BACKUP_FILE! >nul
        echo ✅ Backup created: !BACKUP_FILE!

        del philgeps_data.db
        echo ✅ Database cleared

        REM Reinitialize
        python -c "import sys; sys.path.insert(0, 'bidintel-main/backend'); from models.database import Database; db = Database(); print('✅ New database initialized')"
    ) else (
        echo ⚠️  Database file not found
    )
) else (
    echo Cancelled.
)
pause
goto menu

:exit_script
echo.
echo 👋 Goodbye!
echo.
exit /b 0
