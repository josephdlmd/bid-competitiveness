"""Parallel scraper using multiple browser tabs for faster scraping."""

from scraper.browser import BrowserHandler
from scraper.auth import PhilGEPSAuth
from scraper.parser import PhilGEPSParser
from models.database import Database
from models.schemas import BidNotice, ScrapingLog
from config.settings import settings
from utils.logger import logger
from utils.retry import retry_on_failure
import time
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from threading import Thread, Lock
from playwright.sync_api import Page


class ParallelPhilGEPSScraper:
    """
    Parallel scraper that uses multiple browser tabs to scrape bids simultaneously.

    This implementation:
    - Launches a SINGLE browser process
    - Logs in ONCE and shares authentication across all tabs
    - Creates multiple tabs (pages) that work in parallel
    - Uses threading to coordinate parallel workers
    - Achieves 3× speedup with minimal memory overhead
    """

    def __init__(self, num_workers: int = 3):
        """
        Initialize parallel scraper.

        Args:
            num_workers: Number of parallel workers (tabs) to use. Default is 3.
        """
        self.num_workers = num_workers
        self.browser_handler = BrowserHandler()
        self.db = Database()
        self.main_page = None
        self.auth = None
        self.db_lock = Lock()  # For thread-safe database writes

    def run(self) -> Dict:
        """
        Run the complete parallel scraping workflow.

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
            logger.info(f"Starting PARALLEL PhilGEPS scraping ({self.num_workers} workers)")
            logger.info("=" * 60)

            # Step 1: Initialize browser (single instance)
            logger.info("Initializing browser...")
            self.main_page = self.browser_handler.init_browser()

            # Step 2: Authenticate ONCE
            logger.info("Authenticating (login once for all workers)...")
            self.auth = PhilGEPSAuth(self.main_page)
            if not self.auth.login():
                raise Exception("Authentication failed")

            # Step 3: Navigate to bid notices list page
            self.browser_handler.navigate(settings.PHILGEPS_BID_LIST)

            # Step 3.5: Apply filters if configured
            self._apply_filters()

            # Step 4: Get list of bid notices from all pages
            bid_list = self._get_all_bids_with_pagination()
            logger.info(f"Found {len(bid_list)} total bid notices across all pages")

            if not bid_list:
                logger.warning("No bids to scrape")
                return results

            # Step 5: Filter out already-scraped bids
            bids_to_scrape = []
            for bid_summary in bid_list:
                if self._is_already_scraped(bid_summary['reference_number']):
                    logger.info(f"⏭️  Skipping already scraped bid: {bid_summary['reference_number']}")
                    results['skipped'] += 1
                else:
                    bids_to_scrape.append(bid_summary)

            logger.info(f"Bids to scrape: {len(bids_to_scrape)} (skipped {results['skipped']} already scraped)")

            if not bids_to_scrape:
                logger.info("All bids already scraped, nothing to do")
                results['success'] = True
                return results

            # Step 6: Split work among workers
            work_chunks = self._split_work(bids_to_scrape, self.num_workers)

            # Step 7: Create worker tabs (pages)
            logger.info(f"Creating {self.num_workers} browser tabs for parallel scraping...")
            worker_pages = []
            for i in range(self.num_workers):
                # Each worker gets its own page (tab) in the same browser
                page = self.browser_handler.context.new_page()
                page.set_default_timeout(settings.BROWSER_TIMEOUT)
                worker_pages.append(page)
                logger.info(f"  Worker {i+1}: {len(work_chunks[i])} bids assigned")

            # Step 8: Run workers in parallel using threads
            logger.info(f"Starting parallel scraping with {self.num_workers} workers...")
            worker_results = [{} for _ in range(self.num_workers)]
            threads = []

            for worker_id in range(self.num_workers):
                thread = Thread(
                    target=self._worker,
                    args=(worker_id, worker_pages[worker_id], work_chunks[worker_id], worker_results[worker_id])
                )
                threads.append(thread)
                thread.start()

            # Wait for all workers to complete
            for thread in threads:
                thread.join()

            # Step 9: Close worker pages
            logger.debug("Closing worker pages...")
            for page in worker_pages:
                try:
                    page.close()
                except Exception as e:
                    logger.debug(f"Error closing worker page: {e}")

            # Step 10: Aggregate results
            for worker_result in worker_results:
                results['total_scraped'] += worker_result.get('scraped', 0)
                results['new_records'] += worker_result.get('new_records', 0)
                results['errors'] += worker_result.get('errors', 0)

            results['success'] = True

        except Exception as e:
            logger.error(f"Parallel scraping session failed: {str(e)}")
            results['success'] = False

        finally:
            # Close worker pages if they were created
            try:
                if 'worker_pages' in locals():
                    logger.debug("Closing worker pages in finally block...")
                    for page in worker_pages:
                        try:
                            if not page.is_closed():
                                page.close()
                        except Exception as e:
                            logger.debug(f"Error closing worker page in finally: {e}")
            except Exception as e:
                logger.debug(f"Error in worker pages cleanup: {e}")

            # Cleanup browser
            self._cleanup()

            # Log results
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            results['end_time'] = end_time
            results['duration_seconds'] = duration

            self._log_session(results)

            logger.info("=" * 60)
            logger.info(f"Parallel scraping completed in {duration:.2f} seconds")
            logger.info(f"Workers: {self.num_workers}, Total: {results['total_scraped']}, New: {results['new_records']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
            logger.info("=" * 60)

        return results

    def _worker(self, worker_id: int, page: Page, bid_list: List[Dict], result: Dict) -> None:
        """
        Worker function that runs in a separate thread.

        Each worker:
        - Has its own browser tab (page)
        - Processes its assigned list of bids
        - Reports results back via the result dict

        Args:
            worker_id: Worker identifier (0-based)
            page: Playwright Page instance (tab) for this worker
            bid_list: List of bids to scrape
            result: Dictionary to store results (modified in place)
        """
        result['scraped'] = 0
        result['new_records'] = 0
        result['errors'] = 0

        logger.info(f"[Worker {worker_id+1}] Started with {len(bid_list)} bids")

        for idx, bid_summary in enumerate(bid_list, 1):
            try:
                # Scrape bid details
                bid_data = self._scrape_bid_details(page, bid_summary['url'])

                if bid_data:
                    # Save to database (thread-safe)
                    with self.db_lock:
                        self.db.save_bid_notice(bid_data)

                    result['new_records'] += 1
                    result['scraped'] += 1
                    logger.info(f"[Worker {worker_id+1}] ({idx}/{len(bid_list)}) ✅ Saved: {bid_data['reference_number']}")

                # Rate limiting - wait between requests
                time.sleep(settings.REQUEST_DELAY_SECONDS)

            except Exception as e:
                logger.error(f"[Worker {worker_id+1}] ❌ Error on bid {bid_summary.get('reference_number')}: {str(e)}")
                result['errors'] += 1
                continue

        logger.info(f"[Worker {worker_id+1}] Completed: {result['scraped']} scraped, {result['errors']} errors")

    def _scrape_bid_details(self, page: Page, url: str) -> Dict:
        """
        Scrape full details from a bid notice page using the provided page.

        Args:
            page: Playwright Page instance to use
            url: URL of the bid notice detail page

        Returns:
            dict: Bid notice data
        """
        try:
            # Navigate to bid detail page
            full_url = url if url.startswith('http') else f"{settings.PHILGEPS_BASE_URL}{url}"
            page.goto(full_url, wait_until='domcontentloaded')

            # Wait for content to load
            time.sleep(2)

            # Get page HTML
            html = page.content()

            # Parse bid details
            parser = PhilGEPSParser(html)
            bid_data = parser.parse_bid_notice()

            # Add source URL
            bid_data['url'] = full_url

            # Scrape PDF document links
            bid_data['documents'] = self._scrape_document_links(page, bid_data.get('reference_number'))

            return bid_data

        except Exception as e:
            logger.error(f"Error scraping bid details from {url}: {str(e)}")
            return None

    def _scrape_document_links(self, page: Page, reference_number: str) -> List[Dict]:
        """
        Scrape PDF document links from the preview modal.

        Args:
            page: Playwright Page instance to use
            reference_number: Bid reference number

        Returns:
            list: List of document dictionaries
        """
        try:
            if not reference_number:
                return []

            # Try to find and click Preview link
            try:
                preview_link = page.locator('a[rel="facebox"]:has-text("Preview")')
                link_count = preview_link.count()

                if link_count == 0:
                    # Fallback: look for any facebox link
                    all_facebox = page.locator('a[rel="facebox"]')
                    facebox_count = all_facebox.count()

                    for i in range(facebox_count):
                        href_path = all_facebox.nth(i).get_attribute('href_path')
                        if href_path and 'tender_doc_view' in href_path:
                            preview_link = all_facebox.nth(i)
                            break

                if preview_link.count() > 0:
                    preview_link.first.click()
                    time.sleep(1)

                    # Parse document links from modal
                    html = page.content()
                    parser = PhilGEPSParser(html)
                    return parser.parse_document_links()

            except Exception as e:
                logger.debug(f"Could not open preview modal for {reference_number}: {str(e)}")

            return []

        except Exception as e:
            logger.error(f"Error scraping documents for {reference_number}: {str(e)}")
            return []

    def _split_work(self, items: List, num_chunks: int) -> List[List]:
        """
        Split work evenly among workers using round-robin distribution.

        Args:
            items: List of items to split
            num_chunks: Number of chunks to create

        Returns:
            List of lists, each containing items for one worker
        """
        chunks = [[] for _ in range(num_chunks)]
        for idx, item in enumerate(items):
            worker_id = idx % num_chunks
            chunks[worker_id].append(item)
        return chunks

    def _is_already_scraped(self, reference_number: str) -> bool:
        """Check if bid already exists in database."""
        return self.db.bid_exists(reference_number)

    def _apply_filters(self):
        """
        Apply filters if configured.

        Note: Filters are applied via URL parameters in _build_pagination_url()
        rather than through UI manipulation. This is simpler and more reliable
        for parallel scraping.
        """
        # Filters are handled via URL parameters, so this is a no-op
        pass

    def _get_all_bids_with_pagination(self) -> List[Dict]:
        """Get all bids with pagination (using main page)."""
        all_bids = []

        try:
            # Get first page
            logger.info("Getting bids from page 1...")
            bids = self._get_bid_list()
            all_bids.extend(bids)

            # Check for pagination
            total_pages = self._get_total_pages()

            if total_pages and total_pages > 1:
                logger.info(f"Found {total_pages} total pages, scraping all pages...")

                for page_num in range(2, total_pages + 1):
                    try:
                        logger.info(f"Getting bids from page {page_num} of {total_pages}...")
                        next_page_url = self._build_pagination_url(page_num)
                        self.browser_handler.navigate(next_page_url)
                        time.sleep(2)

                        page_bids = self._get_bid_list()
                        all_bids.extend(page_bids)
                    except Exception as e:
                        logger.error(f"Error scraping page {page_num}: {str(e)}")
                        continue

            return all_bids

        except Exception as e:
            logger.error(f"Error in pagination: {str(e)}")
            return all_bids

    def _get_bid_list(self) -> List[Dict]:
        """Extract bid list from current page."""
        try:
            html = self.browser_handler.get_html()
            soup = BeautifulSoup(html, 'lxml')

            bids = []
            rows = soup.select('tbody tr')

            for row in rows:
                try:
                    # Extract reference number and URL
                    ref_link = row.select_one('td:nth-of-type(1) a')
                    if not ref_link:
                        continue

                    reference_number = ref_link.get_text(strip=True)
                    url = ref_link.get('href', '')

                    # Extract title
                    title_cell = row.select_one('td:nth-of-type(2)')
                    title = title_cell.get_text(strip=True) if title_cell else ''

                    bids.append({
                        'reference_number': reference_number,
                        'url': url,
                        'title': title
                    })

                except Exception as e:
                    logger.debug(f"Error parsing row: {str(e)}")
                    continue

            return bids

        except Exception as e:
            logger.error(f"Error getting bid list: {str(e)}")
            return []

    def _get_total_pages(self) -> Optional[int]:
        """Extract total number of pages from pagination info."""
        try:
            html = self.browser_handler.get_html()
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
        """Build pagination URL with filters."""
        from urllib.parse import urlencode

        params = {
            'page': page_num,
            'direction': 'Tenders.tender_start_datetime+desc'
        }

        if settings.FILTER_PUBLISH_DATE_FROM:
            params['searchPublishDateFrom'] = settings.FILTER_PUBLISH_DATE_FROM
        if settings.FILTER_PUBLISH_DATE_TO:
            params['searchPublishDateTo'] = settings.FILTER_PUBLISH_DATE_TO
        if settings.FILTER_CLASSIFICATION:
            params['searchClassification'] = settings.FILTER_CLASSIFICATION
        if settings.FILTER_BUSINESS_CATEGORY:
            params['searchBussinessCategory'] = settings.FILTER_BUSINESS_CATEGORY

        return f"{settings.PHILGEPS_BID_LIST}?{urlencode(params)}"

    def _log_session(self, results: Dict):
        """Log scraping session to database."""
        try:
            log_data = {
                'start_time': results['start_time'],
                'end_time': results['end_time'],
                'duration_seconds': results['duration_seconds'],
                'total_scraped': results['total_scraped'],
                'new_records': results['new_records'],
                'errors': results['errors'],
                'success': results['success'],
                'notes': f"Parallel scraping with {self.num_workers} workers"
            }
            self.db.save_scraping_log(log_data)
        except Exception as e:
            logger.error(f"Error logging session: {str(e)}")

    def _cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.browser_handler:
                self.browser_handler.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    # Run parallel scraper
    scraper = ParallelPhilGEPSScraper(num_workers=3)
    results = scraper.run()

    if results['success']:
        print(f"\n✅ Scraping completed successfully!")
        print(f"   Duration: {results['duration_seconds']:.2f} seconds")
        print(f"   Total scraped: {results['total_scraped']}")
        print(f"   New records: {results['new_records']}")
        print(f"   Errors: {results['errors']}")
    else:
        print(f"\n❌ Scraping failed")
