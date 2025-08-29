"""
Unified CLI interface for Etsy scraper.
Single entry point for all scraping operations.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from etsy_scraper.core.scraper import EtsyScraper
from etsy_scraper.utils.logger import setup_logger
from etsy_scraper.core.config import DATA_DIR

logger = setup_logger(__name__, log_file="etsy_scraper.log")


def parse_proxy(proxy_url: str) -> Optional[dict]:
    """Parse proxy URL into dictionary format."""
    if not proxy_url:
        return None
    
    try:
        return {"http": proxy_url, "https": proxy_url}
    except Exception as e:
        logger.error(f"Invalid proxy format: {e}")
        return None


def print_banner():
    """Print application banner."""
    print("""
    ===============================================
    Etsy Scraper - Unified CLI
    ===============================================
    Extract products, shops, and metrics from Etsy
    ===============================================
    """)


def print_summary(results: dict, operation: str):
    """Print operation summary."""
    print("\n" + "="*50)
    print(f"{operation.upper()} SUMMARY")
    print("="*50)
    
    if results.get("success"):
        print("Status: SUCCESS")
    else:
        print("Status: FAILED")
    
    stats = results.get("stats", {})
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    if "total_items" in results:
        print(f"Total items in database: {results['total_items']}")
    elif "total_shops" in results:
        print(f"Total shops in database: {results['total_shops']}")
    
    print("="*50)


def cmd_products(args, scraper):
    """Handle product scraping command."""
    logger.info("Starting product scraping...")
    
    # Clear data if requested
    if args.clear_data:
        from etsy_scraper.data.manager import DataManager
        dm = DataManager("products", args.csv_path)
        dm.clear_data()
        print("Existing product data cleared.\n")
    
    results = scraper.scrape_products(
        max_pages=args.max_pages,
        start_page=args.start_page,
        csv_path=args.csv_path
    )
    
    # Save results
    results_file = DATA_DIR / "product_scraping_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print_summary(results, "Product Scraping")
    
    # Show CSV location
    print(f"\nCSV file: {args.csv_path}")
    
    return 0 if results.get("success") else 1


def cmd_shops(args, scraper):
    """Handle shop extraction command."""
    logger.info("Starting shop extraction from listings...")
    
    results = scraper.scrape_shops_from_listings(
        products_csv=args.products_csv,
        output_csv=args.output_csv,
        max_items=args.max_items
    )
    
    print_summary(results, "Shop Extraction")
    
    # Show CSV location
    print(f"\nCSV file: {args.output_csv}")
    
    return 0 if results.get("success") else 1


def cmd_metrics(args, scraper):
    """Handle shop metrics extraction command."""
    logger.info("Starting shop metrics extraction...")
    
    # Check if shops CSV exists
    if not Path(args.shops_csv).exists():
        logger.error(f"Shops CSV not found: {args.shops_csv}")
        print(f"\nError: Shops CSV not found: {args.shops_csv}")
        print("Please run 'shops' command first to extract shops from listings.")
        return 1
    
    results = scraper.scrape_shop_metrics(
        shops_csv=args.shops_csv,
        output_csv=args.output_csv,
        max_shops=args.max_items
    )
    
    print_summary(results, "Metrics Extraction")
    
    # Show CSV location
    print(f"\nCSV file: {args.output_csv}")
    
    return 0 if results.get("success") else 1


def cmd_all(args, scraper):
    """Handle complete pipeline command."""
    logger.info("Starting complete scraping pipeline...")
    
    # Stage 1: Products
    print("\n" + "="*60)
    print("STAGE 1: Scraping Products")
    print("="*60)
    
    product_results = scraper.scrape_products(
        max_pages=args.max_pages,
        start_page=args.start_page
    )
    
    if not product_results.get("success"):
        print("\nProduct scraping failed. Stopping pipeline.")
        return 1
    
    print_summary(product_results, "Product Scraping")
    
    # Stage 2: Shops
    print("\n" + "="*60)
    print("STAGE 2: Extracting Shops")
    print("="*60)
    
    # Reset stats for next stage
    scraper.stats = {key: 0 for key in scraper.stats}
    
    shop_results = scraper.scrape_shops_from_listings(
        max_items=args.max_items
    )
    
    if not shop_results.get("success"):
        print("\nShop extraction failed. Stopping pipeline.")
        return 1
    
    print_summary(shop_results, "Shop Extraction")
    
    # Stage 3: Metrics
    print("\n" + "="*60)
    print("STAGE 3: Extracting Metrics")
    print("="*60)
    
    # Reset stats for next stage
    scraper.stats = {key: 0 for key in scraper.stats}
    
    metrics_results = scraper.scrape_shop_metrics(
        max_shops=args.max_items
    )
    
    print_summary(metrics_results, "Metrics Extraction")
    
    print("\n" + "="*60)
    print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    print("="*60)
    print(f"Products CSV: {DATA_DIR / 'etsy_products.csv'}")
    print(f"Shops CSV: {DATA_DIR / 'shops_from_listings.csv'}")
    print(f"Metrics CSV: {DATA_DIR / 'shop_metrics.csv'}")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Etsy Scraper - Extract products, shops, and metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global arguments
    parser.add_argument("--proxy", help="Proxy URL (e.g., http://user:pass@host:port)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Test configuration without scraping")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Products command
    products_parser = subparsers.add_parser("products", help="Scrape product listings")
    products_parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum pages to scrape (default: 10, use 0 for all pages)"
    )
    products_parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Starting page number (default: 1)"
    )
    products_parser.add_argument(
        "--csv-path",
        type=Path,
        default=DATA_DIR / "etsy_products.csv",
        help=f"CSV output path (default: {DATA_DIR}/etsy_products.csv)"
    )
    products_parser.add_argument(
        "--clear-data",
        action="store_true",
        help="Clear existing data before starting"
    )
    
    # Shops command
    shops_parser = subparsers.add_parser("shops", help="Extract shops from listings")
    shops_parser.add_argument(
        "--products-csv",
        type=Path,
        default=DATA_DIR / "etsy_products.csv",
        help=f"Path to products CSV (default: {DATA_DIR}/etsy_products.csv)"
    )
    shops_parser.add_argument(
        "--output-csv",
        type=Path,
        default=DATA_DIR / "shops_from_listings.csv",
        help=f"Output CSV path (default: {DATA_DIR}/shops_from_listings.csv)"
    )
    shops_parser.add_argument(
        "--max-items",
        type=int,
        default=100,
        help="Maximum items to process (default: 100, use 0 for all items)"
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Extract shop metrics")
    metrics_parser.add_argument(
        "--shops-csv",
        type=Path,
        default=DATA_DIR / "shops_from_listings.csv",
        help=f"Path to shops CSV (default: {DATA_DIR}/shops_from_listings.csv)"
    )
    metrics_parser.add_argument(
        "--output-csv",
        type=Path,
        default=DATA_DIR / "shop_metrics.csv",
        help=f"Output CSV path (default: {DATA_DIR}/shop_metrics.csv)"
    )
    metrics_parser.add_argument(
        "--max-items",
        type=int,
        default=100,
        help="Maximum shops to process (default: 100, use 0 for all shops)"
    )
    
    # All command (complete pipeline)
    all_parser = subparsers.add_parser("all", help="Run complete pipeline")
    all_parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Maximum pages for products (default: 10, use 0 for all pages)"
    )
    all_parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Starting page number (default: 1)"
    )
    all_parser.add_argument(
        "--max-items",
        type=int,
        default=100,
        help="Maximum items for shops/metrics (default: 100, use 0 for all items)"
    )
    
    args = parser.parse_args()
    
    # If no subcommand provided, default to running 'products' with defaults
    if not args.command:
        argv_with_default = sys.argv[1:] + ["products"]
        args = parser.parse_args(argv_with_default)
    
    # Set logging level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # Handle dry run
    if args.dry_run:
        print("DRY RUN MODE - Configuration Test")
        print(f"Command: {args.command}")
        print(f"Proxy: {'Configured' if args.proxy else 'None'}")
        
        if args.command == "products":
            max_pages = getattr(args, 'max_pages', 10)
            print(f"Max pages: {max_pages if max_pages > 0 else 'All'}")
            print(f"Start page: {getattr(args, 'start_page', 1)}")
        elif args.command in ["shops", "metrics"]:
            max_items = getattr(args, 'max_items', 100)
            print(f"Max items: {max_items if max_items > 0 else 'All'}")
        
        print("\nConfiguration valid. Exiting dry run.")
        return 0
    
    # Parse proxy
    proxy_config = parse_proxy(args.proxy) if args.proxy else None
    
    # Initialize scraper
    logger.info(f"Initializing Etsy scraper for command: {args.command}")
    scraper = EtsyScraper(proxy=proxy_config)
    
    try:
        # Execute command
        if args.command == "products":
            return cmd_products(args, scraper)
        elif args.command == "shops":
            return cmd_shops(args, scraper)
        elif args.command == "metrics":
            return cmd_metrics(args, scraper)
        elif args.command == "all":
            return cmd_all(args, scraper)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.warning("Operation interrupted by user")
        print("\n\nOperation interrupted. Partial results saved.")
        return 2
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\nError: {e}")
        return 1
        
    finally:
        scraper.close()
        logger.info("Scraper closed")


if __name__ == "__main__":
    sys.exit(main())