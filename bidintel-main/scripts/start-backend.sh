#!/bin/bash
# PhilGEPS Public Scraper - Start Backend Only

set -e  # Exit on error

echo "========================================"
echo "Starting Backend API Server"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the philgeps-public-bundle directory"
    exit 1
fi

# Check if setup was run
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment and start backend
source venv/bin/activate
cd backend

echo "Starting FastAPI server on http://0.0.0.0:8000"
echo "Press Ctrl+C to stop"
echo ""

python3 backend_api.py
