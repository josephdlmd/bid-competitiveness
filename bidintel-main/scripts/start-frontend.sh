#!/bin/bash
# PhilGEPS Public Scraper - Start Frontend Only

set -e  # Exit on error

echo "========================================"
echo "Starting Frontend Development Server"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the philgeps-public-bundle directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Error: Frontend dependencies not installed. Please run ./scripts/setup.sh first"
    exit 1
fi

# Start frontend
cd frontend

echo "Starting Vite dev server on http://localhost:5173"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
