"""Authentication handler for PhilGEPS with reCAPTCHA support."""

from playwright.sync_api import Page
from config.settings import settings
from utils.logger import logger
from typing import Optional
import time
import random


class PhilGEPSAuth:
    """Handles authentication to PhilGEPS portal with reCAPTCHA solving."""

    RECAPTCHA_SITE_KEY = "6LetQD4qAAAAABLlVgHRuIAx2MEeudtDWkJRxODi"

    def __init__(self, page: Page):
        """
        Initialize authentication handler.

        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.is_logged_in = False

    def _human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Add a random delay to simulate human behavior.

        Args:
            min_seconds: Minimum delay in seconds
            max_seconds: Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _click_recaptcha_checkbox(self) -> bool:
        """
        Automatically click the reCAPTCHA checkbox.

        Returns:
            bool: True if click was successful
        """
        try:
            # The reCAPTCHA checkbox is inside an iframe
            # We need to switch to the iframe context to click it

            # Wait for the reCAPTCHA iframe to load
            logger.debug("Looking for reCAPTCHA iframe...")
            time.sleep(1)

            # Find the reCAPTCHA anchor frame (contains the checkbox)
            recaptcha_frame = self.page.frame_locator('iframe[src*="google.com/recaptcha/api2/anchor"]')

            if recaptcha_frame:
                logger.debug("Found reCAPTCHA iframe, locating checkbox...")

                # Find and click the checkbox inside the iframe
                # The checkbox is usually a div with class "recaptcha-checkbox-border"
                # or we can target the larger clickable area
                checkbox = recaptcha_frame.locator('#recaptcha-anchor')

                # Wait for checkbox to be visible
                checkbox.wait_for(state="visible", timeout=5000)

                # Add human-like delay before clicking
                self._human_delay(0.3, 0.7)

                # Click the checkbox
                checkbox.click()
                logger.debug("Clicked reCAPTCHA checkbox")

                return True
            else:
                logger.warning("Could not find reCAPTCHA iframe")
                return False

        except Exception as e:
            logger.warning(f"Failed to auto-click reCAPTCHA checkbox: {str(e)}")
            return False

    def _check_recaptcha_response(self) -> Optional[str]:
        """
        Check if reCAPTCHA has been successfully solved.

        Returns:
            str: reCAPTCHA response token if solved, None otherwise
        """
        try:
            response = self.page.evaluate("""
                () => {
                    try {
                        if (typeof grecaptcha !== 'undefined') {
                            const response = grecaptcha.getResponse();
                            return response && response.length > 0 ? response : null;
                        }
                    } catch (e) {
                        return null;
                    }
                    return null;
                }
            """)
            return response
        except Exception as e:
            logger.debug(f"Error checking reCAPTCHA response: {str(e)}")
            return None

    def _simulate_mouse_movement(self, target_selector: str):
        """
        Simulate human-like mouse movement before clicking.

        This helps Google reCAPTCHA recognize human behavior patterns.

        Args:
            target_selector: CSS selector of the element to move towards
        """
        try:
            # Get element position
            element = self.page.locator(target_selector).first
            if element.count() > 0:
                box = element.bounding_box()
                if box:
                    # Move mouse to a point near the element first
                    # Then move to the actual element (simulates cursor approach)
                    nearby_x = box['x'] + box['width'] / 2 + random.randint(-50, -20)
                    nearby_y = box['y'] + box['height'] / 2 + random.randint(-30, 30)

                    self.page.mouse.move(nearby_x, nearby_y)
                    time.sleep(random.uniform(0.1, 0.3))

                    # Move to actual element
                    target_x = box['x'] + box['width'] / 2 + random.randint(-5, 5)
                    target_y = box['y'] + box['height'] / 2 + random.randint(-5, 5)
                    self.page.mouse.move(target_x, target_y)
                    time.sleep(random.uniform(0.2, 0.5))
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed (not critical): {e}")

    def login(self, username: str = None, password: str = None) -> bool:
        """
        Login to PhilGEPS with reCAPTCHA handling.

        Args:
            username: PhilGEPS username (defaults to settings)
            password: PhilGEPS password (defaults to settings)

        Returns:
            bool: True if login successful, False otherwise
        """
        username = username or settings.PHILGEPS_USERNAME
        password = password or settings.PHILGEPS_PASSWORD

        try:
            logger.info("Attempting to login to PhilGEPS...")

            # Navigate to login page
            self.page.goto(settings.PHILGEPS_LOGIN_URL, timeout=settings.BROWSER_TIMEOUT)

            # Wait for page to fully load (better trust signals for reCAPTCHA)
            logger.debug("Waiting for page to fully load...")
            try:
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logger.debug("Network idle timeout (not critical)")
                self.page.wait_for_load_state('domcontentloaded', timeout=5000)

            # Check for and dismiss any existing error flash messages
            # This can happen when using persistent browser profiles
            self._dismiss_error_dialog()

            # Add human-like delay after page load (simulate reading)
            self._human_delay(1.5, 2.5)

            # Wait for the user type dropdown to be visible (this is the first field to fill)
            self.page.wait_for_selector('select[name="type"]', timeout=10000)

            # Select user type (Merchant) - THIS MUST BE FIRST
            logger.info("Selecting user type: Merchant...")
            self.page.select_option('select[name="type"]', value='Marchant')

            # Human delay after dropdown selection
            self._human_delay(0.5, 1.0)

            # Now wait for login form fields to be visible
            self.page.wait_for_selector('input[name="username"]', timeout=10000)

            # Fill in credentials with human-like typing
            logger.info("Filling in credentials...")
            # Type username with delays between keystrokes (more human)
            self.page.locator('input[name="username"]').click()
            self._human_delay(0.3, 0.6)
            self.page.locator('input[name="username"]').fill(username, timeout=5000)

            # Small delay before moving to password field
            self._human_delay(0.5, 1.0)

            # Type password
            self.page.locator('input[name="password"]').click()
            self._human_delay(0.3, 0.6)
            self.page.locator('input[name="password"]').fill(password, timeout=5000)

            # Longer delay before interacting with reCAPTCHA (appears more human)
            # This is critical - Google analyzes behavior before the click
            logger.debug("Pausing before reCAPTCHA (simulating human behavior)...")
            self._human_delay(2.0, 4.0)

            # Handle reCAPTCHA
            logger.info(f"Solving reCAPTCHA using method: {settings.RECAPTCHA_SOLVE_METHOD}")
            if not self._solve_recaptcha():
                logger.error("Failed to solve reCAPTCHA")
                return False

            # Wait for reCAPTCHA callbacks to complete
            # After solving, JavaScript might need time to enable the submit button
            logger.info("Waiting for form to be ready after reCAPTCHA...")
            time.sleep(2)

            # Submit login form
            logger.info("Submitting login form...")
            submit_button = self.page.locator('input[type="submit"]')

            # Wait for button to be enabled and clickable
            try:
                submit_button.wait_for(state="visible", timeout=5000)
                # Check if button is disabled and wait for it to be enabled
                for _ in range(10):  # Try for up to 10 seconds
                    is_disabled = submit_button.get_attribute('disabled')
                    if is_disabled is None:  # Button is enabled
                        break
                    time.sleep(1)

                submit_button.click(timeout=10000)
            except Exception as e:
                logger.error(f"Failed to click submit button: {str(e)}")
                # Try force clicking as fallback
                logger.info("Attempting force click...")
                submit_button.click(force=True, timeout=5000)

            # Wait for navigation after login
            time.sleep(3)

            # Check if login was successful
            if self.is_authenticated():
                logger.info("Successfully logged in to PhilGEPS")
                self.is_logged_in = True
                return True
            else:
                # Get more debug info
                current_url = self.page.url
                page_title = self.page.title()

                # Check for error messages on page
                error_messages = []
                error_selectors = [
                    '.error', '.alert-danger', '.text-danger',
                    '[class*="error"]', '[class*="alert"]'
                ]
                for selector in error_selectors:
                    try:
                        elements = self.page.locator(selector).all()
                        for elem in elements:
                            text = elem.text_content()
                            if text and len(text.strip()) > 0:
                                error_messages.append(text.strip())
                    except:
                        pass

                logger.error("Login failed - check credentials or CAPTCHA solution")
                logger.error(f"Current URL: {current_url}")
                logger.error(f"Page title: {page_title}")
                if error_messages:
                    logger.error(f"Error messages on page: {', '.join(error_messages[:3])}")

                # Save screenshot for debugging
                try:
                    screenshot_path = f"debug_login_failed_{int(time.time())}.png"
                    self.page.screenshot(path=screenshot_path)
                    logger.info(f"Screenshot saved to: {screenshot_path}")
                except Exception as e:
                    logger.debug(f"Could not save screenshot: {e}")

                return False

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def _solve_recaptcha(self) -> bool:
        """
        Solve reCAPTCHA challenge based on configured method.

        Note: PhilGEPS login page ALWAYS has the reCAPTCHA checkbox.
        It's a required part of the login form (username, password, Merchant type, reCAPTCHA).

        The checkbox must always be clicked. What varies is what happens after:
        - With persistent profile + trusted session: Click → instant green checkmark
        - With persistent profile + verification: Click → image challenges appear
        - Without persistent profile: Click → image challenges appear

        Returns:
            bool: True if CAPTCHA solved successfully
        """
        logger.info("Solving reCAPTCHA (checkbox must be clicked)...")
        method = settings.RECAPTCHA_SOLVE_METHOD.lower()

        if method == "manual":
            return self._solve_recaptcha_manual()
        elif method == "2captcha":
            return self._solve_recaptcha_2captcha()
        elif method == "auto":
            return self._solve_recaptcha_auto()
        else:
            logger.error(f"Unknown reCAPTCHA solve method: {method}")
            return False

    def _solve_recaptcha_manual(self) -> bool:
        """
        Semi-automated reCAPTCHA solving - automatically clicks checkbox,
        waits for manual solving only if image challenges appear.

        Workflow:
        1. Auto-click the reCAPTCHA checkbox
        2. If instant verification → Done! ✓
        3. If image challenges appear → Wait for user to solve them

        Returns:
            bool: True if CAPTCHA solved
        """
        # Simulate mouse movement towards reCAPTCHA (helps with trust signals)
        logger.debug("Simulating human-like mouse movement...")
        try:
            # Try to move mouse towards the reCAPTCHA iframe
            self._simulate_mouse_movement('iframe[src*="google.com/recaptcha"]')
        except:
            logger.debug("Mouse movement simulation skipped (element not found)")

        # Add a small delay before clicking (more natural)
        self._human_delay(0.5, 1.0)

        # Automatically click the reCAPTCHA checkbox
        logger.info("=" * 70)
        logger.info("🤖 AUTO-CLICKING reCAPTCHA checkbox...")
        logger.info("=" * 70)

        try:
            # Click the reCAPTCHA checkbox inside the iframe
            success = self._click_recaptcha_checkbox()

            if not success:
                logger.warning("⚠️  Auto-click failed, please click the checkbox manually")
                logger.warning("=" * 70)
                logger.warning("  📋 MANUAL ACTION REQUIRED:")
                logger.warning("     1. Look at the browser window")
                logger.warning("     2. Click the reCAPTCHA checkbox manually")
                logger.warning("=" * 70)
            else:
                logger.info("✓ Checkbox clicked successfully!")
                logger.info("⏳ Waiting to see if verification is needed...")

                # Wait a moment to see what happens after the click
                time.sleep(3)

                # Check if instantly verified (trusted session)
                response = self._check_recaptcha_response()
                if response:
                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("✅ reCAPTCHA verified instantly! (Trusted session)")
                    logger.info("=" * 70)
                    return True

                # Not instantly verified - check if image challenge appeared
                logger.info("")
                logger.info("=" * 70)
                logger.info("📸 Image challenge appeared - MANUAL SOLVING REQUIRED")
                logger.info("=" * 70)
                logger.info("")
                logger.info("  📋 PLEASE COMPLETE THE IMAGE CHALLENGE:")
                logger.info("     1. Look at the browser window")
                logger.info("     2. Select the images as requested")
                logger.info("     3. Click 'Verify' when done")
                logger.info("")
                logger.info(f"  ⏱️  Timeout: {settings.RECAPTCHA_TIMEOUT} seconds")
                logger.info("")
                logger.info("=" * 70)

        except Exception as e:
            logger.warning(f"Error during auto-click: {e}")
            logger.warning("Please click the checkbox manually")
            logger.warning("=" * 70)

        # Wait for reCAPTCHA to be solved (check for response token)
        start_time = time.time()
        timeout = settings.RECAPTCHA_TIMEOUT
        last_message_time = start_time
        check_interval = 2  # Check every 2 seconds

        while time.time() - start_time < timeout:
            try:
                # Check if reCAPTCHA response exists
                response = self._check_recaptcha_response()

                if response:
                    logger.info("")
                    logger.info("=" * 70)
                    logger.info("✅ reCAPTCHA solved successfully!")
                    logger.info("=" * 70)
                    return True

                # Show progress every 10 seconds
                elapsed = time.time() - start_time
                if elapsed - (last_message_time - start_time) >= 10:
                    remaining = int(timeout - elapsed)
                    logger.info(f"⏳ Still waiting for image challenge solution... ({remaining}s remaining)")
                    last_message_time = time.time()

            except Exception as e:
                logger.debug(f"Checking CAPTCHA status: {str(e)}")

            time.sleep(check_interval)

        logger.error("")
        logger.error("=" * 70)
        logger.error("❌ Timeout waiting for manual CAPTCHA solution")
        logger.error("=" * 70)
        logger.error("")
        logger.error("💡 TROUBLESHOOTING:")
        logger.error("   - Make sure the browser window is visible (set HEADLESS_MODE=false)")
        logger.error("   - Try increasing RECAPTCHA_TIMEOUT in .env file")
        logger.error("   - Consider using persistent browser profile (USE_PERSISTENT_PROFILE=true)")
        logger.error("")
        return False

    def _solve_recaptcha_2captcha(self) -> bool:
        """
        Solve reCAPTCHA using 2captcha API service.

        Returns:
            bool: True if CAPTCHA solved
        """
        if not settings.TWOCAPTCHA_API_KEY:
            logger.error("2captcha API key not configured. Set TWOCAPTCHA_API_KEY in .env")
            logger.error("Get your API key from: https://2captcha.com")
            return False

        try:
            from twocaptcha import TwoCaptcha

            logger.info("=" * 70)
            logger.info("🤖 Solving reCAPTCHA with 2captcha service...")
            logger.info("=" * 70)

            solver = TwoCaptcha(settings.TWOCAPTCHA_API_KEY)

            # Get current page URL
            page_url = self.page.url

            # Solve reCAPTCHA
            logger.info("📤 Submitting CAPTCHA to 2captcha... (this may take 30-60 seconds)")
            logger.info("💰 Note: This will use credits from your 2captcha account")

            result = solver.recaptcha(
                sitekey=self.RECAPTCHA_SITE_KEY,
                url=page_url
            )

            captcha_response = result['code']
            logger.info("📥 Received CAPTCHA solution from 2captcha")

            # Inject the CAPTCHA response
            self.page.evaluate(f"""
                (response) => {{
                    document.getElementById('g-recaptcha-response').innerHTML = response;
                    if (typeof grecaptcha !== 'undefined') {{
                        grecaptcha.getResponse = function() {{ return response; }};
                    }}
                }}
            """, captcha_response)

            logger.info("=" * 70)
            logger.info("✅ reCAPTCHA solved with 2captcha!")
            logger.info("=" * 70)
            return True

        except Exception as e:
            logger.error("")
            logger.error("=" * 70)
            logger.error(f"❌ 2captcha solving failed: {str(e)}")
            logger.error("=" * 70)
            logger.error("")
            logger.error("💡 TROUBLESHOOTING:")
            logger.error("   - Check your API key is correct in .env file")
            logger.error("   - Verify account balance at https://2captcha.com")
            logger.error("   - Make sure you have sufficient credits")
            logger.error("")
            return False

    def _solve_recaptcha_auto(self) -> bool:
        """
        Attempt automatic reCAPTCHA solving using playwright-recaptcha.

        Note: This method may not be reliable and is not recommended for production.

        Returns:
            bool: True if CAPTCHA solved
        """
        try:
            from playwright_recaptcha.recaptchav2 import recaptchav2

            logger.warning("=" * 70)
            logger.warning("⚠️  Attempting automatic CAPTCHA solving (experimental)...")
            logger.warning("=" * 70)
            logger.warning("")
            logger.warning("⚠️  WARNING:")
            logger.warning("   - This method is experimental and may not work reliably")
            logger.warning("   - It uses audio challenges which may be detected")
            logger.warning("   - Consider using 2captcha or manual method for production")
            logger.warning("")
            logger.warning("=" * 70)

            # Use playwright-recaptcha to solve
            # Note: This library uses audio challenge which may be detected
            logger.info("🤖 Starting automatic solving (this may take 30-60 seconds)...")
            success = recaptchav2.solve_recaptcha(self.page, timeout=60000)

            if success:
                logger.info("")
                logger.info("=" * 70)
                logger.info("✅ reCAPTCHA solved automatically!")
                logger.info("=" * 70)
                return True
            else:
                logger.error("")
                logger.error("=" * 70)
                logger.error("❌ Automatic CAPTCHA solving failed")
                logger.error("=" * 70)
                logger.error("")
                logger.error("💡 Try switching to manual or 2captcha method instead")
                logger.error("")
                return False

        except ImportError:
            logger.error("")
            logger.error("=" * 70)
            logger.error("❌ playwright-recaptcha not installed")
            logger.error("=" * 70)
            logger.error("")
            logger.error("📦 To install: pip install playwright-recaptcha")
            logger.error("")
            return False
        except Exception as e:
            logger.error("")
            logger.error("=" * 70)
            logger.error(f"❌ Automatic CAPTCHA solving failed: {str(e)}")
            logger.error("=" * 70)
            logger.error("")
            logger.error("💡 Try switching to manual or 2captcha method instead")
            logger.error("")
            return False

    def _dismiss_error_dialog(self) -> None:
        """
        Dismiss error flash dialog if present on the page.

        This handles residual error messages that may appear when using
        persistent browser profiles, especially the "Invalid username / password / user type"
        error that can appear on initial page load.
        """
        try:
            # Check if error dialog is visible
            error_dialog = self.page.query_selector('#dialogbox-flash')

            if error_dialog and error_dialog.is_visible():
                logger.info("Dismissing error flash dialog from previous session...")

                # Try to click the OK button
                ok_button = self.page.query_selector('#dialogbox-flash button.btn-danger')
                if ok_button:
                    ok_button.click()
                    logger.info("Error dialog dismissed successfully")

                # Wait a moment for the dialog to close
                time.sleep(1)

        except Exception as e:
            # Not critical - just log and continue
            logger.debug(f"No error dialog found or error dismissing it: {str(e)}")

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            # Check current URL
            current_url = self.page.url
            if "login" in current_url.lower():
                return False

            # Check for logged-in indicators
            # Common patterns: user menu, dashboard, logout button
            try:
                # Wait briefly for post-login page to load
                self.page.wait_for_load_state('networkidle', timeout=5000)

                # Check for common authenticated page elements
                # Adjust these selectors based on actual PhilGEPS structure
                selectors_to_try = [
                    'a[href*="logout"]',
                    '.user-menu',
                    '.user-info',
                    '#user-profile',
                    'nav[class*="user"]',
                    '[class*="dashboard"]'
                ]

                for selector in selectors_to_try:
                    try:
                        self.page.wait_for_selector(selector, timeout=2000)
                        logger.debug(f"Found auth indicator: {selector}")
                        return True
                    except:
                        continue

                # If none found, check if we're not on login page
                if "dashboard" in current_url.lower() or "home" in current_url.lower():
                    return True

                return False

            except:
                return False

        except Exception as e:
            logger.warning(f"Auth check failed: {str(e)}")
            return False

    def logout(self) -> bool:
        """
        Logout from PhilGEPS.

        Returns:
            bool: True if logout successful
        """
        try:
            logger.info("Logging out from PhilGEPS...")

            # Check if confirmation dialog is already open
            confirm_button = self.page.locator('#logout_click')
            if confirm_button.count() > 0:
                logger.debug("Logout confirmation dialog already open, clicking confirm...")
            else:
                # Find and click logout link to open confirmation dialog
                # Use more specific selector to avoid matching the confirmation button
                logout_link = self.page.locator('a[href*="logout"]:not(#logout_click)').first
                try:
                    logout_link.click(timeout=5000)
                    logger.debug("Clicked logout link, waiting for confirmation dialog...")
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Failed to click logout link: {e}")
                    # Maybe we're already at logout or dialog is open
                    pass

            # Try to click the confirmation button with multiple strategies
            try:
                # Wait for the button to be attached
                confirm_button = self.page.locator('#logout_click')
                confirm_button.wait_for(state="attached", timeout=5000)

                # Try scrolling into view first
                try:
                    confirm_button.scroll_into_view_if_needed(timeout=2000)
                except:
                    logger.debug("Scroll into view not needed or failed")

                # Force click the button since visibility detection is unreliable
                confirm_button.click(force=True, timeout=5000)
                logger.debug("Clicked confirmation button")

            except Exception as e:
                logger.warning(f"Failed to click confirmation button: {e}")
                # Strategy 2: Try direct navigation to logout URL as fallback
                logger.info("Attempting direct logout via URL...")
                self.page.goto("https://philgeps.gov.ph/users/logout", timeout=10000)

            # Wait for logout to complete
            time.sleep(2)

            self.is_logged_in = False
            logger.info("Successfully logged out")
            return True

        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            # Even if logout fails, mark as logged out to allow cleanup
            self.is_logged_in = False
            return False

    def refresh_session(self) -> bool:
        """
        Refresh the session if it expires.

        Returns:
            bool: True if session refreshed successfully
        """
        if not self.is_authenticated():
            logger.warning("Session expired, attempting to re-login...")
            return self.login()
        return True
