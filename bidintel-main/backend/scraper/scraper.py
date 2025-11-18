"""Main scraper orchestrator for PhilGEPS."""

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


class PhilGEPSScraper:
    """Main scraper class that orchestrates the scraping workflow."""

    def __init__(self):
        """Initialize scraper."""
        self.browser_handler = BrowserHandler()
        self.db = Database()
        self.page = None
        self.auth = None

    def run(self) -> Dict:
        """
        Run the complete scraping workflow.

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
            'start_time': start_time
        }

        try:
            logger.info("=" * 60)
            logger.info("Starting PhilGEPS scraping session")
            logger.info("=" * 60)

            # Step 1: Initialize browser
            self.page = self.browser_handler.init_browser()

            # Step 2: Authenticate
            self.auth = PhilGEPSAuth(self.page)
            if not self.auth.login():
                raise Exception("Authentication failed")

            # Step 3: Navigate to bid notices list page
            # Using proper URL from BID_WORKFLOW.md
            self.browser_handler.navigate(settings.PHILGEPS_BID_LIST)

            # Step 3.5: Apply filters if configured
            self._apply_filters()

            # Step 4: Get list of bid notices from all pages
            bid_list = self._get_all_bids_with_pagination()
            logger.info(f"Found {len(bid_list)} total bid notices across all pages")

            # Step 5: Process each bid notice
            for bid_summary in bid_list:
                try:
                    # Check if already scraped
                    if self._is_already_scraped(bid_summary['reference_number']):
                        logger.info(f"⏭️  Skipping already scraped bid: {bid_summary['reference_number']} - {bid_summary.get('title', 'N/A')[:60]}")
                        results['skipped'] += 1
                        continue

                    # Scrape full bid details
                    bid_data = self._scrape_bid_details(bid_summary['url'])

                    if bid_data:
                        # Save to database
                        self.db.save_bid_notice(bid_data)
                        results['new_records'] += 1
                        results['total_scraped'] += 1
                        logger.info(f"✅ Saved bid: {bid_data['reference_number']}")

                    # Rate limiting - wait between requests
                    time.sleep(settings.REQUEST_DELAY_SECONDS)

                except Exception as e:
                    logger.error(f"❌ Error processing bid {bid_summary.get('reference_number')}: {str(e)}")
                    results['errors'] += 1
                    continue

            results['success'] = True

        except Exception as e:
            logger.error(f"Scraping session failed: {str(e)}")
            results['success'] = False

        finally:
            # Cleanup
            self._cleanup()

            # Log results
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            results['end_time'] = end_time
            results['duration_seconds'] = duration

            self._log_session(results)

            logger.info("=" * 60)
            logger.info(f"Scraping session completed in {duration:.2f} seconds")
            logger.info(f"Total scraped: {results['total_scraped']}, New: {results['new_records']}, Skipped: {results['skipped']}, Errors: {results['errors']}")
            logger.info("=" * 60)

        return results

    def _get_all_bids_with_pagination(self) -> List[Dict]:
        """
        Get all bid notices from all pages using pagination.

        The PhilGEPS listing shows 20 bids per page with pagination.
        This method loops through all pages and collects all bids.

        Returns:
            list: Combined list of all bid notices from all pages
        """
        all_bids = []
        current_page = 1

        try:
            # Get first page
            logger.info("Getting bids from page 1...")
            bids = self._get_bid_list()
            all_bids.extend(bids)

            # Check for pagination info
            total_pages = self._get_total_pages()

            if total_pages and total_pages > 1:
                logger.info(f"Found {total_pages} total pages, scraping all pages...")

                # Loop through remaining pages
                for page_num in range(2, total_pages + 1):
                    try:
                        logger.info(f"Getting bids from page {page_num} of {total_pages}...")

                        # Build pagination URL with filter parameters
                        next_page_url = self._build_pagination_url(page_num)
                        self.browser_handler.navigate(next_page_url)

                        # Wait for page to load
                        time.sleep(2)

                        # Get bids from this page
                        page_bids = self._get_bid_list()
                        all_bids.extend(page_bids)

                        logger.debug(f"Page {page_num}: Found {len(page_bids)} bids, total so far: {len(all_bids)}")

                    except Exception as e:
                        logger.error(f"Error scraping page {page_num}: {str(e)}")
                        # Continue with next page even if one fails
                        continue

                logger.info(f"Pagination complete: Collected {len(all_bids)} bids from {total_pages} pages")
            else:
                logger.info(f"Single page result: {len(all_bids)} bids")

            return all_bids

        except Exception as e:
            logger.error(f"Error in pagination: {str(e)}")
            # Return what we have so far
            return all_bids

    def _build_pagination_url(self, page_num: int) -> str:
        """
        Build pagination URL with filter parameters preserved.

        Args:
            page_num: Page number to navigate to

        Returns:
            str: Complete URL with page number and filter parameters
        """
        from urllib.parse import urlencode

        # Base parameters
        params = {
            'page': page_num,
            'direction': 'Tenders.tender_start_datetime+desc'
        }

        # Add filter parameters if configured
        if settings.FILTER_PUBLISH_DATE_FROM:
            params['searchPublishDateFrom'] = settings.FILTER_PUBLISH_DATE_FROM

        if settings.FILTER_PUBLISH_DATE_TO:
            params['searchPublishDateTo'] = settings.FILTER_PUBLISH_DATE_TO

        if settings.FILTER_CLASSIFICATION:
            params['searchClassification'] = settings.FILTER_CLASSIFICATION

        if settings.FILTER_BUSINESS_CATEGORY:
            params['searchBussinessCategory'] = settings.FILTER_BUSINESS_CATEGORY

        # Build URL
        url = f"{settings.PHILGEPS_BID_LIST}?{urlencode(params)}"
        logger.debug(f"Built pagination URL: {url}")

        return url

    def _get_total_pages(self) -> Optional[int]:
        """
        Extract total number of pages from pagination info.

        Looks for text like "Page 1 of 13, showing 20 record(s) out of 252 total"

        Returns:
            int: Total number of pages, or None if not found
        """
        try:
            html = self.browser_handler.get_html()
            soup = BeautifulSoup(html, 'lxml')

            # Find pagination text
            paginator = soup.find('div', class_='paginator')
            if paginator:
                # Look for the <p> tag with page info
                page_info = paginator.find('p')
                if page_info:
                    # Extract from text like "Page 1 of 13, showing 20 record(s) out of 252 total"
                    text = page_info.get_text(strip=True)
                    logger.debug(f"Pagination info: {text}")

                    # Extract total pages using regex
                    match = re.search(r'Page\s+\d+\s+of\s+(\d+)', text)
                    if match:
                        total_pages = int(match.group(1))
                        logger.info(f"Total pages: {total_pages}")
                        return total_pages

            logger.debug("No pagination found, assuming single page")
            return None

        except Exception as e:
            logger.warning(f"Error getting total pages: {str(e)}")
            return None

    def _apply_filters(self):
        """
        Apply filters to the bid list page if configured.

        Fills in date range, classification, and business category filters and triggers search.
        """
        try:
            # Check if any filters are configured
            date_from = settings.FILTER_PUBLISH_DATE_FROM
            date_to = settings.FILTER_PUBLISH_DATE_TO
            classification = settings.FILTER_CLASSIFICATION
            business_category = settings.FILTER_BUSINESS_CATEGORY

            if not any([date_from, date_to, classification, business_category]):
                logger.debug("No filters configured, skipping filtering")
                return

            logger.info("Applying filters...")
            if date_from or date_to:
                logger.info(f"  Date: {date_from} to {date_to}")
            if classification:
                logger.info(f"  Classification: {classification}")
            if business_category:
                logger.info(f"  Business Category: {business_category}")

            # Wait for the filter inputs to be available
            time.sleep(2)

            # Fill in "Publish Date From" if configured
            if date_from:
                try:
                    # Use JavaScript to set the value since the field is readonly (jQuery datepicker)
                    self.browser_handler.page.evaluate(f"""
                        (function() {{
                            var input = document.getElementById('searchPublishDateFrom');
                            if (input) {{
                                input.value = '{date_from}';
                                // Trigger change event in case there are listeners
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        }})();
                    """)
                    logger.debug(f"Set Publish Date From: {date_from}")
                except Exception as e:
                    logger.warning(f"Could not set Publish Date From: {e}")

            # Fill in "Publish Date To" if configured
            if date_to:
                try:
                    # Use JavaScript to set the value since the field is readonly (jQuery datepicker)
                    self.browser_handler.page.evaluate(f"""
                        (function() {{
                            var input = document.getElementById('searchPublishDateTo');
                            if (input) {{
                                input.value = '{date_to}';
                                // Trigger change event in case there are listeners
                                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                        }})();
                    """)
                    logger.debug(f"Set Publish Date To: {date_to}")
                except Exception as e:
                    logger.warning(f"Could not set Publish Date To: {e}")

            # Select Classification if configured
            if classification:
                try:
                    classification_select = self.browser_handler.page.locator('#searchClassification')
                    classification_select.select_option(value=classification)
                    logger.debug(f"Set Classification: {classification}")
                except Exception as e:
                    logger.warning(f"Could not set Classification: {e}")

            # Select Business Category if configured
            if business_category:
                try:
                    business_category_select = self.browser_handler.page.locator('#searchBussinessCategory')
                    business_category_select.select_option(value=business_category)
                    logger.debug(f"Set Business Category: {business_category}")
                except Exception as e:
                    logger.warning(f"Could not set Business Category: {e}")

            # Find and click the search/filter button
            try:
                # Look for common search button selectors
                search_button_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Search")',
                    'button:has-text("Filter")',
                    '.btn-search',
                    '#searchButton'
                ]

                button_clicked = False
                for selector in search_button_selectors:
                    try:
                        button = self.browser_handler.page.locator(selector).first
                        if button.count() > 0:
                            button.click()
                            logger.debug(f"Clicked search button: {selector}")
                            button_clicked = True
                            break
                    except:
                        continue

                if not button_clicked:
                    logger.warning("Could not find search button, filters may not be applied")
                    # Try pressing Enter on the date field as fallback
                    try:
                        self.browser_handler.page.locator('#searchPublishDateTo').press('Enter')
                        logger.debug("Pressed Enter on date field as fallback")
                    except:
                        pass

                # Wait for results to load after applying filters
                time.sleep(3)
                logger.info("Filters applied successfully")

            except Exception as e:
                logger.warning(f"Error clicking search button: {e}")

        except Exception as e:
            logger.error(f"Error applying filters: {str(e)}")
            # Don't fail the entire scrape if filtering fails
            logger.warning("Continuing without filters...")

    @retry_on_failure(max_retries=3)
    def _get_bid_list(self) -> List[Dict]:
        """
        Get list of bid notices from listing page.

        Returns:
            list: List of bid notice summaries
        """
        try:
            # Wait for table to load - PhilGEPS uses tbody with tr elements
            # Don't rely on specific table classes as they may change
            logger.info("Waiting for bid list table to load...")

            try:
                # Try to wait for tbody with rows
                self.browser_handler.wait_for_element('tbody tr', timeout=15000)
            except Exception as wait_error:
                logger.warning(f"Could not find tbody tr, trying alternative selectors: {wait_error}")
                # Try alternative - wait for any table
                try:
                    self.browser_handler.wait_for_element('table', timeout=10000)
                    logger.info("Found table element")
                except Exception as e2:
                    logger.error(f"No table found on page: {e2}")
                    # Save page HTML for debugging
                    html = self.browser_handler.get_html()
                    debug_file = 'debug_bid_list_page.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.error(f"Saved page HTML to {debug_file} for debugging")
                    return []

            # Get page HTML
            html = self.browser_handler.get_html()

            # Parse bid list
            parser = PhilGEPSParser(html)
            bids = parser.parse_bid_list_page()

            # If no bids found, save HTML for debugging
            if len(bids) == 0:
                logger.warning("Parser returned 0 bids, saving page HTML for debugging")
                debug_file = 'debug_bid_list_page_no_results.html'
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.warning(f"Saved page HTML to {debug_file}")

            return bids

        except Exception as e:
            logger.error(f"Error getting bid list: {str(e)}")
            return []

    @retry_on_failure(max_retries=3)
    def _scrape_bid_details(self, url: str) -> Dict:
        """
        Scrape full details from a bid notice page.

        Args:
            url: URL of the bid notice detail page

        Returns:
            dict: Bid notice data
        """
        try:
            # Navigate to bid detail page
            full_url = url if url.startswith('http') else f"{settings.PHILGEPS_BASE_URL}{url}"
            self.browser_handler.navigate(full_url)

            # Wait for content to load
            time.sleep(2)

            # Get page HTML
            html = self.browser_handler.get_html()

            # Parse bid details
            parser = PhilGEPSParser(html)
            bid_data = parser.parse_bid_notice()

            # Add source URL
            bid_data['url'] = full_url

            # Scrape PDF document links from preview page
            bid_data['documents'] = self._scrape_document_links(bid_data.get('reference_number'))

            return bid_data

        except Exception as e:
            logger.error(f"Error scraping bid details from {url}: {str(e)}")
            return None

    def _scrape_document_links(self, reference_number: str) -> List[Dict]:
        """
        Scrape PDF document links from the preview modal.

        The Preview link opens a facebox modal/popup that contains the PDF links.
        We need to click the Preview link and wait for the modal to load.

        Args:
            reference_number: Bid reference number

        Returns:
            list: List of document dictionaries
        """
        try:
            if not reference_number:
                logger.warning("No reference number provided, skipping document scraping")
                return []

            # The Preview link is on the current bid detail page
            # We should already be on /tenders/viewBidNotice/{reference_number}
            # Find and click the Preview link (rel="facebox")
            logger.debug(f"Looking for Preview link for bid {reference_number}")

            try:
                # Find the Preview link - it should have:
                # 1. rel="facebox"
                # 2. Text content "Preview"
                # 3. href_path attribute pointing to tender_doc_view

                # Strategy 1: Look for link with text "Preview" and rel="facebox"
                preview_link = self.browser_handler.page.locator('a[rel="facebox"]:has-text("Preview")')

                link_count = preview_link.count()
                logger.debug(f"Found {link_count} Preview link(s) with text 'Preview'")

                # Strategy 2: If not found, look for any facebox link with tender_doc_view in href_path
                if link_count == 0:
                    all_facebox = self.browser_handler.page.locator('a[rel="facebox"]')
                    facebox_count = all_facebox.count()
                    logger.debug(f"Found {facebox_count} total facebox links, checking for tender_doc_view...")

                    # Find the one with tender_doc_view in href_path
                    for i in range(facebox_count):
                        try:
                            href_path = all_facebox.nth(i).get_attribute('href_path')
                            link_text = all_facebox.nth(i).text_content()
                            logger.debug(f"Facebox link {i}: text='{link_text}', href_path='{href_path}'")

                            if href_path and 'tender_doc_view' in href_path:
                                preview_link = all_facebox.nth(i)
                                link_count = 1
                                logger.debug(f"Found tender_doc_view link at index {i}")
                                break
                        except:
                            continue

                if link_count == 0:
                    logger.warning("No Preview link found on the page")
                    return []

                # Get link details for debugging
                try:
                    link_href = preview_link.get_attribute('href_path')
                    link_text = preview_link.text_content()
                    logger.debug(f"Clicking Preview link: text='{link_text}', href_path='{link_href}'")
                except Exception as e:
                    logger.debug(f"Could not get link details: {e}")

                # Click the Preview link
                try:
                    preview_link.click(timeout=5000)
                    logger.debug("Preview link clicked successfully")
                except Exception as e:
                    logger.warning(f"Standard click failed: {e}, trying JavaScript click...")
                    # Fallback to JavaScript click on the specific element with tender_doc_view
                    self.browser_handler.page.evaluate(
                        '() => { const links = document.querySelectorAll(\'a[rel="facebox"]\'); '
                        'for (let link of links) { '
                        '  if (link.getAttribute("href_path") && link.getAttribute("href_path").includes("tender_doc_view")) { '
                        '    link.click(); break; '
                        '  }'
                        '}}'
                    )
                    logger.debug("JavaScript click executed on tender_doc_view link")

                # Wait a moment for facebox to initialize
                time.sleep(2)

                # Try multiple selectors for the modal
                modal_selectors = [
                    '#facebox',
                    '#facebox_overlay',
                    '.facebox',
                    'div[id*="facebox"]',
                    'div[class*="facebox"]',
                    '#loading',  # Facebox loading indicator
                    '.popup',
                    '.modal'
                ]

                modal_found = False
                for selector in modal_selectors:
                    try:
                        element = self.browser_handler.page.locator(selector)
                        if element.count() > 0:
                            logger.debug(f"Found modal element: {selector}")
                            modal_found = True
                            break
                    except:
                        continue

                if not modal_found:
                    logger.warning("No modal elements found after click, checking for direct content load...")
                    # Maybe the content loaded directly without modal
                    time.sleep(3)
                else:
                    # Wait for modal content to load
                    logger.debug("Waiting for modal content to load...")
                    time.sleep(5)  # Longer wait for AJAX

                # Try to find PDF links regardless of modal
                try:
                    # Check if any PDF links appeared
                    pdf_check = self.browser_handler.page.locator('a[href*=".pdf"]')
                    pdf_count = pdf_check.count()
                    logger.debug(f"Found {pdf_count} PDF link(s) on page")
                except Exception as e:
                    logger.debug(f"Error checking for PDF links: {e}")

                # Get the HTML of the entire page (including any modal)
                html = self.browser_handler.get_html()

                # Save HTML for debugging if no documents found
                if 'portal_documents' not in html and '.pdf' not in html:
                    debug_file = f'debug_modal_bid_{reference_number}.html'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    logger.warning(f"No PDF content detected, saved HTML to {debug_file}")

                # Parse document links from the HTML
                parser = PhilGEPSParser(html)
                documents = parser.parse_document_links()

                # Close the modal by pressing Escape or clicking close button
                try:
                    self.browser_handler.page.keyboard.press('Escape')
                    logger.debug("Pressed Escape to close modal")
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"Could not close modal with Escape: {e}")

                # Try clicking close button if exists
                try:
                    close_btn = self.browser_handler.page.locator('#facebox .close, .facebox .close, a.close')
                    if close_btn.count() > 0:
                        close_btn.first.click(timeout=2000)
                        logger.debug("Clicked close button")
                except:
                    pass

                logger.info(f"Found {len(documents)} document(s) for bid {reference_number}")
                return documents

            except Exception as e:
                logger.error(f"Error clicking Preview link or loading modal: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return []

        except Exception as e:
            logger.error(f"Error scraping document links for bid {reference_number}: {str(e)}")
            return []

    def _is_already_scraped(self, reference_number: str) -> bool:
        """
        Check if bid notice has already been scraped.

        Args:
            reference_number: Bid reference number

        Returns:
            bool: True if already scraped
        """
        return self.db.bid_exists(reference_number)

    def _log_session(self, results: Dict) -> None:
        """
        Log scraping session to database.

        Args:
            results: Session results
        """
        try:
            log_entry = ScrapingLog(
                start_time=results['start_time'],
                end_time=results['end_time'],
                duration_seconds=results['duration_seconds'],
                total_scraped=results['total_scraped'],
                new_records=results['new_records'],
                errors=results['errors'],
                success=results['success']
            )
            self.db.save_scraping_log(log_entry)

        except Exception as e:
            logger.error(f"Error logging session: {str(e)}")

    def _cleanup(self) -> None:
        """Cleanup resources."""
        try:
            if self.auth:
                self.auth.logout()
            if self.browser_handler:
                self.browser_handler.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


# Convenience function for scheduled execution
def scrape_philgeps() -> Dict:
    """
    Run PhilGEPS scraper.

    Returns:
        dict: Scraping results
    """
    scraper = PhilGEPSScraper()
    return scraper.run()
