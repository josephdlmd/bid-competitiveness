@echo off
REM Database Status Checker for PhilGEPS Scraper
REM Shows database size, record counts, and performance recommendations

echo ========================================
echo Database Status Report
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo Error: Please run this script from the philgeps-public-bundle directory
    pause
    exit /b 1
)

REM Check if database exists
if not exist "data\philgeps_data.db" (
    echo Error: Database not found at data\philgeps_data.db
    echo Database has not been created yet
    echo Run the scraper to create and populate the database
    pause
    exit /b 1
)

REM Show database file size
echo 📊 DATABASE FILE SIZE:
for %%A in (data\philgeps_data.db) do (
    set size=%%~zA
    set /a size_mb=%%~zA/1048576
)
echo    File: data\philgeps_data.db
echo    Size: %size_mb% MB
echo.

REM Performance check based on size
if %size_mb% LSS 50 (
    echo ✅ Performance Status: EXCELLENT
    echo    Your database is well within optimal size
) else if %size_mb% LSS 200 (
    echo ⚠️  Performance Status: GOOD - Consider optimization
    echo    Recommendation: Run scripts\optimize-db.bat monthly
) else if %size_mb% LSS 1000 (
    echo ⚠️  Performance Status: MODERATE
    echo    Recommendation: Consider migrating to PostgreSQL
    echo    See PERFORMANCE_OPTIMIZATION.md for details
) else (
    echo ❌ Performance Status: NEEDS ATTENTION
    echo    Strong Recommendation: Migrate to PostgreSQL
    echo    SQLite may be too slow at this size
    echo    See PERFORMANCE_OPTIMIZATION.md for migration guide
)
echo.

REM Show record counts and performance
echo 📈 RECORD COUNTS & PERFORMANCE:
echo.
call venv\Scripts\activate.bat
cd backend
python -c "from models.database import Database; from models.schemas import BidNotice, ScrapingLog, LineItem; import time; db = Database(); session = db.get_session(); start = time.time(); count = session.query(BidNotice).count(); count_time = time.time() - start; line_count = session.query(LineItem).count(); log_count = session.query(ScrapingLog).count(); print(f'   Bid Notices: {count:,}'); print(f'   Line Items: {line_count:,}'); print(f'   Scraping Logs: {log_count:,}'); print(); print(f'   Query Speed: {count_time:.3f} seconds'); print(); print('   Performance:', '✅ FAST' if count_time < 0.5 else '⚠️  MODERATE' if count_time < 2 else '❌ SLOW - Optimize recommended'); session.close()"

echo.
echo ========================================
echo Quick Actions:
echo ========================================
echo.
echo 1. Optimize database:        scripts\optimize-db.bat
echo 2. View full guide:           notepad PERFORMANCE_OPTIMIZATION.md
echo 3. Backup database:           copy data\philgeps_data.db data\backup.db
echo.
pause
