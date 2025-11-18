# PhilGEPS Scraper - Quick Start Guide (Windows)

## Easy Commands

All commands should be run from the project root directory (`C:\Users\User\Documents\GitHub\bidintel`)

### Start Everything
```batch
scripts\start.bat
```
This opens two windows:
- Backend API (http://localhost:8000)
- Frontend Dashboard (http://localhost:5173)

### Stop Everything
```batch
scripts\stop-safe.bat
```
Safely stops all running services.

### Run Individual Services

**Backend Only:**
```batch
scripts\start-backend.bat
```

**Frontend Only:**
```batch
scripts\start-frontend.bat
```

**Run Scraper:**
```batch
scripts\run-scraper.bat
```

**Run Scraper with Custom Workers:**
```batch
scripts\run-scraper.bat --workers 3
```

---

## Manual Commands (PowerShell)

If you prefer to run commands manually:

### Backend
```powershell
cd backend
..\venv\Scripts\python.exe backend_api.py
```

### Frontend
```powershell
cd frontend
npm run dev
```

### Scraper
```powershell
cd backend
..\venv\Scripts\python.exe run_public_scraper.py --workers 2
```

---

## Troubleshooting

**If ports are busy:**
```batch
scripts\stop-safe.bat
```

**Check what's running on ports:**
```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

**Kill specific process:**
```powershell
taskkill /F /PID <process_id>
```

---

## URLs

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
