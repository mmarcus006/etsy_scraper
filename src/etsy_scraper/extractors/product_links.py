"""
Product link extractor for Etsy templates pages.
Parses HTML to extract product information from listing cards.
"""

import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class ProductLinkExtractor:
    """Extracts product links and metadata from Etsy search/category pages."""
    
    def __init__(self):
        """Initialize the extractor."""
        self.listing_id_pattern = re.compile(r'/listing/(\d+)/')
        
    def extract_listing_id(self, url: str) -> Optional[str]:
        """
        Extract listing ID from Etsy URL.
        
        Args:
            url: Etsy product URL
            
        Returns:
            Listing ID or None if not found
        """
        match = self.listing_id_pattern.search(url)
        return match.group(1) if match else None
    
    def extract_shop_name_from_url(self, url: str) -> Optional[str]:
        """
        Extract shop name from shop URL.
        
        Args:
            url: Shop URL
            
        Returns:
            Shop name or None
        """
        if '/shop/' in url:
            parts = url.split('/shop/')
            if len(parts) > 1:
                shop_name = parts[1].split('?')[0].split('/')[0]
                return shop_name
        return None
    
    def clean_price(self, price_text: str) -> str:
        """
        Clean and standardize price text.
        
        Args:
            price_text: Raw price text from HTML
            
        Returns:
            Cleaned price string
        """
        # Remove extra whitespace and normalize
        price = ' '.join(price_text.split())
        # Remove "Sale Price:" or similar prefixes
        price = re.sub(r'^(Sale\s+)?Price:\s*', '', price, flags=re.IGNORECASE)
        return price.strip()
    
    def extract_products_from_html(self, html_content: str) -> List[Dict]:
        """
        Extract all product links and metadata from page HTML.
        
        Args:
            html_content: Raw HTML of the page
            
        Returns:
            List of product dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        
        # Multiple possible selectors for listing cards
        card_selectors = [
            'div.v2-listing-card',
            'div.wt-grid__item-xs-6',
            'div[data-listing-id]',
            'article.listing-card'
        ]
        
        listing_cards = []
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                listing_cards = cards
                logger.debug(f"Found {len(cards)} products using selector: {selector}")
                break
        
        if not listing_cards:
            # Fallback: look for any links to /listing/
            listing_links = soup.find_all('a', href=re.compile(r'/listing/\d+'))
            logger.warning(f"Using fallback extraction, found {len(listing_links)} listing links")
            
            for link in listing_links:
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = f"https://www.etsy.com{url}"
                
                listing_id = self.extract_listing_id(url)
                if listing_id and listing_id not in [p['listing_id'] for p in products]:
                    products.append({
                        'listing_id': listing_id,
                        'url': url.split('?')[0],  # Remove query params
                        'title': link.get('title', link.text.strip()),
                        'price': '',
                        'shop_name': '',
                        'shop_url': ''
                    })
            
            return products
        
        # Process each listing card
        for card in listing_cards:
            try:
                product = self._extract_from_card(card)
                if product and product['listing_id']:
                    # Check for duplicates
                    if product['listing_id'] not in [p['listing_id'] for p in products]:
                        products.append(product)
            except Exception as e:
                logger.error(f"Error extracting product from card: {e}")
                continue
        
        logger.info(f"Extracted {len(products)} unique products from page")
        return products
    
    def _extract_from_card(self, card) -> Optional[Dict]:
        """
        Extract product data from a single listing card.
        
        Args:
            card: BeautifulSoup element for the listing card
            
        Returns:
            Product dictionary or None
        """
        product = {
            'listing_id': '',
            'url': '',
            'title': '',
            'price': '',
            'shop_name': '',
            'shop_url': ''
        }
        
        # Try to get listing ID from data attribute first
        listing_id = card.get('data-listing-id')
        
        # Find the main product link
        link_element = card.find('a', href=re.compile(r'/listing/\d+'))
        if not link_element:
            # Try alternative selectors
            link_element = card.select_one('a.listing-link, a.listing-card-title')
        
        if link_element:
            url = link_element.get('href', '')
            if not url.startswith('http'):
                url = f"https://www.etsy.com{url}"
            
            product['url'] = url.split('?')[0]  # Remove query params
            
            if not listing_id:
                listing_id = self.extract_listing_id(url)
            
            product['listing_id'] = listing_id or ''
            
            # Extract title
            title_element = link_element.find('h3') or link_element.find('h2')
            if title_element:
                product['title'] = title_element.text.strip()
            else:
                product['title'] = link_element.get('title', link_element.text.strip())
        
        # Extract price
        price_selectors = [
            'span.currency-value',
            'span.wt-text-title-01',
            'p.wt-text-title-01',
            'span.currency',
            '[data-buy-box-region="price"] span'
        ]
        
        for selector in price_selectors:
            price_element = card.select_one(selector)
            if price_element:
                product['price'] = self.clean_price(price_element.text)
                break
        
        # Extract shop info
        shop_link = card.select_one('a[href*="/shop/"]')
        if shop_link:
            shop_url = shop_link.get('href', '')
            if not shop_url.startswith('http'):
                shop_url = f"https://www.etsy.com{shop_url}"
            
            product['shop_url'] = shop_url.split('?')[0]
            product['shop_name'] = self.extract_shop_name_from_url(shop_url) or ''
            
            # If shop name not in URL, try text
            if not product['shop_name']:
                product['shop_name'] = shop_link.text.strip()
        
        return product if product['listing_id'] else None