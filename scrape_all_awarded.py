"""
Full Awarded Contracts Scraper - All Pages.

This script scrapes ALL pages of awarded contracts from PhilGEPS.
Includes progress tracking, error handling, and resume capability.

Usage:
    python scrape_all_awarded.py                    # Scrape all pages (headless)
    python scrape_all_awarded.py --visible          # Scrape with visible browser
    python scrape_all_awarded.py --max-pages 10     # Limit to first 10 pages
    python scrape_all_awarded.py --start-page 5     # Resume from page 5
"""

import asyncio
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'bidintel-main' / 'backend'))

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from models.database import Database
from scraper.parser import PhilGEPSParser
from scraper.stealth import PlaywrightStealth, HumanBehavior
from utils.logger import logger


class AwardedContractsScraper:
    """Full scraper for all awarded contracts pages."""

    PUBLIC_INDEX_URL = "https://philgeps.gov.ph/Indexes/viewMoreAward"

    def __init__(self, headless: bool = True, max_pages: Optional[int] = None, start_page: int = 1):
        self.db = Database()
        self.stealth = PlaywrightStealth()
        self.headless = headless
        self.max_pages = max_pages
        self.start_page = start_page

        # Statistics
        self.total_awards_found = 0
        self.total_scraped = 0
        self.new_records = 0
        self.skipped = 0
        self.errors = 0
        self.failed_awards = []

    async def run(self):
        """Run the full scraper."""
        print("\n" + "="*80)
        print("🚀 FULL AWARDED CONTRACTS SCRAPER")
        print("="*80)

        if self.max_pages:
            print(f"📄 Max Pages: {self.max_pages}")
        else:
            print(f"📄 Mode: SCRAPE ALL PAGES")

        if self.start_page > 1:
            print(f"▶️  Starting from page: {self.start_page}")

        print(f"👁️  Browser Mode: {'Visible' if not self.headless else 'Headless'}")
        print("="*80)

        start_time = datetime.now()

        async with async_playwright() as playwright:
            # Launch browser
            print("\n📱 Launching browser...")
            browser = await playwright.chromium.launch(
                headless=self.headless,
                args=self.stealth.get_launch_args()
            )

            # Create context with stealth options
            context = await browser.new_context(
                **self.stealth.get_context_options()
            )

            # Create page
            page = await context.new_page()

            # Apply stealth to page
            await self.stealth.apply_stealth(page)

            try:
                # Navigate to awards page
                print(f"🌐 Navigating to: {self.PUBLIC_INDEX_URL}")
                await page.goto(self.PUBLIC_INDEX_URL, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)

                # Detect total pages
                total_pages = await self._detect_total_pages(page)
                print(f"\n📊 Total Pages Detected: {total_pages}")

                # Determine which pages to scrape
                end_page = min(total_pages, self.max_pages) if self.max_pages else total_pages
                pages_to_scrape = range(self.start_page, end_page + 1)

                print(f"📋 Will scrape pages {self.start_page} to {end_page}")
                print("="*80)

                # Scrape all pages
                all_awards = []

                for page_num in pages_to_scrape:
                    try:
                        print(f"\n{'='*80}")
                        print(f"📄 PAGE {page_num}/{end_page}")
                        print(f"{'='*80}")

                        # Navigate to page
                        if page_num > 1:
                            pagination_url = f"{self.PUBLIC_INDEX_URL}?page={page_num}"
                            await page.goto(pagination_url, wait_until='domcontentloaded', timeout=30000)
                            await asyncio.sleep(2)

                        # Extract awards from page
                        html = await page.content()
                        awards = self._extract_awards_from_page(html)

                        print(f"   Found {len(awards)} awards on this page")
                        all_awards.extend(awards)
                        self.total_awards_found += len(awards)

                        # Show running total
                        print(f"   📊 Running Total: {self.total_awards_found} awards found")

                    except Exception as e:
                        print(f"   ❌ Error on page {page_num}: {str(e)}")
                        logger.error(f"Error scraping page {page_num}: {str(e)}")
                        continue

                print(f"\n{'='*80}")
                print(f"📊 AWARDS EXTRACTION COMPLETE")
                print(f"{'='*80}")
                print(f"Total awards found across all pages: {len(all_awards)}")
                print(f"Now scraping individual award details...")
                print(f"{'='*80}")

                # Scrape details for each award
                for i, award_summary in enumerate(all_awards, 1):
                    try:
                        award_num = award_summary['award_notice_number']
                        award_url = award_summary['url']

                        # Check if already scraped
                        if self.db.awarded_contract_exists(award_num):
                            self.skipped += 1
                            if i % 10 == 0 or i == 1:  # Show progress every 10 items
                                print(f"   [{i}/{len(all_awards)}] ⏭️  Skip: {award_num} (exists)")
                            continue

                        # Progress indicator
                        print(f"\n{'─'*80}")
                        print(f"   [{i}/{len(all_awards)}] 🔍 Scraping: {award_num}")

                        # Calculate and show progress
                        progress_pct = (i / len(all_awards)) * 100
                        print(f"   Progress: {progress_pct:.1f}% | New: {self.new_records} | Skipped: {self.skipped} | Errors: {self.errors}")

                        # Navigate to detail page with retries
                        retry_count = 0
                        max_retries = 3
                        success = False

                        while retry_count < max_retries and not success:
                            try:
                                await page.goto(award_url, wait_until='domcontentloaded', timeout=30000)
                                await asyncio.sleep(1.5)
                                success = True
                            except Exception as nav_error:
                                retry_count += 1
                                if retry_count < max_retries:
                                    print(f"       ⚠️  Navigation failed, retry {retry_count}/{max_retries}...")
                                    await asyncio.sleep(2)
                                else:
                                    raise nav_error

                        # Parse the page
                        detail_html = await page.content()
                        parser = PhilGEPSParser(detail_html)
                        award_data = parser.parse_awarded_contract()

                        # Save to database
                        self.db.save_awarded_contract(award_data)
                        self.new_records += 1
                        self.total_scraped += 1

                        # Show preview
                        awardee = award_data.get('awardee_name', 'N/A')
                        agency = award_data.get('procuring_entity', 'N/A')
                        contract_amt = award_data.get('contract_amount')

                        print(f"       ✅ Winner: {awardee[:60]}")
                        print(f"       🏛️  Agency: {agency[:60]}")
                        if contract_amt:
                            print(f"       💰 Amount: PHP {contract_amt:,.2f}")

                    except Exception as e:
                        self.errors += 1
                        self.failed_awards.append({
                            'award_number': award_summary.get('award_notice_number'),
                            'error': str(e)
                        })
                        print(f"       ❌ Error: {str(e)}")
                        logger.error(f"Error scraping {award_summary.get('award_notice_number')}: {str(e)}")
                        continue

            finally:
                await browser.close()

        # Print final summary
        self._print_summary(start_time)

        return {
            'success': True,
            'total_awards_found': self.total_awards_found,
            'total_scraped': self.total_scraped,
            'new_records': self.new_records,
            'skipped': self.skipped,
            'errors': self.errors,
            'failed_awards': self.failed_awards
        }

    async def _detect_total_pages(self, page) -> int:
        """Detect total number of pages from pagination."""
        try:
            html = await page.content()
            soup = BeautifulSoup(html, 'lxml')

            # Look for pagination links
            # PhilGEPS uses pagination like: 1 2 3 ... 67
            pagination_links = soup.select('.pagination a, .pager a, a[href*="page="]')

            max_page = 1
            for link in pagination_links:
                text = link.get_text(strip=True)
                # Try to extract page number
                if text.isdigit():
                    page_num = int(text)
                    max_page = max(max_page, page_num)

                # Also check href for page=X
                href = link.get('href', '')
                if 'page=' in href:
                    try:
                        page_param = href.split('page=')[1].split('&')[0]
                        if page_param.isdigit():
                            max_page = max(max_page, int(page_param))
                    except:
                        pass

            # If we couldn't detect, default to 67 (known from context)
            if max_page == 1:
                logger.warning("Could not detect total pages, defaulting to 67")
                return 67

            return max_page

        except Exception as e:
            logger.error(f"Error detecting total pages: {str(e)}")
            return 67  # Default fallback

    def _extract_awards_from_page(self, html: str) -> List[Dict]:
        """Extract award list from page HTML."""
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
                href = award_link.get('href', '')

                # Handle both relative and absolute URLs
                if href.startswith('http'):
                    award_url = href
                elif href.startswith('/'):
                    award_url = "https://philgeps.gov.ph" + href
                else:
                    award_url = "https://philgeps.gov.ph/" + href

                # Extract title
                title_cell = row.select_one('td:nth-of-type(2)')
                title = title_cell.get_text(strip=True) if title_cell else None

                awards.append({
                    'award_notice_number': award_notice_number,
                    'url': award_url,
                    'title': title
                })

            except Exception as e:
                logger.error(f"Error parsing award row: {str(e)}")
                continue

        return awards

    def _print_summary(self, start_time: datetime):
        """Print final scraping summary."""
        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETE")
        print("="*80)
        print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📊 Total Awards Found: {self.total_awards_found}")
        print(f"🆕 New Records Saved: {self.new_records}")
        print(f"⏭️  Skipped (already in DB): {self.skipped}")
        print(f"❌ Errors: {self.errors}")

        if self.errors > 0 and self.failed_awards:
            print(f"\n⚠️  Failed Awards ({len(self.failed_awards)}):")
            for failed in self.failed_awards[:10]:  # Show first 10
                print(f"   • {failed['award_number']}: {failed['error'][:60]}")
            if len(self.failed_awards) > 10:
                print(f"   ... and {len(self.failed_awards) - 10} more")

        print("="*80)

        if self.new_records > 0:
            print("\n💡 Next steps:")
            print("   1. View data: python view_data.py")
            print("   2. Start API: cd bidintel-main/backend && python backend_api.py")
            print("   3. Start frontend: cd bidintel-main/frontend && npm run dev")
            print(f"   4. Database: philgeps_data.db ({self.new_records} new records)")
            print()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Scrape all awarded contracts from PhilGEPS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scrape_all_awarded.py                    # Scrape all pages (headless)
  python scrape_all_awarded.py --visible          # Scrape with visible browser
  python scrape_all_awarded.py --max-pages 10     # Limit to first 10 pages
  python scrape_all_awarded.py --start-page 5     # Resume from page 5
  python scrape_all_awarded.py --visible --max-pages 5  # Visible, first 5 pages
        """
    )

    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=None,
        help='Maximum number of pages to scrape (default: all)'
    )

    parser.add_argument(
        '--start-page',
        type=int,
        default=1,
        help='Page number to start from (default: 1)'
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    scraper = AwardedContractsScraper(
        headless=not args.visible,
        max_pages=args.max_pages,
        start_page=args.start_page
    )

    await scraper.run()


if __name__ == "__main__":
    print("\n🌐 PhilGEPS Awarded Contracts - Full Scraper")
    print("This will scrape ALL pages of awarded contracts")
    print("Press Ctrl+C to cancel\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
        print("💡 You can resume later with --start-page option")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
