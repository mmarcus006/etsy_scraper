"""
Main execution script for Etsy template scraper.
Provides command-line interface and orchestrates the scraping process.
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.etsy_template_scraper import EtsyTemplateScraper
from utils.logger import setup_logger
from config.settings import DATA_DIR

logger = setup_logger(__name__, log_file="etsy_scraper.log")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape Etsy template category pages and extract product links",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape first 5 pages
  python scraper_main.py --max-pages 5
  
  # Resume from page 10
  python scraper_main.py --start-page 10
  
  # Scrape all pages with custom output
  python scraper_main.py --csv-path my_products.csv
  
  # Clear existing data and start fresh
  python scraper_main.py --clear-data --max-pages 10
        """
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Maximum number of pages to scrape (default: all pages)"
    )
    
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Page number to start from (default: 1 or resume from last)"
    )
    
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Custom path for CSV output file"
    )
    
    parser.add_argument(
        "--proxy",
        type=str,
        help="Proxy URL (e.g., http://user:pass@host:port)"
    )
    
    parser.add_argument(
        "--clear-data",
        action="store_true",
        help="Clear existing data before starting"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test configuration without actually scraping"
    )
    
    return parser.parse_args()


def parse_proxy(proxy_url: str) -> Optional[dict]:
    """
    Parse proxy URL into dictionary format.
    
    Args:
        proxy_url: Proxy URL string
        
    Returns:
        Proxy configuration dictionary or None
    """
    if not proxy_url:
        return None
        
    try:
        # Simple proxy format
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    except Exception as e:
        logger.error(f"Invalid proxy format: {e}")
        return None


def print_banner():
    """Print application banner."""
    banner = """
    ===============================================
    Etsy Template Category Scraper
    ===============================================
    Extracts product links with pagination support
    Saves to CSV with deduplication
    ===============================================
    """
    print(banner)


def print_summary(results: dict):
    """
    Print scraping summary.
    
    Args:
        results: Results dictionary from scraper
    """
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    
    if results.get("success"):
        print("Status: SUCCESS")
    else:
        print("Status: FAILED")
    
    stats = results.get("stats", {})
    print(f"Pages scraped: {stats.get('pages_scraped', 0)}")
    print(f"Products found: {stats.get('products_found', 0)}")
    print(f"Products saved: {stats.get('products_saved', 0)}")
    print(f"Duplicates skipped: {stats.get('duplicates_skipped', 0)}")
    print(f"Blocked pages: {stats.get('blocked_pages', 0)}")
    print(f"Errors: {stats.get('errors', 0)}")
    print(f"Total unique products: {results.get('total_products', 0)}")
    print("="*50)


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # Handle dry run
    if args.dry_run:
        print("DRY RUN MODE - Configuration Test")
        print(f"Max pages: {args.max_pages or 'All'}")
        print(f"Start page: {args.start_page}")
        print(f"CSV path: {args.csv_path or 'Default (data/etsy_products.csv)'}")
        print(f"Proxy: {'Configured' if args.proxy else 'None'}")
        print("\nConfiguration valid. Exiting dry run.")
        return 0
    
    # Parse proxy if provided
    proxy_config = parse_proxy(args.proxy) if args.proxy else None
    
    # Initialize scraper
    logger.info("Initializing Etsy template scraper...")
    scraper = EtsyTemplateScraper(
        proxy=proxy_config,
        max_pages=args.max_pages,
        start_page=args.start_page,
        csv_path=args.csv_path
    )
    
    # Clear data if requested
    if args.clear_data:
        logger.warning("Clearing existing data...")
        scraper.csv_manager.clear_data()
        print("Existing data cleared.\n")
    
    try:
        # Run the scraper
        logger.info("Starting scraping process...")
        results = scraper.scrape_all_pages()
        
        # Save detailed results to JSON
        results_file = DATA_DIR / "scraping_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Detailed results saved to: {results_file}")
        
        # Print summary
        print_summary(results)
        
        # Print CSV location
        print(f"\nCSV file saved to: {scraper.csv_manager.filepath}")
        
        return 0 if results.get("success") else 1
        
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
        print("\n\nScraping interrupted. Partial results saved.")
        return 2
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}")
        return 1
        
    finally:
        # Clean up
        scraper.close()
        logger.info("Scraper closed")


if __name__ == "__main__":
    sys.exit(main())