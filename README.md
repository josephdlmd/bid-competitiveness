# PhilGEPS Awarded Contracts Intelligence System

> **Project Scope**: This codebase is specifically designed for scraping and analyzing **AWARDED CONTRACTS** from PhilGEPS. It tracks completed government contracts showing who won, for how much, and competitive pricing intelligence.

---

## 🎯 What This System Does

This system collects and analyzes **awarded government contracts** from the Philippine Government Electronic Procurement System (PhilGEPS), providing competitive intelligence on:

- **Who wins government contracts** (company names and contact info)
- **Awarded prices** (actual contract amounts)
- **Budget vs. Award analysis** (ABC vs. Contract Amount, savings %)
- **Pricing intelligence** (competitive bidding patterns)
- **Competitor tracking** (monitor rival companies' wins)
- **Agency buying patterns** (which agencies buy what)

---

## 📊 Important Distinction

### This System: Awarded Contracts ✅
- **Focus**: Completed contracts that have been awarded
- **Key Data**: Winner name, contract amount, award date
- **Source**: `https://philgeps.gov.ph/Indexes/viewMoreAward`
- **Use Case**: Competitive intelligence, pricing analysis, market research

### NOT This System: Bid Opportunities ❌
- **Focus**: Open bids you can participate in
- **Key Data**: Requirements, deadlines, specifications
- **Source**: `https://philgeps.gov.ph/Indexes/viewMoreOpenTenders`
- **Note**: This was a previous/separate project that this codebase references for context

---

## 🚀 Quick Start

### 1. First-Time Setup

**Windows:**
```bash
cd bidintel-main
scripts\setup.bat
```

**Mac/Linux:**
```bash
cd bidintel-main
bash scripts/setup.sh
```

### 2. Run the Application

```bash
cd bidintel-main
scripts\start.bat        # Windows
bash scripts/start.sh    # Mac/Linux
```

This starts:
- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:5173

### 3. Collect Awarded Contracts Data

```bash
cd bidintel-main/backend
python run_awarded_scraper.py --workers 1
```

See **[QUICK_START.md](QUICK_START.md)** for detailed instructions.

---

## 📁 Project Structure

```
bid-competitiveness/
├── README.md                           # This file - project overview
├── QUICK_START.md                      # Step-by-step startup guide
├── HOW_TO_RUN.md                       # Complete usage documentation
├── AWARDED_CONTRACTS_PROTOTYPE.md      # Technical documentation
├── SCRAPER_STATUS_REPORT.md            # Scraper testing results
│
└── bidintel-main/                      # Main application directory
    ├── backend/                        # FastAPI backend & scraper
    │   ├── backend_api.py              # API server
    │   ├── run_awarded_scraper.py      # Awarded contracts scraper ⭐
    │   ├── run_public_scraper.py       # (Legacy reference - not primary focus)
    │   ├── models/                     # Database models
    │   │   ├── schemas.py              # AwardedContract model ⭐
    │   │   └── database.py             # Database operations
    │   └── scraper/
    │       ├── awarded_contracts_scraper.py  # Awarded scraper implementation ⭐
    │       └── parser.py               # HTML parsing logic
    │
    ├── frontend/                       # React dashboard
    │   └── src/
    │       ├── components/             # UI components
    │       └── services/api.js         # Backend API client
    │
    ├── scripts/                        # Startup scripts
    │   ├── setup.bat / setup.sh        # One-time setup
    │   ├── start.bat / start.sh        # Start everything
    │   └── run-scraper.bat             # Run scraper
    │
    ├── .env.example                    # Configuration template
    └── requirements.txt                # Python dependencies
```

---

## 💡 What You Get

### Awarded Contract Data Includes:

**Financial Intelligence:**
- Approved Budget (ABC) - Government's max budget
- Contract Amount - Actual winning bid ⭐
- Savings calculation (ABC - Contract Amount)
- Savings percentage

**Winner Information:**
- Awardee company name
- Business address
- Contact person
- Corporate title

**Contract Details:**
- Award notice number
- Award date
- Contract period
- Procurement mode
- Classification (Goods/Services/Infrastructure)

**Agency Information:**
- Procuring entity (government agency)
- Agency location
- Funding source

**Line Items:**
- Specific products/services awarded
- Quantities and specifications
- UNSPSC codes

---

## 🎯 Use Cases

### 1. Competitive Intelligence
Track which companies win the most government contracts in your industry:
```
"Who are the top winners in Medical Equipment contracts?"
"How often does Company X win contracts?"
```

### 2. Pricing Strategy
Analyze winning bid patterns to optimize your pricing:
```
"What's the typical discount from ABC for IT Services?"
"Average winning bid: 22% below approved budget"
```

### 3. Market Research
Understand government procurement trends:
```
"Total awarded contracts in Q1 2025: PHP 500M"
"Most active agencies: DOH, DepEd, DPWH"
```

### 4. Competitor Monitoring
Monitor rival companies' contract wins:
```
"Competitor X won 12 contracts worth PHP 50M this quarter"
"Their average discount: 25% below ABC"
```

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 3-step guide to get started
- **[HOW_TO_RUN.md](HOW_TO_RUN.md)** - Complete setup and usage guide
- **[AWARDED_CONTRACTS_PROTOTYPE.md](AWARDED_CONTRACTS_PROTOTYPE.md)** - Technical documentation
- **[SCRAPER_STATUS_REPORT.md](SCRAPER_STATUS_REPORT.md)** - Testing and status report

---

## 🔧 Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Playwright
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Database**: SQLite (default) or PostgreSQL
- **Scraper**: Playwright-based async scraper with stealth mode

---

## ⚙️ Configuration

The system is configured via `.env` file:

```env
# Database
DATABASE_URL=sqlite:///data/philgeps_data.db

# Scraper settings
HEADLESS_MODE=true
BROWSER_TYPE=chromium

# API Server
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🔍 Frontend Dashboard Features

- **Awarded Contracts Table** - Searchable, filterable, sortable
- **Winner Analytics** - Track top contract winners
- **Pricing Intelligence** - ABC vs. awarded amount analysis
- **Agency Intelligence** - Procurement patterns by agency
- **Product Categories** - UNSPSC-based intelligence
- **Configuration** - Control scraper settings from UI

---

## 🐛 Troubleshooting

**"playwright is not recognized" on Windows:**
```bash
python -m playwright install chromium
```

**No data showing:**
- Run the scraper first: `python run_awarded_scraper.py --workers 1`
- Database starts empty

**Backend not connecting:**
- Check port 8000 is not in use
- Verify `.env` configuration

See **[HOW_TO_RUN.md](HOW_TO_RUN.md)** for complete troubleshooting guide.

---

## 📝 License & Credits

This is a custom-built intelligence system for Philippine government procurement data analysis.

**Data Source**: Philippine Government Electronic Procurement System (PhilGEPS)
- https://philgeps.gov.ph/

---

## 🎉 Getting Help

1. Read **[QUICK_START.md](QUICK_START.md)** for basic setup
2. Check **[HOW_TO_RUN.md](HOW_TO_RUN.md)** for detailed instructions
3. Review **[AWARDED_CONTRACTS_PROTOTYPE.md](AWARDED_CONTRACTS_PROTOTYPE.md)** for technical details

---

**Project Focus**: Awarded Contracts Intelligence
**Last Updated**: 2025-11-18
**Status**: Production Ready ✅
