"""
Main CLI interface for Etsy shop extraction pipeline.
Orchestrates the two-stage process of extracting shop data.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.listing_shop_extractor import ListingShopExtractor
from scrapers.shop_metrics_extractor import ShopMetricsExtractor
from utils.logger import setup_logger
from config.settings import DATA_DIR

logger = setup_logger(__name__, log_file="shop_scraper.log")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract shop information and metrics from Etsy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stage 1: Extract shops from all listings
  python shop_scraper_main.py --stage listings
  
  # Stage 2: Extract metrics from all shops
  python shop_scraper_main.py --stage metrics
  
  # Run both stages
  python shop_scraper_main.py --stage all
  
  # Process limited number with custom paths
  python shop_scraper_main.py --stage listings --max-items 50 --products-csv my_products.csv
  
  # Extract metrics with custom output
  python shop_scraper_main.py --stage metrics --output-csv shop_data.csv
        """
    )
    
    parser.add_argument(
        "--stage",
        choices=["listings", "metrics", "all"],
        default="all",
        help="Which stage to run (default: all)"
    )
    
    parser.add_argument(
        "--products-csv",
        type=str,
        help="Path to products CSV file (for listings stage)"
    )
    
    parser.add_argument(
        "--shops-csv",
        type=str,
        help="Path to shops CSV file (input for metrics stage, output for listings stage)"
    )
    
    parser.add_argument(
        "--output-csv",
        type=str,
        help="Path to output CSV file"
    )
    
    parser.add_argument(
        "--max-items",
        type=int,
        help="Maximum number of items to process"
    )
    
    parser.add_argument(
        "--proxy",
        type=str,
        help="Proxy URL (e.g., http://user:pass@host:port)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show configuration without running"
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
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    except Exception as e:
        logger.error(f"Invalid proxy format: {e}")
        return None


def run_listings_stage(args, proxy_config):
    """
    Run the listings stage to extract shops from product listings.
    
    Args:
        args: Command-line arguments
        proxy_config: Proxy configuration
    """
    logger.info("\n" + "="*60)
    logger.info("STAGE 1: Extracting shops from product listings")
    logger.info("="*60)
    
    # Determine output path for shops CSV
    shops_output = args.shops_csv or args.output_csv
    
    extractor = ListingShopExtractor(
        products_csv_path=args.products_csv,
        shops_csv_path=shops_output,
        proxy=proxy_config
    )
    
    try:
        extractor.process_all_listings(max_listings=args.max_items)
        logger.info("Stage 1 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        return False
    finally:
        extractor.close()


def run_metrics_stage(args, proxy_config):
    """
    Run the metrics stage to extract sales/admirers from shop pages.
    
    Args:
        args: Command-line arguments
        proxy_config: Proxy configuration
    """
    logger.info("\n" + "="*60)
    logger.info("STAGE 2: Extracting metrics from shop pages")
    logger.info("="*60)
    
    # Determine input shops CSV
    shops_input = args.shops_csv
    if not shops_input:
        # Use default path
        shops_input = DATA_DIR / "shops_from_listings.csv"
        if not shops_input.exists():
            logger.error(f"Shops CSV not found: {shops_input}")
            logger.error("Please run stage 1 first: --stage listings")
            return False
    
    extractor = ShopMetricsExtractor(
        shops_csv_path=shops_input,
        metrics_csv_path=args.output_csv,
        proxy=proxy_config
    )
    
    try:
        extractor.process_all_shops(max_shops=args.max_items)
        logger.info("Stage 2 completed successfully")
        return True
    except Exception as e:
        logger.error(f"Stage 2 failed: {e}")
        return False
    finally:
        extractor.close()


def print_banner():
    """Print application banner."""
    banner = """
    ===============================================
    Etsy Shop Data Extraction Pipeline
    ===============================================
    Stage 1: Extract shops from product listings
    Stage 2: Extract metrics from shop pages
    ===============================================
    """
    print(banner)


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Set logging level
    if args.verbose:
        logger.setLevel("DEBUG")
    
    print_banner()
    
    # Handle dry run
    if args.dry_run:
        print("DRY RUN MODE - Configuration:")
        print(f"Stage: {args.stage}")
        print(f"Max items: {args.max_items or 'All'}")
        if args.products_csv:
            print(f"Products CSV: {args.products_csv}")
        if args.shops_csv:
            print(f"Shops CSV: {args.shops_csv}")
        if args.output_csv:
            print(f"Output CSV: {args.output_csv}")
        print(f"Proxy: {'Configured' if args.proxy else 'None'}")
        print("\nConfiguration valid. Exiting dry run.")
        return 0
    
    # Parse proxy
    proxy_config = parse_proxy(args.proxy) if args.proxy else None
    
    success = True
    
    try:
        # Run appropriate stages
        if args.stage in ["listings", "all"]:
            if not run_listings_stage(args, proxy_config):
                success = False
                if args.stage == "all":
                    logger.error("Stage 1 failed, skipping Stage 2")
                    return 1
        
        if args.stage in ["metrics", "all"] and success:
            if not run_metrics_stage(args, proxy_config):
                success = False
        
        # Print final summary
        if success:
            logger.info("\n" + "="*60)
            logger.info("Shop extraction pipeline completed successfully!")
            
            # Show output file locations
            if args.stage in ["listings", "all"]:
                shops_file = args.shops_csv or DATA_DIR / "shops_from_listings.csv"
                logger.info(f"Shops CSV: {shops_file}")
            
            if args.stage in ["metrics", "all"]:
                metrics_file = args.output_csv or DATA_DIR / "shop_metrics.csv"
                logger.info(f"Metrics CSV: {metrics_file}")
            
            logger.info("="*60)
            return 0
        else:
            logger.error("\nPipeline completed with errors")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        return 2
        
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())