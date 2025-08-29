"""
Extracts shop information from Etsy listing pages.
Visits each product listing URL to extract shop name and URL.
"""

import time
import csv
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
from data_management.shop_csv_manager import ShopListingCSVManager

logger = setup_logger(__name__)


class ListingShopExtractor:
    """Extracts shop information from product listing pages."""
    
    def __init__(self, products_csv_path: Optional[str] = None, 
                 shops_csv_path: Optional[str] = None,
                 proxy: Optional[Dict] = None):
        """
        Initialize the listing shop extractor.
        
        Args:
            products_csv_path: Path to products CSV file
            shops_csv_path: Path to output shops CSV file
            proxy: Optional proxy configuration
        """
        # Set default products CSV path
        if products_csv_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            products_csv_path = base_dir / "data" / "etsy_products.csv"
        
        self.products_csv_path = Path(products_csv_path)
        self.proxy = proxy
        
        # Initialize components
        self.session_manager = SessionManager(max_retries=3)
        self.rate_limiter = RateLimiter(min_delay=2.0, max_delay=5.0)
        self.extractor = ShopExtractor()
        self.csv_manager = ShopListingCSVManager(shops_csv_path)
        
        # Statistics
        self.stats = {
            'listings_processed': 0,
            'shops_found': 0,
            'new_shops': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def _make_request(self, url: str, referer: Optional[str] = None) -> tuple[int, str]:
        """
        Make a request to a listing page.
        
        Args:
            url: Listing URL
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
    
    def extract_shop_from_listing(self, listing_url: str) -> Optional[Dict]:
        """
        Extract shop information from a single listing.
        
        Args:
            listing_url: URL of the listing
            
        Returns:
            Shop information dictionary or None
        """
        logger.info(f"Processing listing: {listing_url}")
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Make request
        status, html = self._make_request(listing_url)
        
        if status != 200 or not html:
            logger.error(f"Failed to load listing: {listing_url} (status: {status})")
            self.stats['errors'] += 1
            return None
        
        # Extract shop information
        shop_info = self.extractor.extract_shop_from_listing_page(html)
        
        if shop_info and shop_info.get('shop_name'):
            self.stats['shops_found'] += 1
            return shop_info
        else:
            logger.warning(f"No shop found in listing: {listing_url}")
            return None
    
    def process_all_listings(self, max_listings: Optional[int] = None):
        """
        Process all listings from the products CSV.
        
        Args:
            max_listings: Maximum number of listings to process
        """
        if not self.products_csv_path.exists():
            logger.error(f"Products CSV not found: {self.products_csv_path}")
            return
        
        logger.info("="*60)
        logger.info("Starting shop extraction from listings")
        logger.info(f"Products CSV: {self.products_csv_path}")
        logger.info(f"Output CSV: {self.csv_manager.filepath}")
        logger.info("="*60)
        
        try:
            with open(self.products_csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    # Check max limit
                    if max_listings and self.stats['listings_processed'] >= max_listings:
                        logger.info(f"Reached max listings limit: {max_listings}")
                        break
                    
                    listing_url = row.get('url', '')
                    if not listing_url:
                        continue
                    
                    # Skip if already processed
                    if self.csv_manager.is_listing_processed(listing_url):
                        logger.debug(f"Skipping already processed: {listing_url}")
                        self.stats['skipped'] += 1
                        continue
                    
                    # Extract shop from listing
                    shop_info = self.extract_shop_from_listing(listing_url)
                    
                    if shop_info:
                        # Save to CSV
                        if self.csv_manager.save_shop(shop_info, listing_url):
                            self.stats['new_shops'] += 1
                    
                    self.stats['listings_processed'] += 1
                    
                    # Progress update every 10 listings
                    if self.stats['listings_processed'] % 10 == 0:
                        self._log_progress()
                    
                    # Add delay between listings
                    if row_num < len(list(reader)):  # Not the last item
                        delay = get_random_delay("action_delay")
                        time.sleep(delay)
                        
        except Exception as e:
            logger.error(f"Error processing listings: {e}")
        
        # Final statistics
        self._log_final_stats()
    
    def _log_progress(self):
        """Log progress update."""
        logger.info("-" * 50)
        logger.info("Progress Update:")
        logger.info(f"  Listings processed: {self.stats['listings_processed']}")
        logger.info(f"  Shops found: {self.stats['shops_found']}")
        logger.info(f"  New shops saved: {self.stats['new_shops']}")
        logger.info(f"  Skipped (already processed): {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info("-" * 50)
    
    def _log_final_stats(self):
        """Log final statistics."""
        logger.info("="*60)
        logger.info("Shop Extraction Complete - Final Statistics:")
        logger.info(f"  Total listings processed: {self.stats['listings_processed']}")
        logger.info(f"  Total shops found: {self.stats['shops_found']}")
        logger.info(f"  New unique shops saved: {self.stats['new_shops']}")
        logger.info(f"  Skipped (already processed): {self.stats['skipped']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info(f"  Total unique shops in CSV: {self.csv_manager.get_shop_count()}")
        logger.info(f"  Output file: {self.csv_manager.filepath}")
        logger.info("="*60)
    
    def close(self):
        """Clean up resources."""
        if self.session_manager:
            self.session_manager.close()


def main():
    """Main execution for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract shops from Etsy listing pages")
    parser.add_argument("--products-csv", help="Path to products CSV file")
    parser.add_argument("--output-csv", help="Path to output shops CSV file")
    parser.add_argument("--max-listings", type=int, help="Maximum number of listings to process")
    args = parser.parse_args()
    
    extractor = ListingShopExtractor(
        products_csv_path=args.products_csv,
        shops_csv_path=args.output_csv
    )
    
    try:
        extractor.process_all_listings(max_listings=args.max_listings)
    finally:
        extractor.close()


if __name__ == "__main__":
    main()