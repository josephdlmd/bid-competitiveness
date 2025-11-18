#!/bin/bash
# PhilGEPS Public Scraper - Run Scraper Manually

set -e  # Exit on error

echo "========================================"
echo "Running Public Scraper"
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

# Default workers
WORKERS=2

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./scripts/run-scraper.sh [--workers N]"
            exit 1
            ;;
    esac
done

# Activate virtual environment and run scraper
source venv/bin/activate
cd backend

echo "Running public scraper with $WORKERS workers..."
echo ""

python3 run_public_scraper.py --workers $WORKERS
