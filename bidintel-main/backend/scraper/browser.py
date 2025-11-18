"""Browser automation handler using Playwright."""

from playwright.sync_api import sync_playwright, Browser, Page, Playwright, BrowserContext
from config.settings import settings
from utils.logger import logger
from typing import Optional


class BrowserHandler:
    """Manages browser automation with Playwright."""

    def __init__(self):
        """Initialize browser handler."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def init_browser(self, headless: bool = None) -> Page:
        """
        Initialize browser and return a page instance.

        Uses persistent browser profile if configured, which helps with:
        - Easier reCAPTCHA solving (just checkbox after first login)
        - Session persistence across runs
        - Browser fingerprint consistency

        Args:
            headless: Run browser in headless mode (defaults to settings)

        Returns:
            Page: Playwright Page instance
        """
        if headless is None:
            headless = settings.HEADLESS_MODE

        try:
            logger.info(f"Initializing {settings.BROWSER_TYPE} browser (headless={headless})...")

            self.playwright = sync_playwright().start()

            # Use persistent context if user data directory is configured
            if settings.USE_PERSISTENT_PROFILE and settings.USER_DATA_DIR:
                logger.info(f"Using persistent profile: {settings.USER_DATA_DIR}")
                return self._init_persistent_browser(headless)
            else:
                logger.info("Using temporary browser profile")
                return self._init_temporary_browser(headless)

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    def _init_persistent_browser(self, headless: bool) -> Page:
        """
        Initialize browser with persistent user data directory.

        This maintains cookies, history, and other data between sessions,
        making reCAPTCHA much easier to solve.

        Args:
            headless: Run browser in headless mode

        Returns:
            Page: Playwright Page instance
        """
        # Get browser type
        if settings.BROWSER_TYPE == "chromium":
            browser_type = self.playwright.chromium
        elif settings.BROWSER_TYPE == "firefox":
            browser_type = self.playwright.firefox
        elif settings.BROWSER_TYPE == "webkit":
            browser_type = self.playwright.webkit
        else:
            raise ValueError(f"Unsupported browser type: {settings.BROWSER_TYPE}")

        # Launch persistent context
        self.context = browser_type.launch_persistent_context(
            user_data_dir=settings.USER_DATA_DIR,
            headless=headless,
            ignore_https_errors=True,  # Ignore SSL certificate errors
            args=[
                '--disable-blink-features=AutomationControlled',  # Avoid detection
            ]
        )

        # Get or create first page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        # Set default timeout
        self.page.set_default_timeout(settings.BROWSER_TIMEOUT)

        logger.info("Browser initialized successfully with persistent profile")
        return self.page

    def _init_temporary_browser(self, headless: bool) -> Page:
        """
        Initialize browser with temporary profile (no persistence).

        Args:
            headless: Run browser in headless mode

        Returns:
            Page: Playwright Page instance
        """
        # Launch browser based on type
        if settings.BROWSER_TYPE == "chromium":
            self.browser = self.playwright.chromium.launch(headless=headless)
        elif settings.BROWSER_TYPE == "firefox":
            self.browser = self.playwright.firefox.launch(headless=headless)
        elif settings.BROWSER_TYPE == "webkit":
            self.browser = self.playwright.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser type: {settings.BROWSER_TYPE}")

        # Create new context with SSL error ignoring
        self.context = self.browser.new_context(ignore_https_errors=True)
        # Create new page
        self.page = self.context.new_page()

        # Set default timeout
        self.page.set_default_timeout(settings.BROWSER_TIMEOUT)

        logger.info("Browser initialized successfully with temporary profile")
        return self.page

    def navigate(self, url: str, wait_until: str = "networkidle") -> Page:
        """
        Navigate to a URL.

        Args:
            url: Target URL
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')

        Returns:
            Page: Current page instance
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Call init_browser() first.")

        try:
            logger.info(f"Navigating to: {url}")
            self.page.goto(url, wait_until=wait_until, timeout=settings.BROWSER_TIMEOUT)
            return self.page

        except Exception as e:
            logger.error(f"Navigation error: {str(e)}")
            raise

    def wait_for_element(self, selector: str, timeout: int = None) -> None:
        """
        Wait for element to be visible.

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not initialized.")

        timeout = timeout or settings.BROWSER_TIMEOUT
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)

    def screenshot(self, path: str, full_page: bool = False) -> None:
        """
        Take a screenshot.

        Args:
            path: File path to save screenshot
            full_page: Capture full scrollable page
        """
        if not self.page:
            raise RuntimeError("Browser not initialized.")

        self.page.screenshot(path=path, full_page=full_page)
        logger.info(f"Screenshot saved to: {path}")

    def get_html(self) -> str:
        """
        Get current page HTML content.

        Returns:
            str: HTML content
        """
        if not self.page:
            raise RuntimeError("Browser not initialized.")

        return self.page.content()

    def close(self) -> None:
        """Close browser and cleanup resources."""
        try:
            if self.page:
                self.page.close()
                logger.debug("Page closed")

            # Close context if using persistent profile
            if self.context:
                self.context.close()
                logger.debug("Browser context closed")

            if self.browser:
                self.browser.close()
                logger.debug("Browser closed")

            if self.playwright:
                self.playwright.stop()
                logger.debug("Playwright stopped")

            logger.info("Browser cleanup completed")

        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        self.init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
