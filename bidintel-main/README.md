# PhilGEPS Awarded Contracts Intelligence - Deployment Bundle

> **Primary Focus**: This application is specifically designed for scraping and analyzing **AWARDED CONTRACTS** from PhilGEPS.

A complete, deployment-ready application for tracking and analyzing Philippine Government Electronic Procurement System (PhilGEPS) **awarded contracts** - showing who wins government contracts, for how much, and competitive pricing intelligence.

**Note**: While this codebase contains legacy references to a bid opportunities scraper (from a previous project), the primary focus and purpose is **awarded contracts intelligence**.

## Features

### Awarded Contracts Intelligence (Primary Focus)
- **Awarded Contracts Scraper**: Collects completed government contracts with winner and pricing data
- **Competitive Intelligence**: Track who wins contracts and their pricing strategies
- **Pricing Analysis**: ABC vs. Contract Amount comparison, savings calculations
- **Winner Tracking**: Monitor competitor companies and their contract wins
- **Agency Analytics**: Understand government agency procurement patterns

### Technical Features
- **Public Scraper**: Uses public PhilGEPS URLs - no login credentials needed
- **Async Architecture**: Fast, concurrent scraping with multiple workers
- **FastAPI Backend**: RESTful API with automatic documentation
- **React Frontend**: Modern, responsive dashboard with filtering and analytics
- **SQLite Database**: Lightweight, portable data storage (PostgreSQL also supported)
- **Stealth Mode**: Bot detection evasion for reliable scraping
- **Easy Deployment**: Simple setup scripts for quick deployment

## Architecture

```
bidintel-main/
├── backend/                        # FastAPI backend & scraper
│   ├── backend_api.py              # API server
│   ├── run_awarded_scraper.py      # ⭐ Awarded contracts scraper (PRIMARY)
│   ├── run_public_scraper.py       # (Legacy reference - bid opportunities)
│   ├── scraper/                    # Scraper modules
│   │   ├── awarded_contracts_scraper.py  # ⭐ Main awarded scraper
│   │   └── parser.py               # HTML parsing logic
│   ├── models/                     # Database models
│   │   ├── schemas.py              # AwardedContract model ⭐
│   │   └── database.py             # Database operations
│   ├── config/                     # Configuration
│   └── utils/                      # Utilities
├── frontend/                       # React + Vite frontend
│   ├── src/
│   │   ├── components/             # UI components
│   │   └── services/api.js         # Backend API client
│   └── package.json
├── scripts/                        # Deployment scripts
│   ├── setup.bat / setup.sh        # One-time setup
│   ├── start.bat / start.sh        # Start everything
│   ├── start-backend.bat / .sh     # Backend only
│   ├── start-frontend.bat / .sh    # Frontend only
│   └── run-scraper.bat             # Run awarded scraper
├── requirements.txt                # Python dependencies
├── .env.example                    # Configuration template
└── README.md                       # This file
```

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 18 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 1GB minimum for application + data

### Operating Systems
- **Windows**: Native support with `.bat` scripts
- **Linux**: Ubuntu, Debian, CentOS, etc.
- **macOS**: Full support

## Quick Start

> **Note**: Both Windows (`.bat`) and Linux/Mac (`.sh`) scripts are provided. Use the appropriate one for your system.

### For Windows Users 🪟

#### 1. Initial Setup

```batch
REM Navigate to the bundle directory
cd philgeps-public-bundle

REM Run the setup script
scripts\setup.bat
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Install Playwright browsers
- Create a `.env` configuration file
- Install frontend dependencies
- Initialize the database

#### 2. Configuration

Edit the `.env` file to customize your settings:

```batch
notepad .env
```

**Key settings:**
- `DATABASE_URL`: Database connection (default: SQLite)
- `HEADLESS_MODE`: Run browser in headless mode (true/false)
- `FILTER_PUBLISH_DATE_FROM`: Date range filtering
- `FILTER_CLASSIFICATION`: Filter by classification type

**Note**: This scraper uses public URLs and does **NOT** require PhilGEPS credentials!

#### 3. Start the Application

```batch
REM Start both backend and frontend
scripts\start.bat
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

### For Linux/Mac Users 🐧 🍎

#### 1. Initial Setup

```bash
# Navigate to the bundle directory
cd philgeps-public-bundle

# Run the setup script
./scripts/setup.sh
```

This will:
- Create a Python virtual environment
- Install all Python dependencies
- Install Playwright browsers
- Create a `.env` configuration file
- Install frontend dependencies
- Initialize the database

#### 2. Configuration

Edit the `.env` file to customize your settings:

```bash
nano .env  # or use your preferred editor
```

**Key settings:**
- `DATABASE_URL`: Database connection (default: SQLite)
- `HEADLESS_MODE`: Run browser in headless mode (true/false)
- `FILTER_PUBLISH_DATE_FROM`: Date range filtering
- `FILTER_CLASSIFICATION`: Filter by classification type

**Note**: This scraper uses public URLs and does **NOT** require PhilGEPS credentials!

#### 3. Start the Application

```bash
# Start both backend and frontend
./scripts/start.sh
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Usage

### Running the Scraper

#### Option 1: Manual Run (CLI)

**Windows:**
```batch
REM Run scraper with 2 workers (default)
scripts\run-scraper.bat

REM Run scraper with custom number of workers
scripts\run-scraper.bat --workers 3
```

**Linux/Mac:**
```bash
# Run scraper with 2 workers (default)
./scripts/run-scraper.sh

# Run scraper with custom number of workers
./scripts/run-scraper.sh --workers 3
```

#### Option 2: API Trigger
Use the frontend interface or send a POST request:

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scraper/run" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"one_time": true}'
```

**Linux/Mac:**
```bash
curl -X POST http://localhost:8000/api/scraper/run \
  -H "Content-Type: application/json" \
  -d '{"one_time": true}'
```

#### Option 3: Direct Python

**Windows:**
```batch
call venv\Scripts\activate.bat
cd backend
python run_public_scraper.py --workers 2
```

**Linux/Mac:**
```bash
source venv/bin/activate
cd backend
python3 run_public_scraper.py --workers 2
```

### Starting Individual Services

**Windows:**
```batch
REM Backend only
scripts\start-backend.bat

REM Frontend only
scripts\start-frontend.bat
```

**Linux/Mac:**
```bash
# Backend only
./scripts/start-backend.sh

# Frontend only
./scripts/start-frontend.sh
```

## API Endpoints

### Bids
- `GET /api/bids` - List all bids with filtering
- `GET /api/bids/{id}` - Get single bid details

### Analytics
- `GET /api/stats` - Dashboard statistics
- `GET /api/analytics` - Analytics data for charts

### Scraper Control
- `GET /api/scraper/status` - Get scraper status
- `POST /api/scraper/run` - Start scraper
- `POST /api/scraper/stop` - Stop scraper
- `GET /api/scraper/config` - Get configuration
- `POST /api/scraper/config` - Update configuration

### Logs
- `GET /api/logs` - Scraping session logs

Full API documentation available at: http://localhost:8000/docs

## Production Deployment

### Option 1: Simple Production Build

```bash
# Build frontend for production
cd frontend
npm run build

# Serve with a production server (nginx, etc.)
# Backend runs on port 8000 with uvicorn
```

### Option 2: Docker Deployment
(Docker configuration not included in this bundle but can be added)

### Option 3: VPS Deployment (DigitalOcean, AWS, etc.)

1. **Upload the bundle** to your server
2. **Run setup**:
   ```bash
   ./scripts/setup.sh
   ```
3. **Configure production settings** in `.env`:
   ```
   HEADLESS_MODE=true
   DATABASE_URL=postgresql://...  # Use PostgreSQL for production
   ```
4. **Use process manager** (systemd, supervisor, pm2):
   ```bash
   # Example with systemd
   sudo systemctl start philgeps-backend
   sudo systemctl enable philgeps-backend
   ```

## Database

### SQLite (Default)
The default configuration uses SQLite for simplicity:
```
DATABASE_URL=sqlite:///data/philgeps_data.db
```

Database file location: `data/philgeps_data.db`

### PostgreSQL (Recommended for Production)
For production, use PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost:5432/philgeps_scraper
```

## Troubleshooting

### Scraper Issues

**Problem**: Scraper fails with browser errors
```bash
# Reinstall Playwright browsers
# Mac/Linux:
source venv/bin/activate
playwright install chromium

# Windows:
python -m playwright install chromium
```

**Problem**: "No bids found"
- Check your date filters in `.env`
- Verify PhilGEPS website is accessible
- Try without filters first

### API Issues

**Problem**: Backend fails to start
- Check if port 8000 is already in use: `lsof -i :8000`
- Check logs: `tail -f logs/scraper.log`

**Problem**: CORS errors in frontend
- Verify backend is running on port 8000
- Check CORS settings in `backend/backend_api.py`

### Database Issues

**Problem**: Database errors
```bash
# Reset database
rm data/philgeps_data.db
cd backend
python3 -c "from models.database import Database; Database()"
```

## Maintenance

### Backup Database
```bash
# SQLite
cp data/philgeps_data.db data/philgeps_data.backup.db

# PostgreSQL
pg_dump philgeps_scraper > backup.sql
```

### Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
cd frontend && npm update
```

### View Logs
```bash
# Scraper logs
tail -f logs/scraper.log

# API logs (if running in background)
tail -f backend.log
```

## Performance Tips

1. **Workers**: Start with 2 workers, increase cautiously to avoid detection
2. **Headless Mode**: Use `HEADLESS_MODE=true` for production
3. **Database**: Use PostgreSQL for better performance with large datasets
4. **Rate Limiting**: Keep `REQUEST_DELAY_SECONDS=2` or higher
5. **Persistent Profile**: Enable `USE_PERSISTENT_PROFILE=true` to reduce detection

## Differences from Authenticated Scraper

| Feature | Public Scraper | Authenticated Scraper |
|---------|----------------|----------------------|
| Login Required | ❌ No | ✅ Yes |
| CAPTCHA Challenges | Rare | Frequent |
| Setup Complexity | Simple | Complex |
| Data Completeness | Full | Full |
| Speed | Fast | Slower |
| Session Management | None | Required |

## Support

### Common Questions

**Q: Do I need PhilGEPS credentials?**
A: No! This scraper uses public URLs and requires no authentication.

**Q: How often should I run the scraper?**
A: For daily updates, run once per day. For real-time monitoring, run every few hours.

**Q: Can I run multiple scrapers simultaneously?**
A: Not recommended - use the `--workers` parameter instead for parallel processing.

**Q: What data is collected?**
A: Bid notices, line items, documents, procuring entities, budgets, and deadlines.

## License

[Your License Here]

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
- [Playwright](https://playwright.dev/) - Browser automation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

---

**Need help?** Open an issue or check the logs in `logs/scraper.log`
