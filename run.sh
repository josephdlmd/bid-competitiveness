#!/bin/bash

###############################################################################
# PhilGEPS Scraper - Run Script
#
# Interactive menu to run scraper, API, frontend, or all services
###############################################################################

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to display menu
show_menu() {
    clear
    echo ""
    echo "================================================================================"
    echo -e "${CYAN}🌐 PhilGEPS Scraper - Main Menu${NC}"
    echo "================================================================================"
    echo ""
    echo -e "${YELLOW}SCRAPER OPTIONS:${NC}"
    echo -e "  ${GREEN}1${NC} - Test Scraper (2 pages, visible browser)"
    echo -e "  ${GREEN}2${NC} - Quick Scrape (10 pages, headless)"
    echo -e "  ${GREEN}3${NC} - Full Scrape (all 67 pages, headless)"
    echo -e "  ${GREEN}4${NC} - Custom Scrape (choose options)"
    echo ""
    echo -e "${YELLOW}DATA & API:${NC}"
    echo -e "  ${GREEN}5${NC} - View Scraped Data"
    echo -e "  ${GREEN}6${NC} - Start Backend API"
    echo -e "  ${GREEN}7${NC} - Start Frontend Dashboard"
    echo -e "  ${GREEN}8${NC} - Start Full Stack (API + Frontend)"
    echo ""
    echo -e "${YELLOW}DATABASE:${NC}"
    echo -e "  ${GREEN}9${NC} - Database Stats"
    echo -e "  ${GREEN}10${NC} - Backup Database"
    echo -e "  ${GREEN}11${NC} - Clear Database"
    echo ""
    echo -e "  ${RED}0${NC} - Exit"
    echo ""
    echo "================================================================================"
    echo -n "Select an option: "
}

# Function to run test scraper
run_test_scraper() {
    echo ""
    echo -e "${BLUE}🧪 Running Test Scraper (2 pages)...${NC}"
    echo ""
    python3 scrape_2_pages.py
}

# Function to run quick scrape
run_quick_scrape() {
    echo ""
    echo -e "${BLUE}⚡ Running Quick Scrape (10 pages)...${NC}"
    echo ""
    python3 scrape_all_awarded.py --max-pages 10
}

# Function to run full scrape
run_full_scrape() {
    echo ""
    echo -e "${BLUE}🚀 Running Full Scrape (all 67 pages)...${NC}"
    echo -e "${YELLOW}⚠️  This will take approximately 60-90 minutes${NC}"
    echo ""
    read -p "Continue? (y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        python3 scrape_all_awarded.py
    else
        echo "Cancelled."
    fi
}

# Function to run custom scrape
run_custom_scrape() {
    echo ""
    echo -e "${BLUE}⚙️  Custom Scrape Configuration${NC}"
    echo ""

    # Ask for visible mode
    read -p "Run browser in visible mode? (y/n, default: n): " visible
    if [ "$visible" = "y" ] || [ "$visible" = "Y" ]; then
        VISIBLE_FLAG="--visible"
    else
        VISIBLE_FLAG=""
    fi

    # Ask for max pages
    read -p "Maximum number of pages (1-67, leave blank for all): " max_pages
    if [ -n "$max_pages" ]; then
        MAX_PAGES_FLAG="--max-pages $max_pages"
    else
        MAX_PAGES_FLAG=""
    fi

    # Ask for start page
    read -p "Start from page (default: 1): " start_page
    if [ -n "$start_page" ] && [ "$start_page" != "1" ]; then
        START_PAGE_FLAG="--start-page $start_page"
    else
        START_PAGE_FLAG=""
    fi

    # Build and run command
    CMD="python3 scrape_all_awarded.py $VISIBLE_FLAG $MAX_PAGES_FLAG $START_PAGE_FLAG"
    echo ""
    echo -e "${GREEN}Running: $CMD${NC}"
    echo ""
    $CMD
}

# Function to view data
view_data() {
    echo ""
    echo -e "${BLUE}📊 View Scraped Data${NC}"
    echo ""
    read -p "Number of records to display (default: 5, 'all' for all): " limit

    if [ "$limit" = "all" ]; then
        python3 view_data.py --all
    elif [ -n "$limit" ]; then
        python3 view_data.py --limit "$limit"
    else
        python3 view_data.py
    fi
}

# Function to start backend API
start_backend() {
    echo ""
    echo -e "${BLUE}🔧 Starting Backend API...${NC}"
    echo -e "${GREEN}API will be available at: http://localhost:8000${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""
    cd bidintel-main/backend
    python3 backend_api.py
}

# Function to start frontend
start_frontend() {
    echo ""
    echo -e "${BLUE}🎨 Starting Frontend Dashboard...${NC}"
    echo -e "${GREEN}Dashboard will be available at: http://localhost:5173${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo ""

    # Check if node_modules exists
    if [ ! -d "bidintel-main/frontend/node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Running npm install...${NC}"
        cd bidintel-main/frontend
        npm install
    else
        cd bidintel-main/frontend
    fi

    npm run dev
}

# Function to start full stack
start_fullstack() {
    echo ""
    echo -e "${BLUE}🚀 Starting Full Stack (API + Frontend)...${NC}"
    echo ""
    echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}Frontend Dashboard: http://localhost:5173${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""

    # Check if node_modules exists
    if [ ! -d "bidintel-main/frontend/node_modules" ]; then
        echo -e "${YELLOW}⚠️  node_modules not found. Running npm install...${NC}"
        cd bidintel-main/frontend
        npm install
        cd ../..
    fi

    # Start backend in background
    cd bidintel-main/backend
    python3 backend_api.py &
    BACKEND_PID=$!
    cd ../..

    # Wait a moment for backend to start
    sleep 3

    # Start frontend
    cd bidintel-main/frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ../..

    echo ""
    echo -e "${GREEN}✅ Both services started!${NC}"
    echo -e "${CYAN}Backend PID: $BACKEND_PID${NC}"
    echo -e "${CYAN}Frontend PID: $FRONTEND_PID${NC}"
    echo ""

    # Wait for user to stop
    read -p "Press Enter to stop all services..."

    # Kill processes
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Function to show database stats
show_db_stats() {
    echo ""
    echo -e "${BLUE}📊 Database Statistics${NC}"
    echo ""

    python3 -c "
import sys
sys.path.insert(0, 'bidintel-main/backend')
from models.database import Database
from sqlalchemy import func
from models.schemas import AwardedContract, BidNotice

db = Database()
session = db.get_session()

# Count awarded contracts
awarded_count = session.query(AwardedContract).count()
print(f'🏆 Awarded Contracts: {awarded_count:,}')

# Count bid notices
bid_count = session.query(BidNotice).count()
print(f'📋 Bid Notices: {bid_count:,}')

# Total contract amounts
if awarded_count > 0:
    total_abc = session.query(func.sum(AwardedContract.approved_budget)).scalar() or 0
    total_contract = session.query(func.sum(AwardedContract.contract_amount)).scalar() or 0
    print(f'💰 Total ABC: PHP {total_abc:,.2f}')
    print(f'💵 Total Contract Amount: PHP {total_contract:,.2f}')
    if total_abc > 0:
        savings = total_abc - total_contract
        savings_pct = (savings / total_abc) * 100
        print(f'💡 Total Savings: PHP {savings:,.2f} ({savings_pct:.1f}%)')

session.close()
"
}

# Function to backup database
backup_database() {
    echo ""
    echo -e "${BLUE}💾 Backup Database${NC}"
    echo ""

    if [ ! -f "philgeps_data.db" ]; then
        echo -e "${RED}❌ Database file not found!${NC}"
        return
    fi

    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="philgeps_data_backup_${TIMESTAMP}.db"

    cp philgeps_data.db "$BACKUP_FILE"

    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Database backed up to: $BACKUP_FILE${NC}"
    echo -e "   Size: $SIZE"
}

# Function to clear database
clear_database() {
    echo ""
    echo -e "${RED}⚠️  WARNING: Clear Database${NC}"
    echo ""
    echo "This will DELETE ALL scraped data!"
    read -p "Are you sure? Type 'yes' to confirm: " confirm

    if [ "$confirm" = "yes" ]; then
        # Create backup first
        if [ -f "philgeps_data.db" ]; then
            TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
            BACKUP_FILE="philgeps_data_backup_before_clear_${TIMESTAMP}.db"
            cp philgeps_data.db "$BACKUP_FILE"
            echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"

            rm philgeps_data.db
            echo -e "${GREEN}✅ Database cleared${NC}"

            # Reinitialize
            python3 -c "
import sys
sys.path.insert(0, 'bidintel-main/backend')
from models.database import Database
db = Database()
print('✅ New database initialized')
"
        else
            echo -e "${YELLOW}⚠️  Database file not found${NC}"
        fi
    else
        echo "Cancelled."
    fi
}

# Function to pause
pause() {
    echo ""
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read choice

    case $choice in
        1) run_test_scraper; pause ;;
        2) run_quick_scrape; pause ;;
        3) run_full_scrape; pause ;;
        4) run_custom_scrape; pause ;;
        5) view_data; pause ;;
        6) start_backend ;;
        7) start_frontend ;;
        8) start_fullstack ;;
        9) show_db_stats; pause ;;
        10) backup_database; pause ;;
        11) clear_database; pause ;;
        0)
            echo ""
            echo -e "${GREEN}👋 Goodbye!${NC}"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 1
            ;;
    esac
done
