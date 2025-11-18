"""
Run awarded contracts scraper.

This script runs the awarded contracts scraper to collect data about
contracts that have already been awarded.

Usage:
    python run_awarded_scraper.py              # Run with default 2 workers
    python run_awarded_scraper.py --workers 3  # Run with 3 workers
    python run_awarded_scraper.py --help       # Show help
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.awarded_contracts_scraper import AwardedContractsScraper
from utils.logger import logger
from config.settings import settings


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run PhilGEPS Awarded Contracts Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_awarded_scraper.py                    # Run with 2 workers (default)
  python run_awarded_scraper.py --workers 3        # Run with 3 workers
  python run_awarded_scraper.py --workers 1        # Run with 1 worker (slower but safer)

Features:
  - Scrapes awarded contracts from PhilGEPS public pages
  - No authentication required
  - Extracts ABC (Approved Budget) and Contract Amount (awarded price)
  - Identifies awardee (winner) and award details
  - Supports parallel processing with multiple workers
        """
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of concurrent workers (default: 2)'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (overrides .env setting)'
    )

    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run browser in visible mode (overrides .env setting)'
    )

    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    # Override headless mode if specified
    if args.headless:
        settings.HEADLESS_MODE = True
    elif args.visible:
        settings.HEADLESS_MODE = False

    logger.info("=" * 70)
    logger.info("PhilGEPS Awarded Contracts Scraper")
    logger.info("=" * 70)
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Headless: {settings.HEADLESS_MODE}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info("=" * 70)

    # Create and run scraper
    scraper = AwardedContractsScraper(num_workers=args.workers)
    results = await scraper.run()

    # Print summary
    print("\n" + "=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)

    if results['success']:
        print(f"✅ Status: SUCCESS")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        print(f"📊 Total Scraped: {results['total_scraped']}")
        print(f"🆕 New Records: {results['new_records']}")
        print(f"⏭️  Skipped: {results['skipped']}")
        print(f"❌ Errors: {results['errors']}")

        if results['total_scraped'] > 0:
            print(f"\n💡 Tip: View the data in your database or via the API")
            print(f"   Database location: {settings.DATABASE_URL}")

    else:
        print(f"❌ Status: FAILED")
        print(f"❌ Errors: {results['errors']}")
        print(f"\n💡 Check logs for details: logs/scraper.log")

    print("=" * 70)

    # Return exit code
    return 0 if results['success'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
