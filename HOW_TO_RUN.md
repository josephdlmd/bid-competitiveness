# 🚀 How to Run the PhilGEPS Awarded Contracts Intelligence System

> **Project Focus**: This system is specifically designed for **AWARDED CONTRACTS** intelligence - tracking who wins government contracts and for how much.

## Quick Answer: YES, Everything is Already Connected! ✅

**Frontend ↔️ Backend ↔️ Database** are all connected and ready to use.

- **Frontend**: React app that displays awarded contracts data in a beautiful dashboard
- **Backend API**: FastAPI server that provides data to the frontend
- **Database**: SQLite database that stores all scraped awarded contracts
- **Scraper**: Python script (`run_awarded_scraper.py`) that collects awarded contracts from PhilGEPS

**Note**: While the codebase contains references to a bid opportunities scraper (legacy from previous project), the primary focus is **awarded contracts intelligence**.

---

## 🎯 Method 1: Automated Setup & Run (EASIEST)

### Windows Users

**Step 1: Run Setup (One Time Only)**
```bash
cd bidintel-main
scripts\setup.bat
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Install Playwright browser (Chromium)
- Install frontend dependencies (npm packages)
- Create `.env` configuration file
- Initialize the database

**Step 2: Start Everything**
```bash
cd bidintel-main
scripts\start.bat
```

This will:
- Start the backend API in a new window (http://localhost:8000)
- Start the frontend in a new window (http://localhost:5173)
- Open both automatically!

**That's it!** Open http://localhost:5173 in your browser.

---

### Mac/Linux Users

**Step 1: Run Setup (One Time Only)**
```bash
cd bidintel-main
bash scripts/setup.sh
```

**Step 2: Start Everything**
```bash
cd bidintel-main
bash scripts/start.sh
```

---

## 🎯 Method 2: Manual Setup (More Control)

If you prefer to run things step by step:

### Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Git installed

### Step 1: Set Up Backend

```bash
# Navigate to the project
cd bidintel-main

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
# Windows:
python -m playwright install chromium
# Mac/Linux:
playwright install chromium

# Create configuration file
copy .env.example .env     # Windows
cp .env.example .env       # Mac/Linux
```

### Step 2: Set Up Frontend

```bash
cd frontend
npm install
cd ..
```

### Step 3: Run Backend API (Terminal 1)

```bash
cd backend
python backend_api.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal running!**

### Step 4: Run Frontend (Terminal 2 - New Window)

Open a **NEW terminal window**:

```bash
cd bidintel-main/frontend
npm run dev
```

You should see:
```
VITE ready in X ms
➜  Local:   http://localhost:5173/
```

### Step 5: Open in Browser

Navigate to **http://localhost:5173**

---

## 🔧 Individual Scripts Available

All scripts are in `bidintel-main/scripts/`:

### Windows (.bat files)
- `setup.bat` - One-time setup (installs everything)
- `start.bat` - Start both backend and frontend
- `start-backend.bat` - Start backend API only
- `start-frontend.bat` - Start frontend only
- `run-scraper.bat` - Run the awarded contracts scraper ⭐
- `stop.bat` - Stop all services

### Mac/Linux (.sh files)
- `setup.sh` - One-time setup
- `start.sh` - Start both backend and frontend
- `start-backend.sh` - Start backend API only
- `start-frontend.sh` - Start frontend only
- `run-scraper.sh` - Run the awarded contracts scraper ⭐

---

## 📊 How to Populate the Dashboard with Data

The frontend will show **no data** initially because the database is empty. To collect awarded contracts data:

### Run the Awarded Contracts Scraper

```bash
cd bidintel-main/backend
python run_awarded_scraper.py --workers 1
```

**What this does:**
- Scrapes awarded contracts from https://philgeps.gov.ph/Indexes/viewMoreAward
- Collects winner information, contract amounts, ABC values
- Calculates savings (ABC - Contract Amount)
- Stores in database for analysis

**Recommended settings:**
- Start with `--workers 1` for testing
- Use `--workers 2` for production (faster, but more resource-intensive)

### Check the Data

Once the scraper finishes, refresh the frontend at http://localhost:5173 and you'll see real awarded contracts data!

**Note**: The codebase also contains `run_public_scraper.py` (legacy bid opportunities scraper from previous project), but the primary focus of this system is awarded contracts intelligence.

---

## 🌐 How the Connection Works

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │   Backend API   │         │   Database      │
│   (React)       │ ←────→  │   (FastAPI)     │ ←────→  │   (SQLite)      │
│                 │  HTTP   │                 │  SQL    │                 │
│ localhost:5173  │         │ localhost:8000  │         │ data/*.db       │
└─────────────────┘         └─────────────────┘         └─────────────────┘
        ↑                            ↑
        │                            │
    Your Browser              API Endpoints:
                              /api/bids
                              /api/stats
                              /api/analytics
                              /api/scraper/*
```

### Frontend API Configuration

The frontend is configured to connect to the backend at:
- **Default**: `http://localhost:8000/api`
- **Configurable**: Set `VITE_API_URL` in `.env` for production

See: `bidintel-main/frontend/src/services/api.js`

### Backend CORS Configuration

The backend allows connections from:
- `http://localhost:5173` (Vite dev server)
- `http://127.0.0.1:5173`

See: `bidintel-main/backend/backend_api.py` (line 24-30)

---

## 🎨 What You'll See in the Frontend

The dashboard includes:

1. **All Bids** - Complete table of all bid opportunities
2. **Top Opportunities** - High-value bids filtered by criteria
3. **Products (UNSPSC)** - Intelligence by product category
4. **Agencies** - Intelligence by government agency
5. **Configuration** - Control scraper settings from the UI

### Features
- ✅ Search across titles, descriptions, agencies
- ✅ Filter by classification, region, budget
- ✅ Sort by any column
- ✅ View detailed bid information
- ✅ Pagination for large datasets
- ✅ Real-time data from backend API

---

## 🔍 Testing the Connection

### Test Backend is Running

Open http://localhost:8000/docs in your browser.

You should see the **FastAPI interactive documentation** (Swagger UI).

### Test Frontend Can Reach Backend

1. Open http://localhost:5173
2. Open browser Developer Tools (F12)
3. Go to Console tab
4. Look for network requests to `http://localhost:8000/api/*`
5. No errors = working! ✅

### Test Database Has Data

```bash
cd bidintel-main/backend
python -c "from models.database import Database; db = Database(); print(f'Total bids: {db.get_total_bids()}')"
```

---

## ⚙️ Configuration

### Backend Configuration (.env)

Located at `bidintel-main/.env`:

```env
# Database
DATABASE_URL=sqlite:///data/philgeps_data.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Scraper Settings
HEADLESS_MODE=true
BROWSER_TYPE=chromium
```

### Frontend Configuration

The frontend uses environment variables prefixed with `VITE_`:

```env
# Optional: Override API URL (for production)
VITE_API_URL=http://your-server.com/api
```

---

## 🐛 Troubleshooting

### Frontend Shows "No Data"

**Cause**: Database is empty
**Solution**: Run a scraper to populate data (see "How to Populate" section above)

### Frontend Shows "Network Error" or "Cannot connect"

**Cause**: Backend is not running
**Solution**: Make sure backend is running on port 8000
```bash
cd bidintel-main/backend
python backend_api.py
```

### Backend Port Already in Use

**Cause**: Port 8000 is taken by another application
**Solution**: Change the port in `.env`:
```env
API_PORT=8001
```

Then update frontend API URL to match.

### Frontend Port Already in Use

**Cause**: Port 5173 is taken
**Solution**: Vite will auto-increment to 5174, 5175, etc. Just use the new port shown in the terminal.

### "playwright: command not found" on Windows

**Cause**: Windows doesn't recognize the `playwright` command
**Solution**: Use `python -m playwright` instead
```bash
python -m playwright install chromium
```

---

## 📚 Additional Resources

- **Awarded Contracts Guide**: See `AWARDED_CONTRACTS_PROTOTYPE.md`
- **Quick Start Guide**: See `QUICK_START.md`
- **Scraper Status**: See `SCRAPER_STATUS_REPORT.md`
- **Frontend README**: See `bidintel-main/frontend/README.md`

---

## 💡 Quick Commands Cheat Sheet

### Windows

```bash
# First time setup
cd bidintel-main
scripts\setup.bat

# Start application
scripts\start.bat

# Run awarded contracts scraper ⭐
cd backend
python run_awarded_scraper.py --workers 1

# Stop everything
scripts\stop.bat
```

### Mac/Linux

```bash
# First time setup
cd bidintel-main
bash scripts/setup.sh

# Start application
bash scripts/start.sh

# Run awarded contracts scraper ⭐
cd backend
python run_awarded_scraper.py --workers 1
```

---

## ✅ Success Checklist

After setup, you should have:

- [x] Backend API running at http://localhost:8000
- [x] Frontend running at http://localhost:5173
- [x] API docs accessible at http://localhost:8000/docs
- [x] `.env` file created from `.env.example`
- [x] Database file at `bidintel-main/data/philgeps_data.db`
- [x] All npm packages installed in `frontend/node_modules`
- [x] Playwright browser installed

---

## 🎉 You're Ready!

Everything is connected and ready to use. Just run the **awarded contracts scraper** to populate your database with real PhilGEPS awarded contracts data, and the frontend will automatically display competitive intelligence!

**This system focuses on**: Awarded contracts intelligence - who wins, for how much, pricing patterns, and competitive analysis.

**Questions?** Check the other documentation files:
- **README.md** - Project overview and scope
- **QUICK_START.md** - 3-step startup guide
- **AWARDED_CONTRACTS_PROTOTYPE.md** - Technical details
