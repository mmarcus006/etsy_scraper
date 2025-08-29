"""
Shop data extractors for Etsy pages.
Parses HTML to extract shop information from listing and shop pages.
"""

import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ShopExtractor:
    """Extracts shop information from Etsy pages."""
    
    def extract_shop_from_listing_page(self, html_content: str) -> Dict:
        """
        Extract shop name and URL from a listing page.
        
        Args:
            html_content: Raw HTML of the listing page
            
        Returns:
            Dictionary with shop_name and shop_url
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        shop_info = {
            'shop_name': '',
            'shop_url': ''
        }
        
        # Primary method: Look for shop link in the standard location
        # Example: <a class="wt-text-link-no-underline" href="https://www.etsy.com/shop/PrioriDigitalStudio?ref=...">
        #            <p class="wt-text-heading">PrioriDigitalStudio</p>
        #          </a>
        shop_link = soup.find('a', class_='wt-text-link-no-underline', href=re.compile(r'/shop/'))
        
        if not shop_link:
            # Alternative selector for shop link
            shop_link = soup.find('a', href=re.compile(r'etsy\.com/shop/[^?]+'))
        
        if shop_link:
            # Extract shop URL
            shop_url = shop_link.get('href', '')
            if shop_url:
                # Clean the URL - remove query parameters
                shop_url = shop_url.split('?')[0]
                # Ensure it's a full URL
                if not shop_url.startswith('http'):
                    shop_url = f"https://www.etsy.com{shop_url}"
                shop_info['shop_url'] = shop_url
                
                # Extract shop name from URL
                match = re.search(r'/shop/([^/?]+)', shop_url)
                if match:
                    shop_info['shop_name'] = match.group(1)
            
            # Try to get shop name from text if not extracted from URL
            if not shop_info['shop_name']:
                shop_name_elem = shop_link.find('p', class_='wt-text-heading')
                if shop_name_elem:
                    shop_info['shop_name'] = shop_name_elem.text.strip()
                else:
                    # Fallback to link text
                    shop_info['shop_name'] = shop_link.text.strip()
        
        # Backup method: Look for shop name in seller section
        if not shop_info['shop_name']:
            seller_elem = soup.find('span', string=re.compile(r'seller', re.IGNORECASE))
            if seller_elem and seller_elem.parent:
                # Look for shop name near the seller text
                parent = seller_elem.parent
                for elem in parent.find_all(['a', 'span']):
                    text = elem.text.strip()
                    if text and 'seller' not in text.lower() and len(text) > 2:
                        shop_info['shop_name'] = text
                        break
        
        logger.info(f"Extracted shop: {shop_info['shop_name']} - {shop_info['shop_url']}")
        return shop_info
    
    def extract_shop_metrics(self, html_content: str) -> Dict:
        """
        Extract sales and admirers metrics from a shop page.
        
        Args:
            html_content: Raw HTML of the shop page
            
        Returns:
            Dictionary with sales and admirers data
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        metrics = {
            'sales_count': '',
            'sales_has_href': False,
            'sales_url': '',
            'admirers_count': '',
            'admirers_has_href': False,
            'admirers_url': ''
        }
        
        # Method 1: Look for the metrics section between Contact and Report buttons
        # Find the contact button first as a reference point
        contact_button = soup.find('div', class_='contact-shop-owner-button')
        
        if contact_button:
            # Look for the next sibling div that contains the metrics
            metrics_container = contact_button.find_next_sibling('div')
            
            if metrics_container:
                # Extract sales
                sales_elem = metrics_container.find(string=re.compile(r'\d+\s*Sales', re.IGNORECASE))
                if sales_elem:
                    sales_text = sales_elem.strip()
                    # Extract just the number
                    match = re.search(r'(\d+(?:,\d+)*)', sales_text)
                    if match:
                        metrics['sales_count'] = match.group(1).replace(',', '')
                    
                    # Check if sales is a link
                    parent = sales_elem.parent
                    if parent and parent.name == 'a':
                        metrics['sales_has_href'] = True
                        metrics['sales_url'] = parent.get('href', '')
                
                # Extract admirers
                admirers_elem = metrics_container.find(string=re.compile(r'\d+\s*Admirers', re.IGNORECASE))
                if not admirers_elem:
                    # Sometimes it's inside a link
                    admirers_link = metrics_container.find('a', string=re.compile(r'\d+\s*Admirers', re.IGNORECASE))
                    if admirers_link:
                        admirers_elem = admirers_link.string or admirers_link.text
                        metrics['admirers_has_href'] = True
                        metrics['admirers_url'] = admirers_link.get('href', '')
                
                if admirers_elem:
                    admirers_text = str(admirers_elem).strip()
                    # Extract just the number
                    match = re.search(r'(\d+(?:,\d+)*)', admirers_text)
                    if match:
                        metrics['admirers_count'] = match.group(1).replace(',', '')
        
        # Method 2: Fallback - search for metrics anywhere on the page
        if not metrics['sales_count']:
            # Look for sales pattern anywhere
            sales_pattern = soup.find(string=re.compile(r'\d+(?:,\d+)*\s*Sales', re.IGNORECASE))
            if sales_pattern:
                match = re.search(r'(\d+(?:,\d+)*)', str(sales_pattern))
                if match:
                    metrics['sales_count'] = match.group(1).replace(',', '')
        
        if not metrics['admirers_count']:
            # Look for admirers pattern anywhere
            admirers_link = soup.find('a', href=re.compile(r'/favoriters'))
            if admirers_link:
                admirers_text = admirers_link.text.strip()
                match = re.search(r'(\d+(?:,\d+)*)', admirers_text)
                if match:
                    metrics['admirers_count'] = match.group(1).replace(',', '')
                    metrics['admirers_has_href'] = True
                    metrics['admirers_url'] = admirers_link.get('href', '')
            else:
                # Search for text pattern
                admirers_pattern = soup.find(string=re.compile(r'\d+(?:,\d+)*\s*Admirers', re.IGNORECASE))
                if admirers_pattern:
                    match = re.search(r'(\d+(?:,\d+)*)', str(admirers_pattern))
                    if match:
                        metrics['admirers_count'] = match.group(1).replace(',', '')
        
        # Clean up URLs (make them absolute if relative)
        if metrics['sales_url'] and not metrics['sales_url'].startswith('http'):
            metrics['sales_url'] = f"https://www.etsy.com{metrics['sales_url']}"
        if metrics['admirers_url'] and not metrics['admirers_url'].startswith('http'):
            metrics['admirers_url'] = f"https://www.etsy.com{metrics['admirers_url']}"
        
        logger.info(f"Extracted metrics - Sales: {metrics['sales_count']}, Admirers: {metrics['admirers_count']}")
        return metrics