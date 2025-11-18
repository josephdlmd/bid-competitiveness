# Performance Optimization Guide for Large Databases

## Current Status ✅

Your application already has several optimizations in place:

1. **Database Indexes** - Key fields are indexed:
   - `reference_number` (unique index)
   - `status`
   - `control_number`
   - `publish_date`
   - `closing_date`

2. **API Pagination** - Limits data returned per request:
   - Bids: Default 100, max 1000 per page
   - Logs: Default 50, max 500 per page

3. **Efficient Queries** - Uses SQLAlchemy ORM with proper filtering

---

## Recommended Optimizations by Database Size

### Small Database (< 10,000 bids) - Current Setup ✅
**Status:** No action needed, current SQLite setup is optimal

### Medium Database (10,000 - 100,000 bids) - Optimize SQLite
**Recommended Actions:**

1. **Add Composite Indexes** for common queries:
```sql
CREATE INDEX idx_status_date ON bid_notices(status, publish_date);
CREATE INDEX idx_entity_date ON bid_notices(procuring_entity, closing_date);
CREATE INDEX idx_classification_budget ON bid_notices(classification, approved_budget);
```

2. **Enable SQLite Performance Features** in `.env`:
```ini
# Add these to your .env file
DATABASE_URL=sqlite:///C:/Users/User/Documents/GitHub/bidintel/data/philgeps_data.db?check_same_thread=False
SQLITE_PRAGMA_journal_mode=WAL
SQLITE_PRAGMA_synchronous=NORMAL
SQLITE_PRAGMA_cache_size=-64000
SQLITE_PRAGMA_temp_store=MEMORY
```

3. **Regular Database Maintenance:**
```powershell
# Run monthly to optimize database
cd backend
..\venv\Scripts\python.exe -c "from models.database import Database; db = Database(); db.engine.execute('VACUUM'); db.engine.execute('ANALYZE')"
```

### Large Database (> 100,000 bids) - Switch to PostgreSQL
**Recommended:** Migrate to PostgreSQL for better performance

#### PostgreSQL Setup:

1. **Install PostgreSQL:**
   - Download: https://www.postgresql.org/download/windows/
   - Install with default settings
   - Remember the password you set for user `postgres`

2. **Create Database:**
```sql
-- Run in pgAdmin or psql
CREATE DATABASE philgeps_scraper;
CREATE USER philgeps_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE philgeps_scraper TO philgeps_user;
```

3. **Update `.env` file:**
```ini
DATABASE_URL=postgresql://philgeps_user:your_secure_password@localhost:5432/philgeps_scraper
```

4. **Migrate existing data** (if you have SQLite data):
```powershell
cd backend
..\venv\Scripts\python.exe migrate_to_postgres.py
```

---

## Additional Performance Optimizations

### 1. Frontend Optimizations

**Virtual Scrolling** for large lists (already implemented with pagination)

**Lazy Loading** - Load data as needed:
- ✅ Already using pagination
- ✅ Loads 100 bids at a time
- Consider reducing to 50 for faster initial load

### 2. API Response Caching

Add caching for frequently accessed data:

```python
# Add to backend_api.py
from functools import lru_cache
import time

# Cache stats for 5 minutes
stats_cache = {"data": None, "timestamp": 0}

@app.get("/api/stats")
def get_stats():
    now = time.time()
    if stats_cache["data"] and (now - stats_cache["timestamp"]) < 300:
        return stats_cache["data"]

    # ... existing stats logic ...
    stats_cache["data"] = result
    stats_cache["timestamp"] = now
    return result
```

### 3. Database Connection Pooling

For PostgreSQL, configure connection pooling in `database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 4. Query Optimization

**Use SELECT specific columns** instead of loading entire objects:

```python
# Instead of:
bids = session.query(BidNotice).all()

# Use:
bids = session.query(
    BidNotice.id,
    BidNotice.title,
    BidNotice.status,
    BidNotice.approved_budget
).all()
```

### 5. Background Processing

For long-running scrapes, use background tasks (already implemented):
- ✅ Scraper runs in background
- ✅ Non-blocking API responses

### 6. Monitoring & Analytics

**Track database size:**
```powershell
# SQLite
cd data
dir philgeps_data.db

# PostgreSQL
psql -U philgeps_user -d philgeps_scraper -c "SELECT pg_size_pretty(pg_database_size('philgeps_scraper'));"
```

**Monitor query performance:**
```python
# Enable SQL logging temporarily
engine = create_engine(settings.DATABASE_URL, echo=True)
```

---

## Performance Benchmarks

| Database Size | SQLite Performance | PostgreSQL Performance |
|---------------|-------------------|----------------------|
| 1,000 bids    | ⚡ Excellent       | ⚡ Excellent          |
| 10,000 bids   | ⚡ Good            | ⚡ Excellent          |
| 50,000 bids   | ⚠️ Moderate        | ⚡ Excellent          |
| 100,000+ bids | ❌ Slow            | ⚡ Good               |
| 500,000+ bids | ❌ Very Slow       | ⚡ Good               |
| 1M+ bids      | ❌ Not Recommended | ⚡ Acceptable         |

---

## Quick Performance Check

**Test your current database performance:**

```powershell
cd backend
..\venv\Scripts\python.exe -c "
from models.database import Database
from models.schemas import BidNotice
import time

db = Database()
session = db.get_session()

# Count total records
start = time.time()
count = session.query(BidNotice).count()
count_time = time.time() - start

# Query with filters
start = time.time()
bids = session.query(BidNotice).filter(BidNotice.status == 'Open').limit(100).all()
query_time = time.time() - start

print(f'Total bids: {count}')
print(f'Count query: {count_time:.3f}s')
print(f'Filter query: {query_time:.3f}s')
print()
if count_time > 1:
    print('⚠️  Consider optimization!')
else:
    print('✅ Performance is good')
"
```

---

## Recommended Actions by Current Size

**Run this to check your database size:**
```powershell
cd data
(Get-Item philgeps_data.db).length / 1MB
```

**If < 50 MB:** You're fine, no action needed ✅
**If 50-200 MB:** Add composite indexes (see Medium Database section)
**If > 200 MB:** Consider PostgreSQL migration
**If > 1 GB:** Definitely switch to PostgreSQL

---

## Automated Optimization Script

Create `scripts\optimize-db.bat`:

```batch
@echo off
echo Running database optimization...
cd backend
..\venv\Scripts\python.exe -c "from models.database import Database; db = Database(); db.engine.execute('VACUUM'); db.engine.execute('ANALYZE'); print('✅ Database optimized!')"
pause
```

Run monthly for best performance.
