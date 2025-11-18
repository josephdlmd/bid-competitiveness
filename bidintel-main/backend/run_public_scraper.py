#!/usr/bin/env python3
"""
CLI entry point for public PhilGEPS scraper (no authentication required).

This scraper uses public URLs that don't require login:
- Index: https://philgeps.gov.ph/Indexes/index
- Detail: https://philgeps.gov.ph/Indexes/viewLiveTenderDetails/{bid_id}

Usage:
    python run_public_scraper.py --workers 2
    python run_public_scraper.py --workers 3
    python run_public_scraper.py  # defaults to 2 workers
"""

import argparse
import sys
import asyncio
from scraper.public_scraper import PublicPhilGEPSScraper
from utils.logger import logger


async def async_main(args):
    """Async main function."""
    scraper = PublicPhilGEPSScraper(num_workers=args.workers)
    results = await scraper.run()

    print(f"\n{'='*60}")
    if results['success']:
        print("✅ PUBLIC SCRAPING COMPLETED SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"  Method:       Public URLs (no authentication)")
        print(f"  Duration:     {results['duration_seconds']:.2f} seconds ({results['duration_seconds']/60:.2f} minutes)")
        print(f"  Workers:      {results['workers']}")
        print(f"  Total:        {results['total_scraped']} bids scraped")
        print(f"  New records:  {results['new_records']}")
        print(f"  Skipped:      {results['skipped']} (already in database)")
        print(f"  Errors:       {results['errors']}")

        # Calculate estimated time saved
        if results['workers'] > 1 and results['total_scraped'] > 0:
            sequential_time = results['duration_seconds'] * results['workers']
            time_saved = sequential_time - results['duration_seconds']
            speedup = sequential_time / results['duration_seconds'] if results['duration_seconds'] > 0 else 1
            print(f"\n  Speedup:      {speedup:.1f}× faster than sequential")
            print(f"  Time saved:   ~{time_saved/60:.1f} minutes")
    else:
        print("❌ PUBLIC SCRAPING FAILED")
        print(f"  Check logs for details")

    print(f"{'='*60}\n")

    return 0 if results['success'] else 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run public PhilGEPS scraper (no authentication required)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of concurrent workers (browser tabs) to use. Default: 2'
    )

    args = parser.parse_args()

    # Validate workers
    if args.workers < 1:
        print("Error: Number of workers must be at least 1")
        sys.exit(1)
    if args.workers > 10:
        print("Warning: Using more than 10 workers may trigger bot detection")
        print("Recommended: 2-5 workers for optimal balance")

    print(f"\n{'='*60}")
    print(f"  Public PhilGEPS Scraper (No Authentication)")
    print(f"  Workers: {args.workers} (concurrent)")
    print(f"  Method: Async/Await + Public URLs")
    print(f"  Stealth: Full protection enabled")
    print(f"{'='*60}\n")

    try:
        # Run async main
        exit_code = asyncio.run(async_main(args))
        return exit_code

    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
