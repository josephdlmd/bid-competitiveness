# Awarded Contracts Scraper - Prototype Documentation

## 📋 Overview

This prototype extends the existing PhilGEPS scraper to collect **awarded contracts** data. While the original scraper focused on **open bid opportunities**, this new module focuses on **contracts that have already been awarded**, capturing critical competitive intelligence including:

- **Who won the contract** (Awardee information)
- **ABC** (Approved Budget for the Contract)
- **Contract Amount** (The actual awarded price - what they won for) ⭐
- **Savings analysis** (ABC vs. Contract Amount)
- **Award dates and contract details**
- **Link to original bid** (via Bid Reference Number)

---

## 🎯 Key Differences: Bid Opportunities vs. Awarded Contracts

| Aspect | Bid Opportunities (Original) | Awarded Contracts (New) |
|--------|------------------------------|-------------------------|
| **Purpose** | Track open bids companies can participate in | Track who won contracts and for how much |
| **Status** | Open/Closed (for bidding) | Awarded (contract signed) |
| **Key Data** | Approved Budget, Requirements, Deadlines | Awardee, ABC, Contract Amount, Award Date |
| **URL** | `/Indexes/viewMoreOpenTenders` | `/Indexes/viewMoreAward` |
| **Primary ID** | `reference_number` | `award_notice_number` |
| **Critical Field** | `closing_date` (deadline to bid) | `contract_amount` (awarded price) ⭐ |

---

## 📂 Files Created

### 1. **Database Schema** (`bidintel-main/backend/models/schemas.py`)

Added 3 new models:

#### **`AwardedContract`** (Main Model)
```python
class AwardedContract(Base):
    # Primary identifier
    award_notice_number  # e.g., "1998"

    # Link to original bid
    bid_reference_number  # Links to BidNotice.reference_number (e.g., "6793")
    control_number

    # Awardee (Winner) Information ⭐
    awardee_name          # e.g., "LOUISE AND AEDAN ENTERPRISE INC."
    awardee_address
    awardee_contact_person
    awardee_corporate_title

    # Financial Information (CRITICAL) ⭐
    approved_budget       # ABC - What government budgeted
    contract_amount       # AWARDED PRICE - What awardee won for

    # Contract Details
    contract_number
    contract_effectivity_date
    contract_end_date
    period_of_contract

    # Award Information
    award_title
    award_type
    award_date

    # Other fields (procurement, dates, etc.)
    ...
```

**Helper Methods:**
- `get_savings_amount()` - Returns ABC - Contract Amount
- `get_savings_percentage()` - Returns savings as percentage

#### **`AwardLineItem`**
Line items for awarded contracts (similar to `LineItem` but for awards)

#### **`AwardDocument`**
Documents attached to awarded contracts

### 2. **Parser Methods** (`bidintel-main/backend/scraper/parser.py`)

Added comprehensive parsing for awarded contracts:

```python
class PhilGEPSParser:
    def parse_awarded_contract(self) -> Dict:
        """Parse awarded contract detail page."""
        # Extracts all fields from awarded contract pages

    # Individual extraction methods:
    def _extract_award_notice_number(self)
    def _extract_bid_reference_number(self)
    def _extract_awardee_name(self)           ⭐
    def _extract_awardee_contact_person(self) ⭐
    def _extract_awardee_address(self)        ⭐
    def _extract_contract_amount(self)        ⭐ CRITICAL
    def _extract_award_date(self)
    def _extract_contract_number(self)
    def _extract_contract_effectivity_date(self)
    def _extract_contract_end_date(self)
    def _extract_period_of_contract(self)
    # ... and more
```

### 3. **Database Methods** (`bidintel-main/backend/models/database.py`)

Added awarded contracts operations:

```python
class Database:
    # Core operations
    def save_awarded_contract(award_data: Dict)
    def awarded_contract_exists(award_notice_number: str)
    def get_awarded_contract_by_number(award_notice_number: str)

    # Querying and filtering
    def get_all_awarded_contracts(limit: int, filters: Dict)
    def get_filtered_awarded_contracts(
        date_from, date_to,
        min_budget, max_budget,
        min_contract_amount, max_contract_amount,  ⭐
        classification, category,
        awardee, procuring_entity,
        search_term
    )

    # Specialized queries
    def get_awarded_contracts_by_awardee(awardee_name: str)
    def get_awarded_contracts_by_bid_reference(bid_reference_number: str)

    # Statistics
    def get_award_stats() -> Dict:
        # Returns:
        # - total_awards
        # - total_abc
        # - total_contract_amount
        # - total_savings
        # - avg_savings_percentage
        # - unique_awardees
```

### 4. **Scraper** (`bidintel-main/backend/scraper/awarded_contracts_scraper.py`)

Full-featured async scraper:

```python
class AwardedContractsScraper:
    """
    Scrapes awarded contracts from:
    - Index: https://philgeps.gov.ph/Indexes/viewMoreAward
    - Detail: /Indexes/viewAwardNotice/{award_id}/MORE
    """

    async def run(self) -> Dict:
        """Complete scraping workflow with pagination."""

    async def _worker(worker_id, page, award_list):
        """Parallel worker for concurrent scraping."""

    async def _scrape_award_details(page, url):
        """Scrape individual award detail page."""
```

**Features:**
- ✅ Async/await for concurrent processing
- ✅ Multiple workers (parallel tabs)
- ✅ Stealth mode (bot detection evasion)
- ✅ Pagination support
- ✅ Duplicate detection (skips already scraped)
- ✅ Rate limiting (human-like delays)
- ✅ Error handling and logging
- ✅ No authentication required

### 5. **Run Script** (`bidintel-main/backend/run_awarded_scraper.py`)

Command-line interface:

```bash
# Run with default 2 workers
python run_awarded_scraper.py

# Run with 3 workers
python run_awarded_scraper.py --workers 3

# Run in headless mode
python run_awarded_scraper.py --headless

# Run in visible mode (see browser)
python run_awarded_scraper.py --visible
```

### 6. **Test Script** (`test_awarded_parser.py`)

Tests the parser with reference HTML files:

```bash
python test_awarded_parser.py
```

---

## 🚀 How to Use

### Prerequisites

1. **Install dependencies** (if not already done):
   ```bash
   cd bidintel-main
   pip install -r requirements.txt
   ```

   Then install Playwright browsers:
   - **Windows**: `python -m playwright install chromium`
   - **Mac/Linux**: `playwright install chromium`

2. **Configure settings** in `.env`:
   ```env
   DATABASE_URL=sqlite:///data/philgeps_data.db
   HEADLESS_MODE=true
   BROWSER_TYPE=chromium
   # ... other settings
   ```

### Running the Scraper

#### Option 1: Test with Reference HTML First

```bash
# Test parser with saved HTML files
python test_awarded_parser.py
```

Expected output:
```
✅ Found: Award Notice Number
✅ Found: Awardee Name
✅ Found: ABC (Approved Budget)
✅ Found: Contract Amount (Awarded Price)
✅ Found: Award Date

💡 Savings: PHP 625,000.00 (45.45%)
```

#### Option 2: Run the Scraper

```bash
cd bidintel-main/backend

# Start with 1 worker for testing
python run_awarded_scraper.py --workers 1

# Production: use 2-3 workers
python run_awarded_scraper.py --workers 2
```

Expected output:
```
✅ Status: SUCCESS
⏱️  Duration: 45.23 seconds
📊 Total Scraped: 25
🆕 New Records: 25
⏭️  Skipped: 0
❌ Errors: 0
```

### Querying the Data

```python
from models.database import Database

db = Database()

# Get all awarded contracts
awards = db.get_all_awarded_contracts(limit=10)

# Filter by awardee
awards = db.get_awarded_contracts_by_awardee("LOUISE AND AEDAN")

# Get statistics
stats = db.get_award_stats()
print(f"Total Awards: {stats['total_awards']}")
print(f"Total ABC: PHP {stats['total_abc']:,.2f}")
print(f"Total Contract Amount: PHP {stats['total_contract_amount']:,.2f}")
print(f"Total Savings: PHP {stats['total_savings']:,.2f}")
print(f"Avg Savings: {stats['avg_savings_percentage']:.2f}%")

# Link awards to bids
bid_ref = "6793"
awards = db.get_awarded_contracts_by_bid_reference(bid_ref)
# This shows who won bid #6793
```

---

## 📊 Example Data Flow

### Index Page → List of Awards

```
Award Notice #1998
├─ Bid Ref: 6793
├─ Title: Various Electromagnetic Flowmeter
├─ Awardee: LOUISE AND AEDAN ENTERPRISE INC.
└─ Award Date: 12-Nov-2025
```

### Detail Page → Full Award Details

```
Award Notice Number: 1998
Bid Reference Number: 6793 (links to original bid)

AWARDEE (Winner):
├─ Name: LOUISE AND AEDAN ENTERPRISE INC.
├─ Contact: AXELL JAY CATAPANG
├─ Address: No. 19 Don Pedro Subdivision...
└─ Corporate Title: Proprietor

FINANCIAL ANALYSIS:
├─ ABC (Approved Budget): PHP 1,375,000.00
├─ Contract Amount (Won For): PHP 750,000.00 ⭐
└─ Savings: PHP 625,000.00 (45.45%) 💰

CONTRACT DETAILS:
├─ Award Date: 12-Nov-2025
├─ Period: 30-Day(s)
├─ Classification: Goods
└─ Procurement Mode: Small Value Procurement
```

---

## 🔗 Integration with Existing System

### Database Tables

The new tables coexist with existing ones:

```
Existing Tables:
├─ bid_notices           (Open bids)
├─ line_items           (Bid line items)
└─ bid_documents        (Bid documents)

New Tables:
├─ awarded_contracts     (Awarded contracts) ⭐
├─ award_line_items     (Award line items)
└─ award_documents      (Award documents)
```

### Linking Bids to Awards

```python
# Find who won a specific bid
bid = db.get_bid_by_reference("6793")
awards = db.get_awarded_contracts_by_bid_reference("6793")

if awards:
    award = awards[0]
    print(f"Bid #{bid.reference_number} was awarded to: {award.awardee_name}")
    print(f"ABC: PHP {award.approved_budget:,.2f}")
    print(f"Won for: PHP {award.contract_amount:,.2f}")
    print(f"Savings: {award.get_savings_percentage():.2f}%")
```

---

## 🎯 Key Insights You Can Extract

### 1. Competitive Intelligence

```python
# Who wins the most contracts?
awardees = db.get_filtered_awarded_contracts(
    date_from=datetime(2025, 1, 1),
    limit=1000
)

from collections import Counter
winners = Counter([a.awardee_name for a in awardees])
top_10 = winners.most_common(10)
```

### 2. Pricing Analysis

```python
# What's the typical discount from ABC?
awards = db.get_filtered_awarded_contracts(
    min_contract_amount=100000,
    max_contract_amount=10000000
)

avg_discount = sum(a.get_savings_percentage() for a in awards) / len(awards)
print(f"Average discount from ABC: {avg_discount:.2f}%")
```

### 3. Awardee Performance

```python
# Track specific competitor
competitor_awards = db.get_awarded_contracts_by_awardee("HIRAYA TECHNOLOGY")

for award in competitor_awards:
    print(f"{award.award_title}: PHP {award.contract_amount:,.2f}")
```

---

## ⚙️ Technical Details

### HTML Parsing Strategy

The parser uses BeautifulSoup to extract data from PhilGEPS pages:

```python
# Example: Extract Contract Amount
<label>Contract Amount:</label><br>PHP 750,000.00<br><br>

# Parser logic:
label = soup.find('label', string=re.compile(r'Contract Amount', re.I))
sibling = label.find_next_sibling(string=True)
amount_str = re.sub(r'[^\d.]', '', sibling.strip())  # Remove "PHP", commas
return float(amount_str)
```

### Workflow Comparison

| Step | Bid Opportunities | Awarded Contracts |
|------|-------------------|-------------------|
| 1. Index URL | `viewMoreOpenTenders` | `viewMoreAward` |
| 2. Parse table | Extract bid refs | Extract award numbers |
| 3. Detail URL | `/tenders/viewBidNotice/{id}` | `/Indexes/viewAwardNotice/{id}/MORE` |
| 4. Parse fields | 35+ bid fields | 30+ award fields |
| 5. Save to DB | `save_bid_notice()` | `save_awarded_contract()` |
| 6. Primary key | `reference_number` | `award_notice_number` |

---

## 📈 Future Enhancements

### Potential API Endpoints

```python
# backend_api.py additions:

@app.get("/api/awarded-contracts")
def get_awarded_contracts():
    """List awarded contracts with filtering."""

@app.get("/api/awarded-contracts/{award_id}")
def get_awarded_contract_detail(award_id: str):
    """Get single awarded contract."""

@app.get("/api/awarded-contracts/by-awardee/{awardee}")
def get_by_awardee(awardee: str):
    """Get all contracts won by specific awardee."""

@app.get("/api/awarded-contracts/stats")
def get_award_stats():
    """Get award statistics (savings, totals, etc.)."""

@app.get("/api/competitiveness/{bid_ref}")
def get_competitiveness_analysis(bid_ref: str):
    """
    Link bid to award, show:
    - Original ABC
    - Number of bidders
    - Winning price
    - Savings percentage
    """
```

### Frontend Features

```javascript
// Competitiveness Dashboard
- List of awarded contracts
- Filter by awardee, date range, amount
- Savings analysis charts
- Top winners leaderboard
- ABC vs. Contract Amount comparison graphs
- Bid-to-Award linking (see who won what)
```

---

## ✅ Testing Checklist

- [x] Database schema created
- [x] Parser methods implemented
- [x] Database methods implemented
- [x] Scraper implemented
- [x] Run script created
- [x] Test script created
- [ ] Test parser with reference HTML
- [ ] Test scraper with live website (1-2 pages)
- [ ] Test database operations
- [ ] Verify all critical fields extracted
- [ ] Test savings calculation
- [ ] Test bid-to-award linking

---

## 🐛 Troubleshooting

### Issue: Parser returns None for critical fields

**Solution**: Check HTML structure hasn't changed:
```bash
python test_awarded_parser.py
```

### Issue: Database errors

**Solution**: Recreate tables:
```python
from models.database import Database
db = Database()  # Automatically creates tables
```

### Issue: Scraper finds no awards

**Solution**: Check filters in `.env`:
```env
FILTER_PUBLISH_DATE_FROM=
FILTER_PUBLISH_DATE_TO=
```

---

## 📝 Summary

This prototype successfully extends the PhilGEPS scraper to collect awarded contracts data, providing critical competitive intelligence including:

✅ **Who wins government contracts** (Awardee tracking)
✅ **Approved Budget (ABC)** - What government allocated
✅ **Contract Amount** - What contracts were awarded for ⭐
✅ **Savings analysis** - ABC vs. Awarded Price
✅ **Award dates and contract details**
✅ **Link to original bids** - Track opportunities to outcomes

**Next Steps:**
1. Test the parser: `python test_awarded_parser.py`
2. Run a test scrape: `python run_awarded_scraper.py --workers 1`
3. Query the data using the Database methods
4. Add API endpoints for frontend integration
5. Build dashboard visualizations

**Architecture**: Clean separation following existing patterns, making it easy to maintain and extend alongside the bid opportunities scraper.
