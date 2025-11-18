"""
Awarded Contracts scraper - No authentication required.

This scraper uses public URLs to scrape awarded contracts from PhilGEPS:
- Index: https://philgeps.gov.ph/Indexes/viewMoreAward
- Detail: /Indexes/viewAwardNotice/{award_id}/MORE

Key data extracted:
- Award Notice Number (primary identifier)
- Awardee name and details (who won)
- ABC (Approved Budget for Contract)
- Contract Amount (the actual awarded price) ⭐
- Award date and contract details
- Links to original bid reference number

Advantages:
- No login/session management
- No "session expired" warnings
- Direct access to award data
- Parallel processing support
"""

import asyncio
import time
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from config.settings import settings
from utils.logger import logger
from models.database import Database
from scraper.parser import PhilGEPSParser
from scraper.stealth import PlaywrightStealth, HumanBehavior


class AwardedContractsScraper:
    """
    Public PhilGEPS awarded contracts scraper using async API - no authentication required.

    Uses public URLs:
    - Award list: https://philgeps.gov.ph/Indexes/viewMoreAward
    - Award detail: /Indexes/viewAwardNotice/{award_id}/MORE

    Features:
    - Async/await for concurrent scraping
    - Full stealth protection
    - No login required
    - Parallel processing with multiple workers
    - Validates parsed data before saving
    """

    # Public URLs (no authentication)
    PUBLIC_INDEX_URL = "https://philgeps.gov.ph/Indexes/viewMoreAward"
    PUBLIC_DETAIL_URL_TEMPLATE = "https://philgeps.gov.ph/Indexes/viewAwardNotice/{award_id}/MORE"

    def __init__(self, num_workers: int = 2):
        """
        Initialize awarded contracts scraper.

        Args:
            num_workers: Number of concurrent workers (tabs). Default is 2.
        """
        self.num_workers = num_workers
        self.db = Database()
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.main_page: Optional[Page] = None
        self.stealth = PlaywrightStealth()  # Initialize stealth config

    async def run(self) -> Dict:
        """
        Run the complete awarded contracts scraping workflow.

        Returns:
            dict: Scraping results summary
        """
        start_time = datetime.now(timezone.utc)
        results = {
            'success': False,
            'total_scraped': 0,
            'new_records': 0,
            'errors': 0,
            'skipped': 0,
            'start_time': start_time,
            'workers': self.num_workers
        }

        try:
            logger.info("=" * 60)
            logger.info(f"Starting AWARDED CONTRACTS scraping ({self.num_workers} workers)")
            logger.info("No authentication required - using public URLs")
            logger.info("=" * 60)

            # Step 1: Initialize browser
            logger.info("Initializing async browser...")
            await self._init_browser()

            # Step 2: Navigate to public index page
            logger.info("Navigating to awarded contracts page...")
            await self.main_page.goto(
                self.PUBLIC_INDEX_URL,
                wait_until='domcontentloaded',
                timeout=30000
            )

            # Human-like wait for page to load
            await HumanBehavior.simulate_reading(self.main_page, duration_seconds=2.0)

            # Step 3: Get all awarded contracts with pagination
            award_list = await self._get_all_awards_with_pagination()
            logger.info(f"Found {len(award_list)} total awarded contracts across all pages")

            if not award_list:
                logger.warning("No awarded contracts found to scrape")
                logger.warning("This could mean:")
                logger.warning("  1. The filters are too restrictive")
                logger.warning("  2. There are no awarded contracts matching your criteria")
                logger.warning("  3. The page structure has changed")
                results['success'] = True  # Not an error, just no work to do
                return results

            # Step 4: Filter out already-scraped awards
            awards_to_scrape = []
            for award_summary in award_list:
                if self._is_already_scraped(award_summary['award_notice_number']):
                    logger.info(f"⏭️  Skipping already scraped award: {award_summary['award_notice_number']}")
                    results['skipped'] += 1
                else:
                    awards_to_scrape.append(award_summary)

            logger.info(f"Awards to scrape: {len(awards_to_scrape)} (skipped {results['skipped']} already scraped)")

            if not awards_to_scrape:
                logger.info("All awarded contracts already scraped, nothing to do")
                results['success'] = True
                return results

            # Step 5: Split work among workers
            work_chunks = self._split_work(awards_to_scrape, self.num_workers)

            # Step 6: Create worker pages with stealth
            # Reuse main_page for first worker to reduce tab count
            if self.num_workers == 1:
                logger.info(f"Using main page as single worker (no new tabs)...")
                worker_pages = [self.main_page]
                logger.info(f"  Worker 1: {len(work_chunks[0])} awards assigned (reusing main page)")
            else:
                logger.info(f"Creating {self.num_workers} browser tabs with stealth...")
                worker_pages = []

                # First worker reuses main_page
                worker_pages.append(self.main_page)
                logger.info(f"  Worker 1: {len(work_chunks[0])} awards assigned (reusing main page)")

                # Create additional workers
                for i in range(1, self.num_workers):
                    page = await self.context.new_page()
                    page.set_default_timeout(settings.BROWSER_TIMEOUT)

                    # Apply stealth to worker page
                    await self.stealth.apply_stealth(page)

                    worker_pages.append(page)
                    logger.info(f"  Worker {i+1}: {len(work_chunks[i])} awards assigned, stealth applied")

            # Step 7: Run workers concurrently
            logger.info(f"Starting awarded contracts scraping with {self.num_workers} concurrent workers...")

            # Create worker tasks
            worker_tasks = [
                self._worker(worker_id, worker_pages[worker_id], work_chunks[worker_id])
                for worker_id in range(self.num_workers)
            ]

            # Run all workers concurrently and wait for completion
            worker_results = await asyncio.gather(*worker_tasks, return_exceptions=True)

            # Step 8: Close worker pages (but not main_page)
            logger.debug("Closing worker pages...")
            for page in worker_pages:
                if page != self.main_page:
                    try:
                        await page.close()
                    except Exception as e:
                        logger.debug(f"Error closing worker page: {e}")

            # Step 9: Aggregate results
            for worker_result in worker_results:
                if isinstance(worker_result, Exception):
                    logger.error(f"Worker failed with exception: {worker_result}")
                    results['errors'] += 1
                elif isinstance(worker_result, dict):
                    results['total_scraped'] += worker_result.get('scraped', 0)
                    results['new_records'] += worker_result.get('new_records', 0)
                    results['errors'] += worker_result.get('errors', 0)

            results['success'] = True

        except Exception as e:
            logger.error(f"Awarded contracts scraping session failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            results['success'] = False

        finally:
            # Cleanup
            await self._cleanup()

            # Log results
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            results['end_time'] = end_time
            results['duration_seconds'] = duration

            self._log_session(results)

            logger.info("=" * 60)
            logger.info(f"Awarded contracts scraping completed in {duration:.2f} seconds")
            logger.info(f"Workers: {self.num_workers}, Total: {results['total_scraped']}, New: {results['new_records']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
            logger.info("=" * 60)

        return results

    async def _worker(self, worker_id: int, page: Page, award_list: List[Dict]) -> Dict:
        """
        Worker coroutine that processes assigned awarded contracts concurrently.

        Args:
            worker_id: Worker identifier (0-based)
            page: Playwright Page instance (tab) for this worker
            award_list: List of awards to scrape

        Returns:
            dict: Worker results
        """
        result = {
            'scraped': 0,
            'new_records': 0,
            'errors': 0
        }

        logger.info(f"[Worker {worker_id+1}] Started with {len(award_list)} awards")

        for idx, award_summary in enumerate(award_list, 1):
            try:
                # Use actual URL from listing page
                detail_url = award_summary.get('url') or self.PUBLIC_DETAIL_URL_TEMPLATE.format(
                    award_id=award_summary['award_notice_number']
                )

                # Scrape award details
                award_data = await self._scrape_award_details(page, detail_url)

                if award_data:
                    # Validate that we have an award notice number before saving
                    if not award_data.get('award_notice_number'):
                        logger.warning(f"[Worker {worker_id+1}] ({idx}/{len(award_list)}) ⚠️  Skipping award {award_summary['award_notice_number']}: Parser returned NULL award_notice_number (likely old/incompatible HTML structure)")
                        result['errors'] += 1
                    else:
                        # Save to database
                        self.db.save_awarded_contract(award_data)

                        result['new_records'] += 1
                        result['scraped'] += 1
                        logger.info(f"[Worker {worker_id+1}] ({idx}/{len(award_list)}) ✅ Saved: Award #{award_data['award_notice_number']} - {award_data.get('awardee_name', 'N/A')}")

                # Rate limiting - human-like random delay
                delay = HumanBehavior.random_delay(
                    min_seconds=settings.REQUEST_DELAY_SECONDS * 0.8,
                    max_seconds=settings.REQUEST_DELAY_SECONDS * 1.5
                )
                logger.debug(f"[Worker {worker_id+1}] Waiting {delay:.2f}s before next request")
                await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"[Worker {worker_id+1}] ❌ Error on award {award_summary.get('award_notice_number')}: {str(e)}")
                result['errors'] += 1
                continue

        logger.info(f"[Worker {worker_id+1}] Completed: {result['scraped']} scraped, {result['errors']} errors")
        return result

    async def _scrape_award_details(self, page: Page, url: str) -> Optional[Dict]:
        """
        Scrape full details from an awarded contract page.

        Args:
            page: Playwright Page instance to use
            url: Full URL of the awarded contract detail page

        Returns:
            dict: Awarded contract data or None if failed
        """
        try:
            # Navigate to award detail page
            await page.goto(url, wait_until='domcontentloaded')

            # Simulate human reading behavior
            await HumanBehavior.simulate_reading(page, duration_seconds=2.0)

            # Get page HTML
            html = await page.content()

            # Parse awarded contract details (use new parser method)
            parser = PhilGEPSParser(html)
            award_data = parser.parse_awarded_contract()

            # Add source URL
            award_data['url'] = url

            # Note: Document scraping not implemented yet for awarded contracts
            award_data['documents'] = []

            return award_data

        except Exception as e:
            logger.error(f"Error scraping award details from {url}: {str(e)}")
            return None

    async def _init_browser(self):
        """Initialize async browser with stealth."""
        try:
            self.playwright = await async_playwright().start()

            # Get browser type
            if settings.BROWSER_TYPE == "chromium":
                browser_type = self.playwright.chromium
            elif settings.BROWSER_TYPE == "firefox":
                browser_type = self.playwright.firefox
            else:
                browser_type = self.playwright.chromium

            # Get stealth launch arguments
            launch_args = self.stealth.get_launch_args()
            logger.debug(f"Using stealth browser args: {len(launch_args)} args")

            # Use persistent context if configured (shares session across runs)
            if settings.USE_PERSISTENT_PROFILE and settings.USER_DATA_DIR:
                logger.info(f"Using persistent profile with stealth: {settings.USER_DATA_DIR}")

                # Get context options for stealth
                context_options = self.stealth.get_context_options()

                self.context = await browser_type.launch_persistent_context(
                    user_data_dir=settings.USER_DATA_DIR,
                    headless=settings.HEADLESS_MODE,
                    args=launch_args,
                    **context_options
                )

                # Get or create first page
                if self.context.pages:
                    self.main_page = self.context.pages[0]
                else:
                    self.main_page = await self.context.new_page()

                # Apply stealth JavaScript injections
                await self.stealth.apply_stealth(self.main_page)
                logger.info("✓ Stealth measures applied to main page")
            else:
                logger.info("Using temporary browser profile with stealth")

                # Get context options for stealth
                context_options = self.stealth.get_context_options()

                self.browser = await browser_type.launch(
                    headless=settings.HEADLESS_MODE,
                    args=launch_args
                )
                self.context = await self.browser.new_context(**context_options)
                self.main_page = await self.context.new_page()

                # Apply stealth JavaScript injections
                await self.stealth.apply_stealth(self.main_page)
                logger.info("✓ Stealth measures applied to main page")

            self.main_page.set_default_timeout(settings.BROWSER_TIMEOUT)
            logger.info("Async browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize async browser: {str(e)}")
            raise

    async def _get_all_awards_with_pagination(self) -> List[Dict]:
        """Get all awarded contracts from public index with pagination."""
        all_awards = []

        try:
            # Get first page
            logger.info("Getting awards from page 1...")
            awards = await self._get_award_list()
            all_awards.extend(awards)

            # Check for pagination
            total_pages = await self._get_total_pages()

            if total_pages and total_pages > 1:
                logger.info(f"Found {total_pages} total pages, scraping all pages...")

                for page_num in range(2, total_pages + 1):
                    try:
                        logger.info(f"Getting awards from page {page_num} of {total_pages}...")
                        next_page_url = self._build_pagination_url(page_num)
                        await self.main_page.goto(next_page_url, wait_until='domcontentloaded')

                        # Human-like delay between pagination
                        delay = HumanBehavior.random_delay(1.5, 3.5)
                        await asyncio.sleep(delay)

                        page_awards = await self._get_award_list()
                        all_awards.extend(page_awards)
                    except Exception as e:
                        logger.error(f"Error scraping page {page_num}: {str(e)}")
                        continue

            return all_awards

        except Exception as e:
            logger.error(f"Error in pagination: {str(e)}")
            return all_awards

    async def _get_award_list(self) -> List[Dict]:
        """Extract awarded contracts list from current page."""
        try:
            html = await self.main_page.content()
            soup = BeautifulSoup(html, 'lxml')

            awards = []
            rows = soup.select('tbody tr')

            for row in rows:
                try:
                    # Extract award notice number and URL
                    award_link = row.select_one('td:nth-of-type(1) a')
                    if not award_link:
                        continue

                    award_notice_number = award_link.get_text(strip=True)

                    # Extract actual href - use the real URL from the page
                    href = award_link.get('href', '')
                    # Build full URL if href is relative
                    if href.startswith('/'):
                        detail_url = f"https://philgeps.gov.ph{href}"
                    elif href.startswith('http'):
                        detail_url = href
                    else:
                        # Fallback to template if href is invalid
                        detail_url = self.PUBLIC_DETAIL_URL_TEMPLATE.format(award_id=award_notice_number)

                    # Extract bid reference number
                    bid_ref_cell = row.select_one('td:nth-of-type(2)')
                    bid_reference_number = bid_ref_cell.get_text(strip=True) if bid_ref_cell else ''

                    # Extract title
                    title_cell = row.select_one('td:nth-of-type(3)')
                    title = title_cell.get_text(strip=True) if title_cell else ''

                    # Extract awardee
                    awardee_cell = row.select_one('td:nth-of-type(4)')
                    awardee = awardee_cell.get_text(strip=True) if awardee_cell else ''

                    # Extract award date
                    date_cell = row.select_one('td:nth-of-type(5)')
                    award_date = date_cell.get_text(strip=True) if date_cell else ''

                    awards.append({
                        'award_notice_number': award_notice_number,
                        'bid_reference_number': bid_reference_number,
                        'title': title,
                        'awardee': awardee,
                        'award_date': award_date,
                        'url': detail_url
                    })

                except Exception as e:
                    logger.debug(f"Error parsing row: {str(e)}")
                    continue

            return awards

        except Exception as e:
            logger.error(f"Error getting award list: {str(e)}")
            return []

    async def _get_total_pages(self) -> Optional[int]:
        """Extract total number of pages from pagination info."""
        try:
            html = await self.main_page.content()
            soup = BeautifulSoup(html, 'lxml')

            paginator = soup.find('div', class_='paginator')
            if paginator:
                page_info = paginator.find('p')
                if page_info:
                    text = page_info.get_text(strip=True)
                    match = re.search(r'Page\s+\d+\s+of\s+(\d+)', text)
                    if match:
                        return int(match.group(1))

            return None

        except Exception as e:
            logger.error(f"Error getting total pages: {str(e)}")
            return None

    def _build_pagination_url(self, page_num: int) -> str:
        """Build pagination URL with filters for awarded contracts index."""
        from urllib.parse import urlencode

        params = {
            'page': page_num,
            'direction': 'Awards.award_date+desc'
        }

        # Add filters if configured (reuse same filter settings)
        if settings.FILTER_PUBLISH_DATE_FROM:
            params['searchPublishDateFrom'] = settings.FILTER_PUBLISH_DATE_FROM
        if settings.FILTER_PUBLISH_DATE_TO:
            params['searchPublishDateTo'] = settings.FILTER_PUBLISH_DATE_TO
        if settings.FILTER_CLASSIFICATION:
            params['searchClassification'] = settings.FILTER_CLASSIFICATION
        if settings.FILTER_BUSINESS_CATEGORY:
            params['searchBussinessCategory'] = settings.FILTER_BUSINESS_CATEGORY

        return f"{self.PUBLIC_INDEX_URL}?{urlencode(params)}"

    def _split_work(self, items: List, num_chunks: int) -> List[List]:
        """Split work evenly among workers using round-robin."""
        chunks = [[] for _ in range(num_chunks)]
        for idx, item in enumerate(items):
            worker_id = idx % num_chunks
            chunks[worker_id].append(item)
        return chunks

    def _is_already_scraped(self, award_notice_number: str) -> bool:
        """Check if awarded contract already exists in database."""
        return self.db.awarded_contract_exists(award_notice_number)

    def _log_session(self, results: Dict):
        """Log scraping session to database."""
        try:
            from models.schemas import ScrapingLog

            log_entry = ScrapingLog(
                start_time=results['start_time'],
                end_time=results['end_time'],
                duration_seconds=results['duration_seconds'],
                total_scraped=results['total_scraped'],
                new_records=results['new_records'],
                errors=results['errors'],
                success=results['success'],
                notes=f"Awarded contracts scraping (no auth) with {self.num_workers} workers"
            )
            self.db.save_scraping_log(log_entry)
        except Exception as e:
            logger.error(f"Error logging session: {str(e)}")

    async def _cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.main_page:
                await self.main_page.close()

            if self.context:
                await self.context.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()

            logger.info("Awarded contracts scraper browser cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


async def main():
    """Main entry point for awarded contracts scraper."""
    scraper = AwardedContractsScraper(num_workers=2)
    results = await scraper.run()

    if results['success']:
        print(f"\n✅ Awarded contracts scraping completed successfully!")
        print(f"   Duration: {results['duration_seconds']:.2f} seconds")
        print(f"   Total scraped: {results['total_scraped']}")
        print(f"   New records: {results['new_records']}")
        print(f"   Errors: {results['errors']}")
    else:
        print(f"\n❌ Awarded contracts scraping failed")

    return results


if __name__ == "__main__":
    # Run awarded contracts scraper
    asyncio.run(main())
