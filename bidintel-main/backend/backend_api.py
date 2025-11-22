"""FastAPI backend server for PhilGEPS Dashboard."""

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, extract
from models.schemas import BidNotice, LineItem, ScrapingLog, AwardedContract, AwardLineItem, AwardDocument
from models.database import Database
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging
import asyncio
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="PhilGEPS Dashboard API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = Database()

# Configuration file path
CONFIG_FILE = Path("data/scraper_config.json")
CONFIG_FILE.parent.mkdir(exist_ok=True)

# Scraper status tracking
scraper_status = {
    "running": False,
    "last_run": None,
    "current_progress": None,
    "error": None
}


# Pydantic models for API requests
class ScraperConfig(BaseModel):
    """Configuration for scraper execution."""
    credentials: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class ScraperRunRequest(BaseModel):
    """Request to run scraper with optional custom parameters."""
    config: Optional[ScraperConfig] = None
    one_time: bool = True  # If True, run once; if False, run on schedule


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "PhilGEPS Dashboard API",
        "version": "2.0.0",
        "endpoints": {
            "bids": [
                "/api/bids",
                "/api/bids/{id}",
                "/api/stats",
                "/api/analytics"
            ],
            "awarded_contracts": [
                "/api/awarded-contracts",
                "/api/awarded-contracts/{award_notice_number}",
                "/api/awarded-contracts/stats/summary",
                "/api/awarded-contracts/analytics/top-winners",
                "/api/awarded-contracts/analytics/by-agency",
                "/api/awarded-contracts/analytics/trends"
            ],
            "scraper": [
                "/api/scraper/config",
                "/api/scraper/status",
                "/api/scraper/run",
                "/api/scraper/stop"
            ],
            "system": [
                "/api/logs",
                "/health"
            ]
        }
    }


@app.get("/api/bids")
def get_bids(
    status: Optional[str] = Query(None, description="Filter by status"),
    classification: Optional[str] = Query(None, description="Filter by classification"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    min_budget: Optional[float] = Query(None, description="Minimum approved budget"),
    max_budget: Optional[float] = Query(None, description="Maximum approved budget"),
    date_from: Optional[str] = Query(None, description="Publish date from (ISO format)"),
    date_to: Optional[str] = Query(None, description="Publish date to (ISO format)"),
    search: Optional[str] = Query(None, description="Search in title, description, reference number"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    List all bids with optional filtering.

    Query Parameters:
    - status: Filter by status (Open, Closed, Evaluation, Published)
    - classification: Filter by classification (Goods, Services, Infrastructure)
    - category: Filter by business category
    - min_budget: Minimum approved budget
    - max_budget: Maximum approved budget
    - date_from: Publish date from (ISO format)
    - date_to: Publish date to (ISO format)
    - search: Search in title, description, reference number
    - limit: Results per page (default: 100)
    - offset: Pagination offset
    """
    session = db.get_session()
    try:
        query = session.query(BidNotice)

        # Apply filters
        if status:
            query = query.filter(BidNotice.status == status)

        if classification:
            query = query.filter(BidNotice.classification == classification)

        if category:
            query = query.filter(BidNotice.category.ilike(f"%{category}%"))

        if min_budget is not None:
            query = query.filter(BidNotice.approved_budget >= min_budget)

        if max_budget is not None:
            query = query.filter(BidNotice.approved_budget <= max_budget)

        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(BidNotice.publish_date >= date_from_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use ISO format.")

        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(BidNotice.publish_date <= date_to_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use ISO format.")

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (BidNotice.title.ilike(search_pattern)) |
                (BidNotice.description.ilike(search_pattern)) |
                (BidNotice.reference_number.ilike(search_pattern))
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination and get results
        bids = query.order_by(BidNotice.publish_date.desc()).offset(offset).limit(limit).all()

        return {
            "data": [bid.to_dict() for bid in bids],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bids: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@app.get("/api/bids/{bid_id}")
def get_bid(bid_id: int):
    """
    Get single bid with full details including line items.

    Path Parameters:
    - bid_id: The ID of the bid notice
    """
    session = db.get_session()
    try:
        bid = session.query(BidNotice).filter(BidNotice.id == bid_id).first()

        if not bid:
            raise HTTPException(status_code=404, detail="Bid not found")

        bid_dict = bid.to_dict()

        # Line items are already included in to_dict(), but ensure they're loaded
        return bid_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bid {bid_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@app.get("/api/stats")
def get_stats():
    """
    Get dashboard statistics.

    Returns:
    - total_bids: Total number of bid notices
    - active_bids: Number of open/active bids
    - total_budget: Sum of all approved budgets
    - total_scraping_sessions: Total number of scraping sessions
    """
    session = db.get_session()
    try:
        total_bids = session.query(BidNotice).count()
        active_bids = session.query(BidNotice).filter(
            BidNotice.status.in_(['Open', 'Active'])
        ).count()

        # Calculate total budget (sum of approved_budget)
        total_budget = session.query(func.sum(BidNotice.approved_budget)).scalar() or 0.0

        # Get scraping sessions count
        total_scraping_sessions = session.query(ScrapingLog).count()

        return {
            "total_bids": total_bids,
            "active_bids": active_bids,
            "total_budget": float(total_budget),
            "total_scraping_sessions": total_scraping_sessions
        }

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@app.get("/api/analytics")
def get_analytics(time_range: str = Query("30d", description="Time range: 7d, 30d, 90d, all")):
    """
    Get analytics data for charts.

    Query Parameters:
    - time_range: "7d", "30d", "90d", "all" (default: "30d")

    Returns:
    - status_counts: Count of bids by status
    - classification_counts: Count of bids by classification
    - budget_by_classification: Sum of budgets by classification
    - top_agencies: Top 10 agencies by bid count
    - monthly_trend: Monthly trend data (count and budget)
    """
    session = db.get_session()
    try:
        # Calculate date filter
        if time_range == "7d":
            cutoff = datetime.now() - timedelta(days=7)
        elif time_range == "30d":
            cutoff = datetime.now() - timedelta(days=30)
        elif time_range == "90d":
            cutoff = datetime.now() - timedelta(days=90)
        else:
            cutoff = datetime.min

        # Status counts
        status_counts = {}
        status_results = session.query(
            BidNotice.status,
            func.count(BidNotice.id)
        ).filter(
            BidNotice.publish_date >= cutoff,
            BidNotice.publish_date.isnot(None)
        ).group_by(BidNotice.status).all()

        for status, count in status_results:
            if status:  # Only include non-null statuses
                status_counts[status] = count

        # Classification counts
        classification_counts = {}
        classification_results = session.query(
            BidNotice.classification,
            func.count(BidNotice.id)
        ).filter(
            BidNotice.publish_date >= cutoff,
            BidNotice.publish_date.isnot(None)
        ).group_by(BidNotice.classification).all()

        for classification, count in classification_results:
            if classification:  # Only include non-null classifications
                classification_counts[classification] = count

        # Budget by classification
        budget_by_classification = {}
        budget_results = session.query(
            BidNotice.classification,
            func.sum(BidNotice.approved_budget)
        ).filter(
            BidNotice.publish_date >= cutoff,
            BidNotice.publish_date.isnot(None)
        ).group_by(BidNotice.classification).all()

        for classification, total in budget_results:
            if classification:  # Only include non-null classifications
                budget_by_classification[classification] = float(total or 0)

        # Top agencies with bid count and total budget
        top_agencies_results = session.query(
            BidNotice.procuring_entity,
            func.count(BidNotice.id),
            func.sum(BidNotice.approved_budget)
        ).filter(
            BidNotice.publish_date >= cutoff,
            BidNotice.publish_date.isnot(None),
            BidNotice.procuring_entity.isnot(None)
        ).group_by(
            BidNotice.procuring_entity
        ).order_by(
            func.count(BidNotice.id).desc()
        ).limit(10).all()

        top_agencies = [
            {
                "name": agency,
                "count": count,
                "total_budget": float(total_budget or 0)
            }
            for agency, count, total_budget in top_agencies_results
        ]

        # Monthly trend (last 12 months)
        # Use database-agnostic date formatting
        if 'postgresql' in db.engine.url.drivername:
            # PostgreSQL: use to_char
            month_expr = func.to_char(BidNotice.publish_date, 'YYYY-MM').label('month')
        else:
            # SQLite and others: use strftime
            month_expr = func.strftime('%Y-%m', BidNotice.publish_date).label('month')

        monthly_trend_data = session.query(
            month_expr,
            func.count(BidNotice.id).label('count'),
            func.sum(BidNotice.approved_budget).label('budget')
        ).filter(
            BidNotice.publish_date >= cutoff,
            BidNotice.publish_date.isnot(None)
        ).group_by('month').order_by('month').all()

        monthly_trend = []
        for month, count, budget in monthly_trend_data:
            monthly_trend.append([
                month,
                {
                    "count": count,
                    "budget": float(budget or 0)
                }
            ])

        # Combine classification data for frontend compatibility
        by_classification = {}
        all_classifications = set(classification_counts.keys()) | set(budget_by_classification.keys())
        for classification in all_classifications:
            by_classification[classification] = {
                "count": classification_counts.get(classification, 0),
                "total_budget": budget_by_classification.get(classification, 0.0)
            }

        return {
            "status_counts": status_counts,
            "classification_counts": classification_counts,
            "budget_by_classification": budget_by_classification,
            "by_classification": by_classification,  # New: Combined structure for frontend
            "top_agencies": top_agencies,
            "monthly_trend": monthly_trend
        }

    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@app.get("/api/logs")
def get_scraping_logs(
    limit: int = Query(50, ge=1, le=500, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get scraping logs with pagination.

    Query Parameters:
    - limit: Results per page (default: 50)
    - offset: Pagination offset

    Returns:
    - data: List of scraping log entries
    - total: Total number of logs
    """
    session = db.get_session()
    try:
        query = session.query(ScrapingLog)

        # Get total count
        total = query.count()

        # Get logs ordered by most recent first
        logs = query.order_by(ScrapingLog.start_time.desc()).offset(offset).limit(limit).all()

        return {
            "data": [log.to_dict() for log in logs],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error fetching scraping logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        session.close()


@app.get("/api/scraper/config")
def get_scraper_config():
    """
    Get current scraper configuration.

    Returns:
    - Configuration loaded from file or defaults
    """
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        else:
            # Return defaults (without sensitive data)
            return {
                "credentials": {
                    "username": "",
                    "password": ""
                },
                "filters": {
                    "dateRange": {"from": "", "to": ""},
                    "classification": "",
                    "businessCategory": ""
                },
                "settings": {
                    "headless": True,
                    "interval": 60,
                    "delay": 2,
                    "maxRetries": 3
                }
            }
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading configuration: {str(e)}")


@app.post("/api/scraper/config")
def save_scraper_config(config: Dict[str, Any]):
    """
    Save scraper configuration.

    Body:
    - config: Configuration object with credentials, filters, and settings

    Returns:
    - Success message
    """
    try:
        # Save to file
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info("Scraper configuration saved successfully")
        return {
            "success": True,
            "message": "Configuration saved successfully",
            "config": config
        }
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")


@app.get("/api/scraper/status")
def get_scraper_status():
    """
    Get current scraper status.

    Returns:
    - running: Whether scraper is currently running
    - last_run: Timestamp of last scraper run
    - current_progress: Current progress if running
    - error: Last error if any
    """
    return scraper_status


def _sanitize_config(config: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize and validate configuration.

    - Convert empty strings to None
    - Validate data types
    - Remove invalid values
    """
    if not config:
        return None

    sanitized = {}

    # Sanitize credentials
    if "credentials" in config:
        creds = config["credentials"]
        sanitized["credentials"] = {
            "username": creds.get("username") or None,
            "password": creds.get("password") or None
        }
        # Remove if both are None
        if not sanitized["credentials"]["username"] and not sanitized["credentials"]["password"]:
            sanitized.pop("credentials", None)

    # Sanitize filters
    if "filters" in config:
        filters = config["filters"]
        date_range = filters.get("dateRange", {})
        sanitized["filters"] = {
            "dateRange": {
                "from": date_range.get("from") or None,
                "to": date_range.get("to") or None
            },
            "classification": filters.get("classification") or None,
            "businessCategory": filters.get("businessCategory") or None
        }

    # Sanitize settings
    if "settings" in config:
        scraper_settings = config["settings"]
        sanitized["settings"] = {}

        if "headless" in scraper_settings:
            sanitized["settings"]["headless"] = bool(scraper_settings["headless"])
        if "interval" in scraper_settings:
            try:
                sanitized["settings"]["interval"] = int(scraper_settings["interval"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid interval value: {scraper_settings['interval']}")
        if "delay" in scraper_settings:
            try:
                sanitized["settings"]["delay"] = int(scraper_settings["delay"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid delay value: {scraper_settings['delay']}")
        if "maxRetries" in scraper_settings:
            try:
                sanitized["settings"]["maxRetries"] = int(scraper_settings["maxRetries"])
            except (ValueError, TypeError):
                logger.warning(f"Invalid maxRetries value: {scraper_settings['maxRetries']}")

    return sanitized if sanitized else None


async def _run_scraper_async(config: Optional[Dict[str, Any]] = None) -> Dict:
    """
    Async scraper execution using PublicPhilGEPSScraper (no authentication required).
    This function runs the public scraper which doesn't need credentials.
    """
    import os

    # Import public scraper here to avoid circular imports
    from scraper.public_scraper import PublicPhilGEPSScraper
    from config.settings import settings

    # Store original values for restoration
    original_values = {}

    try:
        # Get number of workers from config (default: 2)
        num_workers = 2

        # Apply custom configuration if provided
        if config:
            logger.info(f"Applying runtime configuration: {json.dumps(config, indent=2)}")

            if "filters" in config:
                filters = config["filters"]
                date_range = filters.get("dateRange", {})
                if "from" in date_range:
                    original_values["FILTER_PUBLISH_DATE_FROM"] = settings.FILTER_PUBLISH_DATE_FROM
                    settings.FILTER_PUBLISH_DATE_FROM = date_range["from"]
                    logger.debug(f"Override date from: {date_range['from'] or '(empty)'}")
                if "to" in date_range:
                    original_values["FILTER_PUBLISH_DATE_TO"] = settings.FILTER_PUBLISH_DATE_TO
                    settings.FILTER_PUBLISH_DATE_TO = date_range["to"]
                    logger.debug(f"Override date to: {date_range['to'] or '(empty)'}")
                if "classification" in filters:
                    original_values["FILTER_CLASSIFICATION"] = settings.FILTER_CLASSIFICATION
                    settings.FILTER_CLASSIFICATION = filters["classification"]
                    logger.debug(f"Override classification: {filters['classification'] or '(empty)'}")
                if "businessCategory" in filters:
                    original_values["FILTER_BUSINESS_CATEGORY"] = settings.FILTER_BUSINESS_CATEGORY
                    settings.FILTER_BUSINESS_CATEGORY = filters["businessCategory"]
                    logger.debug(f"Override business category: {filters['businessCategory'] or '(empty)'}")

            if "settings" in config:
                scraper_settings = config["settings"]
                if "headless" in scraper_settings:
                    original_values["HEADLESS_MODE"] = settings.HEADLESS_MODE
                    settings.HEADLESS_MODE = scraper_settings["headless"]
                    logger.debug(f"Override headless: {scraper_settings['headless']}")
                if "interval" in scraper_settings:
                    original_values["SCRAPE_INTERVAL_MINUTES"] = settings.SCRAPE_INTERVAL_MINUTES
                    settings.SCRAPE_INTERVAL_MINUTES = scraper_settings["interval"]
                if "delay" in scraper_settings:
                    original_values["REQUEST_DELAY_SECONDS"] = settings.REQUEST_DELAY_SECONDS
                    settings.REQUEST_DELAY_SECONDS = scraper_settings["delay"]
                    logger.debug(f"Override delay: {scraper_settings['delay']}")
                if "maxRetries" in scraper_settings:
                    original_values["MAX_RETRIES"] = settings.MAX_RETRIES
                    settings.MAX_RETRIES = scraper_settings["maxRetries"]
                    logger.debug(f"Override max retries: {scraper_settings['maxRetries']}")
                if "workers" in scraper_settings:
                    num_workers = int(scraper_settings.get("workers", 2))
                    logger.debug(f"Using {num_workers} workers")

        # Run public scraper (no authentication required)
        logger.info(f"Executing PUBLIC scraper with {num_workers} workers...")
        scraper = PublicPhilGEPSScraper(num_workers=num_workers)
        results = await scraper.run()
        logger.info(f"Public scraper execution completed: {results}")
        return results

    finally:
        # Restore original settings
        if original_values:
            logger.debug("Restoring original settings...")
            for key, value in original_values.items():
                setattr(settings, key, value)


async def run_scraper_background(config: Optional[Dict[str, Any]] = None):
    """
    Run public scraper in background with optional custom configuration.

    This function runs the async public scraper (no authentication required).

    Args:
        config: Optional configuration to override defaults
    """
    global scraper_status

    try:
        scraper_status["running"] = True
        scraper_status["error"] = None
        scraper_status["current_progress"] = "Initializing public scraper..."

        logger.info("Starting PUBLIC scraper in background (no authentication)...")

        # Sanitize configuration
        sanitized_config = _sanitize_config(config)
        if sanitized_config:
            logger.info("Using custom configuration for this run")
        else:
            logger.info("Using default configuration from .env")

        # Run public scraper (async, no thread pool needed)
        scraper_status["current_progress"] = "Running public scraper..."
        results = await _run_scraper_async(sanitized_config)

        scraper_status["last_run"] = datetime.now().isoformat()
        scraper_status["current_progress"] = f"Completed: {results['new_records']} new, {results.get('skipped', 0)} skipped"

        logger.info(f"Public scraper background task completed successfully")

    except Exception as e:
        logger.error(f"Public scraper background task failed: {str(e)}", exc_info=True)
        scraper_status["error"] = str(e)
        scraper_status["current_progress"] = "Failed"
    finally:
        scraper_status["running"] = False


@app.post("/api/scraper/run")
async def run_scraper(request: ScraperRunRequest, background_tasks: BackgroundTasks):
    """
    Trigger scraper to run with optional custom configuration.

    Body:
    - config: Optional configuration to override defaults
    - one_time: If True, run once; if False, run on schedule

    Returns:
    - Success message with task ID
    """
    if scraper_status["running"]:
        raise HTTPException(status_code=409, detail="Scraper is already running")

    try:
        config_dict = None
        if request.config:
            config_dict = request.config.dict(exclude_none=True)

        # Add scraper task to background
        background_tasks.add_task(run_scraper_background, config_dict)

        return {
            "success": True,
            "message": "Scraper started in background",
            "one_time": request.one_time
        }
    except Exception as e:
        logger.error(f"Error starting scraper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting scraper: {str(e)}")


@app.post("/api/scraper/stop")
def stop_scraper():
    """
    Stop the currently running scraper.

    Returns:
    - Success message

    Note: This is a graceful stop request. The scraper may take time to stop.
    """
    if not scraper_status["running"]:
        raise HTTPException(status_code=400, detail="Scraper is not running")

    # In a real implementation, you'd need to handle process termination
    # For now, we just set the flag
    scraper_status["running"] = False
    scraper_status["current_progress"] = "Stopping..."

    return {
        "success": True,
        "message": "Scraper stop requested"
    }


# ============================================================================
# AWARDED CONTRACTS API ENDPOINTS
# ============================================================================

@app.get("/api/awarded-contracts")
def get_awarded_contracts(
    procuring_entity: Optional[str] = Query(None, description="Filter by procuring entity/agency"),
    awardee: Optional[str] = Query(None, description="Filter by awardee/winner name"),
    classification: Optional[str] = Query(None, description="Filter by classification (Goods, Services, Infrastructure)"),
    category: Optional[str] = Query(None, description="Filter by business category"),
    min_budget: Optional[float] = Query(None, description="Minimum approved budget (ABC)"),
    max_budget: Optional[float] = Query(None, description="Maximum approved budget (ABC)"),
    min_contract_amount: Optional[float] = Query(None, description="Minimum contract amount"),
    max_contract_amount: Optional[float] = Query(None, description="Maximum contract amount"),
    date_from: Optional[str] = Query(None, description="Award date from (ISO format)"),
    date_to: Optional[str] = Query(None, description="Award date to (ISO format)"),
    search: Optional[str] = Query(None, description="Search in title, awardee, agency"),
    limit: int = Query(100, ge=1, le=1000, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    List all awarded contracts with optional filtering.

    Returns paginated list of awarded contracts with comprehensive filtering options.
    """
    try:
        # Build filters
        filters = {}
        if procuring_entity:
            filters['procuring_entity'] = procuring_entity
        if awardee:
            filters['awardee_name'] = awardee
        if classification:
            filters['classification'] = classification
        if category:
            filters['category'] = category
        if date_from:
            filters['date_from'] = datetime.fromisoformat(date_from)
        if date_to:
            filters['date_to'] = datetime.fromisoformat(date_to)
        if min_budget:
            filters['min_budget'] = min_budget
        if max_budget:
            filters['max_budget'] = max_budget
        if min_contract_amount:
            filters['min_contract_amount'] = min_contract_amount
        if max_contract_amount:
            filters['max_contract_amount'] = max_contract_amount
        if search:
            filters['search_term'] = search

        # Get contracts
        contracts = db.get_filtered_awarded_contracts(**filters)

        # Apply pagination
        total = len(contracts)
        contracts_page = contracts[offset:offset + limit]

        # Convert to dict for JSON response
        results = []
        for contract in contracts_page:
            contract_dict = contract.to_dict()
            # Add calculated savings
            if contract.approved_budget and contract.contract_amount:
                savings = contract.approved_budget - contract.contract_amount
                savings_pct = (savings / contract.approved_budget) * 100
                contract_dict['savings'] = savings
                contract_dict['savings_percentage'] = savings_pct
            results.append(contract_dict)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": results
        }

    except Exception as e:
        logger.error(f"Error getting awarded contracts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/awarded-contracts/{award_notice_number}")
def get_awarded_contract(award_notice_number: str):
    """
    Get a single awarded contract by award notice number.

    Returns complete details including line items and documents.
    """
    try:
        contract = db.get_awarded_contract_by_number(award_notice_number)
        if not contract:
            raise HTTPException(status_code=404, detail=f"Awarded contract {award_notice_number} not found")

        # Convert to dict
        result = contract.to_dict()

        # Add savings calculation
        if contract.approved_budget and contract.contract_amount:
            savings = contract.approved_budget - contract.contract_amount
            savings_pct = (savings / contract.approved_budget) * 100
            result['savings'] = savings
            result['savings_percentage'] = savings_pct

        # Add line items
        result['line_items'] = [item.to_dict() for item in contract.line_items]

        # Add documents
        result['documents'] = [doc.to_dict() for doc in contract.documents]

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting awarded contract: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/awarded-contracts/stats/summary")
def get_awarded_contracts_stats():
    """
    Get awarded contracts statistics.

    Returns:
    - Total number of contracts
    - Total ABC and contract amounts
    - Total savings
    - Average savings percentage
    - Unique awardees and agencies
    """
    try:
        stats = db.get_award_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting awarded contracts stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/awarded-contracts/analytics/top-winners")
def get_top_winners(limit: int = Query(10, ge=1, le=100, description="Number of top winners")):
    """
    Get top winning companies/awardees.

    Returns list of companies with most contracts won and total amounts.
    """
    try:
        session = db.get_session()

        # Query top winners by count and total amount
        results = session.query(
            AwardedContract.awardee_name,
            func.count(AwardedContract.id).label('contract_count'),
            func.sum(AwardedContract.contract_amount).label('total_amount'),
            func.sum(AwardedContract.approved_budget).label('total_abc'),
            func.avg(AwardedContract.contract_amount).label('avg_amount')
        ).filter(
            AwardedContract.awardee_name.isnot(None)
        ).group_by(
            AwardedContract.awardee_name
        ).order_by(
            func.count(AwardedContract.id).desc()
        ).limit(limit).all()

        session.close()

        winners = []
        for row in results:
            total_savings = (row.total_abc or 0) - (row.total_amount or 0)
            savings_pct = (total_savings / row.total_abc * 100) if row.total_abc else 0

            winners.append({
                'awardee_name': row.awardee_name,
                'contract_count': row.contract_count,
                'total_amount': float(row.total_amount) if row.total_amount else 0,
                'total_abc': float(row.total_abc) if row.total_abc else 0,
                'total_savings': float(total_savings),
                'avg_savings_percentage': float(savings_pct),
                'avg_contract_amount': float(row.avg_amount) if row.avg_amount else 0
            })

        return {"top_winners": winners}

    except Exception as e:
        logger.error(f"Error getting top winners: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/awarded-contracts/analytics/by-agency")
def get_contracts_by_agency(limit: int = Query(10, ge=1, le=100)):
    """
    Get awarded contracts grouped by procuring entity/agency.

    Returns agencies with most contracts and spending.
    """
    try:
        session = db.get_session()

        results = session.query(
            AwardedContract.procuring_entity,
            func.count(AwardedContract.id).label('contract_count'),
            func.sum(AwardedContract.contract_amount).label('total_amount'),
            func.sum(AwardedContract.approved_budget).label('total_abc'),
            func.avg(AwardedContract.contract_amount).label('avg_amount')
        ).filter(
            AwardedContract.procuring_entity.isnot(None)
        ).group_by(
            AwardedContract.procuring_entity
        ).order_by(
            func.sum(AwardedContract.contract_amount).desc()
        ).limit(limit).all()

        session.close()

        agencies = []
        for row in results:
            total_savings = (row.total_abc or 0) - (row.total_amount or 0)

            agencies.append({
                'procuring_entity': row.procuring_entity,
                'contract_count': row.contract_count,
                'total_amount': float(row.total_amount) if row.total_amount else 0,
                'total_abc': float(row.total_abc) if row.total_abc else 0,
                'total_savings': float(total_savings),
                'avg_contract_amount': float(row.avg_amount) if row.avg_amount else 0
            })

        return {"agencies": agencies}

    except Exception as e:
        logger.error(f"Error getting contracts by agency: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/awarded-contracts/analytics/trends")
def get_contract_trends(
    period: str = Query("month", description="Period: day, week, month, year"),
    limit: int = Query(12, ge=1, le=100)
):
    """
    Get contract award trends over time.

    Returns time series data of contracts and amounts.
    """
    try:
        session = db.get_session()

        # Determine grouping based on period
        if period == "day":
            time_group = func.date(AwardedContract.award_date)
        elif period == "week":
            time_group = func.strftime('%Y-W%W', AwardedContract.award_date)
        elif period == "year":
            time_group = extract('year', AwardedContract.award_date)
        else:  # month (default)
            time_group = func.strftime('%Y-%m', AwardedContract.award_date)

        results = session.query(
            time_group.label('period'),
            func.count(AwardedContract.id).label('contract_count'),
            func.sum(AwardedContract.contract_amount).label('total_amount'),
            func.avg(AwardedContract.contract_amount).label('avg_amount')
        ).filter(
            AwardedContract.award_date.isnot(None)
        ).group_by(
            time_group
        ).order_by(
            time_group.desc()
        ).limit(limit).all()

        session.close()

        trends = []
        for row in results:
            trends.append({
                'period': str(row.period),
                'contract_count': row.contract_count,
                'total_amount': float(row.total_amount) if row.total_amount else 0,
                'avg_contract_amount': float(row.avg_amount) if row.avg_amount else 0
            })

        return {"trends": list(reversed(trends))}  # Reverse for chronological order

    except Exception as e:
        logger.error(f"Error getting contract trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    # Note: For development with auto-reload, run: uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
