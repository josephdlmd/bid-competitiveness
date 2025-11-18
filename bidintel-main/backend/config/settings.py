"""Configuration settings for the PhilGEPS scraper."""

import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # PhilGEPS Credentials
    PHILGEPS_USERNAME = os.getenv("PHILGEPS_USERNAME")
    PHILGEPS_PASSWORD = os.getenv("PHILGEPS_PASSWORD")

    # PhilGEPS URLs - Complete navigation workflow from BID_WORKFLOW.md
    PHILGEPS_BASE_URL = "https://philgeps.gov.ph"

    # Step 1: Login (2 URLs)
    PHILGEPS_LOGIN_PAGE = "https://philgeps.gov.ph/Indexes/login"  # Login form page
    PHILGEPS_LOGIN_URL = "https://philgeps.gov.ph/users/login"  # Form submission endpoint

    # Step 2: Bulletin Board
    PHILGEPS_BULLETIN_BOARD = "https://philgeps.gov.ph/access/bulletin_board_dashboard"

    # Step 3: Bid Opportunities List
    PHILGEPS_BID_LIST = "https://philgeps.gov.ph/BulletinBoard/view_more_current_oppourtunities"

    # Step 4: Bid Detail (template - requires bid_id)
    PHILGEPS_BID_DETAIL = "https://philgeps.gov.ph/tenders/viewBidNotice/{bid_id}"

    # Document Viewer
    PHILGEPS_DOC_VIEWER = "https://philgeps.gov.ph/Tenders/tender_doc_view/{bid_id}/{bid_id}"

    # Document Downloads (from PDF_DOCUMENT_STRUCTURE.md)
    PHILGEPS_PDF_BASE = "https://philgeps.gov.ph/portal_documents/bid_notice_documents"
    PHILGEPS_PDF_PATTERN = "{base}/bid_notice_{bid_id}/bid_notice_document/{timestamp}_{filename}.pdf"
    PHILGEPS_ZIP_PATTERN = "{base}/bid_notice_{bid_id}/tender_doc.zip"

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///philgeps_data.db")

    # Scraper Settings
    SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL_MINUTES", "60"))
    SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", "3"))  # Hour to run daily (0-23), default 3 AM
    SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", "0"))  # Minute to run daily (0-59), default 00
    SCHEDULE_TIMEZONE = os.getenv("SCHEDULE_TIMEZONE", "Asia/Manila")  # Philippine time
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_DELAY_SECONDS = int(os.getenv("REQUEST_DELAY_SECONDS", "2"))

    # Date Filtering (format: DD-MMM-YYYY, e.g., "13-Nov-2025")
    # Special values: "TODAY", "YESTERDAY", "AUTO" (yesterday to today)
    # Leave empty to scrape all bids without date filtering
    _FILTER_PUBLISH_DATE_FROM_RAW = os.getenv("FILTER_PUBLISH_DATE_FROM", "")
    _FILTER_PUBLISH_DATE_TO_RAW = os.getenv("FILTER_PUBLISH_DATE_TO", "")

    @staticmethod
    def _calculate_date(date_value: str, offset_days: int = 0) -> str:
        """
        Calculate date based on special keywords or return as-is.

        Args:
            date_value: Date string (can be "TODAY", "YESTERDAY", "AUTO", or "DD-MMM-YYYY")
            offset_days: Days to offset from today (negative for past, positive for future)

        Returns:
            str: Date in DD-MMM-YYYY format or empty string
        """
        if not date_value:
            return ""

        date_value_upper = date_value.upper().strip()

        if date_value_upper == "TODAY":
            target_date = datetime.now()
        elif date_value_upper == "YESTERDAY":
            target_date = datetime.now() - timedelta(days=1)
        elif date_value_upper == "AUTO":
            # AUTO uses offset_days: -1 for FROM (yesterday), 0 for TO (today)
            target_date = datetime.now() + timedelta(days=offset_days)
        else:
            # Return as-is if it's a specific date
            return date_value

        # Format as DD-MMM-YYYY (e.g., "14-Nov-2025")
        return target_date.strftime("%d-%b-%Y")

    # Calculate actual date values (evaluated at class definition time)
    FILTER_PUBLISH_DATE_FROM = _calculate_date.__func__(_FILTER_PUBLISH_DATE_FROM_RAW, offset_days=-1)
    FILTER_PUBLISH_DATE_TO = _calculate_date.__func__(_FILTER_PUBLISH_DATE_TO_RAW, offset_days=0)

    # Classification Filtering
    # Options: 1=Civil Works - Infra Project, 2=Goods, 3=Goods - General Support Services, 4=Consulting Services
    # Leave empty to scrape all classifications
    FILTER_CLASSIFICATION = os.getenv("FILTER_CLASSIFICATION", "")  # e.g., "1" or "2"

    # Business Category Filtering
    # Options: 60-524 (see PhilGEPS website for full list)
    # Leave empty to scrape all business categories
    FILTER_BUSINESS_CATEGORY = os.getenv("FILTER_BUSINESS_CATEGORY", "")  # e.g., "100" or "300"

    # Browser Settings
    HEADLESS_MODE = os.getenv("HEADLESS_MODE", "true").lower() == "true"
    BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
    BROWSER_TIMEOUT = 30000  # milliseconds

    # Persistent Browser Profile (RECOMMENDED for easier reCAPTCHA)
    USE_PERSISTENT_PROFILE = os.getenv("USE_PERSISTENT_PROFILE", "true").lower() == "true"
    USER_DATA_DIR = os.getenv("USER_DATA_DIR", str(Path(__file__).resolve().parent.parent / "browser_profile"))

    # reCAPTCHA Settings
    RECAPTCHA_SOLVE_METHOD = os.getenv("RECAPTCHA_SOLVE_METHOD", "manual")  # manual, 2captcha, auto
    TWOCAPTCHA_API_KEY = os.getenv("TWOCAPTCHA_API_KEY")  # Required if using 2captcha
    RECAPTCHA_TIMEOUT = int(os.getenv("RECAPTCHA_TIMEOUT", "120"))  # seconds to wait for manual solving

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/scraper.log")

    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    PROFILE_DIR = Path(USER_DATA_DIR) if USER_DATA_DIR else None

    # Notifications (optional)
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

    @classmethod
    def get_bid_detail_url(cls, bid_id: str) -> str:
        """
        Get URL for specific bid notice detail page.

        Args:
            bid_id: Bid notice reference number (e.g., "7297")

        Returns:
            str: Complete URL to bid notice page
        """
        return cls.PHILGEPS_BID_DETAIL.format(bid_id=bid_id)

    @classmethod
    def get_document_viewer_url(cls, bid_id: str) -> str:
        """
        Get URL for bid document viewer page.

        Args:
            bid_id: Bid notice reference number

        Returns:
            str: Complete URL to document viewer
        """
        return cls.PHILGEPS_DOC_VIEWER.format(bid_id=bid_id)

    @classmethod
    def get_zip_download_url(cls, bid_id: str) -> str:
        """
        Get URL for downloading ZIP bundle of all bid documents.

        Args:
            bid_id: Bid notice reference number

        Returns:
            str: Complete URL to download tender_doc.zip
        """
        return cls.PHILGEPS_ZIP_PATTERN.format(base=cls.PHILGEPS_PDF_BASE, bid_id=bid_id)

    @classmethod
    def get_pdf_download_url(cls, bid_id: str, timestamp: str, filename: str) -> str:
        """
        Get URL for downloading specific PDF document.

        Args:
            bid_id: Bid notice reference number
            timestamp: Document timestamp
            filename: PDF filename

        Returns:
            str: Complete URL to download PDF
        """
        return cls.PHILGEPS_PDF_PATTERN.format(
            base=cls.PHILGEPS_PDF_BASE,
            bid_id=bid_id,
            timestamp=timestamp,
            filename=filename
        )

    @classmethod
    def validate(cls):
        """Validate required settings."""
        if not cls.PHILGEPS_USERNAME or not cls.PHILGEPS_PASSWORD:
            raise ValueError(
                "PHILGEPS_USERNAME and PHILGEPS_PASSWORD must be set in .env file"
            )

        # Create required directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

        # Create browser profile directory if using persistent profile
        if cls.USE_PERSISTENT_PROFILE and cls.PROFILE_DIR:
            cls.PROFILE_DIR.mkdir(exist_ok=True)

        return True


# Create settings instance
settings = Settings()
