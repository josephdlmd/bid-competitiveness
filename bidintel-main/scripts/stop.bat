@echo off
REM PhilGEPS Public Scraper - Stop Script for Windows
REM This script stops all running PhilGEPS services

echo ========================================
echo PhilGEPS Public Scraper - Stopping
echo ========================================
echo.

REM Stop backend (Python/Uvicorn processes)
echo Stopping backend API server...
taskkill /F /FI "WINDOWTITLE eq PhilGEPS Backend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" >nul 2>&1

REM Stop frontend (Node/Vite processes)
echo Stopping frontend development server...
taskkill /F /FI "WINDOWTITLE eq PhilGEPS Frontend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq node.exe" /FI "MEMUSAGE gt 50000" >nul 2>&1

REM Stop scraper if running
echo Stopping scraper...
taskkill /F /FI "WINDOWTITLE eq PhilGEPS Scraper*" >nul 2>&1

echo.
echo ========================================
echo All services stopped!
echo ========================================
echo.

pause
