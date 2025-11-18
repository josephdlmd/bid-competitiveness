"""
Custom stealth techniques for Playwright to avoid bot detection.

This module provides anti-detection measures that work with both
persistent and non-persistent browser contexts.

Since playwright-stealth doesn't work with launch_persistent_context,
we implement custom techniques:
- Navigator property masking (webdriver, platform, etc.)
- User agent rotation
- WebGL/Canvas fingerprinting protection
- Viewport randomization
- Language/timezone spoofing
- Chrome runtime evasion
"""

import random
from typing import Dict, List, Optional, Tuple
from playwright.async_api import Page, BrowserContext


class StealthConfig:
    """Configuration for stealth techniques."""

    # Realistic user agents (Chrome on Windows/Mac/Linux)
    USER_AGENTS = [
        # Chrome on Windows 10/11
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",

        # Chrome on macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",

        # Chrome on Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    ]

    # Realistic viewport sizes (common desktop resolutions)
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 720},
    ]

    # Browser languages (prioritize English for Philippines)
    LANGUAGES = [
        ["en-US", "en"],
        ["en-GB", "en"],
        ["en-PH", "en", "tl"],
    ]

    @classmethod
    def get_random_user_agent(cls) -> str:
        """Get a random realistic user agent."""
        return random.choice(cls.USER_AGENTS)

    @classmethod
    def get_random_viewport(cls) -> Dict[str, int]:
        """Get a random viewport size."""
        return random.choice(cls.VIEWPORTS).copy()

    @classmethod
    def get_random_languages(cls) -> List[str]:
        """Get random language preferences."""
        return random.choice(cls.LANGUAGES).copy()


class PlaywrightStealth:
    """
    Custom stealth implementation for Playwright.

    Works with both persistent and non-persistent contexts.
    Implements JavaScript injections to mask automation markers.
    """

    # JavaScript to override navigator.webdriver
    WEBDRIVER_OVERRIDE = """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """

    # JavaScript to override Chrome runtime
    CHROME_RUNTIME_OVERRIDE = """
    window.chrome = {
        runtime: {},
        loadTimes: function() {},
        csi: function() {},
        app: {}
    };
    """

    # JavaScript to override permissions
    PERMISSIONS_OVERRIDE = """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    """

    # JavaScript to override plugins
    PLUGINS_OVERRIDE = """
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                description: "",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            }
        ]
    });
    """

    # JavaScript to override languages
    LANGUAGES_OVERRIDE_TEMPLATE = """
    Object.defineProperty(navigator, 'languages', {{
        get: () => {languages}
    }});
    """

    # JavaScript to fix WebGL vendor
    WEBGL_VENDOR_OVERRIDE = """
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter.call(this, parameter);
    };
    """

    # JavaScript to add realistic screen properties
    SCREEN_OVERRIDE = """
    Object.defineProperty(screen, 'availTop', { get: () => 0 });
    Object.defineProperty(screen, 'availLeft', { get: () => 0 });
    """

    def __init__(
        self,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        languages: Optional[List[str]] = None,
    ):
        """
        Initialize stealth configuration.

        Args:
            user_agent: Custom user agent (random if None)
            viewport: Custom viewport size (random if None)
            languages: Custom language preferences (random if None)
        """
        self.user_agent = user_agent or StealthConfig.get_random_user_agent()
        self.viewport = viewport or StealthConfig.get_random_viewport()
        self.languages = languages or StealthConfig.get_random_languages()

    async def apply_stealth(self, page: Page):
        """
        Apply stealth techniques to a Playwright page.

        This injects JavaScript to mask automation markers.

        Args:
            page: Playwright Page instance
        """
        # Inject all stealth scripts
        await page.add_init_script(self.WEBDRIVER_OVERRIDE)
        await page.add_init_script(self.CHROME_RUNTIME_OVERRIDE)
        await page.add_init_script(self.PERMISSIONS_OVERRIDE)
        await page.add_init_script(self.PLUGINS_OVERRIDE)
        await page.add_init_script(self.WEBGL_VENDOR_OVERRIDE)
        await page.add_init_script(self.SCREEN_OVERRIDE)

        # Inject language override
        languages_js = self.LANGUAGES_OVERRIDE_TEMPLATE.format(
            languages=str(self.languages)
        )
        await page.add_init_script(languages_js)

    def get_launch_args(self) -> List[str]:
        """
        Get browser launch arguments for stealth.

        Returns:
            List of Chrome/Chromium arguments
        """
        return [
            # Disable automation flags
            '--disable-blink-features=AutomationControlled',

            # Disable dev-shm usage (helps with Docker/Linux)
            '--disable-dev-shm-usage',

            # Additional stealth args
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--allow-running-insecure-content',

            # Performance and stability
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-software-rasterizer',

            # Avoid detection
            '--disable-blink-features=AutomationControlled',
            '--exclude-switches=enable-automation',
            '--disable-infobars',

            # Realistic browsing
            '--window-size=1920,1080',
            '--start-maximized',
        ]

    def get_context_options(self) -> Dict:
        """
        Get browser context options for stealth.

        Returns:
            Dictionary of context options
        """
        return {
            'user_agent': self.user_agent,
            'viewport': self.viewport,
            'locale': 'en-US',
            'timezone_id': 'Asia/Manila',
            'permissions': [],
            'ignore_https_errors': True,
            'extra_http_headers': {
                'Accept-Language': ', '.join(self.languages),
            }
        }


class HumanBehavior:
    """Simulate human-like behavior patterns."""

    @staticmethod
    def random_delay(min_seconds: float = 1.5, max_seconds: float = 4.5) -> float:
        """
        Generate a random delay with human-like variance.

        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay

        Returns:
            Random delay in seconds
        """
        # Use normal distribution for more realistic timing
        mean = (min_seconds + max_seconds) / 2
        std_dev = (max_seconds - min_seconds) / 4

        delay = random.gauss(mean, std_dev)

        # Clamp to min/max
        return max(min_seconds, min(max_seconds, delay))

    @staticmethod
    async def simulate_reading(page: Page, duration_seconds: float = 2.0):
        """
        Simulate human reading time with random scrolling.

        Args:
            page: Playwright Page instance
            duration_seconds: Base reading duration
        """
        import asyncio

        # Add variance to reading time
        actual_duration = HumanBehavior.random_delay(
            duration_seconds * 0.8,
            duration_seconds * 1.2
        )

        # Scroll a bit (humans scroll while reading)
        scroll_times = random.randint(0, 2)

        for _ in range(scroll_times):
            scroll_amount = random.randint(100, 300)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(0.3, 0.8))

        # Wait remaining time
        await asyncio.sleep(actual_duration)

    @staticmethod
    async def simulate_mouse_movement(page: Page, num_movements: int = 3):
        """
        Simulate random mouse movements.

        Args:
            page: Playwright Page instance
            num_movements: Number of random movements
        """
        import asyncio

        viewport = page.viewport_size
        if not viewport:
            return

        for _ in range(num_movements):
            x = random.randint(0, viewport['width'])
            y = random.randint(0, viewport['height'])

            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))


# Convenience function for quick stealth setup
async def apply_stealth_to_page(page: Page, stealth: Optional[PlaywrightStealth] = None):
    """
    Quick helper to apply stealth to a page.

    Args:
        page: Playwright Page instance
        stealth: Optional stealth config (creates new if None)
    """
    if stealth is None:
        stealth = PlaywrightStealth()

    await stealth.apply_stealth(page)


async def test_stealth(page: Page):
    """
    Test stealth effectiveness by checking common detection points.

    Args:
        page: Playwright Page instance

    Returns:
        dict: Test results
    """
    results = {
        'webdriver': await page.evaluate("navigator.webdriver"),
        'chrome_runtime': await page.evaluate("!!window.chrome && !!window.chrome.runtime"),
        'plugins_length': await page.evaluate("navigator.plugins.length"),
        'languages': await page.evaluate("navigator.languages"),
        'user_agent': await page.evaluate("navigator.userAgent"),
    }

    return results
