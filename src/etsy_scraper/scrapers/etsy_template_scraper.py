"""
Etsy template category scraper with pagination support.
Extracts all product links from category pages using curl-cffi for DataDome bypass.
"""

import time
import json
import random
from typing import Dict, Optional, List, Tuple
from bs4 import BeautifulSoup
from curl_cffi import requests
from curl_cffi.requests import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.etsy_flow_config import (
    URLS, HEADERS, SESSION_PARAMS, TIMING, 
    CURL_CFFI_CONFIG, VALIDATION, get_random_delay
)
from utils.logger import setup_logger
from extractors.product_links import ProductLinkExtractor
from scrapers.pagination import PaginationHandler
from scrapers.session_manager import SessionManager, RateLimiter
from data.csv_manager import ProductCSVManager

logger = setup_logger(__name__)


class EtsyTemplateScraper:
    """Scrapes Etsy template category pages with pagination support."""
    
    def __init__(self, proxy: Optional[Dict] = None, max_pages: Optional[int] = None, 
                 start_page: int = 1, csv_path: Optional[str] = None):
        """
        Initialize the Etsy template scraper.
        
        Args:
            proxy: Optional proxy configuration dict
            max_pages: Maximum number of pages to scrape (None for all)
            start_page: Page number to start from (default 1)
            csv_path: Custom path for CSV output file
        """
        self.proxy = proxy
        self.max_pages = max_pages
        self.start_page = start_page
        self.session_data = SESSION_PARAMS.copy()
        
        # Initialize components
        self.session_manager = SessionManager(max_retries=3)
        self.rate_limiter = RateLimiter(min_delay=1.0, max_delay=3.0)
        self.extractor = ProductLinkExtractor()
        self.pagination = PaginationHandler()
        self.csv_manager = ProductCSVManager(csv_path)
        
        # Statistics tracking
        self.stats = {
            "pages_scraped": 0,
            "products_found": 0,
            "products_saved": 0,
            "duplicates_skipped": 0,
            "errors": 0,
            "blocked_pages": 0
        }
        
    def _make_request(self, url: str, referer: Optional[str] = None) -> Tuple[int, str]:
        """
        Make a request with curl-cffi impersonation.
        
        Args:
            url: Target URL
            referer: Optional referer header
            
        Returns:
            Tuple of (status_code, response_text)
        """
        headers = HEADERS.copy()
        if referer:
            headers["referer"] = referer
            
        # Add session tracking headers
        headers["x-ebid"] = self.session_data.get("ebid", "")
        headers["x-browser-id"] = self.session_data.get("browser_id", "")
        
        # Get session from manager
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
            
            # Check for DataDome protection
            if self._is_blocked(response):
                logger.error(f"DataDome block detected on {url}")
                self.stats["blocked_pages"] += 1
                return response.status_code, response.text
                
            return response.status_code, response.text
            
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            self.stats["errors"] += 1
            return 0, ""
    
    def _is_blocked(self, response) -> bool:
        """Check if the response indicates bot detection."""
        # Check status code
        if response.status_code in VALIDATION["blocked_status_codes"]:
            return True
            
        # Check for DataDome indicators
        headers_str = str(response.headers).lower()
        for indicator in VALIDATION["datadome_indicators"]:
            if indicator.lower() in headers_str:
                logger.warning(f"DataDome indicator found: {indicator}")
                return True
                
        # Check response content for captcha
        content_lower = response.text.lower()
        if "captcha" in content_lower or "challenge" in content_lower:
            if "datadome" in content_lower:
                return True
                
        return False
    
    def _validate_page(self, content: str) -> bool:
        """
        Validate that the page loaded correctly.
        
        Args:
            content: Page HTML content
            
        Returns:
            Boolean indicating if page is valid
        """
        indicators = VALIDATION["success_indicators"].get("templates_page", [])
        content_lower = content.lower()
        
        for indicator in indicators:
            if indicator.lower() not in content_lower:
                logger.warning(f"Missing indicator '{indicator}' for templates page")
                return False
                
        return True
    
    def scrape_single_page(self, url: str, page_number: int, referer: Optional[str] = None) -> Dict:
        """
        Scrape a single page of templates.
        
        Args:
            url: Page URL to scrape
            page_number: Current page number
            referer: Optional referer URL
            
        Returns:
            Dictionary with scraping results
        """
        logger.info(f"Scraping page {page_number}: {url}")
        
        # Make request
        status, content = self._make_request(url, referer)
        
        if status != 200:
            logger.error(f"Failed to load page {page_number}. Status: {status}")
            return {"success": False, "products": [], "has_next": False}
        
        if not self._validate_page(content):
            logger.error(f"Page {page_number} validation failed")
            return {"success": False, "products": [], "has_next": False}
        
        # Extract products
        products = self.extractor.extract_products_from_html(content)
        logger.info(f"Found {len(products)} products on page {page_number}")
        
        # Extract pagination info
        pagination_info = self.pagination.extract_pagination_info(content)
        
        return {
            "success": True,
            "products": products,
            "has_next": pagination_info["has_next"],
            "next_url": pagination_info.get("next_page_url"),
            "total_pages": pagination_info.get("total_pages")
        }
    
    def scrape_all_pages(self) -> Dict:
        """
        Scrape all pages from the templates category.
        
        Returns:
            Dictionary with complete scraping results
        """
        logger.info("="*60)
        logger.info("Starting Etsy template category scraper with pagination")
        logger.info(f"Starting from page {self.start_page}")
        if self.max_pages:
            logger.info(f"Maximum pages to scrape: {self.max_pages}")
        logger.info("="*60)
        
        # Check if resuming
        last_page = self.csv_manager.get_last_page_scraped()
        if last_page > 0 and self.start_page == 1:
            self.start_page = last_page + 1
            logger.info(f"Resuming from page {self.start_page} (last scraped: {last_page})")
        
        current_page = self.start_page
        base_url = URLS["templates"]
        referer = None
        
        while True:
            # Check max pages limit
            if self.max_pages and (current_page - self.start_page + 1) > self.max_pages:
                logger.info(f"Reached maximum page limit ({self.max_pages})")
                break
            
            # Build URL for current page
            if current_page == 1:
                url = base_url
            else:
                url = self.pagination.build_page_url(base_url, current_page)
            
            # Add human-like delay between pages
            if current_page > self.start_page:
                delay = get_random_delay("page_navigation")
                logger.info(f"Waiting {delay:.1f} seconds before next page...")
                time.sleep(delay)
            
            # Scrape the page
            result = self.scrape_single_page(url, current_page, referer)
            
            if not result["success"]:
                logger.error(f"Failed to scrape page {current_page}")
                # Try to continue with next page
                if current_page < 10:  # Only try first 10 pages aggressively
                    current_page += 1
                    continue
                else:
                    break
            
            # Save products to CSV
            if result["products"]:
                save_stats = self.csv_manager.save_products(result["products"], current_page)
                self.stats["products_found"] += save_stats["total"]
                self.stats["products_saved"] += save_stats["saved"]
                self.stats["duplicates_skipped"] += save_stats["duplicates"]
            
            self.stats["pages_scraped"] += 1
            
            # Check if there's a next page
            if not result["has_next"]:
                logger.info("No more pages to scrape")
                break
            
            # Update referer for next request
            referer = url
            current_page += 1
            
            # Log progress every 5 pages
            if current_page % 5 == 0:
                self._log_progress()
        
        # Final statistics
        self._log_final_stats()
        
        return {
            "success": self.stats["pages_scraped"] > 0,
            "stats": self.stats,
            "total_products": self.csv_manager.get_product_count()
        }
    
    def _log_progress(self):
        """Log scraping progress."""
        logger.info("-" * 50)
        logger.info("Progress Update:")
        logger.info(f"  Pages scraped: {self.stats['pages_scraped']}")
        logger.info(f"  Products found: {self.stats['products_found']}")
        logger.info(f"  Products saved: {self.stats['products_saved']}")
        logger.info(f"  Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info("-" * 50)
    
    def _log_final_stats(self):
        """Log final scraping statistics."""
        logger.info("="*60)
        logger.info("Scraping Complete - Final Statistics:")
        logger.info(f"  Pages scraped: {self.stats['pages_scraped']}")
        logger.info(f"  Products found: {self.stats['products_found']}")
        logger.info(f"  Products saved: {self.stats['products_saved']}")
        logger.info(f"  Duplicates skipped: {self.stats['duplicates_skipped']}")
        logger.info(f"  Blocked pages: {self.stats['blocked_pages']}")
        logger.info(f"  Errors: {self.stats['errors']}")
        logger.info(f"  Total unique products in CSV: {self.csv_manager.get_product_count()}")
        logger.info(f"  CSV file: {self.csv_manager.filepath}")
        logger.info("="*60)
    
    def close(self):
        """Clean up session."""
        if self.session_manager:
            self.session_manager.close()


def main():
    """Main execution for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Etsy template category pages")
    parser.add_argument("--max-pages", type=int, help="Maximum number of pages to scrape")
    parser.add_argument("--start-page", type=int, default=1, help="Page to start from")
    parser.add_argument("--csv-path", help="Custom CSV output path")
    args = parser.parse_args()
    
    scraper = EtsyTemplateScraper(
        max_pages=args.max_pages,
        start_page=args.start_page,
        csv_path=args.csv_path
    )
    
    try:
        results = scraper.scrape_all_pages()
        
        # Save summary results
        with open('scraping_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        if results["success"]:
            print(f"\n✓ Scraping completed successfully!")
            print(f"Total products scraped: {results['total_products']}")
        else:
            print("\n✗ Scraping failed!")
            
    finally:
        scraper.close()


if __name__ == "__main__":
    main()