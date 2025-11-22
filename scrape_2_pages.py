"""
Quick test scraper - First 2 pages only.

This script scrapes just the first 2 pages of awarded contracts
for quick testing and validation.

Usage:
    python scrape_2_pages.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'bidintel-main' / 'backend'))

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from models.database import Database
from scraper.parser import PhilGEPSParser
from scraper.stealth import PlaywrightStealth, HumanBehavior
from utils.logger import logger


class TwoPageScraper:
    """Scrapes only the first 2 pages of awarded contracts."""

    PUBLIC_INDEX_URL = "https://philgeps.gov.ph/Indexes/viewMoreAward"

    def __init__(self):
        self.db = Database()
        self.stealth = PlaywrightStealth()

    async def run(self):
        """Run the scraper for 2 pages only."""
        print("\n" + "="*80)
        print("🚀 QUICK TEST SCRAPER - FIRST 2 PAGES ONLY")
        print("="*80)

        start_time = datetime.now()
        total_scraped = 0
        new_records = 0
        errors = 0

        async with async_playwright() as playwright:
            # Launch browser
            print("\n📱 Launching browser...")
            browser = await playwright.chromium.launch(
                headless=False,  # Visible mode for testing
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

                # Scrape 2 pages
                all_awards = []

                for page_num in range(1, 3):  # Pages 1 and 2
                    print(f"\n📄 Scraping Page {page_num}/2...")

                    if page_num > 1:
                        # Navigate to page 2
                        pagination_url = f"{self.PUBLIC_INDEX_URL}?page={page_num}"
                        await page.goto(pagination_url, wait_until='domcontentloaded')
                        await asyncio.sleep(2)

                    # Get awards from current page
                    html = await page.content()
                    awards = self._extract_awards_from_page(html)
                    print(f"   Found {len(awards)} awards on page {page_num}")
                    all_awards.extend(awards)

                print(f"\n📊 Total awards found: {len(all_awards)}")

                # Scrape details for each award
                print(f"\n🔍 Scraping award details...")

                for i, award_summary in enumerate(all_awards, 1):
                    try:
                        award_num = award_summary['award_notice_number']
                        award_url = award_summary['url']

                        # Check if already scraped
                        if self.db.awarded_contract_exists(award_num):
                            print(f"   [{i}/{len(all_awards)}] ⏭️  Skip: {award_num} (already exists)")
                            continue

                        print(f"   [{i}/{len(all_awards)}] 🔍 Scraping: {award_num}")

                        # Navigate to detail page
                        await page.goto(award_url, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(1.5)

                        # Parse the page
                        detail_html = await page.content()
                        parser = PhilGEPSParser(detail_html)
                        award_data = parser.parse_awarded_contract()

                        # Save to database
                        self.db.save_awarded_contract(award_data)
                        new_records += 1
                        total_scraped += 1

                        # Show preview
                        awardee = award_data.get('awardee_name', 'N/A')
                        agency = award_data.get('procuring_entity', 'N/A')
                        contract_amt = award_data.get('contract_amount')

                        print(f"       ✅ Winner: {awardee[:50]}")
                        print(f"       🏛️  Agency: {agency[:50]}")
                        if contract_amt:
                            print(f"       💰 Amount: PHP {contract_amt:,.2f}")

                    except Exception as e:
                        errors += 1
                        print(f"       ❌ Error: {str(e)}")
                        logger.error(f"Error scraping {award_summary.get('award_notice_number')}: {str(e)}")
                        continue

            finally:
                await browser.close()

        # Print summary
        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*80)
        print("✅ SCRAPING COMPLETE")
        print("="*80)
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📊 Total Awards Found: {len(all_awards)}")
        print(f"🆕 New Records Saved: {new_records}")
        print(f"⏭️  Skipped (duplicates): {total_scraped - new_records}")
        print(f"❌ Errors: {errors}")
        print("="*80)

        if new_records > 0:
            print("\n💡 Next steps:")
            print("   1. View data: python view_data.py")
            print("   2. Or query database directly")
            print(f"   3. Database: philgeps_data.db")

        return {
            'success': True,
            'total_scraped': total_scraped,
            'new_records': new_records,
            'errors': errors
        }

    def _extract_awards_from_page(self, html: str):
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
                award_url = "https://philgeps.gov.ph" + award_link.get('href', '')

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


async def main():
    """Main entry point."""
    scraper = TwoPageScraper()
    await scraper.run()


if __name__ == "__main__":
    print("\n🧪 Quick Test Scraper")
    print("This will scrape ONLY the first 2 pages (approx 50 awards)")
    print("Perfect for testing!\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
