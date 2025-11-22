# PhilGEPS Awarded Contracts Scraper

Complete scraping solution for PhilGEPS awarded contracts data.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Data Viewing](#data-viewing)
- [API & Dashboard](#api--dashboard)

## ✨ Features

- **Full Scraper**: Scrape all 67 pages of awarded contracts (~1,600+ awards)
- **Test Scraper**: Quick 2-page scraper for testing
- **Resume Capability**: Continue from any page if interrupted
- **Progress Tracking**: Real-time progress and statistics
- **Error Handling**: Automatic retries and error recovery
- **Data Viewer**: CLI tool to browse scraped data
- **REST API**: FastAPI backend with comprehensive endpoints
- **React Dashboard**: Professional analytics dashboard

## 🚀 Installation

### 1. Install Python Dependencies

```bash
cd bidintel-main/backend
pip install -r requirements.txt
```

### 2. Install Playwright Browser

```bash
playwright install chromium
```

## 📖 Usage

### Quick Test (2 Pages)

Test the scraper with just 2 pages (~50 awards):

```bash
python scrape_2_pages.py
```

### Full Scraper (All Pages)

#### Scrape All Pages (Headless Mode)

```bash
python scrape_all_awarded.py
```

#### Scrape with Visible Browser

```bash
python scrape_all_awarded.py --visible
```

#### Limit to First N Pages

```bash
python scrape_all_awarded.py --max-pages 10
```

#### Resume from Page N

```bash
python scrape_all_awarded.py --start-page 20
```

#### Combined Options

```bash
python scrape_all_awarded.py --visible --max-pages 5 --start-page 10
```

## 📝 Scripts

### scrape_all_awarded.py

**Full production scraper with all features:**

- Automatically detects total pages (67)
- Scrapes all awarded contracts
- Progress tracking with percentage
- Error recovery with retries
- Resume capability
- Configurable via command-line

**Options:**
- `--visible`: Run browser in visible mode (not headless)
- `--max-pages N`: Limit to first N pages
- `--start-page N`: Start from page N (for resuming)

**Example Output:**
```
================================================================================
🚀 FULL AWARDED CONTRACTS SCRAPER
================================================================================
📄 Max Pages: 67
👁️  Browser Mode: Headless
================================================================================

📊 Total Pages Detected: 67
📋 Will scrape pages 1 to 67

================================================================================
📄 PAGE 1/67
================================================================================
   Found 25 awards on this page
   📊 Running Total: 25 awards found

────────────────────────────────────────────────────────────────────────────────
   [1/1650] 🔍 Scraping: AWD-2024-12345
   Progress: 0.1% | New: 1 | Skipped: 0 | Errors: 0
       ✅ Winner: ABC COMPANY INC.
       🏛️  Agency: DEPARTMENT OF PUBLIC WORKS AND HIGHWAYS
       💰 Amount: PHP 1,234,567.89

...

================================================================================
✅ SCRAPING COMPLETE
================================================================================
⏱️  Duration: 3600.0 seconds (60.0 minutes)
📊 Total Awards Found: 1650
🆕 New Records Saved: 1650
⏭️  Skipped (already in DB): 0
❌ Errors: 0
================================================================================
```

### scrape_2_pages.py

**Quick test scraper for validation:**

- Scrapes only first 2 pages (~50 awards)
- Runs in visible mode by default
- Perfect for testing changes
- No command-line options

```bash
python scrape_2_pages.py
```

## 🔍 Data Viewing

### View Scraped Data

View the scraped data in your terminal:

```bash
# View first 5 records
python view_data.py

# View first 10 records
python view_data.py --limit 10

# View all records
python view_data.py --all
```

**Example Output:**
```
================================================================================
📊 AWARDED CONTRACTS DATA
================================================================================

📈 Total records in database: 150
📋 Showing: 5 record(s)
================================================================================

================================================================================
🏆 AWARD #1 - AWD-2024-12345
================================================================================

📋 IDENTIFIERS:
   Award Notice Number: AWD-2024-12345
   Bid Reference Number: BID-2024-98765
   Control Number: CTL-2024-56789

🏆 AWARDEE (WINNER):
   Company: ABC TRADING CORPORATION
   Contact Person: JUAN DELA CRUZ
   Address: 123 MAIN STREET, MAKATI CITY, METRO MANILA

💰 FINANCIAL:
   ABC (Approved Budget): PHP 1,500,000.00
   Contract Amount (Won For): PHP 1,350,000.00
   💡 Savings: PHP 150,000.00 (10.0%)

📝 CONTRACT DETAILS:
   Title: PROCUREMENT OF OFFICE SUPPLIES
   Classification: Goods
   Period: 30 DAYS
   Award Date: 2024-11-15
   Contract Number: CN-2024-001

🏛️ PROCURING ENTITY:
   Agency: DEPARTMENT OF EDUCATION - DIVISION OF MAKATI
   Address: MAKATI CITY, METRO MANILA
   Delivery Location: MAKATI CITY

📅 OTHER INFO:
   Procurement Mode: Public Bidding
   Category: Government Procurement
   Funding Source: General Fund

📄 DOCUMENTS (3):
   • Notice of Award: AWD-2024-12345-NOA.pdf
     URL: https://philgeps.gov.ph/GEPSNONPILOT/Tender/...
   • Contract: AWD-2024-12345-CONTRACT.pdf
     URL: https://philgeps.gov.ph/GEPSNONPILOT/Tender/...

================================================================================
📊 QUICK STATS:
   Total ABC: PHP 225,000,000.00
   Total Contract Amount: PHP 202,500,000.00
   Total Savings: PHP 22,500,000.00
   Average Savings: 10.0%

   Unique Procuring Entities: 45
   Unique Awardees: 89
```

## 🌐 API & Dashboard

### Start the Backend API

```bash
cd bidintel-main/backend
python backend_api.py
```

API will be available at: `http://localhost:8000`

### API Endpoints

#### Awarded Contracts

- `GET /api/awarded-contracts` - List all contracts (with filtering)
  - Query params: `procuring_entity`, `awardee`, `classification`, `search`, `limit`, `offset`, etc.
- `GET /api/awarded-contracts/{award_notice_number}` - Get single contract
- `GET /api/awarded-contracts/stats/summary` - Overall statistics
- `GET /api/awarded-contracts/analytics/top-winners` - Top winning companies
- `GET /api/awarded-contracts/analytics/by-agency` - Spending by agency
- `GET /api/awarded-contracts/analytics/trends` - Time series data

### Start the Frontend Dashboard

```bash
cd bidintel-main/frontend
npm install
npm run dev
```

Dashboard will be available at: `http://localhost:5173`

### Dashboard Features

- **🏆 Awarded Contracts Page**: Browse all contracts with search and filtering
  - Stats cards showing totals and averages
  - Data table with pagination
  - Advanced search and filters

- **📊 Winners Analytics Page**: Visual analytics dashboard
  - Top 10 Winners chart
  - Top 10 Procuring Entities chart
  - Monthly trends visualization
  - Interactive charts and statistics

## 📊 Database

All scraped data is stored in: `philgeps_data.db` (SQLite database)

### Database Schema

**awarded_contracts** table:
- Award identifiers (award_notice_number, bid_reference_number, control_number)
- Awardee information (name, contact, address)
- Financial data (approved_budget, contract_amount, savings)
- Contract details (title, classification, dates, period)
- Procuring entity (name, address, delivery location)
- Other metadata (procurement_mode, category, funding_source)

**awarded_line_items** table:
- Individual items in each contract
- Linked to awarded_contracts

**awarded_documents** table:
- Document attachments (Notice of Award, Contract, etc.)
- URLs and metadata

## 🎯 Best Practices

### For Testing
1. Use `scrape_2_pages.py` for quick validation
2. Run with `--visible` to see what's happening
3. Check data immediately with `view_data.py`

### For Production
1. Use `scrape_all_awarded.py` for full data collection
2. Run in headless mode for efficiency
3. Use `--max-pages` for partial updates
4. Monitor progress and handle interruptions with `--start-page`

### Performance Tips
- First full scrape: ~60-90 minutes for all 67 pages
- Subsequent runs: Much faster (only new awards)
- Average: 2-3 seconds per award detail page
- Network speed is the main factor

## 🛠️ Troubleshooting

### Browser Won't Launch
```bash
# Reinstall Playwright browsers
playwright install chromium
```

### Import Errors
```bash
# Reinstall all dependencies
pip install -r bidintel-main/backend/requirements.txt
```

### Database Locked
```bash
# Close all connections and restart
rm philgeps_data.db  # WARNING: This deletes all data!
```

## 📈 Roadmap

- [x] Basic scraper for awarded contracts
- [x] Full scraper with progress tracking
- [x] REST API with comprehensive endpoints
- [x] React dashboard with analytics
- [ ] CSV/Excel export functionality
- [ ] Automated scheduling (cron jobs)
- [ ] Email notifications for new awards
- [ ] Advanced analytics (win rates, competitive analysis)

## 💡 Tips

1. **Start Small**: Test with 2-5 pages before full scrape
2. **Check Data**: Always verify with `view_data.py` after scraping
3. **Use Dashboard**: Visual dashboard is easier than CLI for analysis
4. **Backup Database**: Copy `philgeps_data.db` before major operations
5. **Monitor Progress**: Watch the progress percentage to estimate completion time
