@echo off
REM Database Optimization Script for PhilGEPS Scraper
REM Run this monthly to keep your database performing well

echo ========================================
echo Database Optimization Tool
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
    echo Please run the scraper first to create the database
    pause
    exit /b 1
)

echo Optimizing SQLite database...
echo.

REM Run VACUUM and ANALYZE
call venv\Scripts\activate.bat
cd backend
python -c "from models.database import Database; db = Database(); print('Running VACUUM...'); db.engine.execute('VACUUM'); print('Running ANALYZE...'); db.engine.execute('ANALYZE'); print('\n✅ Database optimized successfully!')"

echo.
echo ========================================
echo Optimization Complete!
echo ========================================
echo.
echo Your database has been:
echo - Defragmented (VACUUM)
echo - Statistics updated (ANALYZE)
echo.
echo Recommendation: Run this monthly for best performance
echo.
pause
