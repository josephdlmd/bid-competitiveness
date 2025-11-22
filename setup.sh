#!/bin/bash

###############################################################################
# PhilGEPS Scraper - Setup Script
#
# This script installs all dependencies and sets up the environment
###############################################################################

set -e  # Exit on error

echo ""
echo "================================================================================"
echo "🚀 PhilGEPS Scraper - Setup"
echo "================================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${BLUE}[1/6]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Check if pip is installed
echo -e "${BLUE}[2/6]${NC} Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not found. Please install pip.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip found${NC}"
echo ""

# Install Python dependencies
echo -e "${BLUE}[3/6]${NC} Installing Python dependencies..."
echo "This may take a few minutes..."
cd bidintel-main/backend
pip3 install -r requirements.txt
echo -e "${GREEN}✅ Python dependencies installed${NC}"
echo ""

# Install Playwright browsers
echo -e "${BLUE}[4/6]${NC} Installing Playwright browsers..."
echo "This will download Chromium browser..."
python3 -m playwright install chromium
echo -e "${GREEN}✅ Playwright browsers installed${NC}"
echo ""

# Initialize database
echo -e "${BLUE}[5/6]${NC} Initializing database..."
cd ../..
if [ -f "philgeps_data.db" ]; then
    echo -e "${YELLOW}⚠️  Database already exists. Skipping initialization.${NC}"
else
    echo "Creating database tables..."
    python3 -c "
import sys
sys.path.insert(0, 'bidintel-main/backend')
from models.database import Database
db = Database()
print('✅ Database initialized successfully')
"
fi
echo ""

# Check Node.js and npm (optional, for frontend)
echo -e "${BLUE}[6/6]${NC} Checking Node.js installation (for frontend)..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js ${NODE_VERSION} found${NC}"

    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✅ npm ${NPM_VERSION} found${NC}"

        # Install frontend dependencies
        echo "Installing frontend dependencies..."
        cd bidintel-main/frontend
        npm install
        cd ../..
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠️  npm not found. Frontend setup skipped.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Node.js not found. Frontend setup skipped.${NC}"
    echo "   To use the dashboard, install Node.js from: https://nodejs.org"
fi
echo ""

# Setup complete
echo "================================================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================================================================"
echo ""
echo "Next steps:"
echo ""
echo "  1. Run the scraper:"
echo -e "     ${BLUE}./run.sh${NC}"
echo ""
echo "  2. Or run individual commands:"
echo -e "     ${BLUE}python3 scrape_all_awarded.py${NC}              # Scrape all pages"
echo -e "     ${BLUE}python3 scrape_2_pages.py${NC}                  # Test with 2 pages"
echo -e "     ${BLUE}python3 view_data.py${NC}                       # View scraped data"
echo ""
echo "  3. Start the dashboard:"
echo -e "     ${BLUE}cd bidintel-main/backend && python3 backend_api.py${NC}"
echo -e "     ${BLUE}cd bidintel-main/frontend && npm run dev${NC}"
echo ""
echo "For more information, see: README_SCRAPER.md"
echo ""
