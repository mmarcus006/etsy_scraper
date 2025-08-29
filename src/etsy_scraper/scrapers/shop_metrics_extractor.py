"""
Extracts sales and admirers metrics from Etsy shop pages.
Visits each shop URL to extract metrics and check for HREFs.
"""

import time
from typing import Dict, Optional
from pathlib import Path
from curl_cffi.requests import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.etsy_flow_config import (
    HEADERS, SESSION_PARAMS, TIMING, 
    CURL_CFFI_CONFIG, VALIDATION, get_random_delay
)
from utils.logger import setup_logger
from extractors.shop_extractors import ShopExtractor
from scrapers.session_manager import SessionManager, RateLimiter
from data_management.shop_csv_manager import ShopListingCSVManager, ShopMetricsCSVManager

logger = setup_logger(__name__)


class ShopMetricsExtractor:
    """Extracts metrics from Etsy shop pages."""
    
    def __init__(self, shops_csv_path: Optional[str] = None,
                 metrics_csv_path: Optional[str] = None,
                 proxy: Optional[Dict] = None):
        """
        Initialize the shop metrics extractor.
        
        Args:
            shops_csv_path: Path to shops CSV file (input)
            metrics_csv_path: Path to metrics CSV file (output)
            proxy: Optional proxy configuration
        """
        # Set default shops CSV path
        if shops_csv_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            shops_csv_path = base_dir / "data" / "shops_from_listings.csv"
        
        self.shops_csv_path = Path(shops_csv_path)
        self.proxy = proxy
        
        # Initialize components
        self.session_manager = SessionManager(max_retries=3)
        self.rate_limiter = RateLimiter(min_delay=3.0, max_delay=6.0)
        self.extractor = ShopExtractor()
        self.csv_manager = ShopMetricsCSVManager(metrics_csv_path)
        
        # Statistics
        self.stats = {
            'shops_processed': 0,
            'metrics_extracted': 0,
            'shops_with_sales': 0,
            'shops_with_admirers': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def _make_request(self, url: str, referer: Optional[str] = None) -> tuple[int, str]:
        """
        Make a request to a shop page.
        
        Args:
            url: Shop URL
            referer: Optional referer header
            
        Returns:
            Tuple of (status_code, html_content)
        """
        headers = HEADERS.copy()
        if referer:
            headers["referer"] = referer
        
        # Add session tracking headers
        headers["x-ebid"] = SESSION_PARAMS.get("ebid", "")
        headers["x-browser-id"] = SESSION_PARAMS.get("browser_id", "")
        
        session = self.session_manager.get_session()
        
        try:
            response = session.get(
                url,
                headers=headers,
                impersonate=CURL_CFFI_CONFIG["impersonate"],
                timeout=CURL_CFFI_CONFIG["timeout"],
                verify=CURL_CFFI_CONFIG["verify"],
                allow_redirects=CURL_CFFI_CONFIG["allow_redirects"],
                proxies=self.proxy if self.proxy else None
            )
            
            # Check for blocks
            if self._is_blocked(response):
                logger.warning(f"Blocked on {url}")
                self.session_manager.handle_block_detection()
                return response.status_code, ""
            
            return response.status_code, response.text
            
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return 0, ""
    
    def _is_blocked(self, response) -> bool:
        """Check if response indicates blocking."""
        if response.status_code in [403, 429, 503]:
            return True
            
        headers_str = str(response.headers).lower()
        for indicator in VALIDATION.get("datadome_indicators", []):
            if indicator.lower() in headers_str:
                return True
                
        return False
    
    def extract_metrics_from_shop(self, shop_name: str, shop_url: str) -> Optional[Dict]:
        """
        Extract metrics from a single shop page.
        
        Args:
            shop_name: Name of the shop
            shop_url: URL of the shop
            
        Returns:
            Metrics dictionary or None
        """
        logger.info(f"Processing shop: {shop_name}")
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Make request
        status, html = self._make_request(shop_url)
        
        if status != 200 or not html:
            logger.error(f"Failed to load shop: {shop_url} (status: {status})")
            self.stats['errors'] += 1
            return None
        
        # Extract metrics
        metrics = self.extractor.extract_shop_metrics(html)
        
        if metrics:
            # Update statistics
            if metrics.get('sales_count'):
                self.stats['shops_with_sales'] += 1
            if metrics.get('admirers_count'):
                self.stats['shops_with_admirers'] += 1
            
            self.stats['metrics_extracted'] += 1
            
            # Log interesting findings
            if metrics.get('admirers_has_href'):
                logger.info(f"  Found admirers link for {shop_name}: {metrics['admirers_url']}")
            if metrics.get('sales_has_href'):
                logger.info(f"  Found sales link for {shop_name}: {metrics['sales_url']}")
                
            return metrics
        else:
            logger.warning(f"No metrics found for shop: {shop_name}")
            return None
    
    def process_all_shops(self, max_shops: Optional[int] = None):
        """
        Process all shops from the shops CSV.
        
        Args:
            max_shops: Maximum number of shops to process
        """
        if not self.shops_csv_path.exists():
            logger.error(f"Shops CSV not found: {self.shops_csv_path}")
            return
        
        logger.info("="*60)
        logger.info("Starting shop metrics extraction")
        logger.info(f"Shops CSV: {self.shops_csv_path}")
        logger.info(f"Output CSV: {self.csv_manager.filepath}")
        logger.info("="*60)
        
        # Load shops from CSV
        shops_csv_manager = ShopListingCSVManager(self.shops_csv_path)
        shops = shops_csv_manager.get_all_shops()
        
        if not shops:
            logger.warning("No shops found in CSV")
            return
        
        logger.info(f"Found {len(shops)} shops to process")
        
        for idx, shop_data in enumerate(shops, 1):
            # Check max limit
            if max_shops and self.stats['shops_processed'] >= max_shops:
                logger.info(f"Reached max shops limit: {max_shops}")
                break
            
            shop_name = shop_data.get('shop_name', '')
            shop_url = shop_data.get('shop_url', '')
            
            if not shop_name or not shop_url:
                logger.warning(f"Invalid shop data: {shop_data}")
                continue
            
            # Skip if already processed
            if self.csv_manager.is_shop_processed(shop_name):
                logger.debug(f"Skipping already processed: {shop_name}")
                self.stats['skipped'] += 1
                continue
            
            # Extract metrics from shop page
            metrics = self.extract_metrics_from_shop(shop_name, shop_url)
            
            if metrics:
                # Save to CSV
                self.csv_manager.save_metrics(shop_name, shop_url, metrics)
            
            self.stats['shops_processed'] += 1
            
            # Progress update every 10 shops
            if self.stats['shops_processed'] % 10 == 0:
                self._log_progress()
            
            # Add delay between shops
            if idx < len(shops):  # Not the last item
                delay = get_random_delay("page_navigation")
                logger.debug(f"Waiting {delay:.1f} seconds before next shop...")
                time.sleep(delay)
        
        # Final statistics
        self._log_final_stats()
    
    def _log_progress(self):
        """Log progress update."""
        logger.info("-" * 50)
        logger.info("Progress Update:")
        logger.info(f"  Shops processed: {self.stats['shops_processed']}")
        logger.info(f"  Metrics extracted: {self.stats['metrics_extracted']}")
        logger.info(f"  Shops with sales: {self.stats['shops_with_sales']}")
        logger.info(f"  Shops with admirers: {self.stats['shops_with_admirers']}")
        logger.info(f"  Skipped (already processed): {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("-" * 50)
    
    def _log_final_stats(self):
        """Log final statistics."""
        logger.info("="*60)
        logger.info("Shop Metrics Extraction Complete - Final Statistics:")
        logger.info(f"  Total shops processed: {self.stats['shops_processed']}")
        logger.info(f"  Metrics successfully extracted: {self.stats['metrics_extracted']}")
        logger.info(f"  Shops with sales data: {self.stats['shops_with_sales']}")
        logger.info(f"  Shops with admirers data: {self.stats['shops_with_admirers']}")
        logger.info(f"  Skipped (already processed): {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        
        # Get summary statistics
        summary = self.csv_manager.get_metrics_summary()
        if summary:
            logger.info("-" * 60)
            logger.info("Metrics Summary:")
            logger.info(f"  Total sales across all shops: {summary.get('total_sales', 0):,}")
            logger.info(f"  Total admirers across all shops: {summary.get('total_admirers', 0):,}")
            logger.info(f"  Average sales per shop: {summary.get('avg_sales', 0):,}")
            logger.info(f"  Average admirers per shop: {summary.get('avg_admirers', 0):,}")
            logger.info(f"  Shops with sales link: {summary.get('shops_with_sales_link', 0)}")
            logger.info(f"  Shops with admirers link: {summary.get('shops_with_admirers_link', 0)}")
        
        logger.info(f"  Output file: {self.csv_manager.filepath}")
        logger.info("="*60)
    
    def close(self):
        """Clean up resources."""
        if self.session_manager:
            self.session_manager.close()


def main():
    """Main execution for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract metrics from Etsy shop pages")
    parser.add_argument("--shops-csv", help="Path to shops CSV file")
    parser.add_argument("--output-csv", help="Path to output metrics CSV file")
    parser.add_argument("--max-shops", type=int, help="Maximum number of shops to process")
    args = parser.parse_args()
    
    extractor = ShopMetricsExtractor(
        shops_csv_path=args.shops_csv,
        metrics_csv_path=args.output_csv
    )
    
    try:
        extractor.process_all_shops(max_shops=args.max_shops)
    finally:
        extractor.close()


if __name__ == "__main__":
    main()