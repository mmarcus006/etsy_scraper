"""
Unified Etsy scraper with modular architecture.
Handles products, shops, and metrics extraction using existing utilities.
"""

import datetime
import os
import time
import random
from typing import Dict, Optional, List, Tuple, Any
from pathlib import Path
from bs4 import BeautifulSoup
import logging
import sys
from tqdm import tqdm

try:
    from curl_cffi.requests import Session
    from curl_cffi.requests import Response
except ImportError as e:
    logging.error("curl_cffi is not installed. Please install it using: uv add curl-cffi")
    logging.error(f"Import error: {e}")
    sys.exit(1)

from etsy_scraper.core.config import (
    URLS, HEADERS, CURL_CONFIG, TIMING, VALIDATION,
    MAX_RETRIES, MAX_REQUESTS_PER_SESSION, get_random_delay
)
from etsy_scraper.data.manager import DataManager
from etsy_scraper.extractors.html_parser import DataExtractor
from etsy_scraper.utils.pagination import PaginationHandler
from etsy_scraper.utils.session import SessionManager, RateLimiter

logger = logging.getLogger(__name__)


class EtsyScraper:
    """Unified scraper for all Etsy data extraction needs."""
    
    def __init__(self, proxy: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize the Etsy scraper.
        
        Args:
            proxy: Optional proxy configuration
        """
        self.proxy = proxy
        
        # Initialize utilities
        self.session_manager = SessionManager(max_retries=MAX_RETRIES)
        self.rate_limiter = RateLimiter(min_delay=TIMING["page_min"], max_delay=TIMING["page_max"])
        self.pagination = PaginationHandler()
        self.extractor = DataExtractor()
        
        # Statistics tracking
        self.stats = {
            "pages_scraped": 0,
            "items_found": 0,
            "items_saved": 0,
            "duplicates": 0,
            "errors": 0,
            "blocked": 0
        }
    
    def _make_request(self, url: str, referer: Optional[str] = None) -> Tuple[int, str]:
        """
        Make HTTP request with anti-bot protection.
        
        Args:
            url: Target URL
            referer: Optional referer header
            
        Returns:
            Tuple of (status_code, html_content)
        """
        headers = HEADERS.copy()
        if referer:
            headers["referer"] = referer
        
        session = self.session_manager.get_session()
        
        try:
            response = session.get(
                url,
                headers=headers,
                impersonate=CURL_CONFIG["impersonate"],
                timeout=CURL_CONFIG["timeout"],
                verify=CURL_CONFIG["verify"],
                allow_redirects=CURL_CONFIG["allow_redirects"],
                proxies=self.proxy
            )
            if response.status_code == 200:
                logger.info(f"Successfully loaded page {url}")
                #create new folder with todays name, and write contents of response to file with the page number in the file name
#                today = datetime.datetime.now().strftime("%Y-%m-%d")
#                os.makedirs(today, exist_ok=True)
#                with open(f"{today}/page_{url.split('page=')[1]}.html", "w") as f:
#                    f.write(response.text)
#            else:
#                logger.error(f"Failed to load page {url} with status code #{response.status_code}")
#                return response.status_code, ""
            
            if self._is_blocked(response):
                logger.warning(f"Block detected on {url}")
                self.stats["blocked"] += 1
                self.session_manager.handle_block_detection()
                return response.status_code, ""
            
            return response.status_code, response.text
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            self.stats["errors"] += 1
            return 0, ""
    
    def _is_blocked(self, response: Response) -> bool:
        """Check if response indicates bot detection."""
        if response.status_code in VALIDATION["blocked_status_codes"]:
            return True
        
        headers_str = str(response.headers).lower()
        for indicator in VALIDATION["datadome_indicators"]:
            if indicator.lower() in headers_str:
                return True
        
        if "captcha" in response.text.lower():
            return True
        
        return False
    
    def scrape_products(self, max_pages: Optional[int] = None, 
                       start_page: int = 1,
                       csv_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape product listings with pagination.
        
        Args:
            max_pages: Maximum pages to scrape
            start_page: Starting page number
            csv_path: Custom CSV output path
            
        Returns:
            Scraping results dictionary
        """
        logger.info("="*60)
        logger.info("Starting product scraping with pagination")
        logger.info(f"Start page: {start_page}, Max pages: {max_pages or 'All'}")
        logger.info("="*60)
        
        # Initialize data manager
        data_manager = DataManager("products", csv_path)
        
        # Check for resume
        last_page = data_manager.get_last_page_scraped()
        if last_page > 0 and start_page == 1:
            start_page = last_page + 1
            logger.info(f"Resuming from page {start_page}")
        
        current_page = start_page
        base_url = URLS["templates"]
        referer = None
        
        # Calculate total pages for progress bar
        total_pages = max_pages if max_pages else 100  # Estimate 100 if unlimited
        
        # Create progress bar for pages
        with tqdm(total=total_pages, desc="Scraping pages", unit="page", 
                  initial=current_page - start_page) as pbar:
            
            while True:
                # Check max pages
                if max_pages and (current_page - start_page + 1) > max_pages:
                    logger.info(f"Reached max pages limit: {max_pages}")
                    break
                
                # Build URL
                url = base_url if current_page == 1 else self.pagination.build_page_url(base_url, current_page)
                
                # Rate limiting
                if current_page > start_page:
                    self.rate_limiter.wait_if_needed()
                
                # Make request
                logger.info(f"Scraping page {current_page}: {url}")
                status, content = self._make_request(url, referer)
                
                if status != 200:
                    logger.error(f"Failed to load page {current_page}")
                    if current_page < 10:  # Try early pages more aggressively
                        current_page += 1
                        continue
                    else:
                        break
                
                # Extract products
                products = self.extractor.extract_products(content)
                logger.info(f"Found {len(products)} products on page {current_page}")
                
                # Save to CSV
                if products:
                    save_stats = data_manager.save_items(products, current_page)
                    self.stats["items_found"] += save_stats["total"]
                    self.stats["items_saved"] += save_stats["saved"]
                    self.stats["duplicates"] += save_stats["duplicates"]
                
                self.stats["pages_scraped"] += 1
                
                # Check for next page
                pagination_info = self.pagination.extract_pagination_info(content)
                if not pagination_info["has_next"]:
                    logger.info("No more pages to scrape")
                    break
                
                referer = url
                current_page += 1
                pbar.update(1)  # Update progress bar
                
                # Progress update
                if current_page % 5 == 0:
                    self._log_progress()
        
        self._log_final_stats()
        
        return {
            "success": self.stats["pages_scraped"] > 0,
            "stats": self.stats,
            "total_items": data_manager.get_count()
        }
    
    def scrape_shops_from_listings(self, products_csv: Optional[str] = None,
                                  output_csv: Optional[str] = None,
                                  max_items: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract shop information from product listings.
        
        Args:
            products_csv: Path to products CSV
            output_csv: Path for shops output
            max_items: Maximum listings to process
            
        Returns:
            Extraction results
        """
        logger.info("="*60)
        logger.info("Extracting shops from product listings")
        logger.info("="*60)
        
        # Initialize managers
        products_dm = DataManager("products", products_csv)
        shops_dm = DataManager("shops", output_csv)
        
        # Get all products
        products = products_dm.get_all_items()
        if not products:
            logger.error("No products found in CSV")
            return {"success": False, "stats": self.stats}
        
        processed = 0
        items_to_process = min(len(products), max_items) if max_items else len(products)
        
        with tqdm(total=items_to_process, desc="Extracting shops", unit="listing") as pbar:
            for product in products:
                if max_items and processed >= max_items:
                    break
                
                listing_url = product.get("url", "")
                if not listing_url or shops_dm.is_processed(listing_url):
                    continue
                
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Fetch listing page
                status, content = self._make_request(listing_url)
                if status == 200:
                    shop_info = self.extractor.extract_shop_from_listing(content)
                    if shop_info and shop_info.get("shop_name"):
                        shop_info["listing_url"] = listing_url
                        save_stats = shops_dm.save_items([shop_info])
                        self.stats["items_saved"] += save_stats["saved"]
                
                processed += 1
                self.stats["items_found"] += 1
                pbar.update(1)
                
                if processed % 10 == 0:
                    logger.info(f"Processed {processed} listings, found {self.stats['items_saved']} shops")
        
        return {
            "success": True,
            "stats": self.stats,
            "total_shops": shops_dm.get_count()
        }
    
    def scrape_shop_metrics(self, shops_csv: Optional[str] = None,
                          output_csv: Optional[str] = None,
                          max_shops: Optional[int] = None) -> Dict[str, Any]:
        """
        Extract metrics (sales, admirers) from shop pages.
        
        Args:
            shops_csv: Path to shops CSV
            output_csv: Path for metrics output
            max_shops: Maximum shops to process
            
        Returns:
            Extraction results
        """
        logger.info("="*60)
        logger.info("Extracting metrics from shop pages")
        logger.info("="*60)
        
        # Initialize managers
        shops_dm = DataManager("shops", shops_csv)
        metrics_dm = DataManager("metrics", output_csv)
        
        # Get all shops
        shops = shops_dm.get_all_items()
        if not shops:
            logger.error("No shops found in CSV")
            return {"success": False, "stats": self.stats}
        
        processed = 0
        shops_to_process = min(len(shops), max_shops) if max_shops else len(shops)
        
        with tqdm(total=shops_to_process, desc="Extracting metrics", unit="shop") as pbar:
            for shop in shops:
                if max_shops and processed >= max_shops:
                    break
                
                shop_name = shop.get("shop_name", "")
                shop_url = shop.get("shop_url", "")
                
                if not shop_url or metrics_dm.is_processed(shop_name):
                    continue
                
                # Rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Fetch shop page
                status, content = self._make_request(shop_url)
                if status == 200:
                    metrics = self.extractor.extract_shop_metrics(content)
                    metrics["shop_name"] = shop_name
                    metrics["shop_url"] = shop_url
                    
                    save_stats = metrics_dm.save_items([metrics])
                    self.stats["items_saved"] += save_stats["saved"]
                
                processed += 1
                self.stats["items_found"] += 1
                pbar.update(1)
                
                if processed % 10 == 0:
                    logger.info(f"Processed {processed} shops")
        
        return {
            "success": True,
            "stats": self.stats,
            "total_shops": metrics_dm.get_count()
        }
    
    def _log_progress(self) -> None:
        """Log scraping progress."""
        logger.info("-" * 50)
        logger.info(f"Progress: Pages={self.stats['pages_scraped']}, "
                   f"Found={self.stats['items_found']}, "
                   f"Saved={self.stats['items_saved']}, "
                   f"Duplicates={self.stats['duplicates']}")
        logger.info("-" * 50)
    
    def _log_final_stats(self) -> None:
        """Log final statistics."""
        logger.info("="*60)
        logger.info("Scraping Complete:")
        for key, value in self.stats.items():
            logger.info(f"  {key}: {value}")
        logger.info("="*60)
    
    def close(self) -> None:
        """Clean up resources."""
        if self.session_manager:
            self.session_manager.close()