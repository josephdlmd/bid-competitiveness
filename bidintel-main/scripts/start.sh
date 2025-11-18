#!/bin/bash
# PhilGEPS Public Scraper - Start Script
# This script starts both the backend API and frontend development server

set -e  # Exit on error

echo "========================================"
echo "PhilGEPS Public Scraper - Starting"
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

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend API server..."
source venv/bin/activate
cd backend
python3 backend_api.py &
BACKEND_PID=$!
cd ..
echo "✓ Backend API started (PID: $BACKEND_PID)"
echo "   API available at: http://localhost:8000"

# Wait for backend to be ready
echo ""
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start"
        cleanup
        exit 1
    fi
    sleep 1
done

# Start frontend
echo ""
echo "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo "   Frontend available at: http://localhost:5173"

# Keep script running
echo ""
echo "========================================"
echo "✅ Application is running!"
echo "========================================"
echo ""
echo "Access the application at: http://localhost:5173"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
