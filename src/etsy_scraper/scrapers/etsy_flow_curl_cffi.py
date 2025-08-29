"""
Etsy flow replication using curl-cffi for DataDome bypass
Implements the 3-page flow: Templates -> Listing -> Shop
"""

import time
import json
import random
from typing import Dict, Optional, Tuple
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

logger = setup_logger(__name__)


class EtsyFlowCurlCffi:
    """Replicates Etsy browsing flow using curl-cffi for anti-bot bypass."""
    
    def __init__(self, proxy: Optional[Dict] = None):
        """
        Initialize the Etsy flow replicator.
        
        Args:
            proxy: Optional proxy configuration dict
        """
        self.session = Session()
        self.proxy = proxy
        self.extracted_data = {}
        self.session_data = SESSION_PARAMS.copy()
        
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
        
        try:
            response = self.session.get(
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
                logger.debug(f"Response headers: {response.headers}")
                return response.status_code, response.text
                
            return response.status_code, response.text
            
        except Exception as e:
            logger.error(f"Request failed for {url}: {str(e)}")
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
    
    def _validate_page(self, page_type: str, content: str) -> bool:
        """
        Validate that the page loaded correctly.
        
        Args:
            page_type: Type of page (templates_page, listing_page, shop_page)
            content: Page HTML content
            
        Returns:
            Boolean indicating if page is valid
        """
        indicators = VALIDATION["success_indicators"].get(page_type, [])
        content_lower = content.lower()
        
        for indicator in indicators:
            if indicator.lower() not in content_lower:
                logger.warning(f"Missing indicator '{indicator}' for {page_type}")
                return False
                
        logger.info(f"Successfully validated {page_type}")
        return True
    
    def _extract_data_from_page(self, page_type: str, content: str):
        """Extract relevant data from each page."""
        soup = BeautifulSoup(content, 'html.parser')
        
        if page_type == "templates_page":
            # Extract category information
            listings = soup.find_all('div', class_='v2-listing-card')
            self.extracted_data['template_count'] = len(listings)
            logger.info(f"Found {len(listings)} template listings")
            
        elif page_type == "listing_page":
            # Extract listing details
            title = soup.find('h1', class_='wt-text-body-01')
            if title:
                self.extracted_data['listing_title'] = title.text.strip()
                
            price = soup.find('p', class_='wt-text-title-largest')
            if price:
                self.extracted_data['listing_price'] = price.text.strip()
                
            # Extract seller name
            seller_link = soup.find('a', href=lambda x: x and '/shop/' in x)
            if seller_link:
                self.extracted_data['seller_name'] = seller_link.text.strip()
                
            logger.info(f"Extracted listing: {self.extracted_data.get('listing_title', 'Unknown')}")
            
        elif page_type == "shop_page":
            # Extract shop information
            shop_name = soup.find('h1', class_='wt-text-heading-01')
            if shop_name:
                self.extracted_data['shop_name'] = shop_name.text.strip()
                
            item_count = soup.find('span', class_='wt-text-caption')
            if item_count and 'items' in item_count.text:
                self.extracted_data['shop_items'] = item_count.text.strip()
                
            logger.info(f"Extracted shop: {self.extracted_data.get('shop_name', 'Unknown')}")
    
    def navigate_to_templates(self) -> bool:
        """
        Step 1: Navigate to personal finance templates page.
        
        Returns:
            Boolean indicating success
        """
        logger.info("Step 1: Navigating to personal finance templates...")
        
        status, content = self._make_request(URLS["templates"])
        
        if status != 200:
            logger.error(f"Failed to load templates page. Status: {status}")
            return False
            
        if not self._validate_page("templates_page", content):
            logger.error("Templates page validation failed")
            return False
            
        self._extract_data_from_page("templates_page", content)
        
        logger.info("Successfully loaded templates page")
        return True
    
    def select_listing(self) -> bool:
        """
        Step 2: Navigate to specific listing.
        
        Returns:
            Boolean indicating success
        """
        logger.info("Step 2: Selecting ADHD budget planner listing...")
        
        # Add human-like delay
        delay = get_random_delay("page1_to_page2")
        logger.info(f"Waiting {delay:.1f} seconds before clicking listing...")
        time.sleep(delay)
        
        status, content = self._make_request(
            URLS["listing"],
            referer=URLS["templates"]
        )
        
        if status != 200:
            logger.error(f"Failed to load listing page. Status: {status}")
            return False
            
        if not self._validate_page("listing_page", content):
            logger.error("Listing page validation failed")
            return False
            
        self._extract_data_from_page("listing_page", content)
        
        logger.info("Successfully loaded listing page")
        return True
    
    def visit_seller_shop(self) -> bool:
        """
        Step 3: Navigate to seller's shop.
        
        Returns:
            Boolean indicating success
        """
        logger.info("Step 3: Visiting seller's shop...")
        
        # Add human-like delay
        delay = get_random_delay("page2_to_page3")
        logger.info(f"Waiting {delay:.1f} seconds before visiting shop...")
        time.sleep(delay)
        
        status, content = self._make_request(
            URLS["shop"],
            referer=URLS["listing"]
        )
        
        if status != 200:
            logger.error(f"Failed to load shop page. Status: {status}")
            return False
            
        if not self._validate_page("shop_page", content):
            logger.error("Shop page validation failed")
            return False
            
        self._extract_data_from_page("shop_page", content)
        
        logger.info("Successfully loaded shop page")
        return True
    
    def run_flow(self) -> Dict:
        """
        Execute the complete 3-page flow.
        
        Returns:
            Dictionary with extracted data and success status
        """
        logger.info("Starting Etsy flow replication with curl-cffi...")
        logger.info(f"Using impersonation: {CURL_CFFI_CONFIG['impersonate']}")
        
        results = {
            "success": False,
            "pages_loaded": 0,
            "data": {},
            "errors": []
        }
        
        try:
            # Step 1: Templates page
            if self.navigate_to_templates():
                results["pages_loaded"] += 1
            else:
                results["errors"].append("Failed to load templates page")
                return results
            
            # Step 2: Listing page
            if self.select_listing():
                results["pages_loaded"] += 1
            else:
                results["errors"].append("Failed to load listing page")
                return results
            
            # Step 3: Shop page
            if self.visit_seller_shop():
                results["pages_loaded"] += 1
                results["success"] = True
            else:
                results["errors"].append("Failed to load shop page")
                
        except Exception as e:
            logger.error(f"Flow execution failed: {str(e)}")
            results["errors"].append(str(e))
        
        results["data"] = self.extracted_data
        
        # Log summary
        logger.info("="*50)
        logger.info("Flow Execution Summary:")
        logger.info(f"Success: {results['success']}")
        logger.info(f"Pages loaded: {results['pages_loaded']}/3")
        if self.extracted_data:
            logger.info("Extracted data:")
            for key, value in self.extracted_data.items():
                logger.info(f"  {key}: {value}")
        if results["errors"]:
            logger.error(f"Errors: {results['errors']}")
        logger.info("="*50)
        
        return results
    
    def close(self):
        """Clean up session."""
        if self.session:
            self.session.close()


def main():
    """Main execution for testing."""
    scraper = EtsyFlowCurlCffi()
    
    try:
        results = scraper.run_flow()
        
        # Save results
        with open('curl_cffi_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        if results["success"]:
            print("\n✓ Flow completed successfully!")
            print(f"Extracted: {results['data']}")
        else:
            print("\n✗ Flow failed!")
            print(f"Errors: {results['errors']}")
            
    finally:
        scraper.close()


if __name__ == "__main__":
    main()