#!/bin/bash
# PhilGEPS Public Scraper - Setup Script
# This script sets up the application for the first time

set -e  # Exit on error

echo "========================================"
echo "PhilGEPS Public Scraper - Setup"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the philgeps-public-bundle directory"
    exit 1
fi

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Step 2: Create virtual environment
echo ""
echo "Step 2: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 3: Activate virtual environment and install dependencies
echo ""
echo "Step 3: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Step 4: Install Playwright browsers
echo ""
echo "Step 4: Installing Playwright browsers..."
playwright install chromium
echo "✓ Playwright browsers installed"

# Step 5: Setup .env file
echo ""
echo "Step 5: Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo "⚠️  Please edit .env file to configure your settings"
else
    echo "✓ .env file already exists"
fi

# Step 6: Create necessary directories
echo ""
echo "Step 6: Creating directories..."
mkdir -p data logs browser_profile
echo "✓ Directories created"

# Step 7: Initialize database
echo ""
echo "Step 7: Initializing database..."
python3 -c "import sys; sys.path.insert(0, 'backend'); from models.database import Database; db = Database(); print('✓ Database initialized')"

# Step 8: Check Node.js for frontend
echo ""
echo "Step 8: Checking Node.js for frontend..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    echo "   Frontend will not be available until Node.js is installed."
else
    NODE_VERSION=$(node --version)
    echo "✓ Found Node.js $NODE_VERSION"

    # Install frontend dependencies
    echo ""
    echo "Step 9: Installing frontend dependencies..."
    cd frontend
    npm install
    echo "✓ Frontend dependencies installed"
    cd ..
fi

# Done
echo ""
echo "========================================"
echo "✅ Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your configuration"
echo "  2. Run: ./scripts/start.sh"
echo ""
